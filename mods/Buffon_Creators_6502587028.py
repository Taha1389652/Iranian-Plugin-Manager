# Released under the MIT License. See LICENSE for details.
#
"""Implements football games (both co-op and teams varieties)."""

# ba_meta require api 9
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

from typing import TYPE_CHECKING
import random
import math

import babase
import bascenev1 as bs
from bascenev1lib.actor.spaz import Spaz
from bascenev1lib.game.hockey import PuckDiedMessage, Player, Team, HockeyGame
from bascenev1lib.gameutils import SharedObjects
from bascenev1lib.actor.scoreboard import Scoreboard
from bascenev1lib.actor.powerupbox import PowerupBoxFactory
from bascenev1lib.actor.playerspaz import PlayerSpaz, PlayerSpazHurtMessage
from bascenev1lib.actor.spazfactory import SpazFactory

if TYPE_CHECKING:
    from typing import Any, Sequence, Dict, Type, List, Optional, Union


class NewPlayerSpaz(PlayerSpaz):
    def on_bomb_press(self) -> None:
        # Bomb throwing disabled: pressing the bomb button does nothing.
        return None

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
                bs.playsound(SpazFactory.get().block_sound,
                             1.0,
                             position=self.node.position)
                return True

            # If we were recently hit, don't count this as another.
            local_time = bs.time(timeformat=bs.TimeFormat.MILLISECONDS)
            assert isinstance(local_time, int)
            if (self._last_hit_time is None
                    or local_time - self._last_hit_time > 1000):
                self._num_times_hit += 1
                self._last_hit_time = local_time

            mag = msg.magnitude * self.impact_scale
            velocity_mag = msg.velocity_magnitude * self.impact_scale
            damage_scale = 0.22

            # If they've got a shield, deliver it to that instead.
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
                    bs.playsound(SpazFactory.get().shield_down_sound,
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
                    bs.playsound(SpazFactory.get().shield_hit_sound,
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
                bs.playsound(sound, 1.0, position=self.node.position)

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
                        babase.WeakCall(self.curse_explode,
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


class Puck(bs.Actor):
    """A lovely giant hockey puck."""

    def __init__(self, position: Sequence[float] = (0.0, 1.0, 0.0)):
        super().__init__()
        shared = SharedObjects.get()
        activity = self.getactivity()

        self._spawn_pos = (position[0], position[1] + 1.0, position[2])
        self.last_players_to_touch: Dict[int, Player] = {}
        self.scored = False
        assert activity is not None
        assert isinstance(activity, SoccerGame)
        pmats = [shared.object_material, activity.puck_material]
        self.node = bs.newnode('prop',
                               delegate=self,
                               attrs={
                                   'model': bs.getmodel('frostyPelvis'),
                                   'color_texture':
                                        bs.gettexture('aliBSRemoteIOSQR'),
                                   'color': (0.05, 0.3, 1.0),
                                   'body': 'sphere',
                                   'reflection': 'soft',
                                   'reflection_scale': [0.2],
                                   'shadow_size': 0.5,
                                   'is_area_of_interest': True,
                                   'position': self._spawn_pos,
                                   'materials': pmats
                               })
        bs.animate(self.node, 'model_scale', {0: 0, 0.2: 1.2, 0.26: 1.0})

    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, bs.DieMessage):
            assert self.node
            self.node.delete()
            activity = self._activity()
            if activity and not msg.immediate:
                activity.handlemessage(PuckDiedMessage(self))

        elif isinstance(msg, bs.OutOfBoundsMessage):
            assert self.node
            self.node.position = self._spawn_pos

        elif isinstance(msg, bs.HitMessage):
            assert self.node
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
        else:
            super().handlemessage(msg)


# ba_meta export game
class SoccerGame(HockeyGame):
    """Football game for teams mode."""

    name = 'Buffon Creator'
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
        bs.BoolSetting('شوت خودکار توپ به دروازه', default=False),
        bs.BoolSetting('Epic Mode', default=False),
    ]

    _H_FRACS = [-0.85, -0.65, -0.45, -0.25, -0.08, 0.0, 0.08,
                0.25, 0.45, 0.65, 0.85]
    _V_FRACS = [0.08, 0.2, 0.35, 0.5, 0.65, 0.8, 0.95]
    _POWER_LEVELS = {
        'افسانه‌ای': (20.0, 23.0),
    }
    _TRAJECTORIES = ['هوایی']
    _APPROACH_CURVE = {
        'وسط': 0.0,
        'چپ': -3.5,
        'راست': 3.5,
        'جلوی_دروازه': 1.2,
        'پشت_دروازه': -1.8,
    }

    @classmethod
    def get_supported_maps(cls, sessiontype: Type[bs.Session]) -> List[str]:
        return bs.getmaps('hockey')

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
        self._auto_shoot = bool(settings.get('شوت خودکار توپ به دروازه', False))
        self._current_shot_target: Optional[Sequence[float]] = None
        self._epic_mode = bool(settings['Epic Mode'])
        
        self.slow_motion = self._epic_mode
        self.default_music = (bs.MusicType.EPIC
                              if self._epic_mode else bs.MusicType.FOOTBALL)
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
        self._score_to_win = int(settings['Score to Win'])
        self._time_limit = float(settings['Time Limit'])

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
        self._goal_target_pos = defs.boxes['goal2'][0:3]
        self._goal_scale = defs.boxes['goal2'][6:9]

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

        self._spawn_puck()
        self._update_scoreboard()
        bs.playsound(self._chant_sound)

        self._credit_text = bs.NodeActor(
            bs.newnode('text',
                       attrs={
                           'text': ('Creator:Buffon\n'
                                     'Telegram:@TechOtice\n'
                                     'Rubika:@TechOtice'),
                           'host_only': True,
                           'v_attach': 'top',
                           'h_attach': 'center',
                           'h_align': 'center',
                           'v_align': 'top',
                           'position': (-90, -34),
                           'scale': 1.15,
                           'color': (1.0, 0.78, 0.05),
                           'shadow': 1.0,
                           'flatness': 0.0,
                           'maxwidth': 340,
                       }))

    def spawn_player(self, player: Player) -> bs.Actor:
        from babase import _math

        if isinstance(self.session, bs.DualTeamSession):
            position = self.map.get_start_position(player.team.id)
        else:
            position = self.map.get_ffa_start_position(self.players)
        angle = None

        name = player.getname()
        color = player.color
        highlight = player.highlight

        light_color = _math.normalized_color(color)
        display_color = bs.safecolor(color, target_intensity=0.75)

        if self._hit_players:
            spaz = PlayerSpaz(color=color,
                              highlight=highlight,
                              character=player.character,
                              player=player)
        else:
            spaz = NewPlayerSpaz(color=color,
                                  highlight=highlight,
                                  character=player.character,
                                  player=player)

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
        bs.playsound(self._spawn_sound, 1, position=spaz.node.position)
        light = bs.newnode('light', attrs={'color': light_color})
        spaz.node.connectattr('position', light, 'position')
        bs.animate(light, 'intensity', {0: 0, 0.25: 1, 0.5: 0})
        bs.timer(0.5, light.delete)
        return spaz

    def _get_random_spawn_position(self) -> Sequence[float]:
        base = self._center_flag_pos
        target = self._goal_target_pos
        dx = target[0] - base[0]
        dz = target[2] - base[2]
        dist = math.sqrt(dx * dx + dz * dz) or 1.0
        back_x, back_z = -dx / dist, -dz / dist
        perp_x, perp_z = -back_z, back_x

        back_dist = random.uniform(4.5, 7.0)
        lateral = random.uniform(-2.5, 2.5)
        return (base[0] + back_x * back_dist + perp_x * lateral, base[1],
                base[2] + back_z * back_dist + perp_z * lateral)

    def _pick_random_shot(self) -> Dict[str, Any]:
        approach = random.choice(list(self._APPROACH_CURVE.keys()))
        return {
            'h_frac': random.choice(self._H_FRACS),
            'v_frac': random.choice(self._V_FRACS),
            'power': random.choice(list(self._POWER_LEVELS.keys())),
            'trajectory': random.choice(self._TRAJECTORIES),
            'approach': approach,
            'curve': self._APPROACH_CURVE[approach] * random.uniform(0.7, 1.3),
        }

    def _pick_aerial_target(self) -> Sequence[float]:
        target = self._goal_target_pos
        scale = self._goal_scale
        half_w = max(0.6, abs(scale[0]) * 0.5 * 0.85)
        height = max(1.4, abs(scale[1]) * 0.9)
        h_frac = random.choice(self._H_FRACS)
        v_frac = random.choice(self._V_FRACS)
        return (target[0] + h_frac * half_w, target[1] + v_frac * height,
                target[2])

    def _spawn_puck(self) -> None:
        if self._auto_shoot:
            self._puck_spawn_pos = self._get_random_spawn_position()
        bs.playsound(self._swipsound)
        bs.playsound(self._whistle_sound)
        self._flash_puck_spawn()
        assert self._puck_spawn_pos is not None
        self._puck = Puck(position=self._puck_spawn_pos)
        if self._auto_shoot:
            this_puck = self._puck
            shot = self._pick_random_shot()
            shoot_delay = 0.5
            bs.timer(shoot_delay, babase.WeakCall(self._shoot_puck, this_puck, shot))
            reset_delay = shoot_delay + random.uniform(2.0, 3.0)
            bs.timer(reset_delay, babase.WeakCall(self._check_force_reset, this_puck))

    def _shoot_puck(self, puck: Puck, shot: Dict[str, Any]) -> None:
        if puck is None or puck.node is None or self._puck is not puck:
            return
        target = self._goal_target_pos
        scale = self._goal_scale
        half_w = max(0.6, abs(scale[0]) * 0.5 * 0.85)
        height = max(1.4, abs(scale[1]) * 0.9)
        tx = target[0] + shot['h_frac'] * half_w
        ty = target[1] + shot['v_frac'] * height
        tz = target[2]
        self._current_shot_target = (tx, ty, tz)

        pos = puck.node.position
        dx, dy, dz = tx - pos[0], ty - pos[1], tz - pos[2]
        dist = math.sqrt(dx * dx + dy * dy + dz * dz) or 0.001
        speed = random.uniform(*self._POWER_LEVELS[shot['power']])

        vy = speed * 0.55
        vx = (dx / dist) * speed
        vz = (dz / dist) * speed
        perp_x, perp_z = -dz / dist, dx / dist
        curve = shot['curve']
        puck.node.velocity = (vx + perp_x * curve, vy, vz + perp_z * curve)
        bs.playsound(self._swipsound)

        bs.timer(0.28, babase.WeakCall(self._home_puck, puck, speed, 1))
        bs.timer(0.55, babase.WeakCall(self._home_puck, puck, speed, 2))
        bs.timer(0.85, babase.WeakCall(self._home_puck, puck, speed, 3))

    def _home_puck(self, puck: Puck, speed: float, stage: int = 3) -> None:
        if (puck is None or puck.node is None or self._puck is not puck
                or self._current_shot_target is None):
            return
        if stage == 2:
            self._current_shot_target = self._pick_aerial_target()
        tx, ty, tz = self._current_shot_target
        pos = puck.node.position
        dx, dy, dz = tx - pos[0], ty - pos[1], tz - pos[2]
        dist = math.sqrt(dx * dx + dy * dy + dz * dz)
        if dist < 0.001:
            return
        if stage == 1:
            vy = dy / dist * speed * 0.95 + 4.5
        elif stage == 2:
            vy = dy / dist * speed * 0.65 + 1.2
        else:
            vy = dy / dist * speed * 0.6 + 1.0
        puck.node.velocity = (dx / dist * speed, vy, dz / dist * speed)

    def _check_force_reset(self, puck: Puck) -> None:
        if puck is None:
            return
        if self._puck is puck and puck.node:
            puck.handlemessage(bs.DieMessage(immediate=True))
            self._spawn_puck()
#made by buffon
#telegram:TechOtice
