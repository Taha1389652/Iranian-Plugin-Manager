# Released under the MIT License. See LICENSE for details.
#
"""Implements football games (both co-op and teams varieties)."""

# ba_meta require api 9
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

from typing import TYPE_CHECKING

import babase
import bascenev1 as bs
import random
import math
import colorsys
import json
import os
import traceback
from bascenev1lib.actor.spaz import Spaz
from bascenev1lib.game.hockey import PuckDiedMessage, Player, Team, HockeyGame
from bascenev1lib.gameutils import SharedObjects
from bascenev1lib.actor.scoreboard import Scoreboard
from bascenev1lib.actor.powerupbox import PowerupBoxFactory
from bascenev1lib.actor.playerspaz import PlayerSpaz, PlayerSpazHurtMessage
from bascenev1lib.actor.spazfactory import SpazFactory
from bascenev1lib.actor.popuptext import PopupText

if TYPE_CHECKING:
    from typing import Any, Sequence, Dict, Type, List, Optional, Union, Tuple


# --- stretch-jump (back-to-back jumps reach just above the crossbar) --------
JUMP_COMBO_WINDOW = 0.9     # s: a jump this soon after the last one = combo
JUMP_HEAD_CLEARANCE = 0.12  # m: how far the HEAD should pass above the bar
JUMP_HEAD_OFFSET = 0.75     # m: head height above the spaz node position
JUMP_MAX_TIME = 0.8         # s: the boost loop never runs longer than this
JUMP_STRETCH_MAX = 1.18     # body scale at the top of a boosted jump

# --- double jump (a second jump while already in the air) -------------------
DJ_TARGET_VY = 6.0          # m/s: fallback if the first jump was not measured
DJ_MAX_TIME = 0.35          # s: the push loop never runs longer than this
DJ_AIR_GAP = 0.3            # m: higher than this above the ground = airborne
DJ_MIN_DELAY = 0.12         # s: min time between the two jump presses
DJ_MAX_PUSH_DV = 3.0        # m/s: max speed gained per 16 ms push


class BombControlSpaz(PlayerSpaz):
    """PlayerSpaz that can be forbidden from dropping bombs, and (optionally)
    stretches upwards on back-to-back jumps so the head just clears the
    crossbar."""

    bombs_allowed: bool = True

    # stretch-jump state (switched on by the game in spawn_player)
    jump_boost: bool = False
    head_target_y: Optional[float] = None
    jump_gravity: float = 20.0
    _jcombo: int = 0
    _jlast: float = -99.0
    _jtimer: Optional[bs.Timer] = None
    _jend: float = 0.0
    _jprev: Optional[Tuple[float, float, float]] = None   # (t, vy, mag)
    _jgain: float = 0.0        # measured vertical velocity gained per unit mag
    _no_stretch: bool = False

    # double-jump state (switched on by the game in spawn_player)
    double_jump: bool = False
    _dj_used: bool = False
    _dj_first_vy: float = 0.0   # peak upward speed of the ground jump
    _dj_target: float = 6.0
    _dj_ground_y: Optional[float] = None
    _dj_press_t: float = -99.0
    _dj_end: float = 0.0
    _dj_prev: Optional[Tuple[float, float, float]] = None  # (t, vy, mag)
    _dj_timer: Optional[bs.Timer] = None
    _dj_gtimer: Optional[bs.Timer] = None

    # ---- double jump -------------------------------------------------------
    def _dj_ground_tick(self) -> None:
        """Learns the floor height and re-arms the air jump on landing."""
        node = self.node
        if not node:
            self._dj_gtimer = None
            return
        y = node.position[1]
        vy = node.velocity[1]
        if self._dj_ground_y is None or y < self._dj_ground_y:
            self._dj_ground_y = y
        if y < self._dj_ground_y + DJ_AIR_GAP:
            self._dj_used = False
            if vy < 1.0:                       # standing: forget old jump
                self._dj_first_vy = 0.0
        if not self._dj_used and vy > self._dj_first_vy:
            self._dj_first_vy = vy             # measure the first jump

    def _try_air_jump(self) -> bool:
        """Returns True if this jump press was used as an air jump."""
        node = self.node
        if not node or not self.is_alive():
            return False
        now = bs.time()
        if self._dj_gtimer is None:
            self._dj_gtimer = bs.Timer(0.016,
                                       bs.WeakCall(self._dj_ground_tick),
                                       repeat=True)
        y = node.position[1]
        if not self._dj_used and node.velocity[1] > self._dj_first_vy:
            self._dj_first_vy = node.velocity[1]
        if self._dj_ground_y is None or y < self._dj_ground_y:
            self._dj_ground_y = y
        since = now - self._dj_press_t
        self._dj_press_t = now
        if y < self._dj_ground_y + DJ_AIR_GAP:     # on the ground: normal jump
            self._dj_used = False
            return False
        if self._dj_used or since < DJ_MIN_DELAY:
            return False
        self._dj_used = True
        # same speed as the first jump (measured), so the same height
        self._dj_target = (min(self._dj_first_vy, 12.0)
                           if self._dj_first_vy > 3.0 else DJ_TARGET_VY)
        # the stretch-jump loop must not fight with the air jump
        self._jtimer = None
        self._jprev = None
        self._dj_end = now + DJ_MAX_TIME
        self._dj_prev = None
        self._dj_timer = bs.Timer(0.016, bs.WeakCall(self._dj_tick),
                                  repeat=True)
        return True

    def _dj_tick(self) -> None:
        """Pushes the player upwards until the air jump speed is reached."""
        try:
            node = self.node
            now = bs.time()
            if not node or now > self._dj_end or not self.is_alive():
                self._dj_stop()
                return
            pos, vel = node.position, node.velocity
            vy = vel[1]
            g = max(self.jump_gravity, 8.0)
            # learn how much the last push really changed vy (shared gain)
            if self._dj_prev is not None:
                pt, pvy, pmag = self._dj_prev
                dt = max(now - pt, 1e-3)
                dv = (vy - pvy) + g * dt
                if pmag > 0.0 and dv > 0.02:
                    k = dv / pmag
                    self._jgain = k if self._jgain <= 0 else (
                        0.5 * self._jgain + 0.5 * k)
            if vy >= self._dj_target:
                self._dj_stop()
                return
            dv_wanted = min(self._dj_target - vy, DJ_MAX_PUSH_DV)
            if self._jgain > 0.0:
                mag = min(dv_wanted / self._jgain, 6000.0)
            else:
                mag = 150.0                       # probe push, then learn
            if mag > 1.0:
                node.handlemessage('impulse', pos[0], pos[1], pos[2],
                                   0, 0, 0, mag, 0, 0, 0, 0, 1.0, 0)
            self._dj_prev = (now, vy, mag)
        except Exception:
            traceback.print_exc()
            self._dj_stop()

    def _dj_stop(self) -> None:
        self._dj_timer = None
        self._dj_prev = None

    def on_jump_press(self) -> None:
        super().on_jump_press()
        if self.double_jump:
            try:
                if self._try_air_jump():
                    return
            except Exception:
                traceback.print_exc()
        if not self.jump_boost or self.head_target_y is None or not self.node:
            return
        try:
            now = bs.time()
            if now - self._jlast <= JUMP_COMBO_WINDOW:
                self._jcombo += 1
            else:
                self._jcombo = 1
            self._jlast = now
            if self._jcombo >= 2:                 # only BACK-TO-BACK jumps
                self._jend = now + JUMP_MAX_TIME
                self._jprev = None
                self._jtimer = bs.Timer(0.016, bs.WeakCall(self._jump_tick),
                                        repeat=True)
        except Exception:
            traceback.print_exc()

    def _set_stretch(self, f: float) -> None:
        if self._no_stretch or not self.node:
            return
        try:
            self.node.mesh_scale = f
        except Exception:                         # engine has no such scale
            self._no_stretch = True

    def _jump_tick(self) -> None:
        """Closed loop: while rising, add upward push until the predicted
        apex of the HEAD is just above the crossbar; never above it."""
        try:
            node = self.node
            now = bs.time()
            if (not node or self.head_target_y is None or now > self._jend
                    or not self.is_alive()):
                self._jump_stop()
                return
            pos, vel = node.position, node.velocity
            y, vy = pos[1], vel[1]
            if vy <= 0.3:                         # past the apex: done
                if self._jprev is not None:
                    self._jump_stop()
                return
            g = max(self.jump_gravity, 8.0)
            # learn how much the last push really changed vy
            if self._jprev is not None:
                pt, pvy, pmag = self._jprev
                dt = max(now - pt, 1e-3)
                dv = (vy - pvy) + g * dt
                if pmag > 0.0 and dv > 0.02:
                    k = dv / pmag
                    self._jgain = k if self._jgain <= 0 else (
                        0.5 * self._jgain + 0.5 * k)
            head = y + JUMP_HEAD_OFFSET
            room = self.head_target_y - head      # height still to gain
            apex_gap = room - vy * vy / (2.0 * g)  # > 0: apex too low
            mag = 0.0
            if apex_gap > 0.03 and room > 0.05:
                need_vy = math.sqrt(2.0 * g * room)
                dv_wanted = min(max(need_vy - vy, 0.0), 3.0)
                if self._jgain > 0.0:
                    mag = min(dv_wanted / self._jgain, 6000.0)
                else:
                    mag = 150.0                   # probe push, then learn
                if mag > 1.0:
                    node.handlemessage('impulse', pos[0], pos[1], pos[2],
                                       0, 0, 0, mag, 0, 0, 0, 0, 1.0, 0)
            self._jprev = (now, vy, mag)
            # stretch with the climb (0 -> 1 over the way to the bar)
            frac = _clamp((head - (self.head_target_y - 1.6)) / 1.6, 0.0, 1.0)
            self._set_stretch(1.0 + (JUMP_STRETCH_MAX - 1.0) * frac)
        except Exception:
            traceback.print_exc()
            self._jump_stop()

    def _jump_stop(self) -> None:
        self._jtimer = None
        self._jprev = None
        self._set_stretch(1.0)

    def on_bomb_press(self) -> None:
        if not self.bombs_allowed:
            return
        super().on_bomb_press()

    def drop_bomb(self) -> Any:
        if not self.bombs_allowed:
            return None
        return super().drop_bomb()


