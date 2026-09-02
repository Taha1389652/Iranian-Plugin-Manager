# -*- coding: utf-8 -*-
# ba_meta require api 9
"""
Infinite Punch Mod (پانچ بی‌نهایت) — for BombSquad / Ballistica

این مود کول‌داون (تاخیر) بین پانچ‌ها رو صفر می‌کنه تا بتونی پیوسته و
بدون وقفه پانچ بزنی؛ هم بدون دستکش بوکس و هم با دستکش بوکس.

نحوه نصب (مهم - هر دو مرحله لازمه):
1) داخل بازی برو به: Settings -> Advanced -> Show Mods Folder
   این پوشه دقیق مربوط به دستگاه/پلتفرم خودت رو باز می‌کنه.
2) فایل infinite_punch.py رو داخل همون پوشه کپی کن.
3) بازی رو کامل ببند و دوباره باز کن.
4) برو به: Settings -> Advanced -> Plugins
   و کنار "Infinite Punch" تیک بزن تا فعال بشه (این قسمت رو یادت نره،
   بدون فعال‌سازی از این منو، مود اجرا نمیشه).
5) دوباره بازی رو ببند و باز کن، بعد وارد یک بازی آفلاین (Solo/Coop/Local)
   شو و پانچ رو بزن — الان بدون وقفه ضربه می‌زنی.
"""

from __future__ import annotations

import babase
from bascenev1lib.actor.spaz import Spaz

_original_init = Spaz.__init__
_original_equip_gloves = Spaz.equip_boxing_gloves
_original_gloves_wear_off = Spaz._gloves_wear_off

_patched = False


def _patched_init(self, *args, **kwargs) -> None:
    _original_init(self, *args, **kwargs)
    # هیچ فاصله‌ای بین دو پانچ نباشه.
    self._punch_cooldown = 0


def _patched_equip_gloves(self) -> None:
    _original_equip_gloves(self)
    self._punch_cooldown = 0


def _patched_gloves_wear_off(self) -> None:
    _original_gloves_wear_off(self)
    self._punch_cooldown = 0


def _apply_patches() -> None:
    global _patched
    if _patched:
        return
    Spaz.__init__ = _patched_init
    Spaz.equip_boxing_gloves = _patched_equip_gloves
    Spaz._gloves_wear_off = _patched_gloves_wear_off
    _patched = True


def _remove_patches() -> None:
    global _patched
    if not _patched:
        return
    Spaz.__init__ = _original_init
    Spaz.equip_boxing_gloves = _original_equip_gloves
    Spaz._gloves_wear_off = _original_gloves_wear_off
    _patched = False


# ba_meta export babase.Plugin
class InfinitePunch(babase.Plugin):
    """پلاگین پانچ بی‌نهایت - باید از منوی Settings > Advanced > Plugins فعال بشه."""

    def on_app_running(self) -> None:
        _apply_patches()

    def on_app_shutdown(self) -> None:
        _remove_patches()

    def has_settings_ui(self) -> bool:
        return False
