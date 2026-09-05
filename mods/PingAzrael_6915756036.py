# PingMod.py - API 9
# ساخته شده توسط Poya Azrael
# @AzraelMods لینک چنل

from __future__ import annotations

import socket
import threading
import time

import bauiv1 as bui
import bascenev1 as bs
from babase import Plugin
from bauiv1 import buttonwidget as bw, apptimer as teck, screenmessage as push
from bauiv1lib import party

# ---------------------------------------------------------------------------
# اگه دکمه دقیقاً روی همون خونه‌ای که تو عکس با کادر قرمز مشخص کردی ننشست،
# فقط همین سه عدد رو کم‌وزیاد کن - نیازی به تغییر بقیه‌ی کد نیست:
X_OFFSET = -17      # فاصله‌ی افقی از لبه‌ی راست پنجره‌ی پارتی؛ بزرگتر = بیشتر بره راست
Y_FROM_TOP = 122    # فاصله‌ی عمودی از لبه‌ی بالای پنجره (هم‌سطح دکمه‌ی "..." بالای پنجره)
BTN_SIZE = 34      # اندازه‌ی دکمه (مربعی، هم‌اندازه بقیه آیکون‌های ستون)

# ### رنگ آیکون رو از همینجا عوض کن ###
# BTN_COLOR = رنگِ پس‌زمینه‌ی دکمه (الان سبزِ تیره، مثل رنگ آیکون تاج تو عکسی که فرستادی)
# TEXT_COLOR = رنگِ نوشته‌ی "Ping" روی دکمه (الان زرد)
# هر رنگ یه تاپل (قرمز, سبز, آبی) هست که هر عدد بین 0 و 1 هست.
# مثلاً (1, 0, 0) = قرمز خالص، (0, 0, 1) = آبی خالص، (1, 1, 1) = سفید.
BTN_COLOR = (0 ,0 ,0)   # ### رنگ پس‌زمینه دکمه رو همینجا عوض کن ###
TEXT_COLOR = (1.0, 0.82, 0.1)    # ### رنگ نوشته‌ی "Ping" رو همینجا عوض کن ###
# ---------------------------------------------------------------------------

_server_ip = "127.0.0.1"
_server_port = 43210
current_ping = 0.0

_orig_connect_to_party = bs.connect_to_party
_orig_disconnect_from_host = bs.disconnect_from_host


def _new_connect_to_party(address, port=43210, print_progress=False):
    global _server_ip, _server_port
    _server_ip = address
    _server_port = port
    return _orig_connect_to_party(address, port, print_progress)


def _new_disconnect_from_host():
    global _server_ip, _server_port
    _server_ip = "127.0.0.1"
    _server_port = 43210
    return _orig_disconnect_from_host()


bs.connect_to_party = _new_connect_to_party
bs.disconnect_from_host = _new_disconnect_from_host


class _PingThread(threading.Thread):
    """پینگ واقعی رو با یه پکت کوچیک UDP اندازه می‌گیره - همون روشی که تو مود دوستت بود."""

    def __init__(self):
        super().__init__(daemon=True)
        self.running = True

    def run(self):
        global current_ping
        while self.running:
            try:
                if _server_ip != "127.0.0.1" and _server_port != 43210:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.settimeout(1)
                    start = time.time()
                    sock.sendto(b"\x0b", (_server_ip, _server_port))
                    try:
                        data, _addr = sock.recvfrom(10)
                        current_ping = (
                            round((time.time() - start) * 1000.0)
                            if data == b"\x0c"
                            else 999
                        )
                    except socket.timeout:
                        current_ping = 999
                    except Exception:
                        current_ping = 0
                    finally:
                        sock.close()
                else:
                    current_ping = 0
            except Exception:
                current_ping = 0
            time.sleep(1)

    def stop(self):
        self.running = False


_ping_thread = _PingThread()
_ping_thread.start()


def _on_ping_press():
    """با زدن دکمه، پینگ فعلی به‌صورت پیام تو چتِ بازی ارسال میشه."""
    try:
        bs.chatmessage(f"My Ping : {int(current_ping)} ms ☄️")
    except Exception as e:
        try:
            push(f"PingMod error: {e}", color=(1, 0.3, 0.3))
        except Exception:
            pass


# --- قلاب زدن به خودِ پنجره‌ی پارتی (بدون دست‌کاری چیز دیگه‌ای توش) ---
_orig_party_init = party.PartyWindow.__init__


def _patched_party_init(self, *args, **kwargs):
    _orig_party_init(self, *args, **kwargs)

    try:
        bw(
            parent=self._root_widget,
            position=(self._width + X_OFFSET, self._height - Y_FROM_TOP),
            size=(BTN_SIZE, BTN_SIZE),
            button_type="square",
            label="Ping",
            text_scale=1.1,
            color=BTN_COLOR,
            textcolor=TEXT_COLOR,
            autoselect=True,
            on_activate_call=_on_ping_press,
        )
    except Exception as e:
        try:
            push(f"PingMod error: {e}", color=(1, 0.3, 0.3))
        except Exception:
            pass
        print(f"PingMod: couldn't add ping button: {e}")


party.PartyWindow.__init__ = _patched_party_init


def _announce_loaded():
    try:
        push("PingMod loaded ✅ (Party > Ping)", color=(0.3, 1, 0.3))
    except Exception:
        pass


# ba_meta require api 9


# ba_meta export plugin
class PingMod(Plugin):

    def on_app_running(self) -> None:
        teck(1.5, _announce_loaded)

    def __del__(self):
        try:
            _ping_thread.stop()
        except Exception:
            pass
