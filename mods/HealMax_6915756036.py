# Released for personal offline use.
# ba_meta require api 9
"""
Immortal / Infinite-Health Mod (Offline Only) — Ballistica API 9
==================================================================

این ماد جونِ اسپز (کاراکترِ) بازیکنِ محلی رو بی‌نهایت می‌کنه و جلوی
کشته‌شدنش رو می‌گیره: هیچ ضربه، بمب، سقوط یا نفرینی کشتش نمی‌ده.

⚠️ فقط در بازی‌های آفلاین/محلی اثر داره
------------------------------------------------
آسیب و فیزیکِ بازیکن‌ها در بازی‌های آنلاین توسط «هاست» (میزبان) محاسبه
می‌شه، نه کلاینتِ شما. یعنی اگر وارد سرورِ کسِ دیگه‌ای بشید، این ماد
هیچ اثری روی گیم‌پلیِ واقعی نداره (چون میزبان همچنان طبق قوانینِ خودش
شما رو می‌کشه). این ماد فقط زمانی واقعاً «بی‌نهایت» می‌کنه که:
  • بازیِ تک‌نفره / کمپین (Co-Op) انجام بدید
  • میزبانِ یک بازیِ محلی/شبکه‌ای خودتون باشید (سرور خودتونه)
  • روی سرورِ خصوصیِ خودتون که خودتون کنترلش می‌کنید بازی کنید

نصب
----
فایل را در پوشه‌ی mods بازی قرار بدید:
  - ویندوز:  Documents/BombSquad/mods
  - مک/لینوکس:  ~/Library/Application Support/BombSquad/mods  یا
                ~/.local/share/ballisticakit/mods
سپس از داخل بازی: Settings > Advanced > Plugins، پلاگین را فعال کنید.
"""

from __future__ import annotations

import babase
import bascenev1 as bs
from bascenev1lib.actor.playerspaz import PlayerSpaz

# نگه‌داشتن رفرنس به متدهای اصلی؛ رفتار اصلی رو جایگزین نمی‌کنیم،
# فقط گسترشش می‌دیم (مهم برای سازگاری با بقیه‌ی ماد‌ها/بازی‌ها).
_orig_init = PlayerSpaz.__init__
_orig_handlemessage = PlayerSpaz.handlemessage


def _stay_immortal(spaz: PlayerSpaz) -> None:
    """جون رو پر می‌کنه، افکت‌های آسیب رو پاک و invincible رو قفل می‌کنه."""
    if not spaz.node:
        return
    spaz.hitpoints = spaz.hitpoints_max
    spaz.node.hurt = 0.0
    spaz.node.invincible = True
    spaz._dead = False  # noqa: SLF001  (برگردوندن وضعیت "زنده" بعد از هر برخورد)


def _patched_init(self: PlayerSpaz, *args, **kwargs) -> None:
    _orig_init(self, *args, **kwargs)
    # موتور بازی خودش بعد از ۱ ثانیه invincible رو خاموش می‌کنه؛
    # ما درست بعدش دوباره روشنش می‌کنیم و برای همیشه نگهش می‌داریم.
    bs.timer(1.1, babase.WeakCall(_stay_immortal, self))


def _patched_handlemessage(self: PlayerSpaz, msg):
    # هر پیامِ مرگ رو خنثی می‌کنیم: به‌جای مردن، جون پر می‌شه.
    if isinstance(msg, bs.DieMessage):
        _stay_immortal(self)
        return None

    # هر ضربه‌ای که بخوره، بعدش بلافاصله جون رو دوباره پر می‌کنیم
    # (برای مواردی که آسیب از مسیرهای دیگه‌ای غیر از بلاک invincible بیاد).
    if isinstance(msg, bs.HitMessage):
        result = _orig_handlemessage(self, msg)
        _stay_immortal(self)
        return result

    # سقوط از نقشه: به‌جای مردن، برمی‌گردونیمش به آخرین نقطه‌ی ایستادنش.
    if isinstance(msg, bs.OutOfBoundsMessage):
        if self.node and self._last_stand_pos:  # noqa: SLF001
            self.node.position = self._last_stand_pos  # noqa: SLF001
        _stay_immortal(self)
        return None

    return _orig_handlemessage(self, msg)


PlayerSpaz.__init__ = _patched_init
PlayerSpaz.handlemessage = _patched_handlemessage


# ba_meta export plugin
class ImmortalOfflinePlugin(babase.Plugin):
    """پلاگینِ اصلیِ ماد؛ فقط یک پیامِ تأییدِ فعال‌سازی نشون می‌ده."""

    def on_app_running(self) -> None:
        babase.screenmessage(
            'Immortal Mod فعال شد — جونت بی‌نهایته (فقط آفلاین)',
            color=(0.4, 1.0, 0.4),
        )
