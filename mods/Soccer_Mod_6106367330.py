# ba_meta require api 8

import bascenev1 as bs
from bascenev1lib.actor.playerspaz import PlayerSpaz


# ============================================================
# SETTINGS
# ============================================================

BALL_POSITION = (0.0, 1.2, 0.0)

LEFT_PLAYER_POSITION = (-3.5, 1.0, 0.0)
RIGHT_PLAYER_POSITION = (3.5, 1.0, 0.0)

LEFT_GOAL_X = -5.2
RIGHT_GOAL_X = 5.2

GOAL_Y_MIN = 0.20
GOAL_Y_MAX = 2.8
GOAL_Z_MAX = 1.8

BALL_RADIUS = 0.72

RESET_DELAY = 1.0
GOAL_COOLDOWN = 1.5


# ============================================================
# PLAYER
# ============================================================

class SoccerPlayer(bs.Player['SoccerTeam']):
    pass


# ============================================================
# TEAM
# ============================================================

class SoccerTeam(bs.Team[SoccerPlayer]):

    def __init__(self) -> None:
        super().__init__()
        self.score = 0


# ============================================================
# BALL
# ============================================================

class SoccerBall(bs.Actor):

    def __init__(self) -> None:
        super().__init__()

        shared = bs.SharedObjects.get()

        self.ball_material = bs.Material()

        # Bouncy ball.
        self.ball_material.add_actions(
            actions=(
                (
                    'modify_part_collision',
                    'friction',
                    0.15,
                ),
                (
                    'modify_part_collision',
                    'stiffness',
                    0.15,
                ),
                (
                    'modify_part_collision',
                    'damping',
                    0.02,
                ),
            )
        )

        self.node = bs.newnode(
            'prop',
            delegate=self,
            attrs={
                'position': BALL_POSITION,
                'body': 'sphere',
                'body_scale': BALL_RADIUS,

                # Round BombSquad object.
                'mesh': bs.getmesh('impactBomb'),
                'color_texture': bs.gettexture(
                    'impactBombColor'
                ),

                'reflection': 'soft',
                'reflection_scale': [0.2],
                'shadow_size': 0.5,

                'materials': (
                    shared.object_material,
                    self.ball_material,
                ),
            },
        )

        self.node.velocity = (
            0.0,
            0.0,
            0.0,
        )

    def reset(self) -> None:

        if not self.node.exists():
            return

        self.node.position = BALL_POSITION

        self.node.velocity = (
            0.0,
            0.0,
            0.0,
        )

        self.node.move_to_front()

    def delete(self) -> None:

        if self.node.exists():
            self.node.delete()


# ============================================================
# GOAL MESSAGE
# ============================================================

class GoalMessage:

    def __init__(self, team_id: int) -> None:
        self.team_id = team_id


# ============================================================
# GAME
# ============================================================

# IMPORTANT:
# This line MUST NOT have "#" in front of it.
#
# It tells BombSquad that this class is a GameActivity.

