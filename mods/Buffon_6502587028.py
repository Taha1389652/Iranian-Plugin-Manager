# Released under the MIT License. See LICENSE for details.
#
"""Implements football games (both co-op and teams varieties)."""

# ba_meta require api 7
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

from typing import TYPE_CHECKING

import ba
import random
import math
from bastd.actor.spaz import Spaz
from bastd.game.hockey import PuckDiedMessage, Player, Team, HockeyGame
from bastd.gameutils import SharedObjects
from bastd.actor.scoreboard import Scoreboard
from bastd.actor.powerupbox import PowerupBoxFactory
from bastd.actor.playerspaz import PlayerSpaz, PlayerSpazHurtMessage
from bastd.actor.spazfactory import SpazFactory

if TYPE_CHECKING:
    from typing import Any, Sequence, Dict, Type, List, Optional, Union


class NewPlayerSpaz(PlayerSpaz):
    def on_bomb_press(self) -> None:
        # Bomb throwing disabled: pressing the bomb button does nothing.
        return None

    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, ba.HitMessage):
            source_player = msg.get_source_player(type(self._player))
            if source_player:
                self.last_player_attacked_by = source_player
                self.last_attacked_time = ba.time()
                self.last_attacked_type = (msg.hit_type, msg.hit_subtype)

            if not self.node:
                return None
            if self.node.invincible:
                ba.playsound(SpazFactory.get().block_sound,
                             1.0,
                             position=self.node.position)
                return True

            # If we were recently hit, don't count this as another.
            # (so punch flurries and bomb pileups essentially count as 1 hit)
            local_time = ba.time(timeformat=ba.TimeFormat.MILLISECONDS)
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
                    # Hit our spaz with an impulse but tell it to only return
                    # theoretical damage; not apply the impulse.
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

                # Its a cleaner event if a hit just kills the shield
                # without damaging the player.
                # However, massive damage events should still be able to
                # damage the player. This hopefully gives us a happy medium.
                max_spillover = SpazFactory.get().max_shield_spillover_damage
                if self.shield_hitpoints <= 0:

                    # FIXME: Transition out perhaps?
                    self.shield.delete()
                    self.shield = None
                    ba.playsound(SpazFactory.get().shield_down_sound,
                                 1.0,
                                 position=self.node.position)

                    # Emit some cool looking sparks when the shield dies.
                    npos = self.node.position
                    ba.emitfx(position=(npos[0], npos[1] + 0.9, npos[2]),
                              velocity=self.node.velocity,
                              count=random.randrange(20, 30),
                              scale=1.0,
                              spread=0.6,
                              chunk_type='spark')

                else:
                    ba.playsound(SpazFactory.get().shield_hit_sound,
                                 0.5,
                                 position=self.node.position)

                # Emit some cool looking sparks on shield hit.
                assert msg.force_direction is not None
                ba.emitfx(position=msg.pos,
                          velocity=(msg.force_direction[0] * 1.0,
                                    msg.force_direction[1] * 1.0,
                                    msg.force_direction[2] * 1.0),
                          count=min(30, 5 + int(damage * 0.005)),
                          scale=0.5,
                          spread=0.3,
                          chunk_type='spark')

                # If they passed our spillover threshold,
                # pass damage along to spaz.
                if self.shield_hitpoints <= -max_spillover:
                    leftover_damage = -max_spillover - self.shield_hitpoints
                    shield_leftover_ratio = leftover_damage / damage

                    # Scale down the magnitudes applied to spaz accordingly.
                    mag *= shield_leftover_ratio
                    velocity_mag *= shield_leftover_ratio
                else:
                    return True  # Good job shield!
            else:
                shield_leftover_ratio = 1.0

            if msg.flat_damage:
                damage = int(msg.flat_damage * self.impact_scale *
                             shield_leftover_ratio)
            else:
                # Hit it with an impulse and get the resulting damage.
                assert msg.force_direction is not None
                if msg.hit_type != 'punch':
                    self.node.handlemessage(
                        'impulse', msg.pos[0], msg.pos[1], msg.pos[2],
                        msg.velocity[0], msg.velocity[1], msg.velocity[2], mag,
                        velocity_mag, msg.radius, 0, msg.force_direction[0],
                        msg.force_direction[1], msg.force_direction[2])

                damage = int(damage_scale * self.node.damage)
            self.node.handlemessage('hurt_sound')

            # Play punch impact sound based on damage if it was a punch.
            if msg.hit_type == 'punch':
                if self.node.hold_node:
                    self.node.hold_node = None
                damage = 0
                sound = SpazFactory.get().punch_sound
                ba.playsound(sound, 1.0, position=self.node.position)

                # Throw up some chunks.
                assert msg.force_direction is not None
                ba.emitfx(position=msg.pos,
                          velocity=(msg.force_direction[0] * 0.5,
                                    msg.force_direction[1] * 0.5,
                                    msg.force_direction[2] * 0.5),
                          count=min(10, 1 + int(100 * 0.0025)),
                          scale=0.3,
                          spread=0.03)

                ba.emitfx(position=msg.pos,
                          chunk_type='sweat',
                          velocity=(msg.force_direction[0] * 1.3,
                                    msg.force_direction[1] * 1.3 + 5.0,
                                    msg.force_direction[2] * 1.3),
                          count=min(30, 1 + int(100 * 0.04)),
                          scale=0.9,
                          spread=0.28)

                # Momentary flash.
                hurtiness = 100 * 0.003
                punchpos = (msg.pos[0] + msg.force_direction[0] * 0.02,
                            msg.pos[1] + msg.force_direction[1] * 0.02,
                            msg.pos[2] + msg.force_direction[2] * 0.02)
                flash_color = (1.0, 0.8, 0.4)
                light = ba.newnode(
                    'light',
                    attrs={
                        'position': punchpos,
                        'radius': 0.12 + hurtiness * 0.12,
                        'intensity': 0.3 * (1.0 + 1.0 * hurtiness),
                        'height_attenuated': False,
                        'color': flash_color
                    })
                ba.timer(0.06, light.delete)

                flash = ba.newnode('flash',
                                   attrs={
                                       'position': punchpos,
                                       'size': 0.17 + 0.17 * hurtiness,
                                       'color': flash_color
                                   })
                ba.timer(0.06, flash.delete)

            if msg.hit_type == 'impact':
                assert msg.force_direction is not None
                ba.emitfx(position=msg.pos,
                          velocity=(msg.force_direction[0] * 2.0,
                                    msg.force_direction[1] * 2.0,
                                    msg.force_direction[2] * 2.0),
                          count=min(10, 1 + int(damage * 0.01)),
                          scale=0.4,
                          spread=0.1)
            if self.hitpoints > 0:

                # It's kinda crappy to die from impacts, so lets reduce
                # impact damage by a reasonable amount *if* it'll keep us alive
                if msg.hit_type == 'impact' and damage > self.hitpoints:
                    # Drop damage to whatever puts us at 10 hit points,
                    # or 200 less than it used to be whichever is greater
                    # (so it *can* still kill us if its high enough)
                    newdamage = max(damage - 200, self.hitpoints - 10)
                    damage = newdamage
                self.node.handlemessage('flash')

                # If we're holding something, drop it.
                if damage > 0.0 and self.node.hold_node:
                    self.node.hold_node = None
                self.hitpoints -= damage
                self.node.hurt = 1.0 - float(
                    self.hitpoints) / self.hitpoints_max

                # If we're cursed, *any* damage blows us up.
                if self._cursed and damage > 0:
                    ba.timer(
                        0.05,
                        ba.WeakCall(self.curse_explode,
                                    msg.get_source_player(ba.Player)))

                # If we're frozen, shatter.. otherwise die if we hit zero
                if self.frozen and (damage > 200 or self.hitpoints <= 0):
                    self.shatter()
                elif self.hitpoints <= 0:
                    self.node.handlemessage(
                        ba.DieMessage(how=ba.DeathType.IMPACT))

            # If we're dead, take a look at the smoothed damage value
            # (which gives us a smoothed average of recent damage) and shatter
            # us if its grown high enough.
            if self.hitpoints <= 0:
                damage_avg = self.node.damage_smoothed * damage_scale
                if damage_avg > 1000:
                    self.shatter()

            activity = self._activity()
            if activity is not None and self._player.exists():
                activity.handlemessage(PlayerSpazHurtMessage(self))
        else:
            super().handlemessage(msg)

