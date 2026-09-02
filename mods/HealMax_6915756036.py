# infinite_lives_mod.py
#
# BombSquad (Ballistica) - "Infinite Lives" mod
# Scope: Elimination game mode, ONLY for one specific player (identified by
# in-game display name). Meant for your own OFFLINE / PRIVATE servers.
#
# HOW IT WORKS
# ------------
# In Elimination mode, each bascenev1.Player has a `lives` counter (or the
# team tracks it, depending on version). When a player dies, the game's
# spawner logic checks `lives` and stops respawning them at 0. This mod
# monkey-patches the spawn/lives-check step so that, for your chosen
# player name only, `lives` never drops to 0 (it's reset back up right
# after any decrement).
#
# INSTALL
# -------
# Drop this file into your BombSquad `mods` folder (same place your other
# mods, like the boxing gloves one, live) and make sure it gets imported
# at startup (via __init__.py in mods, or however you're loading the
# punch-cooldown / boxing glove mod already).
#
# CONFIGURE
# ---------
# Just change MY_PLAYER_NAME below to match your exact in-game name.

from __future__ import annotations

import bascenev1 as bs

try:
    from bascenev1lib.game.elimination import EliminationGame
except ImportError:
    # Fallback for older/newer api9 builds where the module path differs.
    # Check your game's install folder under:
    #   .../ba_data/python/bascenev1lib/game/elimination.py
    # and fix this import to match.
    raise

# ----------------------------------------------------------------------
# EDIT THIS to your exact BombSquad display name (case-sensitive).
MY_PLAYER_NAME = "YourNameHere"
# ----------------------------------------------------------------------


def _get_player_name(player: bs.Player) -> str:
    """Best-effort extraction of a player's display name across versions."""
    try:
        return player.getname()
    except Exception:
        pass
    try:
        return player.name
    except Exception:
        return ""


# Keep a reference to the original method we're wrapping.
_original_handlemessage = EliminationGame.handlemessage


def _patched_handlemessage(self, msg):
    # Let the original logic run first (this is what normally decrements
    # lives on bs.PlayerDiedMessage and checks for game-over conditions).
    result = _original_handlemessage(self, msg)

    if isinstance(msg, bs.PlayerDiedMessage):
        try:
            player = msg.getplayer(bs.Player)
        except Exception:
            player = None

        if player is not None and _get_player_name(player) == MY_PLAYER_NAME:
            # If this game mode stores lives per-player, top it back up.
            if hasattr(player, "lives"):
                if player.lives is not None and player.lives < 1:
                    player.lives = 9999
            # Some builds store lives on a per-team stats object instead.
            # If the per-player patch above doesn't seem to work, look for
            # something like `self._get_spaz_death_action` or a per-team
            # `lives` field in your local elimination.py and mirror the
            # same "top it back up" trick there.

    return result


EliminationGame.handlemessage = _patched_handlemessage

print(f"[infinite_lives_mod] Loaded. Infinite lives active for: {MY_PLAYER_NAME}")
