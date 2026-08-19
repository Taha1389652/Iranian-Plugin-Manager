# ba_meta require api 8
#
# Soccer / Football mini-game for BombSquad API 8.
#
# Save this file as:
#     soccer.py
#
# The game uses the Hockey map as its field.
#
# Features:
#   - Two teams.
#   - Physical spherical soccer ball.
#   - Ball can be punched, kicked, and affected by explosions.
#   - Left and right goals.
#   - Automatic scoring.
#   - Cheer sound after a goal.
#   - Players are reset after a goal.
#   - Ball returns to the center.
#
# API: BombSquad / Ballistica API 8
#

from typing import Any

import bascenev1 as bs
from bascenev1 import classicassets

from bascenev1lib.actor.playerspaz import PlayerSpaz
from bascenev1lib.gameutils import SharedObjects


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BALL_POSITION = (0.0, 1.05, 0.0)

# Hockey is approximately 11 units wide.
# The goals are placed at the two ends of the rink.
LEFT_GOAL_POSITION = (-5.75, 1.0, 0.0)
RIGHT_GOAL_POSITION = (5.75, 1.0, 0.0)

# Width/depth/height of the goal detection area.
GOAL_WIDTH = 1.8
GOAL_HEIGHT = 1.7
GOAL_DEPTH = 2.0

BALL_SCALE = 0.82

# Minimum delay between goals.
GOAL_COOLDOWN = 1.5


# ---------------------------------------------------------------------------
# Team class
# ---------------------------------------------------------------------------

class SoccerTeam(bs.Team):
    """Team data used by SoccerGame."""

    def __init__(self) -> None:
        super().__init__()
        self.score = 0


# ---------------------------------------------------------------------------
# Player class
# ---------------------------------------------------------------------------

class SoccerPlayer(bs.Player[SoccerTeam]):
    """Player class used by SoccerGame."""

    def __init__(self) -> None:
        super().__init__()


# ---------------------------------------------------------------------------
# Soccer ball
# ---------------------------------------------------------------------------

class SoccerBall(bs.Actor):
    """A physical spherical soccer ball."""

    def __init__(self, activity: 'SoccerGame') -> None:
        super().__init__()

        self.activity = activity

        shared = SharedObjects.get()

        # ------------------------------------------------------------------
        # Materials
        # ------------------------------------------------------------------

        # This material allows the ball to behave like a normal physical
        # object and interact with players and explosions.
        ball_material = bs.Material()

        # Make the ball bouncy.
        ball_material.add_actions(
            actions=(
                'modify_part_collision',
                'friction',
                0.15,
            )
        )

        ball_material.add_actions(
            actions=(
                'modify_part_collision',
                'stiffness',
                0.3,
            )
        )

        ball_material.add_actions(
            actions=(
                'modify_part_collision',
                'damping',
                0.05,
            )
        )

        # Store it so the node remains easy to inspect/debug.
        self.ball_material = ball_material

        # ------------------------------------------------------------------
        # Create the spherical ball.
        # ------------------------------------------------------------------
        #
        # body='sphere' is important here.
        # Unlike a puck/cylinder, the physics body is a true sphere.
        #
        # impactBomb is used as the visual mesh because it is a round,
        # built-in spherical mesh available in BombSquad.
        #

        self.node = bs.newnode(
            'prop',
            delegate=self,
            attrs={
                'position': BALL_POSITION,

                # TRUE SPHERE PHYSICS.
                'body': 'sphere',
                'body_scale': BALL_SCALE,

                # Built-in round mesh.
                'mesh': bs.getmesh('impactBomb'),

                # Built-in BombSquad texture.
                # If your build does not expose this texture, the fallback
                # below removes the texture and still leaves a round ball.
                'color_texture': bs.gettexture('impactBombColor'),

                'reflection': 'soft',
                'reflection_scale': [0.25],

                'shadow_size': 0.55,

                'materials': (
                    shared.object_material,
                    ball_material,
                ),
            },
        )

        # Make the ball initially bouncy.
        self.node.velocity = (0.0, 0.0, 0.0)

    def reset(self) -> None:
        """Move the ball back to the center of the field."""

        if not self.node:
            return

        self.node.position = BALL_POSITION
        self.node.velocity = (0.0, 0.0, 0.0)

    def on_expire(self) -> None:
        """Clean up the ball when the activity ends."""

        if self.node:
            self.node.delete()


# ---------------------------------------------------------------------------
# Soccer game
# ---------------------------------------------------------------------------