class NewPlayerSpaz(BombControlSpaz):
    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, bs.HitMessage):
            source_player = msg.get_source_player(type(self._player))
            if source_player:
                self.last_player_attacked_by = source_player
                self.last_attacked_time = bs.time()
                self.last_attacked_type = (msg.hit_type, msg.hit_subtype)

            if not self.node:
                return None
            if self.node.invincible:
                SpazFactory.get().block_sound.play(1.0,
                                                   position=self.node.position)
                return True

            local_time = int(bs.time() * 1000.0)
            assert isinstance(local_time, int)
            if (self._last_hit_time is None
                    or local_time - self._last_hit_time > 1000):
                self._num_times_hit += 1
                self._last_hit_time = local_time

            mag = msg.magnitude * self.impact_scale
            velocity_mag = msg.velocity_magnitude * self.impact_scale
            damage_scale = 0.22

            if self.shield:
                if msg.flat_damage:
                    damage = msg.flat_damage * self.impact_scale
                else:
                    assert msg.force_direction is not None
                    self.node.handlemessage(
                        'impulse', msg.pos[0], msg.pos[1], msg.pos[2],
                        msg.velocity[0], msg.velocity[1], msg.velocity[2], mag,
                        velocity_mag, msg.radius, 1, msg.force_direction[0],
                        msg.force_direction[1], msg.force_direction[2])
                    damage = damage_scale * self.node.damage

                assert self.shield_hitpoints is not None
                self.shield_hitpoints -= int(damage)
                self.shield.hurt = (
                    1.0 -
                    float(self.shield_hitpoints) / self.shield_hitpoints_max)

                max_spillover = SpazFactory.get().max_shield_spillover_damage
                if self.shield_hitpoints <= 0:
                    self.shield.delete()
                    self.shield = None
                    SpazFactory.get().shield_down_sound.play(
                        1.0,
                        position=self.node.position)

                    npos = self.node.position
                    bs.emitfx(position=(npos[0], npos[1] + 0.9, npos[2]),
                              velocity=self.node.velocity,
                              count=random.randrange(20, 30),
                              scale=1.0,
                              spread=0.6,
                              chunk_type='spark')
                else:
                    SpazFactory.get().shield_hit_sound.play(
                        0.5,
                        position=self.node.position)

                assert msg.force_direction is not None
                bs.emitfx(position=msg.pos,
                          velocity=(msg.force_direction[0] * 1.0,
                                    msg.force_direction[1] * 1.0,
                                    msg.force_direction[2] * 1.0),
                          count=min(30, 5 + int(damage * 0.005)),
                          scale=0.5,
                          spread=0.3,
                          chunk_type='spark')

                if self.shield_hitpoints <= -max_spillover:
                    leftover_damage = -max_spillover - self.shield_hitpoints
                    shield_leftover_ratio = leftover_damage / damage
                    mag *= shield_leftover_ratio
                    velocity_mag *= shield_leftover_ratio
                else:
                    return True
            else:
                shield_leftover_ratio = 1.0

            if msg.flat_damage:
                damage = int(msg.flat_damage * self.impact_scale *
                             shield_leftover_ratio)
            else:
                assert msg.force_direction is not None
                if msg.hit_type != 'punch':
                    self.node.handlemessage(
                        'impulse', msg.pos[0], msg.pos[1], msg.pos[2],
                        msg.velocity[0], msg.velocity[1], msg.velocity[2], mag,
                        velocity_mag, msg.radius, 0, msg.force_direction[0],
                        msg.force_direction[1], msg.force_direction[2])
                damage = int(damage_scale * self.node.damage)
            self.node.handlemessage('hurt_sound')

            if msg.hit_type == 'punch':
                if self.node.hold_node:
                    self.node.hold_node = None
                damage = 0
                sound = SpazFactory.get().punch_sound
                sound.play(1.0, position=self.node.position)

                assert msg.force_direction is not None
                bs.emitfx(position=msg.pos,
                          velocity=(msg.force_direction[0] * 0.5,
                                    msg.force_direction[1] * 0.5,
                                    msg.force_direction[2] * 0.5),
                          count=min(10, 1 + int(100 * 0.0025)),
                          scale=0.3,
                          spread=0.03)

                bs.emitfx(position=msg.pos,
                          chunk_type='sweat',
                          velocity=(msg.force_direction[0] * 1.3,
                                    msg.force_direction[1] * 1.3 + 5.0,
                                    msg.force_direction[2] * 1.3),
                          count=min(30, 1 + int(100 * 0.04)),
                          scale=0.9,
                          spread=0.28)

                hurtiness = 100 * 0.003
                punchpos = (msg.pos[0] + msg.force_direction[0] * 0.02,
                            msg.pos[1] + msg.force_direction[1] * 0.02,
                            msg.pos[2] + msg.force_direction[2] * 0.02)
                flash_color = (1.0, 0.8, 0.4)
                light = bs.newnode(
                    'light',
                    attrs={
                        'position': punchpos,
                        'radius': 0.12 + hurtiness * 0.12,
                        'intensity': 0.3 * (1.0 + 1.0 * hurtiness),
                        'height_attenuated': False,
                        'color': flash_color
                    })
                bs.timer(0.06, light.delete)

                flash = bs.newnode('flash',
                                   attrs={
                                       'position': punchpos,
                                       'size': 0.17 + 0.17 * hurtiness,
                                       'color': flash_color
                                   })
                bs.timer(0.06, flash.delete)

            if msg.hit_type == 'impact':
                assert msg.force_direction is not None
                bs.emitfx(position=msg.pos,
                          velocity=(msg.force_direction[0] * 2.0,
                                    msg.force_direction[1] * 2.0,
                                    msg.force_direction[2] * 2.0),
                          count=min(10, 1 + int(damage * 0.01)),
                          scale=0.4,
                          spread=0.1)
            if self.hitpoints > 0:
                if msg.hit_type == 'impact' and damage > self.hitpoints:
                    newdamage = max(damage - 200, self.hitpoints - 10)
                    damage = newdamage
                self.node.handlemessage('flash')

                if damage > 0.0 and self.node.hold_node:
                    self.node.hold_node = None
                self.hitpoints -= damage
                self.node.hurt = 1.0 - float(
                    self.hitpoints) / self.hitpoints_max

                if self._cursed and damage > 0:
                    bs.timer(
                        0.05,
                        bs.WeakCall(self.curse_explode,
                                          msg.get_source_player(bs.Player)))

                if self.frozen and (damage > 200 or self.hitpoints <= 0):
                    self.shatter()
                elif self.hitpoints <= 0:
                    self.node.handlemessage(
                        bs.DieMessage(how=bs.DeathType.IMPACT))

            if self.hitpoints <= 0:
                damage_avg = self.node.damage_smoothed * damage_scale
                if damage_avg > 1000:
                    self.shatter()

            activity = self._activity()
            if activity is not None and self._player.exists():
                activity.handlemessage(PlayerSpazHurtMessage(self))
        else:
            super().handlemessage(msg)

# ===========================================================================
#  SHOT SYSTEM v3  -  pure logic (no engine calls, unit-testable offline)
# ===========================================================================
# Frame used everywhere in the planner:
#   u : along the pitch, 0 = midline, positive towards the TARGET (left) goal,
#       so the right half of the pitch has u < 0
#   v : lateral position,  y : height
# Speed rule: every kick keeps the *horizontal* speed H (random in
# SPEED_RANGE, exactly the old 'افسانه‌ای' power level) - only direction changes.
# Real hockey stadium (from the map data): goals at +-8.45, 3.0 m wide, 1.6 m
# high (floor .. 1.8 m).  Everything below is derived from the map at runtime.

BALL_RADIUS = 0.45
GRAVITY_DEFAULT = 20.0
SPEED_RANGE = (20.0, 23.0)
BALLS_PER_TURN = (5, 10)
TURN_GAP = 2.0                 # seconds between two consecutive shots
SPAWN_LEAD = 0.7               # a new batch appears this long before its 1st shot
SPAWN_POINT_COUNT = 100
SPAWN_FRONT_MARGIN = 1.3       # min distance in front of the right goal mouth
SPAWN_MID_MARGIN = 3.8         # min distance before the midline
BALL_MIN_SPACING = 1.7
TRIGGER_BEFORE_MID = 1.0       # final aim is fixed this far BEFORE the midline
DEADLINE_BEFORE_MID = 0.45     # emergency deadline (still before the midline)
V_LIMIT = 4.2                  # max lateral excursion during the feints
APEX_MAX = 5.0
VY_MAX = 15.0
VY_DOWN = 12.0
MAX_GOAL_HEIGHT = 2.6
H_MIN_AIR = 1.8                # feints never go lower than this (no ice skimming)
H_MAX_AIR = 4.5
MAX_PRE_TIME = 1.1             # hard limit for the whole feint phase (s)
DANCE_BUDGET = 0.75            # the dance is cut after this long (slow frame rates)
BACK_MARGIN = 1.7              # feints stay this far from the right goal mouth


def _clamp(x: float, lo: float, hi: float) -> float:
    return lo if x < lo else hi if x > hi else x


