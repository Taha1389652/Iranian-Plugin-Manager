# Released for personal offline use.
# ba_meta require api 9
"""
Infinite Health Mod (Offline Only) — Ballistica API 9
========================================================

این ماد فقط یک کار می‌کنه: جونِ بازیکنِ محلی هیچ‌وقت از دستِ ضربه،
بمب یا نفرین کم نمی‌مونه (نوار جون همیشه پره) و به همین دلیل نمی‌میره.

چیزهایی که *دست‌نخورده* باقی می‌مونن (طبق خواسته‌ی خودت):
  • فیزیکِ ضربه و بمب — همچنان پرتاب/عقب‌روی طبیعی داری.
  • مرگ در اثرِ سقوط از نقشه — اگه از مپ بیفتی پایین، طبق قانونِ
    خودِ بازی کشته می‌شی (این ماد جلوش رو نمی‌گیره).

⚠️ فقط در بازی‌های آفلاین/محلی اثر داره
------------------------------------------------
آسیب و فیزیکِ بازیکن‌ها در بازی‌های آنلاین توسط «هاست» (میزبان) محاسبه
می‌شه، نه کلاینتِ شما. این ماد فقط زمانی واقعاً اثر داره که:
  • بازیِ تک‌نفره / کمپین (Co-Op) انجام بدید
  • میزبانِ یک بازیِ محلی/شبکه‌ای خودتون باشید (سرور خودتونه)
  • روی سرورِ خصوصیِ خودتون که خودتون کنترلش می‌کنید بازی کنید

نصب
----
فایل را در پوشه‌ی mods بازی قرار بدید و بازی رو کامل ری‌استارت کنید:
  - ویندوز:  Documents/BombSquad/mods
  - مک/لینوکس:  ~/Library/Application Support/BombSquad/mods  یا
                ~/.local/share/ballisticakit/mods
سپس از داخل بازی: Settings > Advanced > Plugins، پلاگین را فعال کنید.
"""

from __future__ import annotations

import babase
import bascenev1 as bs
from bascenev1lib.actor.playerspaz import PlayerSpaz

# نگه‌داشتن رفرنسِ متدِ اصلی؛ رفتار اصلی رو جایگزین نمی‌کنیم، فقط
# بعدش یه قدم اضافه می‌ذاریم (سازگار با بقیه‌ی ماد‌ها می‌مونه).
_orig_handlemessage = PlayerSpaz.handlemessage


def _refill_health(spaz: PlayerSpaz) -> None:
    """فقط جون رو پر می‌کنه و نوارِ جون رو ریست می‌کنه. کاری به فیزیک نداره."""
    if not spaz.node:
        return
    spaz.hitpoints = spaz.hitpoints_max
    spaz.node.hurt = 0.0


def _patched_handlemessage(self: PlayerSpaz, msg):
    if isinstance(msg, bs.DieMessage):
        # سقوط از نقشه = مرگِ واقعی، طبق خواسته‌ی خودت دست نمی‌زنیم بهش.
        if msg.how is bs.DeathType.FALL:
            return _orig_handlemessage(self, msg)
        # هر نوع مرگِ دیگه (ضربه/بمب/نفرین) رو خنثی می‌کنیم: به‌جای
        # مردن، فقط جون رو پر می‌کنیم.
        _refill_health(self)
        return None

    if isinstance(msg, bs.HitMessage):
        # می‌ذاریم آسیب و فیزیک/پرتاب کاملاً طبیعی اجرا بشه...
        result = _orig_handlemessage(self, msg)
        # ...و بلافاصله بعدش فقط جون رو دوباره پر می‌کنیم.
        _refill_health(self)
        return result

    return _orig_handlemessage(self, msg)


PlayerSpaz.handlemessage = _patched_handlemessage


# ba_meta export plugin
class ImmortalOfflinePlugin(babase.Plugin):
    """پلاگینِ اصلیِ ماد؛ فقط یک پیامِ تأییدِ فعال‌سازی نشون می‌ده."""

    def on_app_running(self) -> None:
        babase.screenmessage(
            'Infinite Health Mod فعال شد (سقوط از نقشه هنوز می‌کشتت)',
            color=(0.4, 1.0, 0.4),
        )