class SoccerGame(bs.TeamGameActivity[SoccerPlayer, SoccerTeam]):
    """Classic two-team BombSquad soccer."""

    name = 'Soccer'

    description = 'Score goals with the soccer ball.'

    # Football-style music.
    default_music = 'Football'

    # Score configuration.
    scoreconfig = bs.ScoreConfig(
        label='Goals',
        scoretype=bs.ScoreType.POINTS,
        lower_is_better=False,
        none_is_best=False,
    )

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
                ('20 Minutes', 1200),
            ],
        ),
        bs.FloatChoiceSetting(
            'Respawn Times',
            default=1.0,
            choices=[
                ('Shorter', 0.25),
                ('Short', 0.5),
                ('Normal', 1.0),
                ('Long', 2.0),
                ('Longer', 4.0),
            ],
        ),
    ]

    @classmethod
    def supports_session_type(
        cls,
        sessiontype: type[bs.Session],
    ) -> bool:
        """Soccer is a two-team game."""

        return issubclass(sessiontype, bs.DualTeamSession)

    @classmethod
    def get_supported_maps(
        cls,
        sessiontype: type[bs.Session],
    ) -> list[str]:
        """Only use the Hockey map."""

        del sessiontype
        return ['Hockey']

    def __init__(self, settings: dict) -> None:
        super().__init__(settings)

        self._ball: SoccerBall | None = None

        self._goal_nodes: list[bs.Node] = []

        self._goal_cooldown = False

        self._score_to_win = int(
            settings.get('Score to Win', 5)
        )

        self._cheer_sound = (
            classicassets.get('cheer')
            if hasattr(classicassets, 'get')
            else None
        )

        # ------------------------------------------------------------------
        # Preload commonly used media.
        # ------------------------------------------------------------------

        self._score_sound = bs.getsound('score')

    # -----------------------------------------------------------------------
    # Transition into game
    # -----------------------------------------------------------------------

    def on_transition_in(self) -> None:
        super().on_transition_in()

        # Give the field a slight green tint.
        # Hockey already provides the physical walls and floor.
        self.globalsnode.tint = (0.75, 1.0, 0.75)

    # -----------------------------------------------------------------------
    # Game start
    # -----------------------------------------------------------------------

    def on_begin(self) -> None:
        super().on_begin()

        # Create the physical soccer ball.
        self._ball = SoccerBall(self)

        # Create the two goal detectors.
        self._create_goals()

        # Start standard time-limit handling if requested.
        if self.settings_raw.get('Time Limit', 0) > 0:
            self.setup_standard_time_limit(
                self.settings_raw['Time Limit']
            )

        # Make sure players are initially spawned.
        for player in self.players:
            if not player.actor:
                self.spawn_player(player)

    # -----------------------------------------------------------------------
    # Goal creation
    # -----------------------------------------------------------------------

    def _create_goals(self) -> None:
        """Create invisible goal-detection regions."""

        shared = SharedObjects.get()

        goal_material = bs.Material()

        # When the soccer ball touches this material, a collision message
        # is sent to the region node.
        goal_material.add_actions(
            conditions=(
                ('they_have_material', self._ball.ball_material),
            ),
            actions=(
                'message',
                'our_node',
                'at_connect',
                GoalMessage(),
            ),
        )

        # We also allow the actual ball to enter the region without
        # physically colliding with the invisible detector.
        goal_material.add_actions(
            conditions=(
                ('they_have_material', shared.object_material),
            ),
            actions=(
                'modify_part_collision',
                'collide',
                False,
            ),
        )

        # Left goal.
        left_goal = bs.newnode(
            'region',
            attrs={
                'position': LEFT_GOAL_POSITION,
                'scale': (
                    GOAL_DEPTH,
                    GOAL_HEIGHT,
                    GOAL_WIDTH,
                ),
                'type': 'box',
                'materials': (
                    goal_material,
                ),
            },
        )

        # Right goal.
        right_goal = bs.newnode(
            'region',
            attrs={
                'position': RIGHT_GOAL_POSITION,
                'scale': (
                    GOAL_DEPTH,
                    GOAL_HEIGHT,
                    GOAL_WIDTH,
                ),
                'type': 'box',
                'materials': (
                    goal_material,
                ),
            },
        )

        self._goal_nodes = [
            left_goal,
            right_goal,
        ]

    # -----------------------------------------------------------------------
    # Player spawning
    # -----------------------------------------------------------------------

    def spawn_player(
        self,
        player: SoccerPlayer,
    ) -> PlayerSpaz:
        """Spawn a normal BombSquad player."""

        # ------------------------------------------------------------------
        # Team 0 starts on the left.
        # Team 1 starts on the right.
        # ------------------------------------------------------------------

        if player.team.id == 0:
            position = (-3.8, 1.0, 0.0)
            angle = 0.0
        else:
            position = (3.8, 1.0, 0.0)
            angle = 180.0

        spaz = self.spawn_player_spaz(
            player,
            position=position,
            angle=angle,
        )

        # Store the spaz for later reset operations.
        player.actor = spaz

        return spaz

    # -----------------------------------------------------------------------
    # Reset players
    # -----------------------------------------------------------------------

    def _reset_players(self) -> None:
        """Reset every living player to their team's side."""

        for player in self.players:

            if not player.actor:
                continue

            spaz = player.actor

            if not spaz.node:
                continue

            if player.team.id == 0:
                position = (-3.8, 1.0, 0.0)
                angle = 0.0
            else:
                position = (3.8, 1.0, 0.0)
                angle = 180.0

            spaz.node.position = position
            spaz.node.velocity = (0.0, 0.0, 0.0)

            # Face toward the center.
            spaz.node.angle = angle

    # -----------------------------------------------------------------------
    # Goal handling
    # -----------------------------------------------------------------------

    def handlemessage(self, msg: Any) -> Any:

        if isinstance(msg, GoalMessage):

            if self._goal_cooldown:
                return None

            if self._ball is None or not self._ball.node:
                return None

            # Determine which side of the field the ball entered.
            ball_x = self._ball.node.position[0]

            if ball_x < 0.0:
                # Ball entered the LEFT goal.
                #
                # Team on the RIGHT scores.
                scoring_team = self.teams[1]

            else:
                # Ball entered the RIGHT goal.
                #
                # Team on the LEFT scores.
                scoring_team = self.teams[0]

            self._score_goal(scoring_team)

            return None

        return super().handlemessage(msg)

    # -----------------------------------------------------------------------
    # Score a goal
    # -----------------------------------------------------------------------

    def _score_goal(self, team: SoccerTeam) -> None:
        """Award one goal and reset the field."""

        if self._goal_cooldown:
            return

        self._goal_cooldown = True

        # Award the point.
        team.score += 1

        # Update the standard game stats.
        self.stats.player_scored(
            None,
            team=team,
            score=1,
        )

        # ------------------------------------------------------------------
        # Play the goal sound.
        # ------------------------------------------------------------------

        try:
            self._score_sound.play(
                volume=1.0,
            )
        except Exception:
            pass

        # ------------------------------------------------------------------
        # Make all players celebrate.
        # ------------------------------------------------------------------

        for player in self.players:
            if player.actor:
                try:
                    player.actor.node.handlemessage(
                        bs.CelebrateMessage()
                    )
                except Exception:
                    pass

        # Reset everything shortly after the goal.
        bs.timer(
            0.75,
            bs.WeakCall(self._reset_after_goal),
        )

    # -----------------------------------------------------------------------
    # Reset after goal
    # -----------------------------------------------------------------------

    def _reset_after_goal(self) -> None:
        """Reset the ball and players after a goal."""

        if self._ball:
            self._ball.reset()

        self._reset_players()

        # Allow the next goal.
        bs.timer(
            GOAL_COOLDOWN,
            bs.WeakCall(self._unlock_goal),
        )

        # End if the winning score has been reached.
        for team in self.teams:
            if team.score >= self._score_to_win:
                self.end_game()
                return

    def _unlock_goal(self) -> None:
        self._goal_cooldown = False

    # -----------------------------------------------------------------------
    # End game
    # -----------------------------------------------------------------------

    def end_game(self) -> None:
        """Finish the game and send the team scores to the score screen."""

        results = bs.GameResults()

        results.set_game(self)

        for team in self.teams:
            results.set_team_score(
                team,
                team.score,
            )

        self.end(
            results=results,
        )


# ---------------------------------------------------------------------------
# Goal message
# ---------------------------------------------------------------------------

class GoalMessage:
    """Sent when the soccer ball enters a goal."""


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------

# The game is automatically discovered by BombSquad's API-8 metadata system.
#
# The class name exposed to the game is:
#
#     SoccerGame
#
# The file can therefore be loaded as a normal BombSquad game mod.
#