# ba_meta require api 8

from typing import Any

import bascenev1 as bs
from bascenev1lib.actor.playerspaz import PlayerSpaz


# ============================================================
# SETTINGS
# ============================================================

BALL_POSITION = (0.0, 1.15, 0.0)

LEFT_PLAYER_POSITION = (-3.5, 1.0, 0.0)
RIGHT_PLAYER_POSITION = (3.5, 1.0, 0.0)

# Hockey field ends are approximately here.
LEFT_GOAL_X = -5.2
RIGHT_GOAL_X = 5.2

# Goal area.
GOAL_Y_MIN = 0.25
GOAL_Y_MAX = 2.8
GOAL_Z_MAX = 1.8

BALL_RADIUS = 0.82

GOAL_COOLDOWN = 2.0
RESET_DELAY = 0.8


# ============================================================
# PLAYER
# ============================================================

class SoccerPlayer(bs.Player['SoccerTeam']):
    """Soccer player."""


# ============================================================
# TEAM
# ============================================================

class SoccerTeam(bs.Team[SoccerPlayer]):
    """Soccer team."""

    def __init__(self) -> None:
        super().__init__()
        self.score = 0


# ============================================================
# SOCCER BALL
# ============================================================

class SoccerBall(bs.Actor):
    """A physical spherical soccer ball."""

    def __init__(self) -> None:
        super().__init__()

        shared = bs.SharedObjects.get()

        # Ball material.
        self.ball_material = bs.Material()

        # Make the ball bouncy.
        self.ball_material.add_actions(
            actions=(
                ('modify_part_collision', 'friction', 0.15),
                ('modify_part_collision', 'stiffness', 0.15),
                ('modify_part_collision', 'damping', 0.02),
            )
        )

        # Create a real sphere.
        self.node = bs.newnode(
            'prop',
            delegate=self,
            attrs={
                'position': BALL_POSITION,
                'body': 'sphere',
                'body_scale': BALL_RADIUS,
                'mesh': bs.getmesh('impactBomb'),
                'color_texture': bs.gettexture('impactBombColor'),
                'reflection': 'soft',
                'reflection_scale': [0.2],
                'shadow_size': 0.5,
                'materials': (
                    shared.object_material,
                    self.ball_material,
                ),
            },
        )

        self.node.velocity = (0.0, 0.0, 0.0)

    def reset(self) -> None:
        """Return ball to center."""

        if self.node.exists():
            self.node.position = BALL_POSITION
            self.node.velocity = (0.0, 0.0, 0.0)
            self.node.move_to_front()

    def on_expire(self) -> None:
        if self.node.exists():
            self.node.delete()


# ============================================================
# GOAL MESSAGE
# ============================================================

class GoalMessage:
    """Internal message used when a goal is detected."""

    def __init__(self, team_id: int) -> None:
        self.team_id = team_id


# ============================================================
# GAME
# ============================================================

# IMPORTANT:
# API 8 requires this exact metadata tag.
#
# ba_meta export bascenev1.GameActivity

