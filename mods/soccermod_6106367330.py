# ba_meta require api 8

from __future__ import annotations

from typing import Any

import bascenev1 as bs
from bascenev1lib.gameutils import SharedObjects


# ============================================================
# PLAYER
# ============================================================

class Player(bs.Player['Team']):
    """Soccer player."""


# ============================================================
# TEAM
# ============================================================

class Team(bs.Team[Player]):
    """Soccer team."""

    def __init__(self) -> None:
        self.score = 0


# ============================================================
# SETTINGS
# ============================================================

BALL_POSITION = (0.0, 1.2, 0.0)

BALL_SCALE = 0.55
BALL_DENSITY = 1.15

GOAL_WIDTH = 3.2
GOAL_HEIGHT = 2.15
GOAL_DEPTH = 1.45

POST = 0.13

RESET_DELAY = 1.2


# ============================================================
# BALL
# ============================================================

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
                'density': BALL_DENSITY,

                'materials': (
                    shared.object_material,
                    material,
                ),

                'is_area_of_interest': True,
            },
        )

        # مهم:
        # هر توپ فقط یک بار می‌تواند گل ثبت کند.
        self.scored = False

    def reset(self) -> None:

        if not self.node.exists():
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

        # توپ جدید از نظر گل‌زدن دوباره فعال شود.
        self.scored = False

    def handlemessage(
        self,
        msg: Any,
    ) -> Any:

        if isinstance(
            msg,
            bs.DieMessage,
        ):

            if self.node.exists():
                self.node.delete()

            return None

        if isinstance(
            msg,
            bs.OutOfBoundsMessage,
        ):

            self.reset()

            return None

        return super().handlemessage(msg)


# ============================================================
# GOAL POST
# ============================================================

class GoalPost(bs.Actor):

    def __init__(
        self,
        position: tuple[float, float, float],
        scale: tuple[float, float, float],
        material: bs.Material,
    ) -> None:

        super().__init__()

        shared = SharedObjects.get()

        self.node = bs.newnode(
            'prop',
            delegate=self,
            attrs={
                'position': position,
                'body': 'box',
                'body_scale': scale,

                'mesh': bs.getmesh('puck'),

                'color': (
                    1.0,
                    1.0,
                    1.0,
                ),

                'reflection': 'soft',
                'reflection_scale': [0.3],

                'density': 2.0,

                'materials': (
                    shared.object_material,
                    material,
                ),
            },
        )

    def handlemessage(
        self,
        msg: Any,
    ) -> Any:

        if isinstance(
            msg,
            bs.DieMessage,
        ):

            if self.node.exists():
                self.node.delete()

            return None

        return super().handlemessage(msg)


# ============================================================
# GOAL MESSAGE
# ============================================================

class GoalMessage:

    def __init__(
        self,
        team_id: int,
    ) -> None:

        self.team_id = team_id


# ============================================================
# GAME
# ============================================================

