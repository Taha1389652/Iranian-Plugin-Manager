# ba_meta require api 9
"""
Ping Display Mod - نمایشگر پینگ
=================================

یک دکمه‌ی شناور و همیشه روی صفحه (گوشه‌ی بالا-راست) که پینگ فعلی شما
را نشان می‌دهد و با لمس/کلیک، همان مقدار را به‌صورت پیام چت برای بقیه
ارسال می‌کند. دقیقاً شبیه مودهایی که در چند سرور دیده‌اید.

رنگ‌بندی:
    0   تا 100  میلی‌ثانیه  -> سبز   (اتصال خوب)
    100 تا 300  میلی‌ثانیه  -> زرد   (اتصال متوسط)
    300  به بالا میلی‌ثانیه  -> قرمز  (اتصال ضعیف)

فرمت پیام ارسالی به چت دقیقاً به شکل زیر است:
    My ping : 59.80 ms

نصب:
    این فایل را داخل پوشه‌ی mods بازی کپی کنید:
        اندروید : <sdcard>/BombSquad/mods
        ویندوز  : %appdata%/BombSquad/mods
        لینوکس  : ~/.bombsquad/mods
        مک      : ~/Library/Containers/net.froemling.bombsquad/Data/Library/Application Support/BombSquad/mods
    سپس بازی را ری‌استارت کنید.

نکته‌ی فنی مهم (صداقت کامل نسبت به قابلیت واقعی موتور بازی):
    تابع رسمی موتور برای گرفتن پینگ (`bascenev1.get_client_ping`) از
    نسخه‌ی build 22797 (بازی نسخه‌ی 1.7.62، API نسخه‌ی 9) به بعد اضافه
    شده و اصولاً برای این طراحی شده که هاست/میزبان بازی، پینگ کلاینت‌های
    متصل را ببیند. اگر شما میزبان بازی باشید، این مود پینگ واقعی
    (RTT به میلی‌ثانیه) را نشان می‌دهد. اگر شما کلاینت باشید (یعنی به
    سرور کس دیگری وصل شده‌اید)، موتور بازی در نسخه‌ی فعلی راه رسمی و
    مستندی برای اینکه کلاینت پینگ خودش را از هاست بخواند در اختیار
    نمی‌گذارد؛ در آن حالت مود به‌جای کرش کردن، مقدار "N/A" نشان می‌دهد
    تا وقتی که خودِ بازی این قابلیت را برای کلاینت‌ها هم اضافه کند.
    کد طوری نوشته شده که همین که آن قابلیت اضافه شود، بدون تغییر کار
    خواهد کرد.
"""

from __future__ import annotations

import babase
import bascenev1 as bs
import bauiv1 as bui

# --------------------------------------------------------------------------
# تنظیمات قابل تغییر
# --------------------------------------------------------------------------

# آستانه‌های رنگ (میلی‌ثانیه)
PING_GREEN_MAX = 100.0   # زیر این مقدار: سبز
PING_YELLOW_MAX = 300.0  # زیر این مقدار: زرد ، بالاتر: قرمز

# رنگ‌ها (r, g, b)
COLOR_GREEN = (0.15, 0.9, 0.15)
COLOR_YELLOW = (0.95, 0.85, 0.15)
COLOR_RED = (0.95, 0.2, 0.2)
COLOR_NEUTRAL = (0.8, 0.8, 0.8)  # وقتی پینگ در دسترس نیست

# اندازه و جای‌گذاری دکمه (بر حسب پیکسل مجازی صفحه)
BUTTON_WIDTH = 92
BUTTON_HEIGHT = 36
MARGIN_RIGHT = 90   # فاصله از لبه‌ی راست صفحه
MARGIN_TOP = 60      # فاصله از لبه‌ی بالای صفحه

UPDATE_INTERVAL_SECONDS = 1.0


def _color_for_ping(ping_ms: float) -> tuple[float, float, float]:
    """رنگ مناسب بر اساس مقدار پینگ برمی‌گرداند."""
    if ping_ms < PING_GREEN_MAX:
        return COLOR_GREEN
    if ping_ms < PING_YELLOW_MAX:
        return COLOR_YELLOW
    return COLOR_RED


def _get_local_client_id() -> int | None:
    """client_id مربوط به دستگاه ورودی محلی (خودِ بازیکن) را پیدا می‌کند."""
    try:
        for dev in bs.ls_input_devices():
            try:
                if not dev.is_remote_client():
                    return dev.client_id
            except Exception:
                continue
    except Exception:
        pass
    return None


