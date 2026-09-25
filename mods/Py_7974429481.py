# ba_meta require api 9
"""Arian Football: custom map + game mode + lighting + practice bots, for BombSquad 1.7.62."""
from __future__ import annotations
import random
import babase
import bascenev1 as bs
from bascenev1lib.game.hockey import HockeyGame, Player
from bascenev1lib.maps import FootballStadium
from bascenev1lib.actor.spaz import Spaz


# ba_meta export bascenev1.Map
class ArianMap(FootballStadium):
    """The Arian map: the game's real football stadium, registered under a new name."""
    name = 'Arian'

    @classmethod
    def get_play_types(cls):
        return ['melee', 'hockey', 'team_flag', 'keep_away']

    @classmethod
    def get_preview_texture_name(cls):
        return 'footballStadiumPreview'


# ba_meta export babase.Plugin
class ArianPlugin(babase.Plugin):
    """Registers the Arian map with the engine on launch."""

    def on_app_running(self) -> None:
        try:
            bs.register_map(ArianMap)
        except Exception as exc:
            print('Arian map register failed:', exc)


class PracticeBot(Spaz):
    """A very simple AI player: chases the puck and punches toward it.

    EXPERIMENTAL: hand-written AI, not the game's official bot system.
    May need tuning once tested live.
    """

    def __init__(self, position, color, highlight, activity):
        super().__init__(color=color,
                          highlight=highlight,
                          character=random.choice(
                              ['Kronk', 'Zoe', 'Jack Morgan', 'Mel']),
                          source_player=None,
                          start_invincible=False,
                          powerups_expire=False)
        self._activity = activity
        self.node.position = position
        self._alive = True
        self._think_timer = bs.Timer(0.15, bs.WeakCall(self._think),
                                      repeat=True)

    def _think(self) -> None:
        if not self._alive or not self.node or self.node.hitpoints <= 0:
            return
        activity = self._activity
        if activity is None or not activity.puck_node_exists():
            return
        my_pos = self.node.position
        puck_pos = activity.get_puck_position()
        if puck_pos is None:
            return
        dx = puck_pos[0] - my_pos[0]
        dz = puck_pos[2] - my_pos[2]
        dist = (dx * dx + dz * dz) ** 0.5

        if dist > 0.01:
            self.node.move_left_right = max(-1.0, min(1.0, dx / 3.0))
            self.node.move_up_down = max(-1.0, min(1.0, -dz / 3.0))
        if dist < 2.0:
            self.node.punch_pressed = True
            bs.timer(0.15, bs.WeakCall(self._release_punch))

    def _release_punch(self) -> None:
        if self.node:
            self.node.punch_pressed = False

    def handlemessage(self, msg):
        if isinstance(msg, bs.DieMessage):
            self._alive = False
        return super().handlemessage(msg)


# ba_meta export bascenev1.GameActivity
class ArianFootball(HockeyGame):
    """Football on the Arian map: red ball, lighting effects, optional practice bots."""

    name = 'Arian Football'
    description = 'Football on the Arian map, by Arian.'
    available_settings = [
        *HockeyGame.available_settings,
        bs.BoolSetting('نورپردازی زیبا', default=True),
        bs.IntChoiceSetting(
            'تعداد بات تمرینی',
            choices=[('هیچکدام', 0), ('یک', 1), ('دو', 2), ('سه', 3)],
            default=0),
    ]

    @classmethod
    def get_supported_maps(cls, sessiontype):
        return ['Arian']

    def __init__(self, settings: dict):
        super().__init__(settings)
        self._pretty_lights = bool(settings.get('نورپردازی زیبا', True))
        self._bot_count = int(settings.get('تعداد بات تمرینی', 0))
        self._title_text = None
        self._light_nodes: list = []
        self._bots: list = []

    def puck_node_exists(self) -> bool:
        return self._puck is not None and bool(self._puck.node)

    def get_puck_position(self):
        if self._puck is not None and self._puck.node:
            return self._puck.node.position
        return None

    def _spawn_puck(self) -> None:
        super()._spawn_puck()
        try:
            self._puck.node.color = (1.0, 0.05, 0.05)
        except Exception as exc:
            print('Arian red puck failed:', exc)

    def spawn_player(self, player: Player):
        spaz = super().spawn_player(player)
        try:
            spaz.connect_controls_to_player(enable_bomb=False)
        except Exception as exc:
            print('Arian bomb-disable failed:', exc)
        return spaz

    def on_begin(self) -> None:
        super().on_begin()

        # Big floating title above the field.
        try:
            title_pos = (self._puck_spawn_pos[0],
                         self._puck_spawn_pos[1] + 6.0,
                         self._puck_spawn_pos[2])
            self._title_text = bs.NodeActor(
                bs.newnode('text',
                           attrs={
                               'text': 'Arian',
                               'in_world': True,
                               'position': title_pos,
                               'h_align': 'center',
                               'v_align': 'center',
                               'shadow': 1.0,
                               'flatness': 1.0,
                               'color': (1.0, 1.0, 1.0),
                               'scale': 0.025
                           }))
        except Exception as exc:
            print('Arian title text failed:', exc)

        # Colorful animated stadium lighting.
        if self._pretty_lights:
            try:
                self._setup_pretty_lights()
            except Exception as exc:
                print('Arian lighting failed:', exc)

        # Practice bots (experimental).
        if self._bot_count > 0:
            try:
                self._spawn_bots()
            except Exception as exc:
                print('Arian bots failed:', exc)

    def _setup_pretty_lights(self) -> None:
        base = self._puck_spawn_pos
        colors = [(1.0, 0.3, 0.3), (0.3, 0.5, 1.0), (0.3, 1.0, 0.4),
                  (1.0, 0.85, 0.2)]
        offsets = [(-6.0, 5.0, -3.0), (6.0, 5.0, -3.0), (-6.0, 5.0, 3.0),
                   (6.0, 5.0, 3.0)]
        for offset, color in zip(offsets, colors):
            pos = (base[0] + offset[0], base[1] + offset[1],
                   base[2] + offset[2])
            light = bs.newnode('light',
                               attrs={
                                   'position': pos,
                                   'radius': 0.4,
                                   'intensity': 0.6,
                                   'height_attenuated': False,
                                   'color': color
                               })
            self._light_nodes.append(bs.NodeActor(light))
            bs.animate_array(light, 'color', 3, {
                0.0: color,
                1.0: (color[0] * 0.5, color[1] * 0.5, color[2] * 0.5),
                2.0: color,
            }, loop=True)

    def _spawn_bots(self) -> None:
        base = self._puck_spawn_pos
        team_colors = [(0.2, 0.4, 1.0), (1.0, 0.3, 0.3)]
        for i in range(self._bot_count):
            side = -1 if i % 2 == 0 else 1
            pos = (base[0] + side * 4.0, base[1] + 1.0,
                  base[2] + (i - self._bot_count / 2.0) * 2.0)
            color = team_colors[i % 2]
            bot = PracticeBot(position=pos,
                              color=color,
                              highlight=(1.0, 1.0, 1.0),
                              activity=self)
            self._bots.append(bot)