def _median(xs: List[float]) -> float:
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else 0.5 * (s[n // 2 - 1] + s[n // 2])


class Geometry:
    """Pitch geometry derived from the map's goal boxes (no hard-coded map)."""

    def __init__(self, goal_target: Sequence[float],
                 goal_other: Sequence[float],
                 flag_pos: Optional[Sequence[float]] = None,
                 aoi: Optional[Sequence[float]] = None):
        tx, ty, tz = goal_target[0], goal_target[1], goal_target[2]
        ox, oy, oz = goal_other[0], goal_other[1], goal_other[2]
        self.mid_x = 0.5 * (tx + ox)
        self.mid_z = 0.5 * (tz + oz)
        fx, fz = tx - ox, tz - oz
        n = math.hypot(fx, fz) or 1.0
        self.fx, self.fz = fx / n, fz / n
        self.lx, self.lz = -self.fz, self.fx
        sx, sy, sz = (abs(goal_target[6]), abs(goal_target[7]),
                      abs(goal_target[8]))
        self.goal_depth = abs(self.fx) * sx + abs(self.fz) * sz
        self.goal_width = abs(self.lx) * sx + abs(self.lz) * sz
        cu, cv, _ = self.to_frame(tx, ty, tz)
        self.goal_cu, self.goal_cv = cu, cv
        self.mouth_u = cu - 0.5 * self.goal_depth
        osx, osy, osz = (abs(goal_other[6]), abs(goal_other[7]),
                         abs(goal_other[8]))
        odepth = abs(self.fx) * osx + abs(self.fz) * osz
        ocu, ocv, _ = self.to_frame(ox, oy, oz)
        self.other_mouth_u = ocu + 0.5 * odepth
        self.other_cu, self.other_cv, self.other_depth = ocu, ocv, odepth
        self.floor_y = float(flag_pos[1]) if flag_pos is not None else 0.0
        self.ball_r = BALL_RADIUS
        self.rest_y = self.floor_y + self.ball_r
        self.goal_top = ty + 0.5 * sy
        self.goal_bottom = ty - 0.5 * sy
        lat_extent = 26.0
        if aoi is not None:
            lat_extent = (abs(self.lx) * abs(aoi[6]) +
                          abs(self.lz) * abs(aoi[8]))
        self.v_spawn = _clamp(0.30 * lat_extent, 2.5, 4.2)
        # box in which the ball is allowed to dance before the final aim
        self.u_front = -(TRIGGER_BEFORE_MID + 1.7)
        self.u_back = max(self.other_mouth_u + BACK_MARGIN, self.u_front - 6.0)

    # --- coordinate helpers -------------------------------------------------
    def to_frame(self, x: float, y: float, z: float) -> Tuple[float, float, float]:
        dx, dz = x - self.mid_x, z - self.mid_z
        return (dx * self.fx + dz * self.fz, dx * self.lx + dz * self.lz, y)

    def to_world(self, u: float, v: float, y: float) -> Tuple[float, float, float]:
        return (self.mid_x + u * self.fx + v * self.lx, y,
                self.mid_z + u * self.fz + v * self.lz)

    def vel_to_frame(self, vx: float, vz: float) -> Tuple[float, float]:
        return (vx * self.fx + vz * self.fz, vx * self.lx + vz * self.lz)

    def vel_to_world(self, hu: float, hv: float) -> Tuple[float, float]:
        return (hu * self.fx + hv * self.lx, hu * self.fz + hv * self.lz)

    def set_rest(self, rest_y: float) -> None:
        """Learn the real ball radius from the height of a resting ball."""
        self.rest_y = rest_y
        self.ball_r = _clamp(rest_y - self.floor_y + 0.04, 0.25, 0.7)

    # --- goal window --------------------------------------------------------
    def _top(self) -> float:
        return min(self.goal_top, self.floor_y + MAX_GOAL_HEIGHT)

    def window(self) -> Tuple[float, float, float]:
        """(half_width, y_mid, y_top): aiming window for the BALL CENTRE.
        y_mid = middle of the goal opening, y_top = highest centre height that
        still passes under the crossbar. Nothing is ever aimed below the
        middle of the goal."""
        r = self.ball_r
        half_w = max(0.3, 0.5 * self.goal_width - (r + 0.10))
        y_top = self._top() - (1.1 * r + 0.07)
        y_mid = max(0.5 * (self.goal_bottom + self._top()), self.rest_y + 0.25)
        if y_top < y_mid + 0.15:
            y_mid = y_top - 0.15
        return half_w, y_mid, y_top

    def target_point(self, a: float, b: float) -> Tuple[float, float, float]:
        half_w, y_lo, y_hi = self.window()
        return (self.mouth_u, self.goal_cv + a * half_w,
                y_lo + b * (y_hi - y_lo))

    def crossing_ok(self, v: float, y: float) -> bool:
        """Physical acceptance test for the ball centre at the goal mouth."""
        return self.crossing_reason(v, y) == 'ok'

    def crossing_reason(self, v: float, y: float) -> str:
        if abs(v - self.goal_cv) > 0.5 * self.goal_width - 0.8 * self.ball_r:
            return 'wide'
        if y > self._top() - 0.8 * self.ball_r:
            return 'high'
        if y < self.rest_y - 0.05:
            return 'low'
        return 'ok'


class FlightModel:
    """Ballistic flight with optional linear drag k (k=0 => pure gravity)."""

    def __init__(self, g: float = GRAVITY_DEFAULT, k: float = 0.0):
        self.g, self.k = g, k
        self.g_base = g

    def horiz_time(self, dist: float, h0: float) -> float:
        if dist <= 0.0:
            return 1e-3
        if self.k < 1e-4:
            return dist / h0
        x = min(0.95, self.k * dist / h0)
        return -math.log(1.0 - x) / self.k

    def solve_vy(self, y0: float, y1: float, t: float) -> float:
        t = max(t, 1e-3)
        g, k = self.g, self.k
        if k < 1e-4:
            return (y1 - y0) / t + 0.5 * g * t
        e = math.exp(-k * t)
        return (y1 - y0 + g * t / k) * k / (1.0 - e) - g / k


class PhysCalib:
    """Learns the real gravity / drag from live flights (shared by shots).

    g   : gravity.  Measured from BALL POSITIONS (second difference of three
          consecutive samples, exact for any frame rate) - falling balls and
          every flight.  Velocity read-outs are only a fallback.
    off : correction learned from how high the ball REALLY arrived at the
          goal (covers physics-step effects, drag, ...)
    """

    def __init__(self) -> None:
        self.g = GRAVITY_DEFAULT
        self.k = 0.0
        self.off = 0.0
        self.learned = 0
        self.pos_learned = 0

    def pick_g(self, pos_gs: List[float], vel_gs: List[float]
               ) -> Tuple[float, bool]:
        if len(pos_gs) >= 2:
            return _median(pos_gs), True
        if len(vel_gs) >= 3:
            g = _median(vel_gs)
            if self.pos_learned == 0 or abs(g - self.g) <= 0.3 * self.g:
                return g, False
        return self.g, False

    @staticmethod
    def fit_vertical(acc: List[Tuple[float, float]]
                     ) -> Optional[Tuple[float, float]]:
        """acc = [(vertical speed, measured vertical acceleration)] ->
        (g, k) from  a = -g - k*vy  (least squares)."""
        if len(acc) < 6:
            return None
        vs = [a[0] for a in acc]
        if max(vs) - min(vs) < 6.0:
            return None
        n = float(len(acc))
        mv = sum(vs) / n
        ma = sum(a[1] for a in acc) / n
        sxx = sum((v - mv) ** 2 for v in vs)
        if sxx < 1e-6:
            return None
        slope = sum((v - mv) * (a[1] - ma) for v, a in zip(vs, acc)) / sxx
        g = -(ma - slope * mv)
        k = -slope
        if not (8.0 <= g <= 50.0 and -0.05 <= k <= 0.8):
            return None
        return g, max(k, 0.0)

    def model_for(self, pos_gs: List[float], vel_gs: List[float],
                  ks: List[float], acc: Optional[List[Tuple[float, float]]] = None
                  ) -> FlightModel:
        g, _pos = self.pick_g(pos_gs, vel_gs)
        k = self.k
        fit = self.fit_vertical(acc) if acc else None
        if fit is not None:
            g, k = fit
        elif len(ks) >= 3:
            k = _median(ks)
        g = _clamp(g, 8.0, 50.0)
        m = FlightModel(_clamp(g + self.off, 8.0, 60.0), _clamp(k, 0.0, 0.6))
        m.g_base = g
        return m

    def absorb_residual(self, err_y: float, flight_t: float,
                        model: FlightModel) -> None:
        """err_y = real height at the goal minus the planned height."""
        if flight_t < 0.15:
            return
        err_y = _clamp(err_y, -1.2, 1.2)
        self.learned += 1
        if abs(err_y) < 0.02:
            return
        want = model.g - 2.0 * err_y / (flight_t * flight_t)
        off_new = _clamp(want - model.g_base, -8.0, 14.0)
        self.off += 0.5 * (off_new - self.off)

    def absorb(self, pos_gs: List[float], vel_gs: List[float], ks: List[float],
               acc: Optional[List[Tuple[float, float]]] = None) -> None:
        fit = self.fit_vertical(acc) if acc else None
        g, pos = self.pick_g(pos_gs, vel_gs)
        if fit is not None:
            g, pos = fit[0], True
            self.k += 0.4 * (_clamp(fit[1], 0.0, 0.6) - self.k)
        elif len(ks) >= 3:
            self.k += 0.3 * (_clamp(_median(ks), 0.0, 0.6) - self.k)
        if pos:
            w = 1.0 if self.pos_learned == 0 else 0.4
            self.g += w * (_clamp(g, 8.0, 50.0) - self.g)
            self.pos_learned += 1
            self.learned += 1
        elif len(vel_gs) >= 3 and self.pos_learned == 0:
            self.g += 0.3 * (_clamp(g, 8.0, 50.0) - self.g)
            self.learned += 1


# --- pattern library --------------------------------------------------------
# A script is a list of legs (duration s, heading deg, ball height m at the end
# of the leg).  heading: 0 = towards the goal, +-90 = sideways, +-180 = back
# towards the right goal.  Every leg changes the direction of the ball (speed
# stays H).  All legs are executed before the midline; the very last step is
# the "approach" (flies to the point v_pre at height hf) and the final aim.
_LAT_FRACS = [-0.90, -0.80, -0.68, -0.54, -0.38, -0.2, 0.0, 0.2, 0.38, 0.54,
              0.68, 0.80, 0.90]
_TOP_B = [0.72, 0.82, 0.91, 1.0]       # ALL shots end right under the crossbar
_VARIANTS = 5


def _make_script(rng: random.Random):
    """8-12 direction changes: lift-off, then forward / sideways / BACKWARDS
    legs (never two backward legs in a row, so there is always room to go
    back again), the height goes up and down all the time."""
    n = rng.randint(8, 10)
    legs = [(0.09, rng.uniform(-20.0, 20.0), rng.choice((2.6, 3.0, 3.4)))]
    kinds = ['F']
    sign = rng.choice((-1.0, 1.0))
    high = False
    for i in range(1, n):
        if kinds[-1] == 'B':
            kind = 'F' if rng.random() < 0.6 else 'S'
        else:
            kind = 'B' if rng.random() < 0.6 else rng.choice(('F', 'S'))
        kinds.append(kind)
    # at least 3 backward legs (no two adjacent)
    guard = 0
    while kinds.count('B') < 3 and guard < 50:
        guard += 1
        i = rng.randrange(1, n)
        if kinds[i] != 'B' and kinds[i - 1] != 'B' and (
                i + 1 >= n or kinds[i + 1] != 'B'):
            kinds[i] = 'B'
    for i in range(1, n):
        kind = kinds[i]
        mag = {'F': rng.uniform(25.0, 65.0), 'S': rng.uniform(75.0, 105.0),
               'B': rng.uniform(125.0, 178.0)}[kind]
        sign = -sign                               # left, right, left ...
        high = not high                            # up, down, up, down ...
        h = rng.uniform(3.4, 4.4) if high else rng.uniform(1.9, 2.3)
        # a backward leg of 125..178 deg has almost no sideways part, so its
        # sign is what makes the next sideways leg a real reversal: keep the
        # sign of the SIDEWAYS motion alternating for every leg
        legs.append((rng.uniform(0.045, 0.075), sign * mag, h))
    total = sum(l[0] for l in legs)
    if total > 0.66:
        k = 0.66 / total
        legs = [(d * k, hd, h) for d, hd, h in legs]
    vpre = rng.choice((-3.2, -2.4, -1.6, 1.6, 2.4, 3.2))
    hf = rng.choice((2.3, 2.7, 3.1, 3.5))
    return legs, vpre, hf


class Pattern:
    __slots__ = ('pid', 'a', 'b', 'mirror', 'legs', 'vpre', 'hf')

    def __init__(self, pid: str, a: float, b: float, mirror: int,
                 legs: list, vpre: float, hf: float):
        self.pid, self.a, self.b, self.mirror = pid, a, b, mirror
        self.legs, self.vpre, self.hf = legs, vpre, hf

    def label(self) -> str:
        return '%s(a=%+.2f,b=%.2f,legs=%d,hf=%.1f)' % (
            self.pid, self.a, self.b, len(self.legs), self.hf)


def build_pattern_library() -> List[Pattern]:
    """260 patterns: 13 lateral aims x 4 heights under the bar x 5 dances
    (every dance lasts 0.5-0.66 s)."""
    pats: List[Pattern] = []
    zi = 0
    for b in _TOP_B:
        for a in _LAT_FRACS:
            for j in range(_VARIANTS):
                rng = random.Random(1000003 * zi + 7919 * j + 17)
                legs, vpre, hf = _make_script(rng)
                mir = -1 if (zi + j) % 2 else 1
                pats.append(Pattern('T%03d' % (len(pats) + 1), a, b, mir,
                                    legs, vpre, hf))
            zi += 1
    return pats


def _halton(i: int, base: int) -> float:
    f, r = 1.0, 0.0
    while i > 0:
        f /= base
        r += f * (i % base)
        i //= base
    return r


def build_spawn_points(geo: Geometry,
                       count: int = SPAWN_POINT_COUNT
                       ) -> List[Tuple[float, float]]:
    """100 distinct (u, v) points: right half, in front of the right goal."""
    u_lo = geo.other_mouth_u + SPAWN_FRONT_MARGIN
    u_hi = -SPAWN_MID_MARGIN
    if u_hi - u_lo < 2.5:
        u_lo = u_hi - 2.5
    v_lim = geo.v_spawn
    pts: List[Tuple[float, float]] = []
    i = 7
    while len(pts) < count and i < 5000:
        i += 1
        p = (u_lo + (u_hi - u_lo) * _halton(i, 2),
             -v_lim + 2.0 * v_lim * _halton(i, 3))
        if all(math.hypot(p[0] - q[0], p[1] - q[1]) >= 0.42 for q in pts):
            pts.append(p)
    return pts


class PatternRegistry:
    """Persistent pattern status (live misses)."""
    FILE_NAME = 'buffon_jon_results.json'

    def __init__(self, path: Optional[str] = None, use_default: bool = True):
        self.path = path
        if path is None and use_default:
            self.path = self._default_path()
        self.patterns: Dict[str, Dict[str, Any]] = {}
        self.shots: List[Dict[str, Any]] = []
        self._load()

    @staticmethod
    def _default_path() -> Optional[str]:
        try:
            base = None
            env = getattr(babase.app, 'env', None)
            if env is not None:
                base = getattr(env, 'python_directory_user', None)
            if not base:
                base = getattr(babase.app, 'python_directory_user', None)
            if base and os.path.isdir(base):
                return os.path.join(base, PatternRegistry.FILE_NAME)
        except Exception:
            pass
        return None

    def _load(self) -> None:
        if not self.path or not os.path.exists(self.path):
            return
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                d = json.load(f)
            self.patterns = d.get('patterns', {})
            self.shots = d.get('shots', [])[-400:]
        except Exception:
            self.patterns, self.shots = {}, []

    def save(self) -> None:
        if not self.path:
            return
        try:
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump({'version': 1, 'patterns': self.patterns,
                           'shots': self.shots[-400:]}, f, ensure_ascii=False,
                          indent=1)
        except Exception:
            pass

    def entry(self, pid: str) -> Dict[str, Any]:
        return self.patterns.setdefault(
            pid, {'status': 'sim_ok', 'runs': 0, 'goals': 0,
                  'live_goal': 0, 'live_miss': 0})

    def status(self, pid: str) -> str:
        return self.patterns.get(pid, {}).get('status', 'sim_ok')

    def record_live(self, pid: str, goal: bool, clean: bool) -> None:
        e = self.entry(pid)
        if goal:
            e['live_goal'] += 1
        elif clean:
            e['live_miss'] += 1
            if e['live_miss'] >= 3 and e['live_miss'] > 2 * e['live_goal']:
                e['status'] = 'quarantine'


class PatternBook:
    """All patterns + usability filter + non-repeating random picking."""

    def __init__(self, registry: PatternRegistry, rng: random.Random):
        self.registry = registry
        self._rng = rng
        self.patterns = build_pattern_library()
        self.by_id = {p.pid: p for p in self.patterns}
        self.session_bad: set = set()
        self._bag: List[str] = []

    def usable(self) -> List[Pattern]:
        return [p for p in self.patterns
                if p.pid not in self.session_bad and
                self.registry.status(p.pid) != 'quarantine']

    def pick(self, exclude: Sequence[str] = ()) -> Optional[Pattern]:
        ids = {p.pid for p in self.usable()}
        for _ in range(3):
            if not self._bag:
                self._bag.extend(sorted(ids))
                if not self._bag:
                    return None
                self._rng.shuffle(self._bag)
            while self._bag:
                pid = self._bag.pop()
                if pid in ids and pid not in exclude:
                    return self.by_id[pid]
        return None


def emergency_cmd(geo: Geometry, model: FlightModel, speed: float, u: float,
                  v: float, y: float) -> Tuple[float, float, float]:
    """Last-resort kick: straight at the top centre of the goal."""
    ut, vt, yt = geo.target_point(0.0, 1.0)
    du, dv = ut - u, vt - v
    dh = math.hypot(du, dv) or 1e-3
    t = model.horiz_time(dh, speed)
    vy = _clamp(model.solve_vy(y, yt, t), -VY_DOWN, VY_MAX)
    return (speed * du / dh, speed * dv / dh, vy)


class ShotController:
    """Closed-loop kick controller for ONE ball.

    update() is called every poll with the ball state and returns None or a new
    velocity command (hu, hv, vy) in the pitch frame.
    * script legs: 8-12 direction changes (up, down, sideways, BACKWARDS ...)
      inside the feint box, all before the midline, horizontal speed == H
    * approach: one more leg to the trigger line (still before the midline)
    * final aim: ONE command at the trigger line, aimed straight at the chosen
      point right under the crossbar; afterwards the controller never
      commands again.
    """

    def __init__(self, geo: Geometry, pattern: Pattern, speed: float,
                 calib: PhysCalib):
        self.geo, self.p, self.H, self.calib = geo, pattern, speed, calib
        self.leg = -1
        self.leg_t0 = 0.0
        self.t0: Optional[float] = None
        self.done = False
        self.final: Optional[Dict[str, Any]] = None
        self.cmds: List[Tuple[float, float, float, float, float, float, float]] = []
        self.gs: List[float] = []          # gravity from velocity read-outs
        self.pos_gs: List[float] = []      # gravity from positions (preferred)
        self.acc: List[Tuple[float, float]] = []   # (vertical speed, accel.)
        self.ks: List[float] = []
        self._pts: List[Tuple[float, float]] = []
        self._prev: Optional[Tuple[float, float, float, float]] = None
        self._issued_prev = True
        self.model = FlightModel(calib.g, calib.k)

    # --- calibration samples --------------------------------------------
    def _observe(self, t: float, y: float, vy: float, hh: float) -> None:
        low = self.geo.floor_y + self.geo.ball_r + 0.45
        # (1) positions: second difference of three samples taken AFTER the
        #     last command  ->  a = acceleration, independent of the kick
        if self._issued_prev:
            self._pts = []
        self._pts.append((t, y))
        if len(self._pts) > 3:
            self._pts.pop(0)
        if len(self._pts) == 3:
            (t0, y0), (t1, y1), (t2, y2) = self._pts
            d1, d2 = t1 - t0, t2 - t1
            if (0.008 <= d1 <= 0.1 and 0.008 <= d2 <= 0.1 and
                    min(y0, y1, y2) > low):
                a = 2.0 * ((y2 - y1) / d2 - (y1 - y0) / d1) / (d1 + d2)
                vmid = (y2 - y0) / (t2 - t0)
                self.acc.append((vmid, a))
                g = -a - self.calib.k * vmid
                if 5.0 < g < 60.0:
                    self.pos_gs.append(g)
        # (2) velocity read-outs (fallback only)
        prev = self._prev
        if prev is not None and not self._issued_prev:
            dt = t - prev[0]
            if 0.008 <= dt <= 0.12 and y > low and prev[1] > low:
                gs = (prev[2] - vy) / dt - self.calib.k * 0.5 * (vy + prev[2])
                if 5.0 < gs < 60.0:
                    self.gs.append(gs)
                if prev[3] > 6.0 and hh > 6.0:
                    ks = math.log(prev[3] / hh) / dt
                    if -0.5 < ks < 3.0:
                        self.ks.append(ks)
        self._prev = (t, y, vy, hh)

    # --- main entry ---------------------------------------------------------
    def update(self, t: float, u: float, v: float, y: float,
               hu: float, hv: float, vy: float
               ) -> Optional[Tuple[float, float, float]]:
        if self.done:
            return None
        prev_t = self._prev[0] if self._prev else t
        self._observe(t, y, vy, math.hypot(hu, hv))
        if self.t0 is None:
            self.t0 = t
        u_trig = -TRIGGER_BEFORE_MID
        look = max(t - prev_t, 1.0 / 60.0) * max(hu, 0.0)
        cmd = None
        if (u + look >= u_trig or u >= -DEADLINE_BEFORE_MID or
                t - self.t0 > MAX_PRE_TIME):
            cmd = self._final_cmd(u, v, y)
            self.done = True
        else:
            legs = self.p.legs
            if self.leg < 0:
                self.leg, self.leg_t0 = 0, t
                cmd = self._script_leg(0, u, v, y)
            elif self.leg < len(legs):
                if t - self.t0 >= DANCE_BUDGET:
                    # slow frame rate: cut the rest of the dance, go on
                    self.leg, self.leg_t0 = len(legs), t
                    cmd = self._approach_cmd(u, v, y)
                elif t - self.leg_t0 >= legs[self.leg][0] - 1e-6:
                    self.leg += 1
                    self.leg_t0 = t
                    if self.leg < len(legs):
                        cmd = self._script_leg(self.leg, u, v, y)
                    else:
                        cmd = self._approach_cmd(u, v, y)
        self._issued_prev = cmd is not None
        if cmd is not None:
            self.cmds.append((t, u, v, y, cmd[0], cmd[1], cmd[2]))
        return cmd

    def _g_now(self) -> float:
        """Best gravity estimate right now (this flight's own samples first)."""
        g, _pos = self.calib.pick_g(self.pos_gs, self.gs)
        return _clamp(g + self.calib.off, 8.0, 60.0)

    def _vertical(self, y: float, h_tgt: float, dur: float) -> float:
        g = self._g_now()
        vy = FlightModel(g, 0.0).solve_vy(y, h_tgt, max(dur, 0.04))
        vy = _clamp(vy, -VY_DOWN, VY_MAX)
        if vy > 0.0 and y + vy * vy / (2.0 * g) > self.geo.floor_y + APEX_MAX:
            vy = math.sqrt(2.0 * g * max(0.1, self.geo.floor_y + APEX_MAX - y))
        return vy

    def _inside_box(self, u: float, v: float, th: float, d_eff: float
                    ) -> float:
        """Nearest heading to th for which the ball stays inside the feint box
        (it may not get close to the right goal, the side boards or the
        midline).  Never changes the speed - only the direction."""
        geo, H = self.geo, self.H
        for k in range(0, 181, 5):
            for sgn in ((1.0, -1.0) if k else (1.0,)):
                a = th + sgn * math.radians(k)
                ue = u + H * math.cos(a) * d_eff
                ve = v + H * math.sin(a) * d_eff
                if geo.u_back <= ue <= geo.u_front and abs(ve) <= V_LIMIT:
                    return a
        cu = 0.5 * (geo.u_back + geo.u_front)
        return math.atan2(-v, cu - u)

    def _script_leg(self, idx: int, u: float, v: float, y: float
                    ) -> Tuple[float, float, float]:
        geo = self.geo
        dur, head, h_end = self.p.legs[idx]
        th = math.radians(head * self.p.mirror)
        d_eff = dur + 0.025
        th = self._inside_box(u, v, th, d_eff)
        cx, sx = math.cos(th), math.sin(th)
        h_tgt = _clamp(h_end, H_MIN_AIR, H_MAX_AIR)
        if idx == 0:                # lift off: limited by the maximum kick
            g = self._g_now()
            reach = y + VY_MAX * dur - 0.5 * g * dur * dur - 0.05
            h_tgt = max(min(h_tgt, reach), y + 0.8)
        return (self.H * cx, self.H * sx, self._vertical(y, h_tgt, dur))

    def _approach_cmd(self, u: float, v: float, y: float
                      ) -> Tuple[float, float, float]:
        du = max(-TRIGGER_BEFORE_MID - u, 0.3)
        v_pre = _clamp(self.p.vpre, -V_LIMIT + 0.4, V_LIMIT - 0.4)
        dv = v_pre - v
        dh = math.hypot(du, dv)
        t = dh / self.H
        h_tgt = _clamp(self.p.hf, 2.0, H_MAX_AIR)
        return (self.H * du / dh, self.H * dv / dh,
                self._vertical(y, h_tgt, t))

    def _final_cmd(self, u: float, v: float, y: float
                   ) -> Tuple[float, float, float]:
        model = self.calib.model_for(self.pos_gs, self.gs, self.ks, self.acc)
        self.model = model
        ut, vt, yt = self.geo.target_point(self.p.a, self.p.b)
        du, dv = ut - u, vt - v
        dh = math.hypot(du, dv) or 1e-3
        T = model.horiz_time(dh, self.H)
        vy = model.solve_vy(y, yt, T)
        clamped = vy > VY_MAX
        vy = min(vy, VY_MAX)
        self.final = {'u': u, 'v': v, 'y': y, 'T': T, 'vy': vy,
                      'target': (ut, vt, yt), 'g': model.g, 'k': model.k,
                      'clamped': clamped}
        return (self.H * du / dh, self.H * dv / dh, vy)


class VirtualWorld:
    """Tiny physics world used for pre-flight checks and offline tests."""

    def __init__(self, geo: Geometry, g: float = GRAVITY_DEFAULT,
                 k: float = 0.0, restitution: float = 0.35,
                 floor_drag: float = 0.97, phys_dt: float = 1.0 / 120.0,
                 poll_dt: float = 1.0 / 30.0, speed_noise: float = 0.0,
                 rng: Optional[random.Random] = None):
        self.geo, self.g, self.k = geo, g, k
        self.e, self.fd = restitution, floor_drag
        self.dt, self.poll = phys_dt, poll_dt
        self.noise = speed_noise
        self.rng = rng or random.Random(1)

    def run(self, ctrl: ShotController, u0: float, v0: float,
            max_t: float = 3.5) -> Dict[str, Any]:
        geo = self.geo
        rest = geo.rest_y
        u, v, y = u0, v0, rest
        hu = hv = vy = 0.0
        t = 0.0
        next_poll = 0.0
        late = 0
        max_y = y
        max_av = abs(v)
        res: Dict[str, Any] = {'ok': False, 'crossed': False}
        speeds_ok = True
        mid_cross_t = None
        min_air = 99.0
        min_u = u0
        armed = False
        while t < max_t:
            if t >= next_poll - 1e-9:
                cmd = ctrl.update(t, u, v, y, hu, hv, vy)
                if cmd is not None:
                    if u >= 0.0:
                        late += 1
                    n1 = 1.0 + (self.rng.gauss(0.0, self.noise)
                                if self.noise else 0.0)
                    hu, hv, vy = cmd[0] * n1, cmd[1] * n1, cmd[2] * n1
                    if abs(math.hypot(cmd[0], cmd[1]) - ctrl.H) > 1e-6:
                        speeds_ok = False
                next_poll += self.poll
            dt = self.dt
            pu = u
            vy -= (self.g + self.k * vy) * dt
            hu -= self.k * hu * dt
            hv -= self.k * hv * dt
            u += hu * dt
            v += hv * dt
            y += vy * dt
            if y < rest:
                y = rest
                if vy < 0.0:
                    vy = -vy * self.e if vy < -1.0 else 0.0
                    hu *= self.fd
                    hv *= self.fd
            t += dt
            if y >= H_MIN_AIR - 0.1:
                armed = True
            if armed and not res['crossed'] and not ctrl.done:
                min_air = min(min_air, y)
            min_u = min(min_u, u)
            max_y = max(max_y, y)
            max_av = max(max_av, abs(v))
            if mid_cross_t is None and u >= 0.0:
                mid_cross_t = t
            if pu < geo.mouth_u <= u:
                f = (geo.mouth_u - pu) / max(u - pu, 1e-9)
                res.update(crossed=True, v=v - hv * dt * (1 - f),
                           y=y - vy * dt * (1 - f), t=t)
                res['ok'] = geo.crossing_ok(res['v'], res['y'])
                if ctrl.final is not None:
                    # same learning step as in the real game
                    ctrl.calib.absorb_residual(
                        res['y'] - ctrl.final['target'][2], ctrl.final['T'],
                        ctrl.model)
                break
        res.update(late=late, max_y=max_y, max_abs_v=max_av,
                   speeds_ok=speeds_ok, final=ctrl.final, cmds=len(ctrl.cmds),
                   min_air=min_air, min_u=min_u, cmd_list=list(ctrl.cmds),
                   t_final=(None if ctrl.final is None else ctrl.t0))
        ctrl.calib.absorb(ctrl.pos_gs, ctrl.gs, ctrl.ks, ctrl.acc)
        return res


def preflight(geo: Geometry, pattern: Pattern, speed: float, u0: float,
              v0: float, calib: PhysCalib) -> Tuple[bool, Dict[str, Any]]:
    """Dry-run a shot in the believed physics model; True if it is valid."""
    c = PhysCalib()
    c.g, c.k, c.off = calib.g, calib.k, calib.off
    ctrl = ShotController(geo, pattern, speed, c)
    try:
        res = VirtualWorld(geo, g=c.g + c.off, k=c.k).run(ctrl, u0, v0)
    except Exception:
        return False, {}
    ok = (res['ok'] and res['late'] == 0 and res['speeds_ok'] and
          res['min_air'] >= H_MIN_AIR - 0.5 and
          res['max_y'] <= geo.floor_y + APEX_MAX + 0.8 and
          res['max_abs_v'] <= V_LIMIT + 0.8 and
          res['min_u'] >= geo.u_back - 0.8 and
          not (res['final'] or {}).get('clamped', False))
    return ok, res


class Puck(bs.Actor):
    """A lovely giant hockey puck (the ball)."""

    def __init__(self, position: Sequence[float] = (0.0, 1.0, 0.0)):
        super().__init__()
        shared = SharedObjects.get()
        activity = self.getactivity()

        self.home = (position[0], position[1], position[2])
        self._spawn_pos = (position[0], position[1] + 1.0, position[2])
        self.restores = 0
        self.retiring = False
        self.last_players_to_touch: Dict[int, Player] = {}
        self.scored = False
        self.fired = False
        self.touched_by_player = False
        self.oob = False
        self.repos_t = -99.0
        assert activity is not None
        assert isinstance(activity, BuffonJon)
        pmats = [shared.object_material, activity.puck_material]
        self.node = bs.newnode('prop',
                               delegate=self,
                               attrs={
                                   'mesh': activity.puck_mesh,
                                   'color_texture': activity.puck_tex,
                                   'body': 'sphere',
                                   'reflection': 'soft',
                                   'reflection_scale': [0.0],
                                   'shadow_size': 0.6,
                                   'is_area_of_interest': True,
                                   'position': self._spawn_pos,
                                   'materials': pmats
                               })
        bs.animate(self.node, 'mesh_scale', {0: 0, 0.2: 1.2, 0.26: 1.0})

    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, bs.DieMessage):
            if self.node:
                if not self.retiring and not self.fired:
                    print('[GKB] a ball was removed by the game before its '
                          'shot (it will be restored)')
                self.node.delete()
            activity = self._activity()
            if activity and not msg.immediate:
                activity.handlemessage(PuckDiedMessage(self))
        elif isinstance(msg, bs.OutOfBoundsMessage):
            if self.node:
                self.oob = True
                self.node.position = self._spawn_pos
                self.node.velocity = (0.0, 0.0, 0.0)
        elif isinstance(msg, bs.HitMessage):
            if not self.node:
                return None
            assert msg.force_direction is not None
            self.node.handlemessage(
                'impulse', msg.pos[0], msg.pos[1], msg.pos[2], msg.velocity[0],
                msg.velocity[1], msg.velocity[2], 1.0 * msg.magnitude,
                1.0 * msg.velocity_magnitude, msg.radius, 0,
                msg.force_direction[0], msg.force_direction[1],
                msg.force_direction[2])

            s_player = msg.get_source_player(Player)
            if s_player is not None:
                activity = self._activity()
                if activity:
                    if s_player in activity.players:
                        self.last_players_to_touch[s_player.team.id] = s_player
                        if self.fired:
                            self.touched_by_player = True
        else:
            super().handlemessage(msg)


class _ActiveShot:
    """Bookkeeping of the one ball that is currently being shot."""

    def __init__(self, puck: Puck, pattern: Pattern, ctrl: ShotController,
                 speed: float, t_fire: float):
        self.puck, self.pattern = puck, pattern
        self.ctrl, self.speed, self.t_fire = ctrl, speed, t_fire
        self.goal = False
        self.last_t = -1.0
        self.prev: Optional[Tuple[float, float, float, float]] = None
        self.cross: Optional[Tuple[float, float]] = None
        self.late_cmds = 0
        self.max_dir_dev = 0.0
        self.max_speed_dev = 0.0
        self.cmd_angle = 0.0
        self.check_speed = False
        self.final_u = 0.0
        self.min_y_post = 99.0
        self.min_u = 99.0
        self.launched = False
        self.errors = 0
        self.resends = 0
        self.ack_pending = False
        self.last_world_cmd: Optional[Tuple[float, float, float]] = None
        self.t_cross = -1.0
        self.goal_t = -1.0


# --- goalkeeper bot in the RIGHT goal ---------------------------------------
KEEPER_TICK = 0.02
KEEPER_LEVELS = {            # level: (reaction time s, catch radius m)
    1: (0.45, 0.80),         # easy
    2: (0.28, 1.00),         # normal
    3: (0.14, 1.20),         # hard
}
KEEPER_MIN_SPEED = 2.0       # m/s towards the goal before a ball is a "shot"
KEEPER_DEPTH = 0.5           # m inside the goal mouth where he stands
KEEPER_HAND_Y = 0.9          # m: hand height above the spaz node position
KEEPER_HOLD_TIME = 0.9       # s: how long he keeps the ball after a save
KEEPER_THROW_SPEED = 12.0    # m/s: throw back towards the pitch
KEEPER_COOLDOWN = 0.7        # s: no new catch right after a throw


class GoalKeeper:
    """A bot standing in the RIGHT goal (u < 0).  It reads the flight of every
    ball that is heading for the goal, runs to the predicted crossing point,
    jumps for high balls and CATCHES the ball (holds it, then throws it back
    onto the pitch).  Everything is derived from Geometry, so it works on any
    hockey map."""

    def __init__(self, game: 'BuffonJon', level: int):
        self._game = game
        self.react, self.reach = KEEPER_LEVELS.get(level, KEEPER_LEVELS[2])
        self.spaz: Optional[Spaz] = None
        self._timer: Optional[bs.Timer] = None
        # joystick -> world mapping; the signs are verified at runtime
        self._sx, self._sz = 1.0, -1.0
        self._corr_x = 0.0
        self._corr_z = 0.0
        self._wx = 0.0
        self._wz = 0.0
        self._tv = 0.0                      # lateral position he runs to
        self._threat: Optional[Puck] = None
        self._threat_t = 0.0
        self._held: Optional[Puck] = None
        self._pin = False                   # fallback: carry the ball by hand
        self._release_t = 0.0
        self._cool_until = 0.0
        self._respawn_t = 0.0
        self._last_jump = -9.0
        self.saves = 0

    # ---- life cycle --------------------------------------------------------
    def start(self) -> None:
        geo = self._game._geo
        assert geo is not None
        self._tv = geo.other_cv
        self.spawn()
        self._timer = bs.Timer(KEEPER_TICK, bs.WeakCall(self._tick),
                               repeat=True)

    def _line_u(self) -> float:
        geo = self._game._geo
        assert geo is not None
        return geo.other_mouth_u - KEEPER_DEPTH

    def spawn(self) -> None:
        geo = self._game._geo
        assert geo is not None
        self._respawn_t = 0.0
        self._held = None
        self._threat = None
        char = 'Kronk'
        try:
            if char not in babase.app.classic.spaz_appearances:
                char = 'Spaz'
        except Exception:
            char = 'Spaz'
        spaz = Spaz(color=(1.0, 0.85, 0.1),
                    highlight=(0.15, 0.15, 0.15),
                    character=char,
                    source_player=None,
                    start_invincible=False,
                    can_accept_powerups=False)
        spaz.node.invincible = True         # players cannot hurt the keeper
        spaz.node.name = 'Keeper'
        spaz.node.name_color = (1.0, 0.9, 0.3)
        pos = geo.to_world(self._line_u(), geo.other_cv, geo.floor_y + 0.6)
        face = math.degrees(math.atan2(geo.fx, geo.fz))
        spaz.handlemessage(bs.StandMessage(pos, face))
        self.spaz = spaz
        print('[GKB] goalkeeper ready (reach %.2f m, reaction %.2f s)' %
              (self.reach, self.react))

    # ---- helpers -----------------------------------------------------------
    def _gravity(self) -> float:
        c = self._game._calib
        return _clamp(c.g + c.off, 8.0, 60.0)

    def _alive_spaz(self) -> bool:
        sp = self.spaz
        return bool(sp is not None and sp.node and sp.is_alive())

    def _find_threat(self, geo: Geometry, line_u: float
                     ) -> Optional[Tuple[float, float, float, Puck]]:
        """Soonest ball that is flying at the goal: (t, v, y, puck) = time to
        reach the keeper's line and where (lateral, height) it will be."""
        g = self._gravity()
        half_w = 0.5 * geo.goal_width
        best = None
        for p in self._game._keeper_pucks():
            if p is self._held or not p.node:
                continue
            pos, vel = p.node.position, p.node.velocity
            u, v, y = geo.to_frame(pos[0], pos[1], pos[2])
            hu, hv = geo.vel_to_frame(vel[0], vel[2])
            if hu > -KEEPER_MIN_SPEED or u < line_u - 0.3:
                continue
            t = (u - line_u) / -hu
            if t > 2.5:
                continue
            vk = v + hv * t
            if abs(vk - geo.other_cv) > half_w + 1.2:
                continue                      # going wide: not his business
            yk = max(y + vel[1] * t - 0.5 * g * t * t, geo.rest_y)
            if best is None or t < best[0]:
                best = (t, vk, yk, p)
        return best

    def _idle_target(self, geo: Geometry, line_u: float) -> float:
        """Between shots: shade towards the nearest ball in front of goal."""
        half_w = 0.5 * geo.goal_width
        cv = geo.other_cv
        if self._game._auto_shoot:
            return cv
        best_d, best_v = 99.0, cv
        for p in self._game._keeper_pucks():
            if not p.node or p is self._held:
                continue
            pos = p.node.position
            u, v, _y = geo.to_frame(pos[0], pos[1], pos[2])
            d = u - line_u
            if 0.0 <= d < 12.0 and d < best_d:
                best_d, best_v = d, v
        return cv + _clamp(0.45 * (best_v - cv), -(half_w - 0.5),
                           half_w - 0.5)

    # ---- main loop ---------------------------------------------------------
    def _tick(self) -> None:
        try:
            self._step()
        except Exception:
            self._game._log_error('keeper')

    def _step(self) -> None:
        game = self._game
        geo = game._geo
        if geo is None or game.has_ended():
            return
        now = bs.time()
        if not self._alive_spaz():
            self._held = None
            if self._respawn_t <= 0.0:
                self._respawn_t = now + 1.5
            elif now >= self._respawn_t:
                self.spawn()
            return
        spaz = self.spaz
        assert spaz is not None
        node = spaz.node
        pos, vel = node.position, node.velocity
        u, v, _y = geo.to_frame(pos[0], pos[1], pos[2])
        hu_k, hv_k = geo.vel_to_frame(vel[0], vel[2])
        line_u = self._line_u()
        half_w = 0.5 * geo.goal_width
        cv = geo.other_cv

        # verify the joystick directions (a wrong sign shows up as motion
        # against the command) and flip the sign if needed
        if abs(self._wx) > 0.3:
            self._corr_x = 0.97 * self._corr_x + self._wx * vel[0]
            if self._corr_x < -40.0:
                self._sx, self._corr_x = -self._sx, 0.0
        if abs(self._wz) > 0.3:
            self._corr_z = 0.97 * self._corr_z + self._wz * vel[2]
            if self._corr_z < -40.0:
                self._sz, self._corr_z = -self._sz, 0.0

        hand = (pos[0], pos[1] + KEEPER_HAND_Y, pos[2])

        # ---- holding a ball -------------------------------------------------
        if self._held is not None:
            held = self._held
            if not held.node:
                self._held = None
            else:
                if self._pin:
                    held.node.position = hand
                    held.node.velocity = (vel[0], 0.0, vel[2])
                if now >= self._release_t:
                    self._release(geo, now)

        # ---- decide where to stand --------------------------------------------
        threat = None
        if self._held is None:
            threat = self._find_threat(geo, line_u)
        active = False
        if threat is not None:
            t, vk, yk, puck = threat
            if puck is not self._threat:
                self._threat, self._threat_t = puck, now
            if now - self._threat_t >= self.react:
                active = True
                self._tv = _clamp(vk, cv - half_w + 0.25, cv + half_w - 0.25)
                if (yk > geo.rest_y + 1.5 and t < 0.35
                        and now - self._last_jump > 0.8):
                    self._last_jump = now
                    spaz.on_jump_press()
                    bs.timer(0.15, bs.WeakCall(self._jump_release))
        else:
            self._threat = None
            self._tv += 0.15 * (self._idle_target(geo, line_u) - self._tv)

        # ---- catch --------------------------------------------------------------
        if self._held is None and now >= self._cool_until:
            self._try_catch(geo, hand, now)

        # ---- move ---------------------------------------------------------------
        e = self._tv - v
        eu = line_u - u
        cl = _clamp(2.6 * e - 0.45 * hv_k, -1.0, 1.0)
        cu = _clamp(1.8 * eu - 0.4 * hu_k, -1.0, 1.0)
        if abs(e) < 0.12 and abs(eu) < 0.15 and abs(hv_k) < 0.6:
            cl = cu = 0.0
        self._wx = cl * geo.lx + cu * geo.fx
        self._wz = cl * geo.lz + cu * geo.fz
        spaz.on_move_left_right(self._sx * self._wx)
        spaz.on_move_up_down(self._sz * self._wz)
        spaz.on_run(1.0 if (active or abs(e) > 0.6) else 0.0)

    def _jump_release(self) -> None:
        if self._alive_spaz():
            assert self.spaz is not None
            self.spaz.on_jump_release()

    # ---- catching ------------------------------------------------------------
    def _try_catch(self, geo: Geometry, hand: Sequence[float],
                   now: float) -> None:
        loose = not self._game._auto_shoot
        for p in self._game._keeper_pucks():
            if not p.node:
                continue
            pp, pv = p.node.position, p.node.velocity
            d = math.dist(hand, pp)
            if d > self.reach:
                continue
            hu, _hv = geo.vel_to_frame(pv[0], pv[2])
            speed = math.sqrt(pv[0] ** 2 + pv[1] ** 2 + pv[2] ** 2)
            incoming = hu <= -1.0
            gather = loose and d <= 1.0 and speed < 3.0
            if incoming or gather:
                self._catch(p, hand, now)
                return

    def _catch(self, puck: Puck, hand: Sequence[float], now: float) -> None:
        spaz = self.spaz
        assert spaz is not None
        puck.node.velocity = (0.0, 0.0, 0.0)
        self._pin = False
        try:
            spaz.node.hold_node = puck.node
            if not spaz.node.hold_node:
                self._pin = True            # engine refused: carry it by hand
        except Exception:
            self._pin = True
        if self._pin:
            puck.node.position = hand
        self._held = puck
        self._release_t = now + KEEPER_HOLD_TIME
        self.saves += 1
        try:
            SpazFactory.get().block_sound.play(1.0, position=tuple(hand))
            bs.emitfx(position=tuple(hand), velocity=(0.0, 2.0, 0.0),
                      count=15, scale=0.8, spread=0.4, chunk_type='spark')
            PopupText('SAVE!', position=(hand[0], hand[1] + 1.0, hand[2]),
                      color=(1.0, 0.9, 0.2, 1.0), scale=1.4).autoretain()
        except Exception:
            pass
        print('[GKB] keeper save #%d' % self.saves)

    def _release(self, geo: Geometry, now: float) -> None:
        puck = self._held
        self._held = None
        self._cool_until = now + KEEPER_COOLDOWN
        spaz = self.spaz
        try:
            if spaz is not None and spaz.node:
                spaz.node.hold_node = None
        except Exception:
            pass
        if puck is not None and puck.node:
            hv = random.uniform(-3.0, 3.0)
            wx, wz = geo.vel_to_world(KEEPER_THROW_SPEED, hv)
            puck.node.velocity = (wx, 4.0, wz)


# --- skins (characters) the host can force on every player ---------------
SKIN_NAMES = ['Spaz', 'Zoe', 'Snake Shadow', 'Kronk', 'Mel', 'Jack Morgan',
              'Santa Claus', 'Frosty', 'Bernard', 'Pascal', 'Taobao Mascot',
              'B-9000', 'Agent Johnson', 'Lee', 'Zola', 'Grumbledorf',
              'Pixel', 'Bones', 'Easter Bunny']
SKIN_CHOICES = ([('پیش‌فرض (اسکین خود بازیکن)', 0), ('رندوم', 1)] +
                [(n, i + 2) for i, n in enumerate(SKIN_NAMES)])


# ba_meta export bascenev1.GameActivity
class BuffonJon(HockeyGame):
    """Football game for teams mode (auto-shooting goalkeeper trainer)."""

    name = 'gk'
    description = 'Creator: Buffon | Telegram/Rubika: @TechOtice'
    available_settings = [
        bs.IntSetting(
            'Score to Win',
            min_value=1,
            default=1,
            increment=1,
        ),
        bs.IntChoiceSetting(
            'Time Limit',
            choices=[
                ('None', 0),
                ('1 Minute', 60),
                ('2 Minutes', 120),
                ('5 Minutes', 300),
                ('10 Minutes', 600),
                ('20 Minutes', 1200),
            ],
            default=0,
        ),
        bs.FloatChoiceSetting(
            'Respawn Times',
            choices=[
                ('Shorter', 0.25),
                ('Short', 0.5),
                ('Normal', 1.0),
                ('Long', 2.0),
                ('Longer', 4.0),
            ],
            default=1.0,
        ),
        bs.BoolSetting('پانچ بینهایت', default=False),
        bs.BoolSetting('اسپاون باکس های کمکی', default=True),
        bs.BoolSetting('سرعت در دوییدن', default=True),
        bs.BoolSetting('صدمه زدن به پلیر', default=False),
        bs.BoolSetting('انداختن بمب', default=True),
        bs.BoolSetting('پرش کشیده تا تیرک', default=True),
        bs.BoolSetting('پرش دوبل', default=True),
        bs.BoolSetting('شوت خودکار توپ به دروازه', default=False),
        bs.IntChoiceSetting('گلر دروازه راست',
                            choices=[('خاموش', 0), ('آسان', 1),
                                     ('معمولی', 2), ('سخت', 3)],
                            default=2),
        bs.IntChoiceSetting('اسکین (کاراکتر)', choices=SKIN_CHOICES,
                            default=0),
        bs.BoolSetting('Epic Mode', default=False),
    ]

    @classmethod
    def get_supported_maps(cls, sessiontype: Type[bs.Session]) -> List[str]:
        return babase.app.classic.getmaps('hockey')

    def __init__(self, settings: dict):
        super().__init__(settings)
        shared = SharedObjects.get()
        self._scoreboard = Scoreboard()
        self._cheer_sound = bs.getsound('cheer')
        self._chant_sound = bs.getsound('crowdChant')
        self._foghorn_sound = bs.getsound('foghorn')
        self._swipsound = bs.getsound('swip')
        self._whistle_sound = bs.getsound('refWhistle')
        self._boxing_gloves = bool(settings.get('پانچ بینهایت', False))
        self._enable_powerups = bool(settings.get('اسپاون باکس های کمکی', True))
        self._ice_floor = bool(settings.get('سرعت در دوییدن', True))
        self._hit_players = bool(settings['صدمه زدن به پلیر'])
        self._allow_bombs = bool(settings.get('انداختن بمب', True))
        self._jump_stretch = bool(settings.get('پرش کشیده تا تیرک', True))
        self._double_jump = bool(settings.get('پرش دوبل', True))
        self._auto_shoot = bool(settings.get('شوت خودکار توپ به دروازه', False))
        self._keeper_level = int(settings.get('گلر دروازه راست', 2))
        self._keeper: Optional[GoalKeeper] = None
        self._skin_idx = int(settings.get('اسکین (کاراکتر)', 0))
        self._epic_mode = bool(settings['Epic Mode'])
        self.slow_motion = self._epic_mode
        self.default_music = (bs.MusicType.EPIC
                              if self._epic_mode else bs.MusicType.FOOTBALL)
        self.puck_mesh = bs.getmesh('frostyPelvis')
        self.puck_tex = bs.gettexture('fontSmall0')
        self.puck_material = bs.Material()
        self.puck_material.add_actions(actions=(('modify_part_collision',
                                                 'friction', 0.5)))
        self.puck_material.add_actions(conditions=('they_have_material',
                                                   shared.pickup_material),
                                       actions=('modify_part_collision',
                                                'collide', True))
        self.puck_material.add_actions(
            conditions=(
                ('we_are_younger_than', 100),
                'and',
                ('they_have_material', shared.object_material),
            ),
            actions=('modify_node_collision', 'collide', False),
        )
        self.puck_material.add_actions(
            conditions=('they_have_material', shared.player_material),
            actions=('call', 'at_connect', self._handle_puck_player_collide))
        self.puck_material.add_actions(
            conditions=('they_have_material',
                        PowerupBoxFactory.get().powerup_material),
            actions=(('modify_part_collision', 'physical', False),
                     ('message', 'their_node', 'at_connect', bs.DieMessage())))
        self._score_region_material = bs.Material()
        self._score_region_material.add_actions(
            conditions=('they_have_material', self.puck_material),
            actions=(('modify_part_collision', 'collide',
                      True), ('modify_part_collision', 'physical', False),
                     ('call', 'at_connect', self._handle_score)))
        self._puck_spawn_pos: Optional[Sequence[float]] = None
        self._center_flag_pos: Optional[Sequence[float]] = None
        self._score_regions: Optional[List[bs.NodeActor]] = None
        self._puck: Optional[Puck] = None
        self._spawn_token = 0
        self._score_to_win = int(settings['Score to Win'])
        self._time_limit = float(settings['Time Limit'])

        # --- shot system v2 state ------------------------------------------
        self._rng = random.Random()
        self._registry = PatternRegistry()
        self._book = PatternBook(self._registry, self._rng)
        self._calib = PhysCalib()
        self._geo: Optional[Geometry] = None
        self._spawn_points: List[Tuple[float, float]] = []
        self._spawn_bag: List[int] = []
        self._balls: List[Puck] = []
        self._director_timer: Optional[bs.Timer] = None
        self._fire_due = 0.0
        self._last_spawn = -99.0
        self._fire_errors = 0
        self._stalls = 0
        self._live: List[_ActiveShot] = []
        self._poll_timer: Optional[bs.Timer] = None
        self._drop_timer: Optional[bs.Timer] = None
        self._drop_state: Dict[str, Any] = {}
        self._drop_tries = 0
        self._preflight_fail: Dict[str, int] = {}
        self._shots_fired = 0

    def on_transition_in(self) -> None:
        super().on_transition_in()
        shared = SharedObjects.get()
        activity = bs.getactivity()
        if self._ice_floor:
            activity.map.is_hockey = True
        else:
            activity.map.is_hockey = False
        activity.map.node.materials = [shared.footing_material]
        activity.map.floor.materials = [shared.footing_material]
        activity.map.floor.color = (0.8, 1.0, 0.0)

    def on_begin(self) -> None:
        self.setup_standard_time_limit(self._time_limit)
        if self._enable_powerups:
            self.setup_standard_powerup_drops()

        self._center_flag_pos = self.map.get_flag_position(None)
        self._puck_spawn_pos = self._center_flag_pos
        defs = self.map.defs
        self._geo = Geometry(defs.boxes['goal2'], defs.boxes['goal1'],
                             self._center_flag_pos,
                             defs.boxes.get('area_of_interest_bounds'))
        self._spawn_points = build_spawn_points(self._geo)
        geo = self._geo
        print('[GKB] goal mouth u=%.2f width=%.2f top=%.2f | spawns=%d '
              'u[%.1f..%.1f]' % (geo.mouth_u, geo.goal_width, geo.goal_top,
                                 len(self._spawn_points),
                                 min(p[0] for p in self._spawn_points),
                                 max(p[0] for p in self._spawn_points)))

        self._score_regions = []
        self._score_regions.append(
            bs.NodeActor(
                bs.newnode('region',
                           attrs={
                               'position': defs.boxes['goal2'][0:3],
                               'scale': defs.boxes['goal2'][6:9],
                               'type': 'box',
                               'materials': [self._score_region_material]
                           })))

        if self._keeper_level > 0:
            self._keeper = GoalKeeper(self, self._keeper_level)
            self._keeper.start()

        if self._auto_shoot:
            self._fire_due = bs.time() + 1.5 + SPAWN_LEAD
            self._director_timer = bs.Timer(
                0.02, bs.WeakCall(self._director), repeat=True)
        else:
            self._spawn_puck()
        self._update_scoreboard()
        self._chant_sound.play()

        self._credit_nodes: List[bs.NodeActor] = []
        self._create_credit_text()

    @staticmethod
    def _char_width(ch: str) -> float:
        """Rough relative width of a character (for per-letter layout)."""
        if ch in 'ijl:.,!|':
            return 0.5
        if ch in 'tfrI ':
            return 0.75
        if ch in 'mwMW@&':
            return 1.35
        if ch.isupper():
            return 1.1
        return 1.0

    def _create_credit_text(self) -> None:
        """Bottom-center credit, every letter with its own RGB color."""
        lines = ['Creator:Buffon', 'Telegram&Rubika:@TechOtice']
        scale = 0.8
        unit = 11.0 * scale  # approx. pixel width of an average letter
        y_positions = [62.0, 34.0]
        total_chars = sum(len(line.replace(' ', '')) for line in lines)
        steps = 6
        period = 3.0
        idx = 0
        for line, y in zip(lines, y_positions):
            widths = [self._char_width(c) * unit for c in line]
            x = -sum(widths) * 0.5
            for ch, w in zip(line, widths):
                cx = x + w * 0.5
                x += w
                if ch == ' ':
                    continue
                base_hue = idx / total_chars
                idx += 1
                node = bs.newnode('text',
                                  attrs={
                                      'text': ch,
                                      'host_only': True,
                                      'v_attach': 'bottom',
                                      'h_attach': 'center',
                                      'h_align': 'center',
                                      'v_align': 'center',
                                      'position': (cx, y),
                                      'scale': scale,
                                      'color': colorsys.hsv_to_rgb(
                                          base_hue, 1.0, 1.0),
                                      'shadow': 1.0,
                                      'flatness': 0.0,
                                  })
                keys = {}
                for k in range(steps + 1):
                    hue = (base_hue + k / steps) % 1.0
                    keys[k * period / steps] = colorsys.hsv_to_rgb(
                        hue, 1.0, 1.0)
                bs.animate_array(node, 'color', 3, keys, loop=True)
                self._credit_nodes.append(bs.NodeActor(node))

    def _pick_character(self, player: Player) -> str:
        """Skin chosen in the game settings (falls back to the player's own)."""
        idx = self._skin_idx
        if idx == 0:
            return player.character
        try:
            apps = babase.app.classic.spaz_appearances
        except Exception:
            return player.character
        if idx == 1:
            names = sorted(apps.keys())
            return self._rng.choice(names) if names else player.character
        name = SKIN_NAMES[idx - 2] if 0 <= idx - 2 < len(SKIN_NAMES) else ''
        if name in apps:
            return name
        print('[GKB] skin not found: %s (using the player\'s own)' % name)
        return player.character

    def spawn_player(self, player: Player) -> bs.Actor:
        if isinstance(self.session, bs.DualTeamSession):
            position = self.map.get_start_position(player.team.id)
        else:
            position = self.map.get_ffa_start_position(self.players)
        angle = None

        name = player.getname()
        color = player.color
        highlight = player.highlight

        light_color = babase.normalized_color(color)
        display_color = babase.safecolor(color, target_intensity=0.75)

        character = self._pick_character(player)

        if self._hit_players:
            spaz = BombControlSpaz(color=color,
                                   highlight=highlight,
                                   character=character,
                                   player=player)
        else:
            spaz = NewPlayerSpaz(color=color,
                                  highlight=highlight,
                                  character=character,
                                  player=player)

        spaz.bombs_allowed = self._allow_bombs
        spaz.double_jump = self._double_jump
        if self._double_jump and self._geo is not None:
            spaz.jump_gravity = self._calib.g + self._calib.off
        if self._jump_stretch and self._geo is not None:
            spaz.jump_boost = True
            spaz.head_target_y = self._geo._top() + JUMP_HEAD_CLEARANCE
            spaz.jump_gravity = self._calib.g + self._calib.off
        player.actor = spaz
        assert spaz.node

        if isinstance(self.session, bs.CoopSession) and self.map.getname() in [
                'Courtyard', 'Tower D'
        ]:
            mat = self.map.preloaddata['collide_with_wall_material']
            assert isinstance(spaz.node.materials, tuple)
            assert isinstance(spaz.node.roller_materials, tuple)
            spaz.node.materials += (mat, )
            spaz.node.roller_materials += (mat, )

        spaz.node.name = name
        spaz.node.name_color = display_color
        spaz.connect_controls_to_player()

        if self._boxing_gloves:
            spaz.equip_boxing_gloves()

        spaz.handlemessage(
            bs.StandMessage(
                position,
                angle if angle is not None else random.uniform(0, 360)))
        self._spawn_sound.play(1, position=spaz.node.position)
        light = bs.newnode('light', attrs={'color': light_color})
        spaz.node.connectattr('position', light, 'position')
        bs.animate(light, 'intensity', {0: 0, 0.25: 1, 0.5: 0})
        bs.timer(0.5, light.delete)
        return spaz

    # ======================================================================
    #  Collisions / scoring
    # ======================================================================
    def _handle_puck_player_collide(self) -> None:
        collision = bs.getcollision()
        try:
            puck = collision.sourcenode.getdelegate(Puck, True)
            player = collision.opposingnode.getdelegate(
                PlayerSpaz, True).getplayer(Player, True)
        except bs.NotFoundError:
            return
        puck.last_players_to_touch[player.team.id] = player
        if puck.fired:
            puck.touched_by_player = True

    def _handle_score(self) -> None:
        """A point has been scored (works for any of the balls)."""
        try:
            collision = bs.getcollision()
            puck = collision.opposingnode.getdelegate(Puck, True)
        except bs.NotFoundError:
            return
        if puck.scored:
            return
        puck.scored = True
        for shot in self._live:
            if shot.puck is puck:
                shot.goal = True
                shot.goal_t = bs.time()

        for team in self.teams:
            if team.id == 0:
                scoring_team = team
                team.score += 1
                for player in team.players:
                    if player.actor:
                        player.actor.handlemessage(bs.CelebrateMessage(2.0))
                if (scoring_team.id in puck.last_players_to_touch
                        and puck.last_players_to_touch[scoring_team.id]):
                    self.stats.player_scored(
                        puck.last_players_to_touch[scoring_team.id],
                        20,
                        big_message=True)
                if team.score >= self._score_to_win:
                    self.end_game()

        self._foghorn_sound.play()
        self._cheer_sound.play()

        if not self._auto_shoot:
            bs.timer(1.0, self._kill_puck)

        light = bs.newnode('light',
                           attrs={
                               'position': bs.getcollision().position,
                               'height_attenuated': False,
                               'color': (1, 0, 0)
                           })
        bs.animate(light, 'intensity', {0: 0, 0.5: 1, 1.0: 0}, loop=True)
        bs.timer(1.0, light.delete)
        flash = getattr(bs, 'cameraflash', None)
        if flash is not None:
            flash(duration=10.0)
        self._update_scoreboard()

    # ======================================================================
    #  Normal (non-auto) mode: single puck at the centre, as before
    # ======================================================================
    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, PuckDiedMessage):
            if (self._auto_shoot or self.has_ended()
                    or msg.puck is not self._puck):
                return None
            self._spawn_token += 1
            bs.timer(3.0, bs.WeakCall(self._respawn_puck,
                                            self._spawn_token))
            return None
        return super().handlemessage(msg)

    def _respawn_puck(self, token: int) -> None:
        if token != self._spawn_token or self.has_ended():
            return
        self._spawn_puck()

    def _kill_puck(self) -> None:
        puck = self._puck
        if puck is not None and puck.node:
            puck.handlemessage(bs.DieMessage())

    def _spawn_puck(self) -> None:
        self._spawn_token += 1
        old = self._puck
        if old is not None and old.node:
            old.handlemessage(bs.DieMessage(immediate=True))
        self._puck = None
        self._swipsound.play()
        self._whistle_sound.play()
        self._flash_puck_spawn()
        assert self._puck_spawn_pos is not None
        self._puck = Puck(position=self._puck_spawn_pos)

    # ======================================================================
    #  Auto-shoot mode.  ONE "director" runs every 0.02 s and owns the whole
    #  schedule (no chained timers, so nothing can get lost):
    #    * a batch of 5-10 balls appears SPAWN_LEAD s before its first kick
    #    * EVERY ball is kicked once, one every TURN_GAP s, in random order
    #    * whatever goes wrong (exception, ball destroyed / pushed away, no
    #      pattern accepted ...) the next tick recovers - a kick always follows
    # ======================================================================
    def _keeper_pucks(self) -> List[Puck]:
        """Balls the goalkeeper may react to (never the auto-kicked ones)."""
        if self._auto_shoot:
            return [p for p in self._balls if self._alive(p) and not p.fired]
        return [self._puck] if self._alive(self._puck) else []

    @staticmethod
    def _alive(p: Optional[Puck]) -> bool:
        return p is not None and bool(p.node)

    @staticmethod
    def _log_error(where: str) -> None:
        print('[GKB] ERROR in %s (game keeps running):' % where)
        traceback.print_exc()

    def _flash_at(self, pos: Sequence[float]) -> None:
        light = bs.newnode('light',
                           attrs={
                               'position': pos,
                               'height_attenuated': False,
                               'radius': 0.25,
                               'color': (1.0, 0.6, 0.1)
                           })
        bs.animate(light, 'intensity', {0.0: 0, 0.15: 0.8, 0.35: 0})
        bs.timer(0.4, light.delete)

    def _clear_balls(self) -> None:
        keep = [s.puck for s in self._live]
        for p in self._balls:
            if self._alive(p) and p not in keep:
                p.retiring = True
                p.handlemessage(bs.DieMessage(immediate=True))
        self._balls = []

    def _pick_spawn_indices(self, n: int) -> List[int]:
        """n distinct, well separated points; every point is used equally."""
        pts = self._spawn_points
        chosen: List[int] = []
        for spacing in (BALL_MIN_SPACING, 1.4, 1.1):
            chosen = []
            rejected: List[int] = []
            guard = 0
            while len(chosen) < n and guard < 600:
                guard += 1
                if not self._spawn_bag:
                    self._spawn_bag = list(range(len(pts)))
                    self._rng.shuffle(self._spawn_bag)
                i = self._spawn_bag.pop()
                if all(math.hypot(pts[i][0] - pts[j][0],
                                  pts[i][1] - pts[j][1]) >= spacing
                       for j in chosen):
                    chosen.append(i)
                else:
                    rejected.append(i)
            self._spawn_bag.extend(rejected)
            self._rng.shuffle(self._spawn_bag)
            if len(chosen) >= n:
                return chosen
            if spacing == 1.1 and len(chosen) >= BALLS_PER_TURN[0]:
                return chosen
        return chosen

    def _spawn_batch(self) -> None:
        """Put 5-10 balls on the valid spawn points (right half)."""
        geo = self._geo
        assert geo is not None
        self._clear_balls()
        n = self._rng.randint(BALLS_PER_TURN[0], BALLS_PER_TURN[1])
        for i in self._pick_spawn_indices(n):
            u, v = self._spawn_points[i]
            pos = geo.to_world(u, v, geo.floor_y)
            self._flash_at(pos)
            self._balls.append(Puck(position=pos))
        self._last_spawn = bs.time()
        self._swipsound.play()
        self._whistle_sound.play()
        if self._balls and self._calib.learned < 2 and self._drop_tries < 6:
            self._start_drop_calib(self._balls[0])

    def _unfired(self) -> List[Puck]:
        return [p for p in self._balls if self._alive(p) and not p.fired]

    def _displaced(self, p: Puck) -> bool:
        """Pushed away by a player (left half / too close to the right goal /
        high in the air)?  Plain bouncing after the drop is NOT displaced."""
        geo = self._geo
        assert geo is not None
        pos = p.node.position
        u, v, _y = geo.to_frame(pos[0], pos[1], pos[2])
        return (u > -(SPAWN_MID_MARGIN - 0.5) or abs(v) > geo.v_spawn + 1.3
                or u < geo.other_mouth_u + 0.7
                or pos[1] > geo.rest_y + 2.0)

    def _choose_shooter(self, now: float) -> Optional[Puck]:
        """Random ball with a free lane towards the goal.  A ball that was
        pushed away is put back on its own spawn point (at most every 1.2 s,
        so it can never be teleported in a loop)."""
        geo = self._geo
        assert geo is not None
        ready = []
        for p in self._unfired():
            if self._displaced(p):
                if now - p.repos_t > 1.2:
                    p.repos_t = now
                    p.node.position = p._spawn_pos
                    p.node.velocity = (0.0, 0.0, 0.0)
            else:
                ready.append(p)
        if not ready:
            return None
        st = []
        for p in ready:
            pos = p.node.position
            st.append((p, geo.to_frame(pos[0], pos[1], pos[2])))
        free = []
        for p, (u, v, _y) in st:
            blocked = any(0.0 < (u2 - u) <= 2.2 and abs(v2 - v) < 1.1
                          for q, (u2, v2, _y2) in st if q is not p)
            if not blocked:
                free.append(p)
        return self._rng.choice(free if free else ready)

    def _learn_rest_height(self) -> None:
        geo = self._geo
        assert geo is not None
        ys = []
        for p in self._unfired():
            pos, vel = p.node.position, p.node.velocity
            if abs(vel[1]) < 0.3 and 0.2 < pos[1] < 1.4:
                ys.append(pos[1])
        if len(ys) >= 3:
            geo.set_rest(_median(ys))

    def _select_pattern(self, u: float, v: float, speed: float) -> Pattern:
        """A pattern that passes the dry-run; if none does, the best of the
        tried ones - this function ALWAYS returns a pattern."""
        geo = self._geo
        assert geo is not None
        tried: List[str] = []
        best: Optional[Pattern] = None
        for _ in range(12):
            p = self._book.pick(tried)
            if p is None:
                break
            tried.append(p.pid)
            ok, res = preflight(geo, p, speed, u, v, self._calib)
            if ok:
                return p
            if best is None or res.get('ok'):
                best = p
            n = self._preflight_fail.get(p.pid, 0) + 1
            self._preflight_fail[p.pid] = n
            if n >= 8:
                self._book.session_bad.add(p.pid)
        if best is None:
            best = self._book.patterns[self._rng.randrange(
                len(self._book.patterns))]
        print('[GKB] no pattern passed the dry-run, using %s' % best.pid)
        return best

    # --- the director -------------------------------------------------------
    def _director(self) -> None:
        if self.has_ended() or not self._auto_shoot or self._geo is None:
            return
        try:
            self._director_step()
        except Exception:
            self._log_error('director')
            self._fire_errors += 1

    def _restore_vanished(self) -> None:
        """A ball that was removed by something else before its shot is put
        back on its own spawn point, so every spawned ball still gets shot."""
        for i, p in enumerate(self._balls):
            if p.fired or self._alive(p):
                continue
            if p.restores >= 3:
                continue
            q = Puck(position=p.home)
            q.restores = p.restores + 1
            self._balls[i] = q
            print('[GKB] ball restored (%d)' % q.restores)

    def _director_step(self) -> None:
        now = bs.time()
        self._restore_vanished()
        if self._live and self._poll_timer is None:
            self._start_poll()                 # self-heal
        unfired = self._unfired()
        if (not unfired and now >= self._fire_due - SPAWN_LEAD
                and now - self._last_spawn >= 0.4):
            self._spawn_batch()
            unfired = self._unfired()
        if unfired and now >= self._fire_due and now - self._last_spawn >= 0.55:
            if now - self._fire_due > 2.5:
                self._stalls += 1
                print('[GKB] watchdog: shot was %.1f s late' %
                      (now - self._fire_due))
            if self._fire_errors >= 3:
                self._fire_errors = 0
                self._emergency_fire(now)
            else:
                self._fire(now)

    def _next_due(self, now: float) -> None:
        late = now - self._fire_due
        self._fire_due = (self._fire_due + TURN_GAP if late < 0.6
                          else now + TURN_GAP)

    def _start_poll(self) -> None:
        self._poll_timer = bs.Timer(0.016, bs.WeakCall(self._poll_all),
                                    repeat=True)

    def _fire(self, now: float) -> None:
        """Kick ONE ball now.  Balls that were kicked earlier are NOT touched:
        they keep flying until they have reached the goal."""
        geo = self._geo
        assert geo is not None
        self._learn_rest_height()
        puck = self._choose_shooter(now)
        if puck is None:
            if now - self._fire_due > 0.3:     # waited a bit: use any ball
                cands = self._unfired()
                puck = self._rng.choice(cands) if cands else None
            if puck is None:
                return                         # balls were put back: next tick
        pos = puck.node.position
        u, v, _y = geo.to_frame(pos[0], pos[1], pos[2])
        speed = self._rng.uniform(SPEED_RANGE[0], SPEED_RANGE[1])
        pattern = self._select_pattern(u, v, speed)
        ctrl = ShotController(geo, pattern, speed, self._calib)
        shot = _ActiveShot(puck, pattern, ctrl, speed, bs.time())
        puck.fired = True
        self._live.append(shot)
        self._shots_fired += 1
        self._fire_errors = 0
        self._next_due(now)
        self._whistle_sound.play()
        if self._poll_timer is None:
            self._start_poll()
        self._poll_one(shot)                   # first command without delay

    def _emergency_fire(self, now: float) -> None:
        """Last resort when the normal path keeps failing: still kick."""
        geo = self._geo
        assert geo is not None
        cands = self._unfired()
        if not cands:
            return
        puck = self._rng.choice(cands)
        pos = puck.node.position
        u, v, y = geo.to_frame(pos[0], pos[1], pos[2])
        speed = self._rng.uniform(SPEED_RANGE[0], SPEED_RANGE[1])
        pattern = self._book.patterns[0]
        ctrl = ShotController(geo, pattern, speed, self._calib)
        ctrl.done = True
        shot = _ActiveShot(puck, pattern, ctrl, speed, bs.time())
        model = FlightModel(self._calib.g + self._calib.off, 0.0)
        cmd = emergency_cmd(geo, model, speed, u, min(y, 1.0), y)
        wx, wz = geo.vel_to_world(cmd[0], cmd[1])
        puck.node.velocity = (wx, cmd[2], wz)
        shot.launched = True
        puck.fired = True
        self._live.append(shot)
        self._shots_fired += 1
        self._next_due(now)
        if self._poll_timer is None:
            self._start_poll()
        print('[GKB] emergency kick used')

    # ======================================================================
    #  Live control of the fired balls
    # ======================================================================
    def _poll_all(self) -> None:
        now = bs.time()
        for shot in list(self._live):
            self._poll_one(shot)
            if self._shot_over(shot, now):
                self._finalize_shot(shot)
        if not self._live:
            self._poll_timer = None

    def _shot_over(self, shot: _ActiveShot, now: float) -> bool:
        if not self._alive(shot.puck):
            return True
        if shot.goal and shot.goal_t >= 0.0 and now - shot.goal_t >= 0.9:
            return True
        if shot.t_cross >= 0.0 and now - shot.t_cross >= 0.9:
            return True
        return now - shot.t_fire >= 4.0

    def _poll_one(self, shot: _ActiveShot) -> None:
        try:
            self._poll_shot_inner(shot)
        except Exception:
            self._log_error('poll')
            shot.errors += 1
            if shot.errors >= 2 and not shot.launched:
                self._emergency_launch(shot)

    def _emergency_launch(self, shot: _ActiveShot) -> None:
        geo = self._geo
        puck = shot.puck
        if geo is None or not self._alive(puck):
            return
        shot.ctrl.done = True
        pos = puck.node.position
        u, v, y = geo.to_frame(pos[0], pos[1], pos[2])
        model = FlightModel(self._calib.g + self._calib.off, 0.0)
        cmd = emergency_cmd(geo, model, shot.speed, u, v, y)
        wx, wz = geo.vel_to_world(cmd[0], cmd[1])
        puck.node.velocity = (wx, cmd[2], wz)
        shot.launched = True
        print('[GKB] emergency launch used')

    def _poll_shot_inner(self, shot: _ActiveShot) -> None:
        geo = self._geo
        if geo is None:
            return
        puck = shot.puck
        if not self._alive(puck):
            return
        t = bs.time()
        if t <= shot.last_t + 1e-6:
            return
        pos, vel = puck.node.position, puck.node.velocity
        u, v, y = geo.to_frame(pos[0], pos[1], pos[2])
        hu, hv = geo.vel_to_frame(vel[0], vel[2])
        vy = vel[1]
        hh = math.hypot(hu, hv)
        ctrl = shot.ctrl
        shot.min_u = min(shot.min_u, u)
        if shot.ack_pending and shot.last_t >= 0.0:
            shot.ack_pending = False
            if (hh < 0.35 * shot.speed and shot.resends < 3
                    and shot.last_world_cmd is not None):
                # the kick did not "take" (ball not moving): send it again
                shot.resends += 1
                puck.node.velocity = shot.last_world_cmd
                shot.ack_pending = True
                shot.last_t = t
                return
        if shot.last_t >= 0.0 and shot.check_speed:
            shot.check_speed = False
            shot.max_speed_dev = max(shot.max_speed_dev,
                                     abs(hh - shot.speed) / shot.speed)
        if not ctrl.done:
            cmd = ctrl.update(t, u, v, y, hu, hv, vy)
            if cmd is not None:
                wx, wz = geo.vel_to_world(cmd[0], cmd[1])
                shot.last_world_cmd = (wx, cmd[2], wz)
                puck.node.velocity = shot.last_world_cmd
                shot.launched = True
                shot.check_speed = True
                shot.ack_pending = True
                if u >= 0.0:
                    shot.late_cmds += 1
                if ctrl.done:
                    shot.final_u = u
                    shot.cmd_angle = math.atan2(cmd[1], cmd[0])
        elif hu > 1.0:
            # After the final aim we only WATCH: how straight is the flight?
            dev = abs(math.atan2(hv, hu) - shot.cmd_angle)
            shot.max_dir_dev = max(shot.max_dir_dev, dev)
            if shot.cross is None:
                shot.min_y_post = min(shot.min_y_post, y)
        if shot.cross is None and shot.prev is not None:
            pu = shot.prev[1]
            if pu < geo.mouth_u <= u:
                f = (geo.mouth_u - pu) / max(u - pu, 1e-9)
                shot.cross = (shot.prev[2] + (v - shot.prev[2]) * f,
                              shot.prev[3] + (y - shot.prev[3]) * f)
                shot.t_cross = t
        shot.prev = (t, u, v, y)
        shot.last_t = t

    def _finalize_shot(self, shot: _ActiveShot) -> None:
        if shot in self._live:
            self._live.remove(shot)
        puck = shot.puck
        try:
            self._record_shot(shot)
        except Exception:
            self._log_error('finalize')
        if self._alive(puck):
            puck.retiring = True
            puck.handlemessage(bs.DieMessage(immediate=True))

    def _record_shot(self, shot: _ActiveShot) -> None:
        geo = self._geo
        assert geo is not None
        puck, pat = shot.puck, shot.pattern
        ctrl = shot.ctrl
        ctrl.calib.absorb(ctrl.pos_gs, ctrl.gs, ctrl.ks, ctrl.acc)
        fin = ctrl.final
        grounded = shot.min_y_post < geo.rest_y + 0.12
        if (fin is not None and shot.cross is not None and not puck.oob
                and not puck.touched_by_player):
            # learn from how high the ball REALLY arrived (a ball that hit the
            # ice before the goal counts as "far too low")
            err = shot.cross[1] - fin['target'][2]
            if grounded:
                err = min(err, -0.5)
            self._calib.absorb_residual(err, fin['T'], ctrl.model)
        goal = shot.goal or puck.scored
        reason = 'goal'
        if not goal:
            if puck.oob:
                reason = 'oob'
            elif puck.touched_by_player:
                reason = 'blocked'
            elif shot.cross is None:
                reason = 'no_cross'
            else:
                reason = geo.crossing_reason(shot.cross[0], shot.cross[1])
                if reason == 'ok':
                    reason = 'frame'
        disturbed = shot.max_dir_dev > 0.12 and not grounded
        rec = {'id': pat.pid, 'goal': goal, 'why': reason,
               'speed': round(shot.speed, 2),
               'changes': len(ctrl.cmds),
               'late_cmds': shot.late_cmds,
               'speed_dev': round(shot.max_speed_dev, 3),
               'dir_dev': round(shot.max_dir_dev, 3),
               'final_u': round(shot.final_u, 2),
               'min_u': round(shot.min_u, 2),
               'y_final': None if fin is None else round(fin['y'], 2),
               'min_y_post': round(shot.min_y_post, 2),
               'g': round(ctrl.model.g, 2),
               'k': round(ctrl.model.k, 3),
               'resends': shot.resends,
               'alive_until': round(bs.time() - shot.t_fire, 2),
               't_cross': (None if shot.t_cross < 0 else
                           round(shot.t_cross - shot.t_fire, 2)),
               'grounded': grounded,
               'cross': (None if shot.cross is None else
                         [round(shot.cross[0], 2), round(shot.cross[1], 2)])}
        self._registry.shots.append(rec)
        print('[GKB] shot %s -> %s (%d direction changes, reached goal in '
              '%s s, arrival height %s, g=%.1f)' % (
                  pat.pid, reason, len(ctrl.cmds), rec['t_cross'],
                  None if shot.cross is None else round(shot.cross[1], 2),
                  ctrl.model.g))
        clean = (not goal and reason in ('high', 'wide', 'low', 'frame')
                 and not disturbed)
        self._registry.record_live(pat.pid, goal, clean)
        if self._shots_fired % 5 == 0:
            self._registry.save()

    # ======================================================================
    #  Gravity calibration from the very first falling balls
    # ======================================================================
    def _start_drop_calib(self, puck: Puck) -> None:
        self._drop_tries += 1
        self._drop_state = {'puck': puck, 'pts': [], 'gs': [],
                            'until': bs.time() + 0.6}
        self._drop_timer = bs.Timer(0.016,
                                    bs.WeakCall(self._drop_poll),
                                    repeat=True)

    def _drop_poll(self) -> None:
        st = self._drop_state
        geo = self._geo
        puck = st.get('puck')
        t = bs.time()
        if geo is None or not self._alive(puck) or t > st['until']:
            if len(st.get('gs', [])) >= 2:
                self._calib.absorb(st['gs'], [], [])
            self._drop_timer = None
            return
        y = puck.node.position[1]
        pts = st['pts']
        if not pts or t > pts[-1][0] + 1e-6:
            pts.append((t, y))
        if len(pts) > 3:
            pts.pop(0)
        if len(pts) == 3:
            (t0, y0), (t1, y1), (t2, y2) = pts
            d1, d2 = t1 - t0, t2 - t1
            low = geo.rest_y + 0.12
            if (0.008 <= d1 <= 0.1 and 0.008 <= d2 <= 0.1
                    and min(y0, y1, y2) > low and y2 < y1 < y0):
                a = 2.0 * ((y2 - y1) / d2 - (y1 - y0) / d1) / (d1 + d2)
                if 5.0 < -a < 60.0:
                    st['gs'].append(-a)

# made by buffon
# telegram: TechOtice