class SoccerGame(bs.TeamGameActivity[SoccerPlayer, SoccerTeam]):
    """Two-team soccer game."""

    name = 'Soccer'

    description = 'Score goals with the soccer ball.'

    scoreconfig = bs.ScoreConfig(
        label='Goals',
        scoretype=bs.ScoreType.POINTS,
        lower_is_better=False,
        none_is_best=False,
    )

    default_music = 'Football'

    available_settings = [
        bs.IntSetting(
            'Score to Win',
            default=5,
            min_value=1,
            max_value=99,
            increment=1,
        ),
        bs.IntChoiceSetting(
            'Time Limit',
            default=0,
            choices=[
                ('None', 0),
                ('1 Minute', 60),
                ('2 Minutes', 120),
                ('5 Minutes', 300),
                ('10 Minutes', 600),
            ],
        ),
    ]

    @classmethod
    def supports_session_type(
        cls,
        sessiontype: type[bs.Session],
    ) -> bool:
        return issubclass(
            sessiontype,
            bs.DualTeamSession,
        )

    @classmethod
    def get_supported_maps(
        cls,
        sessiontype: type[bs.Session],
    ) -> list[str]:
        del sessiontype
        return ['Hockey']

    def __init__(self, settings: dict) -> None:
        super().__init__(settings)

        self._ball: SoccerBall | None = None

        self._goal_locked = False

        self._score_to_win = int(
            settings.get('Score to Win', 5)
        )

        self._time_limit = int(
            settings.get('Time Limit', 0)
        )

        self._score_sound = bs.getsound('score')

    # ========================================================
    # TRANSITION
    # ========================================================

    def on_transition_in(self) -> None:
        super().on_transition_in()

        # Slight green tint for the pitch.
        self.globalsnode.tint = (
            0.75,
            1.0,
            0.75,
        )

    # ========================================================
    # BEGIN
    # ========================================================

    def on_begin(self) -> None:
        super().on_begin()

        # Create soccer ball.
        self._ball = SoccerBall()

        # Time limit.
        if self._time_limit > 0:
            self.setup_standard_time_limit(
                self._time_limit
            )

        # Spawn existing players.
        for player in self.players:
            self.spawn_player(player)

        # Start goal checking.
        bs.timer(
            0.05,
            bs.WeakCall(self._check_ball),
            repeat=True,
        )

    # ========================================================
    # SPAWN PLAYER
    # ========================================================

    def spawn_player(
        self,
        player: SoccerPlayer,
    ) -> PlayerSpaz:

        if player.team.id == 0:
            position = LEFT_PLAYER_POSITION
            angle = 0.0
        else:
            position = RIGHT_PLAYER_POSITION
            angle = 180.0

        spaz = self.spawn_player_spaz(
            player,
            position=position,
            angle=angle,
        )

        player.actor = spaz

        return spaz

    # ========================================================
    # RESET PLAYERS
    # ========================================================

    def _reset_players(self) -> None:

        for player in self.players:

            spaz = player.actor

            if spaz is None:
                continue

            if not spaz.node.exists():
                continue

            if player.team.id == 0:
                position = LEFT_PLAYER_POSITION
                angle = 0.0
            else:
                position = RIGHT_PLAYER_POSITION
                angle = 180.0

            spaz.node.position = position
            spaz.node.velocity = (
                0.0,
                0.0,
                0.0,
            )
            spaz.node.angle = angle

    # ========================================================
    # CHECK BALL
    # ========================================================

    def _check_ball(self) -> None:

        if self._ball is None:
            return

        if not self._ball.node.exists():
            return

        if self._goal_locked:
            return

        position = self._ball.node.position

        x = position[0]
        y = position[1]
        z = position[2]

        # Ignore balls that are too high.
        if y < GOAL_Y_MIN or y > GOAL_Y_MAX:
            return

        # Goal must be near the center of the goal.
        if abs(z) > GOAL_Z_MAX:
            return

        # LEFT GOAL.
        if x <= LEFT_GOAL_X:

            # Right team scores.
            self.handlemessage(
                GoalMessage(1)
            )

            return

        # RIGHT GOAL.
        if x >= RIGHT_GOAL_X:

            # Left team scores.
            self.handlemessage(
                GoalMessage(0)
            )

    # ========================================================
    # MESSAGE
    # ========================================================

    def handlemessage(self, msg: Any) -> Any:

        if isinstance(msg, GoalMessage):

            if self._goal_locked:
                return None

            self._score_goal(
                self.teams[msg.team_id]
            )

            return None

        return super().handlemessage(msg)

    # ========================================================
    # SCORE GOAL
    # ========================================================

    def _score_goal(
        self,
        team: SoccerTeam,
    ) -> None:

        if self._goal_locked:
            return

        self._goal_locked = True

        # Add goal.
        team.score += 1

        # Update game stats.
        try:
            self.stats.player_scored(
                None,
                team=team,
                score=1,
            )
        except Exception:
            pass

        # Goal sound.
        try:
            self._score_sound.play(
                volume=1.0
            )
        except Exception:
            pass

        # Celebrate.
        try:
            self.celebrate()
        except Exception:
            pass

        # Reset shortly after goal.
        bs.timer(
            RESET_DELAY,
            bs.WeakCall(
                self._reset_after_goal
            ),
        )

    # ========================================================
    # RESET AFTER GOAL
    # ========================================================

    def _reset_after_goal(self) -> None:

        # Check winning score first.
        for team in self.teams:
            if team.score >= self._score_to_win:

                self._finish_game()
                return

        # Reset ball.
        if self._ball is not None:
            self._ball.reset()

        # Reset players.
        self._reset_players()

        # Unlock goals.
        bs.timer(
            GOAL_COOLDOWN,
            bs.WeakCall(
                self._unlock_goal
            ),
        )

    # ========================================================
    # UNLOCK
    # ========================================================

    def _unlock_goal(self) -> None:
        self._goal_locked = False

    # ========================================================
    # END GAME
    # ========================================================

    def _finish_game(self) -> None:

        results = bs.GameResults()

        results.set_game(self)

        for team in self.teams:
            results.set_team_score(
                team,
                team.score,
            )

        self.end(
            results=results
        )