# ba_meta export bascenev1.GameActivity
class SoccerGame(
    bs.TeamGameActivity[
        Player,
        Team,
    ]
):

    name = 'Soccer'

    description = 'Soccer game.'

    available_settings = [
        bs.IntSetting(
            'Score to Win',
            min_value=1,
            default=5,
            increment=1,
        ),
    ]

    # ========================================================
    # SESSION
    # ========================================================

    @classmethod
    def supports_session_type(
        cls,
        sessiontype: type[bs.Session],
    ) -> bool:

        return issubclass(
            sessiontype,
            bs.DualTeamSession,
        )

    # ========================================================
    # MAP
    # ========================================================

    @classmethod
    def get_supported_maps(
        cls,
        sessiontype: type[bs.Session],
    ) -> list[str]:

        del sessiontype

        assert bs.app.classic is not None

        return bs.app.classic.getmaps(
            'football'
        )

    # ========================================================
    # INIT
    # ========================================================

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

        self._goal_posts: list[GoalPost] = []

        self._net_nodes: list[bs.Node] = []

        self._score_regions: list[bs.NodeActor] = []

        # جلوگیری از چند بار ثبت شدن یک گل
        self._goal_locked = False

        shared = SharedObjects.get()

        # ====================================================
        # BALL MATERIAL
        # ====================================================

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
                    0.35,
                ),
            ),
        )

        # ====================================================
        # GOAL MATERIAL
        # ====================================================

        self._goal_material = bs.Material()

        self._goal_material.add_actions(
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
                    True,
                ),
            ),
        )

        # ====================================================
        # SCORE MATERIAL
        # ====================================================

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

    # ========================================================
    # BEGIN
    # ========================================================

    def on_begin(self) -> None:

        super().on_begin()

        # توپ
        self._spawn_ball()

        # دروازه‌ها
        self._create_goals()

        # مناطق گل
        self._create_goal_regions()

        # بازیکنان
        for player in self.players:
            self.spawn_player(player)

    # ========================================================
    # SPAWN BALL
    # ========================================================

    def _spawn_ball(self) -> None:

        # اگر توپ وجود ندارد بساز.
        if self._ball is None:

            self._ball = SoccerBall(
                BALL_POSITION,
                self._ball_material,
            )

            return

        # اگر توپ هست، فقط ریست کن.
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

    # ========================================================
    # CREATE GOALS
    # ========================================================

    def _create_goals(self) -> None:

        defs = self.map.defs

        if 'goal1' in defs.boxes:

            box = defs.boxes['goal1']

            self._make_goal(
                box[0],
                box[1],
                box[2],
                -1.0,
            )

        if 'goal2' in defs.boxes:

            box = defs.boxes['goal2']

            self._make_goal(
                box[0],
                box[1],
                box[2],
                1.0,
            )

    # ========================================================
    # MAKE GOAL
    # ========================================================

    def _make_goal(
        self,
        x: float,
        y: float,
        z: float,
        direction: float,
    ) -> None:

        width = GOAL_WIDTH
        height = GOAL_HEIGHT
        depth = GOAL_DEPTH
        t = POST

        # FRONT LEFT
        self._make_post(
            (
                x,
                y + height / 2.0,
                z - width / 2.0,
            ),
            (
                t,
                height,
                t,
            ),
        )

        # FRONT RIGHT
        self._make_post(
            (
                x,
                y + height / 2.0,
                z + width / 2.0,
            ),
            (
                t,
                height,
                t,
            ),
        )

        # CROSSBAR
        self._make_post(
            (
                x,
                y + height,
                z,
            ),
            (
                t,
                t,
                width,
            ),
        )

        # BACK POSTS
        back_x = x + direction * depth

        self._make_post(
            (
                back_x,
                y + height / 2.0,
                z - width / 2.0,
            ),
            (
                t,
                height,
                t,
            ),
        )

        self._make_post(
            (
                back_x,
                y + height / 2.0,
                z + width / 2.0,
            ),
            (
                t,
                height,
                t,
            ),
        )

        # BACK CROSSBAR
        self._make_post(
            (
                back_x,
                y + height,
                z,
            ),
            (
                t,
                t,
                width,
            ),
        )

        # TOP LEFT
        self._make_post(
            (
                x + direction * depth / 2.0,
                y + height,
                z - width / 2.0,
            ),
            (
                depth,
                t,
                t,
            ),
        )

        # TOP RIGHT
        self._make_post(
            (
                x + direction * depth / 2.0,
                y + height,
                z + width / 2.0,
            ),
            (
                depth,
                t,
                t,
            ),
        )

        self._make_net(
            x,
            y,
            z,
            direction,
        )

    # ========================================================
    # POST
    # ========================================================

    def _make_post(
        self,
        position: tuple[float, float, float],
        scale: tuple[float, float, float],
    ) -> None:

        self._goal_posts.append(
            GoalPost(
                position,
                scale,
                self._goal_material,
            )
        )

    # ========================================================
    # NET
    # ========================================================

    def _make_net(
        self,
        x: float,
        y: float,
        z: float,
        direction: float,
    ) -> None:

        width = GOAL_WIDTH
        height = GOAL_HEIGHT
        depth = GOAL_DEPTH

        columns = 10
        rows = 7

        # BACK HORIZONTAL
        for row in range(rows + 1):

            yy = y + height * row / rows

            start = z - width / 2.0
            end = z + width / 2.0

            for col in range(columns):

                z1 = (
                    start
                    + (end - start)
                    * col
                    / columns
                )

                z2 = (
                    start
                    + (end - start)
                    * (col + 1)
                    / columns
                )

                self._net_line(
                    (
                        x + direction * depth * 0.98,
                        yy,
                        z1,
                    ),
                    (
                        x + direction * depth * 0.98,
                        yy,
                        z2,
                    ),
                )

        # BACK VERTICAL
        for col in range(columns + 1):

            zz = (
                z
                - width / 2.0
                + width * col / columns
            )

            for row in range(rows):

                y1 = y + height * row / rows
                y2 = y + height * (row + 1) / rows

                self._net_line(
                    (
                        x + direction * depth * 0.98,
                        y1,
                        zz,
                    ),
                    (
                        x + direction * depth * 0.98,
                        y2,
                        zz,
                    ),
                )

        # SIDE NETS
        for side in (-1.0, 1.0):

            side_z = z + side * width / 2.0

            for row in range(rows + 1):

                yy = y + height * row / rows

                self._net_line(
                    (
                        x,
                        yy,
                        side_z,
                    ),
                    (
                        x + direction * depth,
                        yy,
                        side_z,
                    ),
                )

    # ========================================================
    # NET LINE
    # ========================================================

    def _net_line(
        self,
        p1: tuple[float, float, float],
        p2: tuple[float, float, float],
    ) -> None:

        mx = (p1[0] + p2[0]) / 2.0
        my = (p1[1] + p2[1]) / 2.0
        mz = (p1[2] + p2[2]) / 2.0

        try:

            node = bs.newnode(
                'locator',
                attrs={
                    'shape': 'circle',
                    'position': (
                        mx,
                        my,
                        mz,
                    ),
                    'size': [0.035],
                    'color': (
                        0.95,
                        0.95,
                        0.95,
                    ),
                    'opacity': 0.45,
                    'draw_beauty': True,
                },
            )

            self._net_nodes.append(node)

        except Exception:
            pass

    # ========================================================
    # CREATE SCORE REGIONS
    # ========================================================

    def _create_goal_regions(self) -> None:

        defs = self.map.defs

        # -----------------------------
        # GOAL 1
        # -----------------------------

        if 'goal1' in defs.boxes:

            box = defs.boxes['goal1']

            node = bs.newnode(
                'region',
                attrs={
                    'position': box[0:3],
                    'scale': box[6:9],
                    'type': 'box',
                    'materials': (
                        self._score_material,
                    ),
                },
            )

            self._score_regions.append(
                bs.NodeActor(node)
            )

        # -----------------------------
        # GOAL 2
        # -----------------------------

        if 'goal2' in defs.boxes:

            box = defs.boxes['goal2']

            node = bs.newnode(
                'region',
                attrs={
                    'position': box[0:3],
                    'scale': box[6:9],
                    'type': 'box',
                    'materials': (
                        self._score_material,
                    ),
                },
            )

            self._score_regions.append(
                bs.NodeActor(node)
            )

    # ========================================================
    # SPAWN PLAYER
    # ========================================================

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

    # ========================================================
    # GOAL COLLISION
    # ========================================================

    def _goal_collision(self) -> None:

        if self.has_ended():
            return

        if self._goal_locked:
            return

        if self._ball is None:
            return

        # ----------------------------------------------------
        # توپ فعلی قبلاً گل نزده باشد
        # ----------------------------------------------------

        if self._ball.scored:
            return

        try:

            if not self._ball.node.exists():
                return

        except Exception:

            return

        # ----------------------------------------------------
        # COLLISION
        # ----------------------------------------------------

        try:

            collision = bs.getcollision()

        except Exception:

            return

        region = collision.sourcenode

        # ----------------------------------------------------
        # FIND GOAL
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # MARK BALL AS SCORED
        # ----------------------------------------------------

        self._ball.scored = True

        self._goal_locked = True

        # ----------------------------------------------------
        # WHICH TEAM SCORED
        # ----------------------------------------------------

        if goal_id == 0:

            team_id = 1

        else:

            team_id = 0

        if team_id < 0:
            return

        if team_id >= len(self.teams):
            return

        # ----------------------------------------------------
        # SCORE
        # ----------------------------------------------------

        self.handlemessage(
            GoalMessage(team_id)
        )

    # ========================================================
    # HANDLE MESSAGE
    # ========================================================

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

    # ========================================================
    # SCORE GOAL
    # ========================================================

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

        # ----------------------------------------------------
        # ADD SCORE
        # ----------------------------------------------------

        team.score += 1

        # ----------------------------------------------------
        # GOAL MESSAGE
        # ----------------------------------------------------

        bs.broadcastmessage(
            'GOAL! TEAM %d  %d'
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

        # ----------------------------------------------------
        # CAMERA FLASH
        # ----------------------------------------------------

        try:

            bs.cameraflash(
                duration=0.25
            )

        except Exception:

            pass

        # ----------------------------------------------------
        # WIN
        # ----------------------------------------------------

        if team.score >= self._score_to_win:

            bs.timer(
                1.0,
                self._finish_game,
            )

            return

        # ----------------------------------------------------
        # RESET
        # ----------------------------------------------------

        bs.timer(
            RESET_DELAY,
            self._reset_game,
        )

    # ========================================================
    # RESET
    # ========================================================

    def _reset_game(self) -> None:

        if self.has_ended():
            return

        # ----------------------------------------------------
        # RESET BALL
        # ----------------------------------------------------

        self._spawn_ball()

        # ----------------------------------------------------
        # RESET PLAYERS
        # ----------------------------------------------------

        for player in self.players:

            actor = player.actor

            if actor is None:
                continue

            try:

                if not actor.node.exists():
                    continue

            except Exception:

                continue

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

        # ----------------------------------------------------
        # IMPORTANT
        # صبر کوتاه برای خروج توپ از region
        # ----------------------------------------------------

        bs.timer(
            0.4,
            self._unlock_goal,
        )

    # ========================================================
    # UNLOCK
    # ========================================================

    def _unlock_goal(self) -> None:

        if self.has_ended():
            return

        # توپ دوباره می‌تواند گل بزند.
        if self._ball is not None:

            self._ball.scored = False

        self._goal_locked = False

    # ========================================================
    # END GAME
    # ========================================================

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