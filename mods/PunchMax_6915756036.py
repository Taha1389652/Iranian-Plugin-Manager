# -*- coding: utf-8 -*-
# ba_meta require api 9
"""
Infinite Boxing Gloves Mod (بوکس بی‌نهایت) — for BombSquad / Ballistica

این مود باعث میشه دستکش بوکس (Boxing Gloves):
  1) از همون اول بازی روی دست کاراکترت باشه (نیازی به برداشتن پاورآپ نیست)
  2) هیچ‌وقت تموم نشه / از بین نره (بدون تایمر پایان اثر)

توجه مهم:
این مود فقط روی بازی‌هایی اثر می‌ذاره که خودت میزبان (Host) باشی؛
یعنی حالت‌های آفلاین/سولو/محلی، یا سروری که خودت روی همون دستگاه بالا
می‌آری. اگه وارد سرور یک نفر دیگه بشی، اون سرور منطق بازی رو خودش
محاسبه می‌کنه و این مود روی چیزی که بقیه می‌بینن اثری نداره.

نحوه نصب:
1) داخل بازی برو به: Settings -> Advanced -> Show Mods Folder
2) فایل infinite_boxing_gloves.py رو داخل همون پوشه کپی کن.
   (اگه فایل قبلی infinite_punch.py رو گذاشته بودی و نمی‌خوایش، حذفش کن)
3) بازی رو کامل ببند و دوباره باز کن.
4) برو به: Settings -> Advanced -> Plugins
   و کنار "InfiniteBoxingGloves" تیک بزن تا فعال بشه.
5) بازی رو یک‌بار دیگه ری‌استارت کن.
6) یک بازی آفلاین/محلی که خودت میزبانشی شروع کن -> از لحظه اسپاون
   دستکش بوکس روی دستته و هیچ‌وقت هم درنمیاد.
"""

from __future__ import annotations

import babase
from bascenev1lib.actor.spaz import Spaz

_original_gloves_wear_off = Spaz._gloves_wear_off

_patched = False


def _patched_gloves_wear_off(self) -> None:
    # به‌جای درآوردن دستکش، دوباره تجهیزش می‌کنیم -> هیچ‌وقت واقعاً درنمیاد.
    if self.node:
        self.equip_boxing_gloves()


def _apply_patches() -> None:
    global _patched
    if _patched:
        return
    # از همون اول با دستکش بوکس اسپاون بشه.
    Spaz.default_boxing_gloves = True
    # اگه به هر دلیلی تایمر تموم‌شدن اثر صدا زده بشه، دوباره تجهیز میشه.
    Spaz._gloves_wear_off = _patched_gloves_wear_off
    _patched = True


def _remove_patches() -> None:
    global _patched
    if not _patched:
        return
    Spaz.default_boxing_gloves = False
    Spaz._gloves_wear_off = _original_gloves_wear_off
    _patched = False


# ba_meta export babase.Plugin
class InfiniteBoxingGloves(babase.Plugin):
    """دستکش بوکس همیشگی - باید از Settings > Advanced > Plugins فعال بشه."""

    def on_app_running(self) -> None:
        _apply_patches()

    def on_app_shutdown(self) -> None:
        _remove_patches()

    def has_settings_ui(self) -> bool:
        return False