def _get_current_ping_ms() -> float | None:
    """
    پینگ فعلی را (به میلی‌ثانیه) برمی‌گرداند، یا None اگر در دسترس نباشد.

    این تابع چند روش را به ترتیب امتحان می‌کند تا با نسخه‌های مختلف
    موتور بازی سازگار بماند.
    """
    # روش ۱: تابع رسمی موتور (build 22797 / API 9 به بعد)
    get_client_ping = getattr(bs, 'get_client_ping', None)
    if get_client_ping is not None:
        client_id = _get_local_client_id()
        if client_id is not None:
            try:
                ping = get_client_ping(client_id)
                if ping is not None:
                    return float(ping)
            except Exception:
                pass

    return None


class _PingWidget:
    """نگه‌دارنده‌ی ویجت شناور پینگ روی صفحه (overlay)."""

    def __init__(self) -> None:
        self._button: bui.Widget | None = None
        self._timer: babase.AppTimer | None = None
        self._last_ping: float | None = None
        self._create_button()
        # هر ثانیه یک‌بار مقدار پینگ و متن دکمه به‌روزرسانی می‌شود
        self._timer = babase.AppTimer(
            UPDATE_INTERVAL_SECONDS, self._update, repeat=True
        )

    def _screen_pos(self) -> tuple[float, float]:
        try:
            width, height = babase.get_virtual_screen_size()
        except Exception:
            width, height = 1200.0, 800.0
        x = width - MARGIN_RIGHT
        y = height - MARGIN_TOP
        return x, y

    def _create_button(self) -> None:
        try:
            overlay = bui.get_special_widget('overlay_stack')
        except Exception:
            overlay = None
        if overlay is None:
            return

        x, y = self._screen_pos()
        try:
            self._button = bui.buttonwidget(
                parent=overlay,
                position=(x - BUTTON_WIDTH * 0.5, y - BUTTON_HEIGHT * 0.5),
                size=(BUTTON_WIDTH, BUTTON_HEIGHT),
                label='--- ms',
                button_type='square',
                color=COLOR_NEUTRAL,
                textcolor=(1, 1, 1),
                text_scale=0.72,
                on_activate_call=self._send_to_chat,
            )
        except Exception:
            self._button = None

    def _update(self) -> None:
        if self._button is None or not self._button:
            # اگر دکمه به هر دلیلی از بین رفته، دوباره می‌سازیمش
            self._create_button()
            if self._button is None:
                return

        # موقعیت را هم دوباره تنظیم می‌کنیم تا با تغییر اندازه‌ی صفحه هم‌خوان بماند
        x, y = self._screen_pos()
        try:
            bui.widget(
                edit=self._button,
                position=(x - BUTTON_WIDTH * 0.5, y - BUTTON_HEIGHT * 0.5),
            )
        except Exception:
            pass

        ping = _get_current_ping_ms()
        self._last_ping = ping

        if ping is None:
            text = 'N/A'
            color = COLOR_NEUTRAL
        else:
            text = f'{ping:.0f} ms'
            color = _color_for_ping(ping)

        try:
            bui.buttonwidget(edit=self._button, label=text, color=color)
        except Exception:
            pass

    def _send_to_chat(self) -> None:
        ping = self._last_ping
        if ping is None:
            # اگر پینگ موجود نبود فقط برای خودمان پیام می‌دهیم، نه در چت عمومی
            try:
                babase.screenmessage(
                    'پینگ در دسترس نیست (شاید به بازی آنلاین وصل نیستید).',
                    color=(1, 0.5, 0),
                )
            except Exception:
                pass
            return

        message = f'My ping : {ping:.2f} ms'
        try:
            bs.chatmessage(message)
        except Exception:
            # اگر ارسال به چت ممکن نبود (مثلاً در منوی اصلی هستیم)،
            # حداقل به خودمان نشان می‌دهیم
            try:
                babase.screenmessage(message, color=(0, 1, 1))
            except Exception:
                pass


# ba_meta export plugin
class PingDisplay(babase.Plugin):
    """پلاگین اصلی مود نمایش پینگ."""

    def __init__(self) -> None:
        super().__init__()
        self._widget: _PingWidget | None = None

    def on_app_running(self) -> None:
        # ویجت را در ترد منطقی بازی می‌سازیم
        try:
            self._widget = _PingWidget()
        except Exception:
            logging_fallback = getattr(babase, 'print_exception', None)
            if logging_fallback is not None:
                logging_fallback()
