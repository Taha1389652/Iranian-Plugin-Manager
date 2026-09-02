# -*- coding: utf-8 -*-
# ba_meta require api 9
"""
Infinite Punch Mod (پانچ بی‌نهایت) — for BombSquad / Ballistica

این مود کول‌داون (تاخیر) بین پانچ‌ها رو حذف می‌کنه تا بتونی پیوسته و
بدون وقفه پانچ بزنی. بدون دستکش بوکس و با دستکش بوکس، هر دو حالت رو
پوشش می‌ده.

نحوه نصب:
1. داخل خود بازی برو به:
   Settings -> Advanced -> Show Mod Folder
   (یا در نسخه‌های قدیمی‌تر: Content -> My Content -> Show Mod Folder)
   این دکمه پوشه دقیق مربوط به دستگاه/پلتفرم خودت رو برات باز می‌کنه.
2. این فایل (infinite_punch.py) رو داخل همون پوشه کپی کن.
3. بازی رو کامل ببند و دوباره باز کن.
4. وارد یک بازی آفلاین (Local/Solo) شو و پانچ رو نگه‌دار — الان بدون
   وقفه ضربه می‌زنی.

نکته: این مود فقط روی نمونه (instance) بازی خودت اثر می‌ذاره و برای
بازی‌های آنلاین/شبکه‌ای معمولاً توسط سرور رد میشه، پس برای حالت آفلاین
(Solo / Coop / Teams محلی) طراحی شده.
"""

from __future__ import annotations

import bascenev1 as bs
from bascenev1lib.actor.spaz import Spaz

# --------------------------------------------------------------------------
# پچ ۱: هنگام ساخته‌شدن هر Spaz (کاراکتر)، کول‌داون پانچ رو صفر می‌کنیم.
# --------------------------------------------------------------------------
_original_init = Spaz.__init__


def _patched_init(self, *args, **kwargs) -> None:
    _original_init(self, *args, **kwargs)
    # هیچ فاصله‌ای بین دو پانچ نباشه.
    self._punch_cooldown = 0


Spaz.__init__ = _patched_init


# --------------------------------------------------------------------------
# پچ ۲: وقتی پاورآپ "دستکش بوکس" برداشته میشه، بازی خودش کول‌داون رو
# دوباره تنظیم می‌کنه (مثلاً روی مقدار کوتاه‌تر factory.punch_cooldown_gloves).
# ما دوباره صفرش می‌کنیم که همیشه بی‌نهایت بمونه.
# --------------------------------------------------------------------------
_original_equip_gloves = Spaz.equip_boxing_gloves


def _patched_equip_gloves(self) -> None:
    _original_equip_gloves(self)
    self._punch_cooldown = 0


Spaz.equip_boxing_gloves = _patched_equip_gloves


# --------------------------------------------------------------------------
# پچ ۳: وقتی اثر دستکش بوکس تموم میشه (wear off)، بازی کول‌داون عادی رو
# برمی‌گردونه. اینجا هم دوباره صفرش می‌کنیم.
# --------------------------------------------------------------------------
_original_gloves_wear_off = Spaz._gloves_wear_off


def _patched_gloves_wear_off(self) -> None:
    _original_gloves_wear_off(self)
    self._punch_cooldown = 0


Spaz._gloves_wear_off = _patched_gloves_wear_off