# ba_meta export bascenev1.GameActivity
class SoccerGame(
    bs.TeamGameActivity[
        SoccerPlayer,
        SoccerTeam
    ]
):

    name = 'Soccer'

    description = 'Score goals with the soccer ball.'

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

    # --------------------------------------------------------
    # SESSION
    # --------------------------------------------------------

    @classmethod
    def supports_session_type(
        cls,
        sessiontype: type[bs.Session],
    ) -> bool:

        return issubclass(
            sessiontype,
            bs.DualTeamSession,
        )

    # --------------------------------------------------------
    # MAP
    # --------------------------------------------------------

    @classmethod
    def get_supported_maps(
        cls,
        sessiontype: type[bs.Session],
    ) -> list[str]:

        del sessiontype

        return ['Hockey']

    # --------------------------------------------------------
    # INIT
    # --------------------------------------------------------

    def __init__(
        self,
        settings: dict,
    ) -> None:

        super().__init__(settings)

        self._ball: SoccerBall | None = None

        self._goal_locked = False

        self._score_to_win = int(
            settings.get(
                'Score to Win',
                5,
            )
        )

        self._time_limit = int(
            settings.get(
                'Time Limit',
                0,
            )
        )

        self._score_sound = bs.getsound('score')

    # --------------------------------------------------------
    # TRANSITION
    # --------------------------------------------------------

    def on_transition_in(self) -> None:

        super().on_transition_in()

        # Slightly green field.
        self.globalsnode.tint = (
            0.75,
            1.0,
            0.75,
        )

    # --------------------------------------------------------
    # BEGIN
    # --------------------------------------------------------

    def on_begin(self) -> None:

        super().on_begin()

        # Create ball.
        self._ball = SoccerBall()

        # Time limit.
        if self._time_limit > 0:

            self.setup_standard_time_limit(
                self._time_limit
            )

        # Spawn players.
        for player in self.players:

            self.spawn_player(player)

        # Check for goals.
        bs.timer(
            0.05,
            bs.WeakCall(
                self._check_ball
            ),
            repeat=True,
        )

    # --------------------------------------------------------
    # SPAWN
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # RESET PLAYERS
    # --------------------------------------------------------

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

            spaz.node.angular_velocity = (
                0.0,
                0.0,
                0.0,
            )

            spaz.node.angle = angle

    # --------------------------------------------------------
    # CHECK BALL
    # --------------------------------------------------------

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

        # Ball must be inside goal height.
        if y < GOAL_Y_MIN:
            return

        if y > GOAL_Y_MAX:
            return

        # Ball must be close to the middle of the goal.
        if abs(z) > GOAL_Z_MAX:
            return

        # ----------------------------------------------------
        # LEFT GOAL
        # ----------------------------------------------------

        if x <= LEFT_GOAL_X:

            # Right team scores.
            self.handlemessage(
                GoalMessage(1)
            )

            return

        # ----------------------------------------------------
        # RIGHT GOAL
        # ----------------------------------------------------

        if x >= RIGHT_GOAL_X:

            # Left team scores.
            self.handlemessage(
                GoalMessage(0)
            )

            return

    # --------------------------------------------------------
    # MESSAGE
    # --------------------------------------------------------

    def handlemessage(
        self,
        msg,
    ):

        if isinstance(
            msg,
            GoalMessage,
        ):

            if self._goal_locked:
                return None

            if msg.team_id < 0:
                return None

            if msg.team_id >= len(self.teams):
                return None

            team = self.teams[
                msg.team_id
            ]

            self._score_goal(team)

            return None

        return super().handlemessage(msg)

    # --------------------------------------------------------
    # SCORE
    # --------------------------------------------------------

    def _score_goal(
        self,
        team: SoccerTeam,
    ) -> None:

        if self._goal_locked:
            return

        self._goal_locked = True

        # Add goal.
        team.score += 1

        # Show score message.
        bs.broadcastmessage(
            'GOAL!  Team %d  -  %d'
            % (
                team.id + 1,
                team.score,
            ),
            color=(1.0, 1.0, 0.0),
            transient=True,
        )

        # Sound.
        try:
            self._score_sound.play(
                volume=1.0
            )
        except Exception:
            pass

        # Celebration.
        try:
            self.celebrate()
        except Exception:
            pass

        # Reset.
        bs.timer(
            RESET_DELAY,
            bs.WeakCall(
                self._reset_after_goal
            ),
        )

    # --------------------------------------------------------
    # RESET AFTER GOAL
    # --------------------------------------------------------

    def _reset_after_goal(self) -> None:

        # Check winner.
        for team in self.teams:

            if team.score >= self._score_to_win:

                self._finish_game()

                return

        # Reset ball.
        if self._ball is not None:

            self._ball.reset()

        # Reset players.
        self._reset_players()

        # Unlock after cooldown.
        bs.timer(
            GOAL_COOLDOWN,
            bs.WeakCall(
                self._unlock_goal
            ),
        )

    # --------------------------------------------------------
    # UNLOCK
    # --------------------------------------------------------

    def _unlock_goal(self) -> None:

        self._goal_locked = False

    # --------------------------------------------------------
    # FINISH
    # --------------------------------------------------------

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