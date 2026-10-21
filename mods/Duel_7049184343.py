# ba_meta require api 9
# Duel for BombSquad: 1v1 against a strong punching bot.
# Features: boxing-glove punches, kill-cam slow motion, optional Epic Mode.
from __future__ import annotations

import random

import bascenev1 as bs
from bascenev1lib.actor.scoreboard import Scoreboard
from bascenev1lib.actor.spazbot import (
    SpazBotSet,
    SpazBotDiedMessage,
    BrawlerBot,
    BrawlerBotPro,
)


class EasyBot(BrawlerBot):
    punchiness = 0.6
    charge_speed_min = 0.7
    charge_speed_max = 0.9
    default_boxing_gloves = True


class NormalBot(BrawlerBotPro):
    punchiness = 0.9
    charge_speed_min = 0.9
    charge_speed_max = 1.0


class HardBot(BrawlerBotPro):
    # Fast, runs, boxing gloves, punches every time in range.
    punchiness = 1.0
    charge_speed_min = 1.0
    charge_speed_max = 1.0


BOTS = [EasyBot, NormalBot, HardBot]

# Random wave sizes per level (repeated numbers = more likely).
WAVES = [
    [1, 1, 1, 2],
    [1, 1, 2, 2, 3],
    [1, 2, 2, 3, 3, 4, 4],
]
# Punch strength multiplier for bots (player gloves are ~1.7).
BOT_PUNCH_POWER = [1.8, 2.3, 3.0]


class Player(bs.Player['Team']):
    pass


class Team(bs.Team[Player]):
    def __init__(self) -> None:
        self.score = 0


# ba_meta export bascenev1.GameActivity
class DuelGame(bs.TeamGameActivity[Player, Team]):
    name = 'Duel'
    description = 'Beat the bot to the kill limit.'

    @classmethod
    def get_available_settings(
        cls, sessiontype: type[bs.Session]
    ) -> list[bs.Setting]:
        return [
            bs.IntSetting('Kills to Win', min_value=3, default=10, increment=1),
            bs.IntChoiceSetting(
                'Bot Level',
                choices=[('Easy', 0), ('Normal', 1), ('Hard', 2)],
                default=1,
            ),
            bs.BoolSetting('Kill-Cam Slow Motion', default=True),
            bs.BoolSetting('Epic Mode', default=False),
        ]

    @classmethod
    def supports_session_type(cls, sessiontype: type[bs.Session]) -> bool:
        return issubclass(sessiontype, bs.FreeForAllSession) or issubclass(
            sessiontype, bs.DualTeamSession
        )

    @classmethod
    def get_supported_maps(cls, sessiontype: type[bs.Session]) -> list[str]:
        return ['Courtyard', 'Rampage', 'Football Stadium']

    def __init__(self, settings: dict):
        super().__init__(settings)
        self._kills_to_win = int(settings['Kills to Win'])
        self._level = int(settings['Bot Level'])
        self._bot_cls = BOTS[self._level]
        self._wave_pending = False
        self._killcam = bool(settings['Kill-Cam Slow Motion'])
        self._epic = bool(settings['Epic Mode'])
        self._bot_kills = 0
        self._scoreboard = Scoreboard()
        self._bots: SpazBotSet | None = None
        self.slow_motion = self._epic
        self.default_music = (
            bs.MusicType.EPIC if self._epic else bs.MusicType.TO_THE_DEATH
        )

    def on_begin(self) -> None:
        super().on_begin()
        self._bots = SpazBotSet()
        for team in self.teams:
            self._scoreboard.set_team_value(
                team, team.score, self._kills_to_win
            )
        bs.timer(1.0, self._spawn_wave)

    def _buff_bot(self, bot: bs.Actor) -> None:
        # Stronger, more lethal punches. Guarded in case the attribute changes.
        try:
            bot._punch_power_scale = BOT_PUNCH_POWER[self._level]  # type: ignore
        except Exception:
            pass

    def _spawn_wave(self) -> None:
        self._wave_pending = False
        if self.has_ended() or self._bots is None:
            return
        if self._bots.have_living_bots():
            return
        count = random.choice(WAVES[self._level])
        if count > 1:
            bs.broadcastmessage(
                f'{count} bots incoming!', color=(1, 0.5, 0.2), transient=True
            )
        for _ in range(count):
            pos = self.map.get_ffa_start_position(self.players)
            self._bots.spawn_bot(
                self._bot_cls,
                pos=pos,
                spawn_time=1.5,
                on_spawn_call=self._buff_bot,
            )

    def _check_wave(self) -> None:
        if self.has_ended() or self._bots is None or self._wave_pending:
            return
        if not self._bots.have_living_bots():
            self._wave_pending = True
            bs.timer(1.5, self._spawn_wave)

    def spawn_player(self, player: Player) -> bs.Actor:
        spaz = self.spawn_player_spaz(player)
        spaz.equip_boxing_gloves()  # stronger punch
        return spaz

    def _slowmo(self) -> None:
        if not self._killcam or self._epic:
            return
        self.globalsnode.slow_motion = True
        bs.apptimer(1.0, self._slowmo_off)

    def _slowmo_off(self) -> None:
        if not self.has_ended():
            self.globalsnode.slow_motion = self._epic

    def handlemessage(self, msg: object) -> object:
        if isinstance(msg, bs.PlayerDiedMessage):
            super().handlemessage(msg)
            player = msg.getplayer(Player)
            self.respawn_player(player)
            self._bot_kills += 1
            self._slowmo()
            bs.broadcastmessage(
                f'Bot: {self._bot_kills}', color=(1, 0.4, 0.4), transient=True
            )
            if self._bot_kills >= self._kills_to_win:
                self.end_game()
        elif isinstance(msg, SpazBotDiedMessage):
            killer = msg.killerplayer
            if killer is not None and killer.team is not None:
                killer.team.score += 1
                self._scoreboard.set_team_value(
                    killer.team, killer.team.score, self._kills_to_win
                )
                self._slowmo()
                if killer.team.score >= self._kills_to_win:
                    self.end_game()
                    return None
            # Next wave once every bot in this wave is dead.
            bs.timer(0.3, self._check_wave)
        else:
            return super().handlemessage(msg)
        return None

    def end_game(self) -> None:
        results = bs.GameResults()
        for team in self.teams:
            results.set_team_score(team, team.score)
        self.end(results=results)
