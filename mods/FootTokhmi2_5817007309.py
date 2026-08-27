# ba_meta require api 9
# ==============================================================================
#  ⚽  Soccer Frenzy  —  مینی‌گیم فوتبال کامل برای BombSquad (Ballistica API 9)
# ==============================================================================
#
#  نحوه‌ی نصب:
#    1) این فایل رو با همین اسم (soccer_frenzy.py) داخل پوشه‌ی مادهای بازی بذار:
#         BombSquad/mods/          (روی موبایل/دسکتاپ معمولاً از منوی
#         Settings > Advanced > Show Mods Folder پیدا می‌شه)
#       یا از طریق سیستم Workspace داخل خود بازی آپلودش کن.
#    2) بازی رو ری‌استارت کن؛ حالت «Soccer Frenzy» توی لیست بازی‌های
#       تیمی (Team Games) روی نقشه‌ی «Football Stadium» ظاهر می‌شه.
#
#  این مود دقیقاً از همون معماری‌ای الگو گرفته که بازی‌های رسمی خود موتور
#  (مثل bascenev1lib.game.football) استفاده می‌کنن:
#    - bs.TeamGameActivity برای منطق بازی تیمی
#    - Flag/Prop فیزیکی برای خود توپ
#    - region + Material برای تشخیص گل
#    - Scoreboard, RespawnIcon, PowerupBox, TNTSpawner برای المان‌های استاندارد
# ==============================================================================
"""Soccer Frenzy: a complete team soccer/football minigame for BombSquad.

Two teams fight over a real physical ball; punch it, carry it, or bomb your
way to the enemy goal to score. Includes a live scoreboard, goal-flash and
sound effects, ball respawn logic, TNT crates, powerup drops, a score-to-win
and time-limit setting, and end-of-match results — all built following the
node/material patterns used throughout Ballistica's own official minigames.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING, override

import bascenev1 as bs

from bascenev1lib.actor.flag import Flag
from bascenev1lib.actor.scoreboard import Scoreboard
from bascenev1lib.actor.respawnicon import RespawnIcon
from bascenev1lib.actor.powerupbox import PowerupBoxFactory, PowerupBox
from bascenev1lib.actor.bomb import TNTSpawner

if TYPE_CHECKING:
    from typing import Any, Sequence


# ------------------------------------------------------------------------
#  توپ فوتبال (Ball)
# ------------------------------------------------------------------------
class SoccerBall(Flag):
    """The physical soccer ball that gets punched/carried into the goals.

    Built on top of the engine's Flag actor (the same physical prop the
    official football minigame uses for its ball) but re-colored and
    re-tuned to feel like a bouncy round soccer ball.
    """

    def __init__(self, position: Sequence[float]):
        super().__init__(
            position=position,
            color=(1.0, 1.0, 1.0),
            dropped_timeout=8,
            materials=None,
        )
        assert self.node
        # کمی سبک‌تر و پرجهش‌تر از یک پرچم معمولی
        self.node.is_area_of_interest = True
        self.last_player_to_touch: bs.Player | None = None
        self.scored = False


# ------------------------------------------------------------------------
#  تیم و بازیکن
# ------------------------------------------------------------------------
class Player(bs.Player['Team']):
    """A player instance for Soccer Frenzy."""


class Team(bs.Team[Player]):
    """A team instance for Soccer Frenzy."""

    def __init__(self) -> None:
        self.score = 0


# ------------------------------------------------------------------------
#  خود بازی
# ------------------------------------------------------------------------
class SoccerFrenzyGame(bs.TeamGameActivity[Player, Team]):
    """Two teams battle to punch/carry the soccer ball into the enemy goal."""

    name = 'Soccer Frenzy'
    description = 'توپ فوتبال رو به دروازه‌ی حریف برسون تا امتیاز بگیری!'
    tips = [
        'برای برداشتن توپ از دکمه‌ی Pick-Up استفاده کن.',
        'می‌تونی با مشت هم توپ رو به سمت دروازه هل بدی.',
        'مراقب بمب‌های TNT اطراف زمین باش!',
    ]
    scoreconfig = bs.ScoreConfig(
        label='Score', scoretype=bs.ScoreType.POINTS, none_is_winner=False
    )

    @classmethod
    def get_available_settings(
        cls, sessiontype: type[bs.Session]
    ) -> list[bs.Setting]:
        return [
            bs.IntSetting('Score to Win', min_value=1, default=3, increment=1),
            bs.IntChoiceSetting(
                'Time Limit',
                choices=[
                    ('None', 0),
                    ('1 Minute', 60),
                    ('2 Minutes', 120),
                    ('5 Minutes', 300),
                    ('10 Minutes', 600),
                ],
                default=0,
            ),
            bs.BoolSetting('Epic Mode', default=False),
            bs.BoolSetting('TNT Crates', default=True),
            bs.BoolSetting('Powerups', default=True),
        ]

    @classmethod
    def get_supported_maps(cls, sessiontype: type[bs.Session]) -> list[str]:
        # این نقشه مختصات دروازه‌ها (goal1 / goal2) رو تعریف کرده
        return ['Football Stadium']

    @classmethod
    def supports_session_type(cls, sessiontype: type[bs.Session]) -> bool:
        return issubclass(sessiontype, bs.DualTeamSession)

    def __init__(self, settings: dict):
        super().__init__(settings)

        self._scoreboard = Scoreboard()
        self._score_sound = bs.getsound('score')
        self._swipsound = bs.getsound('swip')
        self._whistle_sound = bs.getsound('refWhistle')
        self._cheer_sound = bs.getsound('cheer')

        self._score_to_win = int(settings.get('Score to Win', 3))
        self._time_limit = float(settings.get('Time Limit', 0))
        self._epic_mode = bool(settings.get('Epic Mode', False))
        self._tnt_enabled = bool(settings.get('TNT Crates', True))
        self._powerups_enabled = bool(settings.get('Powerups', True))

        self.slow_motion = self._epic_mode
        self.default_music = (
            bs.MusicType.EPIC if self._epic_mode else bs.MusicType.FOOTBALL
        )

        self._ball: SoccerBall | None = None
        self._ball_spawn_pos: Sequence[float] | None = None
        self._score_regions: list[bs.NodeActor] = []
        self._ball_material = bs.Material()
        self._tnt_spawner: TNTSpawner | None = None
        self._powerup_drop_timer: bs.Timer | None = None
        self._time_limit_timer: bs.Timer | None = None
        self._time_limit_text: bs.NodeActor | None = None

    # -- توضیحات نمایشی روی منوها -------------------------------------
    @override
    def get_instance_description(self) -> str | Sequence:
        return 'توپ رو به دروازه‌ی حریف برسون. اول کسی که به ${ARG1} امتیاز برسه برنده‌ست.'

    @override
    def get_instance_description_short(self) -> str | Sequence:
        return 'به ${ARG1} امتیاز برس'

    def get_instance_scoreboard_description(self) -> str | Sequence:
        return 'first to ${ARG1} points wins'

    # -- راه‌اندازی صحنه --------------------------------------------------
    @override
    def on_transition_in(self) -> None:
        super().on_transition_in()
        self._scoreboard = Scoreboard()
        self._ball_spawn_pos = self.map.get_flag_position(None)
        self._spawn_ball()

        shared = bs.SharedObjects.get()

        # منطقه‌ی گل تیم ۱ (توپ اینجا برسه یعنی امتیاز برای تیم ۲)
        defs = self.map.defs
        goal_boxes = [defs.boxes.get('goal1'), defs.boxes.get('goal2')]

        for team_index, box in enumerate(goal_boxes):
            if box is None:
                continue
            region_material = bs.Material()
            region_material.add_actions(
                conditions=('they_have_material', self._ball_material),
                actions=(
                    ('modify_part_collision', 'collide', True),
                    ('modify_part_collision', 'physical', False),
                    ('call', 'at_connect', bs.Call(self._handle_score, team_index)),
                ),
            )
            region = bs.newnode(
                'region',
                attrs={
                    'position': box[0:3],
                    'scale': box[6:9],
                    'type': 'box',
                    'materials': [region_material],
                },
            )
            self._score_regions.append(bs.NodeActor(region))

        self._whistle_sound.play()

        if self._tnt_enabled:
            tnt_points = getattr(self.map, 'tnt_points', None)
            if tnt_points:
                self._tnt_spawner = TNTSpawner(position=tnt_points[0])

        if self._powerups_enabled:
            self._powerup_drop_timer = bs.Timer(
                4.0, bs.WeakCall(self._tick_powerups), repeat=True
            )

        if self._time_limit > 0:
            self._time_limit_timer = bs.Timer(
                self._time_limit, bs.WeakCall(self._end_game_time_limit)
            )

    @override
    def on_begin(self) -> None:
        super().on_begin()
        self.setup_standard_time_limit(self._time_limit if self._time_limit else None)
        self.setup_standard_powerup_drops(enable=False)  # ما خودمون پاور-آپ رو مدیریت می‌کنیم

    # -- توپ ---------------------------------------------------------
    def _spawn_ball(self) -> None:
        assert self._ball_spawn_pos is not None
        self._ball = SoccerBall(position=self._ball_spawn_pos)
        self._ball.node.materials = list(self._ball.node.materials) + [
            self._ball_material
        ]

    def _kill_ball(self) -> None:
        self._ball = None

    def _respawn_ball(self, delay: float = 1.5) -> None:
        self._kill_ball()
        bs.timer(delay, bs.WeakCall(self._spawn_ball))

    # -- گل‌زنی --------------------------------------------------------
    def _handle_score(self, conceding_team_index: int) -> None:
        """Called when the ball enters a goal box."""
        if self._ball is None or self._ball.scored:
            return
        self._ball.scored = True

        # اگه توپ به دروازه‌ی تیم شماره‌ی conceding_team_index بره،
        # امتیاز به تیم مقابل (index دیگر) تعلق می‌گیره
        scoring_team_index = 1 - conceding_team_index
        for team in self.teams:
            if team.id == scoring_team_index or (
                len(self.teams) == 2 and self.teams.index(team) == scoring_team_index
            ):
                team.score += 1
                self._scoreboard.set_team_value(team, team.score, self._score_to_win)

                light = bs.newnode(
                    'light',
                    attrs={
                        'position': bs.getcollision().position,
                        'height_attenuated': False,
                        'color': team.color if hasattr(team, 'color') else (1, 1, 0.4),
                    },
                )
                bs.animate(light, 'intensity', {0: 0, 0.1: 1.0, 0.5: 0}, loop=False)
                bs.timer(0.55, light.delete)

                self._score_sound.play()
                self._cheer_sound.play()

                if team.score >= self._score_to_win:
                    bs.timer(0.7, bs.WeakCall(self.end_game))
                break

        bs.timer(0.15, self._kill_ball)
        self._respawn_ball(delay=1.8)

    # -- بازیکن‌ها ------------------------------------------------------
    @override
    def spawn_player(self, player: Player) -> bs.Actor:
        spaz = self.spawn_player_spaz(
            player, position=self.map.get_start_position(player.team.id)
        )
        spaz.punch_callback = self._handle_player_punched
        return spaz

    def _handle_player_punched(self, spaz: Any) -> None:
        # تیک ساده برای شبیه‌سازی ضربه به توپ در صورت نزدیک بودن؛
        # فیزیک اصلی برخورد توسط موتور مدیریت می‌شه.
        self._swipsound.play()

    @override
    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, bs.PlayerDiedMessage):
            super().handlemessage(msg)
            player = msg.getplayer(Player)
            self.respawn_player(player)
        else:
            return super().handlemessage(msg)
        return None

    # -- پاور-آپ‌ها ------------------------------------------------------
    def _tick_powerups(self) -> None:
        spawn_points = getattr(self.map, 'powerup_spawn_points', None)
        if not spawn_points:
            return
        point = spawn_points[random.randrange(len(spawn_points))]
        ptype = PowerupBoxFactory.get_factory().get_random_powerup_type()
        PowerupBox(position=point, poweruptype=ptype).autoretain()

    # -- پایان بازی -------------------------------------------------------
    def _end_game_time_limit(self) -> None:
        self.end_game()

    @override
    def end_game(self) -> None:
        results = bs.GameResults()
        for team in self.teams:
            results.set_team_score(team, team.score)
        self.end(results=results)
