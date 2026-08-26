# ba_meta require api 9

from __future__ import annotations

from typing import Any

import bascenev1 as bs
from bascenev1lib.gameutils import SharedObjects


class Player(bs.Player['Team']):
    """Soccer player."""


class Team(bs.Team[Player]):
    """Soccer team."""

    def __init__(self) -> None:
        self.score = 0


BALL_POSITION = (0.0, 1.0, 0.0)

BALL_SCALE = 0.55

# Heavier soccer ball.
BALL_DENSITY = 4.0

RESET_DELAY = 1.2


class SoccerBall(bs.Actor):

    def __init__(
        self,
        position: tuple[float, float, float],
        material: bs.Material,
    ) -> None:

        super().__init__()

        shared = SharedObjects.get()

        self.node = bs.newnode(
            'prop',
            delegate=self,
            attrs={
                'position': position,
                'body': 'sphere',
                'body_scale': BALL_SCALE,

                'mesh': bs.getmesh('bomb'),
                'color_texture': bs.gettexture(
                    'bombColor'
                ),

                'reflection': 'soft',
                'reflection_scale': [0.25],

                'shadow_size': 0.4,

                # Heavier than before.
                'density': BALL_DENSITY,

                'materials': (
                    shared.object_material,
                    material,
                ),

                'is_area_of_interest': True,
            },
        )

        self.scored = False

    def reset(self) -> None:

        try:
            if not self.node.exists():
                return
        except Exception:
            return

        self.node.position = BALL_POSITION

        self.node.velocity = (
            0.0,
            0.0,
            0.0,
        )

        self.node.angular_velocity = (
            0.0,
            0.0,
            0.0,
        )

        self.scored = False

    def handlemessage(
        self,
        msg: Any,
    ) -> Any:

        if isinstance(msg, bs.DieMessage):

            try:
                if self.node.exists():
                    self.node.delete()
            except Exception:
                pass

            return None

        if isinstance(msg, bs.OutOfBoundsMessage):

            self.reset()
            return None

        return super().handlemessage(msg)


class GoalMessage:

    def __init__(
        self,
        team_id: int,
    ) -> None:

        self.team_id = team_id


