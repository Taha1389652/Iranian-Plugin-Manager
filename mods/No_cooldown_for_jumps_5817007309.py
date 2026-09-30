#This mod was made by "(; ____ smileface"

# ba_meta require api 9

from __future__ import annotations
from typing import Any

import babase
import bascenev1 as bs

try:
    from bascenev1lib.actor.spaz import Spaz
except Exception:
    Spaz = None


def _patch_spaz() -> None:
    if Spaz is None:
        return

    if getattr(Spaz, "_jump_patch_done", False):
        return
    Spaz._jump_patch_done = True

    orig_handlemessage = Spaz.handlemessage

    def _new_handlemessage(self, msg: Any):
        try:
            if hasattr(self, "_jump_cooldown"):
                self._jump_cooldown = 0.0
        except Exception:
            pass

        return orig_handlemessage(self, msg)

    Spaz.handlemessage = _new_handlemessage


# ba_meta export plugin
class by_smileface(babase.Plugin):
    def __init__(self):
        _patch_spaz()