class Puck(ba.Actor):
    """A lovely giant hockey puck."""

    def __init__(self, position: Sequence[float] = (0.0, 1.0, 0.0)):
        super().__init__()
        shared = SharedObjects.get()
        activity = self.getactivity()

        # Spawn just above the provided point.
        self._spawn_pos = (position[0], position[1] + 1.0, position[2])
        self.last_players_to_touch: Dict[int, Player] = {}
        self.scored = False
        assert activity is not None
        assert isinstance(activity, SoccerGame)
        pmats = [shared.object_material, activity.puck_material]
        self.node = ba.newnode('prop',
                               delegate=self,
                               attrs={
                                   'model': ba.getmodel('frostyPelvis'),
                                   'color_texture':
                                        ba.gettexture('aliBSRemoteIOSQR'),
                                   'color': (0.05, 0.3, 1.0),
                                   'body': 'sphere',
                                   'reflection': 'soft',
                                   'reflection_scale': [0.2],
                                   'shadow_size': 0.5,
                                   'is_area_of_interest': True,
                                   'position': self._spawn_pos,
                                   'materials': pmats
                               })
        ba.animate(self.node, 'model_scale', {0: 0, 0.2: 1.2, 0.26: 1.0})

    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, ba.DieMessage):
            assert self.node
            self.node.delete()
            activity = self._activity()
            if activity and not msg.immediate:
                activity.handlemessage(PuckDiedMessage(self))

        # If we go out of bounds, move back to where we started.
        elif isinstance(msg, ba.OutOfBoundsMessage):
            assert self.node
            self.node.position = self._spawn_pos

        elif isinstance(msg, ba.HitMessage):
            assert self.node
            assert msg.force_direction is not None
            self.node.handlemessage(
                'impulse', msg.pos[0], msg.pos[1], msg.pos[2], msg.velocity[0],
                msg.velocity[1], msg.velocity[2], 1.0 * msg.magnitude,
                1.0 * msg.velocity_magnitude, msg.radius, 0,
                msg.force_direction[0], msg.force_direction[1],
                msg.force_direction[2])

            # If this hit came from a player, log them as the last to touch us.
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
        ba.IntSetting(
            'Score to Win',
            min_value=1,
            default=1,
            increment=1,
        ),
        ba.IntChoiceSetting(
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
        ba.FloatChoiceSetting(
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
        ba.BoolSetting('پانچ بینهایت', default=False),
        ba.BoolSetting('اسپاون باکس های کمکی', default=True),
        ba.BoolSetting('سرعت در دوییدن', default=True),
        ba.BoolSetting('صدمه زدن به پلیر', default=False),
        ba.BoolSetting('شوت خودکار توپ به دروازه', default=False),
        ba.BoolSetting('Epic Mode', default=False),
    ]

    # --- Buffon Creator: shot-variety tables -----------------------------
    # Horizontal target spots inside the goal mouth (fraction of half-width,
    # negative = left post, positive = right post).
    _H_FRACS = [-0.85, -0.65, -0.45, -0.25, -0.08, 0.0, 0.08,
                0.25, 0.45, 0.65, 0.85]
    # Vertical target spots inside the goal mouth (0 = ground, 1 = crossbar).
    _V_FRACS = [0.08, 0.2, 0.35, 0.5, 0.65, 0.8, 0.95]
    # Shot power presets -> (min_speed, max_speed). Only hard shots now.
    _POWER_LEVELS = {
        'افسانه‌ای': (20.0, 23.0),
    }
    # Shot trajectory shapes -- aerial shots only.
    _TRAJECTORIES = ['هوایی']
    # Approach angle the shot curves in from -> sideways curve amount.
    _APPROACH_CURVE = {
        'وسط': 0.0,
        'چپ': -3.5,
        'راست': 3.5,
        'جلوی_دروازه': 1.2,
        'پشت_دروازه': -1.8,
    }
    # -----------------------------------------------------------------

    @classmethod
    def get_supported_maps(cls, sessiontype: Type[ba.Session]) -> List[str]:
        return ba.getmaps('hockey')

    def __init__(self, settings: dict):
        super().__init__(settings)
        shared = SharedObjects.get()
        self._scoreboard = Scoreboard()
        self._cheer_sound = ba.getsound('cheer')
        self._chant_sound = ba.getsound('crowdChant')
        self._foghorn_sound = ba.getsound('foghorn')
        self._swipsound = ba.getsound('swip')
        self._whistle_sound = ba.getsound('refWhistle')
        self._boxing_gloves = bool(settings.get('پانچ بینهایت', False))
        self._enable_powerups = bool(settings.get('اسپاون باکس های کمکی', True))
        self._ice_floor = bool(settings.get('سرعت در دوییدن', True))
        self._hit_players = bool(settings['صدمه زدن به پلیر'])
        self._auto_shoot = bool(settings.get('شوت خودکار توپ به دروازه', False))
        self._current_shot_target: Optional[Sequence[float]] = None
        self._epic_mode = bool(settings['Epic Mode'])
        # Base class overrides:
        self.slow_motion = self._epic_mode
        self.default_music = (ba.MusicType.EPIC
                              if self._epic_mode else ba.MusicType.FOOTBALL)
        self.puck_material = ba.Material()
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

        # Keep track of which player last touched the puck
        self.puck_material.add_actions(
            conditions=('they_have_material', shared.player_material),
            actions=('call', 'at_connect', self._handle_puck_player_collide))

        # We want the puck to kill powerups; not get stopped by them
        self.puck_material.add_actions(
            conditions=('they_have_material',
                        PowerupBoxFactory.get().powerup_material),
            actions=(('modify_part_collision', 'physical', False),
                     ('message', 'their_node', 'at_connect', ba.DieMessage())))
        self._score_region_material = ba.Material()
        self._score_region_material.add_actions(
            conditions=('they_have_material', self.puck_material),
            actions=(('modify_part_collision', 'collide',
                      True), ('modify_part_collision', 'physical', False),
                     ('call', 'at_connect', self._handle_score)))
        self._puck_spawn_pos: Optional[Sequence[float]] = None
        self._center_flag_pos: Optional[Sequence[float]] = None
        self._score_regions: Optional[List[ba.NodeActor]] = None
        self._puck: Optional[Puck] = None
        self._score_to_win = int(settings['Score to Win'])
        self._time_limit = float(settings['Time Limit'])

    def on_transition_in(self) -> None:
        super().on_transition_in()
        shared = SharedObjects.get()
        activity = ba.getactivity()
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
        else:
            pass

        # Set up goal data (needed before the first puck spawn, since spawn
        # position depends on the direction back from the goal).
        self._center_flag_pos = self.map.get_flag_position(None)
        self._puck_spawn_pos = self._center_flag_pos
        defs = self.map.defs
        self._goal_target_pos = defs.boxes['goal2'][0:3]
        self._goal_scale = defs.boxes['goal2'][6:9]

        # Only the left-side goal (goal2) is used -- the right-side goal
        # (goal1) is intentionally removed, there is no score region for it.
        self._score_regions = []
        self._score_regions.append(
            ba.NodeActor(
                ba.newnode('region',
                           attrs={
                               'position': defs.boxes['goal2'][0:3],
                               'scale': defs.boxes['goal2'][6:9],
                               'type': 'box',
                               'materials': [self._score_region_material]
                           })))

        self._spawn_puck()
        self._update_scoreboard()
        ba.playsound(self._chant_sound)

        # Persistent creator-credit text in the top-left corner.
        self._credit_text = ba.NodeActor(
            ba.newnode('text',
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

    def spawn_player(self, player: Player) -> ba.Actor:
        from ba import _math
        from ba._gameutils import animate
        from ba._coopsession import CoopSession

        if isinstance(self.session, ba.DualTeamSession):
            position = self.map.get_start_position(player.team.id)
        else:
            # otherwise do free-for-all spawn locations
            position = self.map.get_ffa_start_position(self.players)
        angle = None

        name = player.getname()
        color = player.color
        highlight = player.highlight

        light_color = _math.normalized_color(color)
        display_color = ba.safecolor(color, target_intensity=0.75)

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

        # If this is co-op and we're on Courtyard or Runaround, add the
        # material that allows us to collide with the player-walls.
        # FIXME: Need to generalize this.
        if isinstance(self.session, CoopSession) and self.map.getname() in [
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

        # Move to the stand position and add a flash of light.
        spaz.handlemessage(
            ba.StandMessage(
                position,
                angle if angle is not None else random.uniform(0, 360)))
        ba.playsound(self._spawn_sound, 1, position=spaz.node.position)
        light = ba.newnode('light', attrs={'color': light_color})
        spaz.node.connectattr('position', light, 'position')
        animate(light, 'intensity', {0: 0, 0.25: 1, 0.5: 0})
        ba.timer(0.5, light.delete)
        return spaz

    def _get_random_spawn_position(self) -> Sequence[float]:
        """Spawn the puck behind the center, away from the goal, so every
        shot has real distance to cover (harder than a point-blank shot)."""
        base = self._center_flag_pos
        target = self._goal_target_pos
        dx = target[0] - base[0]
        dz = target[2] - base[2]
        dist = math.sqrt(dx * dx + dz * dz) or 1.0
        # Unit vector pointing AWAY from the goal.
        back_x, back_z = -dx / dist, -dz / dist
        # Perpendicular unit vector, for side-to-side variety.
        perp_x, perp_z = -back_z, back_x

        back_dist = random.uniform(4.5, 7.0)
        lateral = random.uniform(-2.5, 2.5)
        return (base[0] + back_x * back_dist + perp_x * lateral, base[1],
                base[2] + back_z * back_dist + perp_z * lateral)

    def _pick_random_shot(self) -> Dict[str, Any]:
        """Randomly pick a hard/very-hard/legendary aerial shot combo."""
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
        """Pick a fresh spot inside the goal mouth (corner, under the
        crossbar, dead center, etc.) -- used to retarget a shot mid-flight
        for more varied trajectories."""
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
        ba.playsound(self._swipsound)
        ba.playsound(self._whistle_sound)
        self._flash_puck_spawn()
        assert self._puck_spawn_pos is not None
        self._puck = Puck(position=self._puck_spawn_pos)
        if self._auto_shoot:
            this_puck = self._puck
            shot = self._pick_random_shot()
            shoot_delay = 0.5
            ba.timer(shoot_delay, ba.WeakCall(self._shoot_puck, this_puck, shot))
            # If nobody scores within 2-3 seconds of the shot (a save),
            # vanish the puck, replant it, and fire a fresh legendary shot.
            reset_delay = shoot_delay + random.uniform(2.0, 3.0)
            ba.timer(reset_delay, ba.WeakCall(self._check_force_reset, this_puck))

    def _shoot_puck(self, puck: Puck, shot: Dict[str, Any]) -> None:
        """Fire the puck as a hard aerial shot toward the goal."""
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

        # All shots are aerial now -- decent upward arc so it clears
        # defenders and drops into the net from above.
        vy = speed * 0.55

        vx = (dx / dist) * speed
        vz = (dz / dist) * speed
        perp_x, perp_z = -dz / dist, dx / dist
        curve = shot['curve']
        puck.node.velocity = (vx + perp_x * curve, vy, vz + perp_z * curve)
        ba.playsound(self._swipsound)

        # Homing correction passes -- still exactly 3 passes like before,
        # but now staged for variety: pass 1 kicks the arc up higher,
        # pass 2 retargets to a fresh spot in the goal (corner, under the
        # crossbar, dead center...), pass 3 locks on for a reliable finish.
        ba.timer(0.28, ba.WeakCall(self._home_puck, puck, speed, 1))
        ba.timer(0.55, ba.WeakCall(self._home_puck, puck, speed, 2))
        ba.timer(0.85, ba.WeakCall(self._home_puck, puck, speed, 3))

    def _home_puck(self, puck: Puck, speed: float, stage: int = 3) -> None:
        if (puck is None or puck.node is None or self._puck is not puck
                or self._current_shot_target is None):
            return
        # Stage 2 -- swap in a new target so the shot doesn't always finish
        # at the spot it started heading for; gives ground/mid/under-bar/
        # corner variety instead of always the same line.
        if stage == 2:
            self._current_shot_target = self._pick_aerial_target()
        tx, ty, tz = self._current_shot_target
        pos = puck.node.position
        dx, dy, dz = tx - pos[0], ty - pos[1], tz - pos[2]
        dist = math.sqrt(dx * dx + dy * dy + dz * dz)
        if dist < 0.001:
            return
        if stage == 1:
            # Early pass -- send it way up high before it dives toward net.
            vy = dy / dist * speed * 0.95 + 4.5
        elif stage == 2:
            # Mid pass -- head toward the freshly picked target.
            vy = dy / dist * speed * 0.65 + 1.2
        else:
            # Final pass -- precise homing so it reliably finds the net.
            vy = dy / dist * speed * 0.6 + 1.0
        puck.node.velocity = (dx / dist * speed, vy, dz / dist * speed)

    def _check_force_reset(self, puck: Puck) -> None:
        """If a player saved the shot, reset and fire a fresh random one."""
        if puck is None:
            return
        if self._puck is puck and puck.node:
            puck.handlemessage(ba.DieMessage(immediate=True))
            self._spawn_puck()
#made by buffon
#telegram:TechOtice