# ba_meta export bascenev1.GameActivity
class SoccerGame(
    bs.TeamGameActivity[
        Player,
        Team,
    ]
):

    name = 'Soccer'

    description = 'Soccer on Hockey.'

    available_settings = [
        bs.IntSetting(
            'Score to Win',
            min_value=1,
            default=5,
            increment=1,
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

        assert bs.app.classic is not None

        football_maps = bs.app.classic.getmaps(
            'football'
        )

        hockey_maps = bs.app.classic.getmaps(
            'hockey'
        )

        result: list[str] = []

        for map_name in (
            football_maps + hockey_maps
        ):

            if map_name not in result:
                result.append(map_name)

        return result

    def __init__(
        self,
        settings: dict,
    ) -> None:

        super().__init__(settings)

        self._score_to_win = int(
            settings.get(
                'Score to Win',
                5,
            )
        )

        self._ball: SoccerBall | None = None

        self._score_regions: list[
            bs.NodeActor
        ] = []

        self._goal_locked = False

        shared = SharedObjects.get()

        self._player_friction_material = bs.Material()

        self._player_friction_material.add_actions(
            conditions=(
                'they_have_material',
                shared.footing_material,
            ),
            actions=(
                (
                    'modify_part_collision',
                    'friction',
                    1.0,
                ),
            ),
        )

        self._ball_material = bs.Material()

        self._ball_material.add_actions(
            conditions=(
                'they_have_material',
                shared.player_material,
            ),
            actions=(
                (
                    'modify_part_collision',
                    'collide',
                    True,
                ),
            ),
        )

        self._ball_material.add_actions(
            conditions=(
                'they_have_material',
                shared.footing_material,
            ),
            actions=(
                (
                    'modify_part_collision',
                    'collide',
                    True,
                ),
                (
                    'modify_part_collision',
                    'friction',
                    0.90,
                ),
            ),
        )

        self._score_material = bs.Material()

        self._score_material.add_actions(
            conditions=(
                'they_have_material',
                self._ball_material,
            ),
            actions=(
                (
                    'modify_part_collision',
                    'collide',
                    True,
                ),
                (
                    'modify_part_collision',
                    'physical',
                    False,
                ),
                (
                    'call',
                    'at_connect',
                    self._goal_collision,
                ),
            ),
        )

    def on_begin(self) -> None:

        super().on_begin()

        self._spawn_ball()

        self._create_goal_regions()

        for player in self.players:
            self.spawn_player(player)

    def _spawn_ball(self) -> None:

        if self._ball is None:

            self._ball = SoccerBall(
                BALL_POSITION,
                self._ball_material,
            )

            return

        try:

            if self._ball.node.exists():

                self._ball.reset()

            else:

                self._ball = SoccerBall(
                    BALL_POSITION,
                    self._ball_material,
                )

        except Exception:

            self._ball = SoccerBall(
                BALL_POSITION,
                self._ball_material,
            )

    def _create_goal_regions(self) -> None:

        defs = self.map.defs

        if 'goal1' not in defs.boxes:
            return

        if 'goal2' not in defs.boxes:
            return

        node1 = bs.newnode(
            'region',
            attrs={
                'position': defs.boxes[
                    'goal1'
                ][0:3],

                'scale': defs.boxes[
                    'goal1'
                ][6:9],

                'type': 'box',

                'materials': (
                    self._score_material,
                ),
            },
        )

        self._score_regions.append(
            bs.NodeActor(node1)
        )

        node2 = bs.newnode(
            'region',
            attrs={
                'position': defs.boxes[
                    'goal2'
                ][0:3],

                'scale': defs.boxes[
                    'goal2'
                ][6:9],

                'type': 'box',

                'materials': (
                    self._score_material,
                ),
            },
        )

        self._score_regions.append(
            bs.NodeActor(node2)
        )

    def spawn_player(
        self,
        player: Player,
    ) -> None:

        position = self.map.get_start_position(
            player.team.id
        )

        self.spawn_player_spaz(
            player,
            position=position,
        )

        actor = player.actor

        if actor is None:
            return

        try:

            if not actor.node.exists():
                return

        except Exception:

            return

        try:

            old_materials = actor.node.materials

            if old_materials is None:
                old_materials = ()

            materials = tuple(old_materials)

            if (
                self._player_friction_material
                not in materials
            ):

                actor.node.materials = (
                    materials
                    + (
                        self._player_friction_material,
                    )
                )

        except Exception:

            pass

    def _goal_collision(self) -> None:

        if self.has_ended():
            return

        if self._goal_locked:
            return

        if self._ball is None:
            return

        if self._ball.scored:
            return

        try:

            if not self._ball.node.exists():
                return

        except Exception:

            return

        try:

            collision = bs.getcollision()

        except Exception:

            return

        region = collision.sourcenode

        goal_id = -1

        for i, score_region in enumerate(
            self._score_regions
        ):

            try:

                if region == score_region.node:

                    goal_id = i
                    break

            except Exception:

                pass

        if goal_id < 0:
            return

        self._goal_locked = True

        self._ball.scored = True

        if goal_id == 0:

            team_id = 0

        else:

            team_id = 1

        if team_id < 0:
            return

        if team_id >= len(self.teams):
            return

        self.handlemessage(
            GoalMessage(team_id)
        )

    def handlemessage(
        self,
        msg: Any,
    ) -> Any:

        if isinstance(
            msg,
            GoalMessage,
        ):

            self._score_goal(
                msg.team_id
            )

            return None

        return super().handlemessage(msg)

    def _score_goal(
        self,
        team_id: int,
    ) -> None:

        if self.has_ended():
            return

        if team_id < 0:
            return

        if team_id >= len(self.teams):
            return

        team = self.teams[team_id]

        team.score += 1

        bs.broadcastmessage(
            'GOAL! TEAM %d   SCORE: %d'
            % (
                team_id + 1,
                team.score,
            ),
            color=(
                1.0,
                1.0,
                0.0,
            ),
            transient=True,
        )

        try:

            bs.cameraflash(
                duration=0.25
            )

        except Exception:

            pass

        if team.score >= self._score_to_win:

            bs.timer(
                1.0,
                self._finish_game,
            )

            return

        bs.timer(
            RESET_DELAY,
            self._reset_game,
        )

    def _reset_game(self) -> None:

        if self.has_ended():
            return

        self._spawn_ball()

        for player in self.players:

            actor = player.actor

            if actor is None:
                continue

            try:

                if not actor.node.exists():
                    continue

            except Exception:

                continue

            try:

                position = (
                    self.map.get_start_position(
                        player.team.id
                    )
                )

                actor.node.position = position

                actor.node.velocity = (
                    0.0,
                    0.0,
                    0.0,
                )

                actor.node.angular_velocity = (
                    0.0,
                    0.0,
                    0.0,
                )

            except Exception:

                pass

        bs.timer(
            0.5,
            self._unlock_goal,
        )

    def _unlock_goal(self) -> None:

        if self.has_ended():
            return

        self._goal_locked = False

        if self._ball is not None:

            try:

                if self._ball.node.exists():

                    self._ball.scored = False

            except Exception:

                pass

    def _finish_game(self) -> None:

        if self.has_ended():
            return

        results = bs.GameResults()

        for team in self.teams:

            results.set_team_score(
                team,
                team.score,
            )

        self.end(
            results=results
        )