# PingMod.py - API 9
# ساخته شده توسط Poya Azrael
# @AzraelMods لینک چنل

from __future__ import annotations

import random
import re
import socket
import textwrap
import threading
import time
import weakref

import babase
import bauiv1 as bui
import bascenev1 as bs
from babase import Plugin
from bauiv1 import buttonwidget as bw, apptimer as teck, screenmessage as push, get_special_widget as gsw
from bauiv1lib import party


def _widget_exists(widget):
    if widget is None:
        return False
    try:
        return bui.exists(widget)
    except AttributeError:
        pass
    except Exception:
        return False
    try:
        return babase.exists(widget)
    except AttributeError:
        pass
    except Exception:
        return False
    return True


X_OFFSET = -350
Y_FROM_TOP = 363
BTN_SIZE = 34

IP_X_OFFSET = -290
IP_Y_FROM_TOP = 363
IP_BTN_SIZE = 34

CLOCK_X_OFFSET = -230
CLOCK_Y_FROM_TOP = 363
CLOCK_BTN_SIZE = 34

CALC_X_OFFSET = -170
CALC_Y_FROM_TOP = 363
CALC_BTN_SIZE = 34

CALC_PANEL_WIDTH = 300
CALC_PANEL_HEIGHT = 380
CALC_PANEL_X_OFFSET = 0
CALC_PANEL_COLOR = (0.12, 0.12, 0.17)
CALC_KEY_COLOR = (0.22, 0.22, 0.28)
CALC_EQUALS_COLOR = (0.25, 0.35, 0.55)
CALC_EQUALS_ARMED_COLOR = (0.15, 0.55, 0.2)
CALC_CLOSE_COLOR = (0.5, 0.15, 0.15)
CALC_CONFIRM_TIMEOUT = 2.5

NOTES_X_OFFSET = -110
NOTES_Y_FROM_TOP = 363
NOTES_BTN_SIZE = 34

NOTES_PANEL_WIDTH = 460
NOTES_PANEL_HEIGHT = 560
NOTES_MAX_CHARS = 4000
NOTES_WRAP_CHARS = 40

PARTY_X_OFFSET = -50
PARTY_Y_FROM_TOP = 363
PARTY_BTN_SIZE = 34

PARTY_PANEL_WIDTH = 380
PARTY_PANEL_HEIGHT = 160


_DEFAULT_COLORS = {
    "ping":  {"bg": (0.0, 0.0, 0.0), "text": (1.0, 0.82, 0.1)},
    "ip":    {"bg": (0.0, 0.0, 0.0), "text": (0.4, 0.8, 1.0)},
    "clock": {"bg": (0.0, 0.0, 0.0), "text": (1.0, 1.0, 1.0)},
    "calc":  {"bg": (0.0, 0.0, 0.0), "text": (0.8, 0.5, 1.0)},
    "notes": {"bg": (0.0, 0.0, 0.0), "text": (0.6, 1.0, 0.6)},
    "party": {"bg": (0.0, 0.0, 0.0), "text": (1.0, 0.55, 0.15)},
}

_LABELS = {"ping": "Ping", "ip": "IP", "clock": "Time", "calc": "Calc", "notes": "Notes", "party": "Party"}

_LABEL_TEXT_SCALE = {"calc": 0.9, "notes": 0.8}

_CONFIG_KEY = "PingMod Icon Colors"


def _load_colors():
    saved = {}
    try:
        raw = babase.app.config.get(_CONFIG_KEY)
        if isinstance(raw, dict):
            saved = raw
    except Exception:
        saved = {}

    colors = {}
    for key, default in _DEFAULT_COLORS.items():
        entry = saved.get(key) if isinstance(saved.get(key), dict) else {}
        try:
            bg = tuple(entry.get("bg", default["bg"]))
            if len(bg) != 3:
                bg = default["bg"]
        except Exception:
            bg = default["bg"]
        try:
            text = tuple(entry.get("text", default["text"]))
            if len(text) != 3:
                text = default["text"]
        except Exception:
            text = default["text"]
        colors[key] = {"bg": bg, "text": text}
    return colors


_colors = _load_colors()

_live_buttons = {"ping": None, "ip": None, "clock": None, "calc": None, "notes": None, "party": None}


def _save_colors():
    try:
        babase.app.config[_CONFIG_KEY] = {
            key: {"bg": list(val["bg"]), "text": list(val["text"])}
            for key, val in _colors.items()
        }
        babase.app.config.commit()
    except Exception as e:
        try:
            push(f"PingMod: Error saving settings: {e}", color=(1, 0.3, 0.3))
        except Exception:
            pass


def _apply_color(key, which, color):
    _colors[key][which] = color
    _save_colors()
    widget = _live_buttons.get(key)
    if widget is not None and _widget_exists(widget):
        try:
            if which == "bg":
                bw(edit=widget, color=color)
            else:
                bw(edit=widget, textcolor=color)
        except Exception:
            pass

_DEFAULT_PANEL_COLORS = {
    "ping":  (0.1, 0.1, 0.14),
    "ip":    (0.12, 0.12, 0.17),
    "calc":  CALC_PANEL_COLOR,
    "notes": (0.12, 0.12, 0.17),
}

_PANEL_LABELS = {
    "ping": "Ping Panel",
    "ip": "IP Panel",
    "calc": "Calculator Panel",
    "notes": "Notes Panel",
}

_PANEL_SECTION_ORDER = ["ping", "ip", "calc", "notes"]

_CONFIG_KEY_PANEL_COLORS = "PingMod Panel Colors"


def _load_panel_colors():
    saved = {}
    try:
        raw = babase.app.config.get(_CONFIG_KEY_PANEL_COLORS)
        if isinstance(raw, dict):
            saved = raw
    except Exception:
        saved = {}

    colors = {}
    for key, default in _DEFAULT_PANEL_COLORS.items():
        try:
            color = tuple(saved.get(key, default))
            if len(color) != 3:
                color = default
        except Exception:
            color = default
        colors[key] = color
    return colors


_panel_colors = _load_panel_colors()

_live_panels = {"ping": None, "ip": None, "calc": None, "notes": None}


def _save_panel_colors():
    try:
        babase.app.config[_CONFIG_KEY_PANEL_COLORS] = {
            key: list(val) for key, val in _panel_colors.items()
        }
        babase.app.config.commit()
    except Exception as e:
        try:
            push(f"PingMod: Error saving panel colors: {e}", color=(1, 0.3, 0.3))
        except Exception:
            pass


def _apply_panel_color(key, color):
    _panel_colors[key] = color
    _save_panel_colors()
    widget = _live_panels.get(key)
    if widget is not None and _widget_exists(widget):
        try:
            bui.containerwidget(edit=widget, color=color)
        except Exception:
            pass

_DEFAULT_LAYOUT = {
    "ping":  {"x": X_OFFSET, "y": Y_FROM_TOP, "size": BTN_SIZE, "shape": "square"},
    "ip":    {"x": IP_X_OFFSET, "y": IP_Y_FROM_TOP, "size": IP_BTN_SIZE, "shape": "square"},
    "clock": {"x": CLOCK_X_OFFSET, "y": CLOCK_Y_FROM_TOP, "size": CLOCK_BTN_SIZE, "shape": "square"},
    "calc":  {"x": CALC_X_OFFSET, "y": CALC_Y_FROM_TOP, "size": CALC_BTN_SIZE, "shape": "square"},
    "notes": {"x": NOTES_X_OFFSET, "y": NOTES_Y_FROM_TOP, "size": NOTES_BTN_SIZE, "shape": "square"},
    "party": {"x": PARTY_X_OFFSET, "y": PARTY_Y_FROM_TOP, "size": PARTY_BTN_SIZE, "shape": "square"},
}

_LAYOUT_LIMITS = {
    "x": (-500, 0),
    "y": (20, 600),
    "size": (18, 70),
}
_LAYOUT_STEP = {"x": 10, "y": 10, "size": 4}
_SHAPES = ["square", "rectangle"]
_SHAPE_LABELS = {"square": "🔲 Square", "rectangle": "▭ Rectangle"}

_CONFIG_KEY_LAYOUT = "PingMod Icon Layout"


def _load_layout():
    saved = {}
    try:
        raw = babase.app.config.get(_CONFIG_KEY_LAYOUT)
        if isinstance(raw, dict):
            saved = raw
    except Exception:
        saved = {}

    layout = {}
    for key, default in _DEFAULT_LAYOUT.items():
        entry = saved.get(key) if isinstance(saved.get(key), dict) else {}
        try:
            x = int(entry.get("x", default["x"]))
        except Exception:
            x = default["x"]
        try:
            y = int(entry.get("y", default["y"]))
        except Exception:
            y = default["y"]
        try:
            size = int(entry.get("size", default["size"]))
        except Exception:
            size = default["size"]
        shape = entry.get("shape", default["shape"])
        if shape not in _SHAPES:
            shape = default["shape"]
        layout[key] = {"x": x, "y": y, "size": size, "shape": shape}
    return layout


_layout = _load_layout()

_live_party_window_ref = None
_live_party_root = None
_live_party_dims = (0, 0)


def _get_live_party_window():
    if _live_party_window_ref is None:
        return None
    return _live_party_window_ref()


def _save_layout():
    try:
        babase.app.config[_CONFIG_KEY_LAYOUT] = {
            key: {"x": val["x"], "y": val["y"], "size": val["size"], "shape": val["shape"]}
            for key, val in _layout.items()
        }
        babase.app.config.commit()
    except Exception as e:
        try:
            push(f"PingMod: Error saving position/size: {e}", color=(1, 0.3, 0.3))
        except Exception:
            pass


def _clamp(value, field):
    lo, hi = _LAYOUT_LIMITS[field]
    return max(lo, min(hi, value))


def _shape_button_type(shape):
    return "square"


def _shape_size(base_size, shape):
    if shape == "rectangle":
        return (int(base_size * 1.6), base_size)
    return (base_size, base_size)


def _create_icon_button(key):
    if _live_party_root is None or not _widget_exists(_live_party_root):
        return None
    cfg = _layout[key]
    size = _shape_size(cfg["size"], cfg["shape"])
    px, py = _live_party_dims
    try:
        btn = bw(
            parent=_live_party_root,
            position=(px + cfg["x"], py - cfg["y"]),
            size=size,
            button_type=_shape_button_type(cfg["shape"]),
            label=_LABELS[key],
            text_scale=_LABEL_TEXT_SCALE.get(key, 1.1),
            color=_colors[key]["bg"],
            textcolor=_colors[key]["text"],
            autoselect=True,
            on_activate_call=_BUTTON_CALLBACKS[key],
        )
    except Exception:
        return None
    _live_buttons[key] = btn
    return btn


def _refresh_icon_button(key, shape_changed):
    widget = _live_buttons.get(key)
    cfg = _layout[key]
    if widget is None or not _widget_exists(widget):
        return
    if shape_changed:
        deleted = False
        try:
            bui.widget(edit=widget, delete=True)
            deleted = True
        except Exception:
            deleted = False
        if deleted:
            _create_icon_button(key)
            return
    try:
        size = _shape_size(cfg["size"], cfg["shape"])
        px, py = _live_party_dims
        bw(edit=widget, position=(px + cfg["x"], py - cfg["y"]), size=size)
    except Exception:
        pass


def _apply_layout(key, **updates):
    for field in ("x", "y", "size"):
        if field in updates:
            _layout[key][field] = _clamp(int(updates[field]), field)
    shape_changed = False
    if "shape" in updates and updates["shape"] in _SHAPES:
        shape_changed = _layout[key]["shape"] != updates["shape"]
        _layout[key]["shape"] = updates["shape"]
    _save_layout()
    _refresh_icon_button(key, shape_changed)

_server_ip = "127.0.0.1"
_server_port = 43210
current_ping = 0.0

IP_AUTO_SEND_DELAY = 2.5

_CONFIG_KEY_IP_AUTO_SEND = "PingMod IP Auto Send Enabled"

_ip_auto_sent_key = None


def _load_ip_auto_send_enabled():
    try:
        val = babase.app.config.get(_CONFIG_KEY_IP_AUTO_SEND)
        if isinstance(val, bool):
            return val
    except Exception:
        pass
    return True


_ip_auto_send_enabled = _load_ip_auto_send_enabled()


def _save_ip_auto_send_enabled():
    try:
        babase.app.config[_CONFIG_KEY_IP_AUTO_SEND] = _ip_auto_send_enabled
        babase.app.config.commit()
    except Exception as e:
        try:
            push(f"PingMod: Error saving IP auto send setting: {e}", color=(1, 0.3, 0.3))
        except Exception:
            pass


_orig_connect_to_party = bs.connect_to_party
_orig_disconnect_from_host = bs.disconnect_from_host


def _auto_send_ip(address, port):
    global _ip_auto_sent_key
    try:
        if not _ip_auto_send_enabled:
            return
        if _server_ip != address or _server_port != port:
            return
        key = (address, port)
        if _ip_auto_sent_key == key:
            return
        _ip_auto_sent_key = key
        bs.chatmessage(f"Server IP : {address}:{port} 🌐")
    except Exception as e:
        try:
            push(f"PingMod error: {e}", color=(1, 0.3, 0.3))
        except Exception:
            pass


def _new_connect_to_party(address, port=43210, print_progress=False):
    global _server_ip, _server_port
    _server_ip = address
    _server_port = port
    result = _orig_connect_to_party(address, port, print_progress)
    teck(IP_AUTO_SEND_DELAY, lambda a=address, p=port: _auto_send_ip(a, p))
    return result


def _new_disconnect_from_host():
    global _server_ip, _server_port, _ip_auto_sent_key
    _server_ip = "127.0.0.1"
    _server_port = 43210
    _ip_auto_sent_key = None
    return _orig_disconnect_from_host()


bs.connect_to_party = _new_connect_to_party
bs.disconnect_from_host = _new_disconnect_from_host


class _PingThread(threading.Thread):

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


PING_GOOD_MAX = 80
PING_WARN_MAX = 150

PING_PANEL_WIDTH = 210
PING_PANEL_HEIGHT = 150
PING_REFRESH_INTERVAL = 1.0

PING_ALERT_COOLDOWN = 15.0
PING_ALERT_CHECK_INTERVAL = 2.0

_CONFIG_KEY_PING_ALERT = "PingMod Ping Alert Enabled"

_ping_panel = None
_ping_alert_state = {"was_red": False, "last_alert": 0.0}


def _load_ping_alert_enabled():
    try:
        val = babase.app.config.get(_CONFIG_KEY_PING_ALERT)
        if isinstance(val, bool):
            return val
    except Exception:
        pass
    return True


_ping_alert_enabled = _load_ping_alert_enabled()


def _save_ping_alert_enabled():
    try:
        babase.app.config[_CONFIG_KEY_PING_ALERT] = _ping_alert_enabled
        babase.app.config.commit()
    except Exception as e:
        try:
            push(f"PingMod: Error saving alert setting: {e}", color=(1, 0.3, 0.3))
        except Exception:
            pass


def _ping_color_for(value):
    if value <= 0:
        return (0.6, 0.6, 0.6)
    if value <= PING_GOOD_MAX:
        return (0.3, 0.85, 0.3)
    if value <= PING_WARN_MAX:
        return (1.0, 0.85, 0.1)
    return (1.0, 0.2, 0.2)


def _send_ping_to_chat():
    try:
        bs.chatmessage(f"My Ping : {int(current_ping)} ms ☄️")
    except Exception as e:
        try:
            push(f"PingMod error: {e}", color=(1, 0.3, 0.3))
        except Exception:
            pass


class _PingPanelWindow:
    def __init__(self):
        w = PING_PANEL_WIDTH
        h = PING_PANEL_HEIGHT
        self._width = w
        self._height = h

        try:
            sw, sh = bui.get_virtual_screen_size()
        except Exception:
            sw, sh = w, h
        pos_x = (sw - w) / 2
        pos_y = (sh - h) / 2

        self.root_widget = bui.containerwidget(
            parent=gsw("overlay_stack"),
            position=(pos_x, pos_y),
            size=(w, h),
            transition="in_scale",
            scale=1.0,
            color=_panel_colors["ping"],
        )
        self._root_widget = self.root_widget
        _live_panels["ping"] = self.root_widget

        bui.textwidget(
            parent=self._root_widget,
            position=(0, h - 22),
            size=(w, 18),
            text="Live Ping",
            h_align="center",
            v_align="center",
            scale=0.9,
            color=(0.9, 0.9, 0.95),
        )

        close_btn = bw(
            parent=self._root_widget,
            position=(w - 14 - 20, h - 28),
            size=(20, 20),
            button_type="square",
            label="✕",
            text_scale=0.7,
            color=CALC_CLOSE_COLOR,
            textcolor=(1, 1, 1),
            autoselect=True,
            on_activate_call=bui.WeakCall(self._close),
        )

        self._value_btn = bw(
            parent=self._root_widget,
            position=(15, h - 78),
            size=(w - 30, 46),
            button_type="square",
            label=f"{int(current_ping)} ms",
            text_scale=1.1,
            color=_ping_color_for(current_ping),
            textcolor=(0, 0, 0),
            autoselect=True,
            on_activate_call=bui.WeakCall(self._send_ping),
        )

        self._alert_btn = bw(
            parent=self._root_widget,
            position=(10, 14),
            size=(w - 20, 32),
            button_type="square",
            label=self._alert_label(),
            text_scale=0.75,
            color=self._alert_color(),
            textcolor=(1, 1, 1),
            autoselect=True,
            on_activate_call=bui.WeakCall(self._toggle_alert),
        )

        bui.containerwidget(
            edit=self._root_widget,
            cancel_button=close_btn,
            on_outside_click_call=bui.WeakCall(self._close),
        )

        self._tick()

    def _alert_label(self):
        return "Ping Alert: ON ✅" if _ping_alert_enabled else "Ping Alert: OFF ❌"

    def _alert_color(self):
        return (0.2, 0.5, 0.25) if _ping_alert_enabled else (0.5, 0.2, 0.2)

    def _toggle_alert(self):
        global _ping_alert_enabled
        _ping_alert_enabled = not _ping_alert_enabled
        _save_ping_alert_enabled()
        if _widget_exists(self._alert_btn):
            try:
                bw(edit=self._alert_btn, label=self._alert_label(), color=self._alert_color())
            except Exception:
                pass

    def _send_ping(self):
        _send_ping_to_chat()

    def _tick(self):
        if not _widget_exists(self._root_widget):
            return
        try:
            bw(
                edit=self._value_btn,
                label=f"{int(current_ping)} ms",
                color=_ping_color_for(current_ping),
            )
        except Exception:
            pass
        teck(PING_REFRESH_INTERVAL, bui.WeakCall(self._tick))

    def _close(self):
        try:
            bui.containerwidget(edit=self._root_widget, transition="out_scale")
        except Exception:
            pass
        global _ping_panel
        _ping_panel = None
        _live_panels["ping"] = None


def _on_ping_press():
    global _ping_panel
    try:
        if _ping_panel is not None and _widget_exists(_ping_panel.root_widget):
            _ping_panel._close()
            return
        _ping_panel = _PingPanelWindow()
    except Exception as e:
        try:
            push(f"PingMod error: {e}", color=(1, 0.3, 0.3))
        except Exception:
            pass


def _ping_alert_tick():
    try:
        connected = _server_ip != "127.0.0.1"
        is_red = connected and current_ping > PING_WARN_MAX
        if is_red and not _ping_alert_state["was_red"]:
            if _ping_alert_enabled:
                now = time.time()
                if now - _ping_alert_state["last_alert"] >= PING_ALERT_COOLDOWN:
                    try:
                        bs.chatmessage(f"My Ping : {int(current_ping)} Ms ⚠️")
                    except Exception:
                        pass
                    _ping_alert_state["last_alert"] = now
        _ping_alert_state["was_red"] = is_red
    except Exception:
        pass
    teck(PING_ALERT_CHECK_INTERVAL, _ping_alert_tick)


IP_PANEL_WIDTH = 380
IP_PANEL_HEIGHT = 320
IP_PANEL_COLOR = (0.12, 0.12, 0.17)

_ip_window = None


def _get_server_name():
    for fn_name in ("get_connection_to_host_info_2", "get_connection_to_host_info"):
        fn = getattr(bs, fn_name, None)
        if fn is None:
            continue
        try:
            info = fn()
        except Exception:
            continue
        if info is None:
            continue
        if isinstance(info, dict):
            for k in ("name", "party_name", "display_string"):
                name = info.get(k)
                if isinstance(name, str) and name.strip():
                    return name.strip()
            continue
        for attr in ("name", "party_name", "display_string"):
            name = getattr(info, attr, None)
            if isinstance(name, str) and name.strip():
                return name.strip()
    return ""


def _ip_row_ip_text():
    return f"{_server_ip}:{_server_port}"


def _ip_row_server_name_text():
    return _get_server_name() or "—"


_IP_PANEL_ROWS = [
    {
        "icon": "🌐",
        "title": "Server IP",
        "get_text": _ip_row_ip_text,
        "send": lambda: f"Server IP : {_server_ip}:{_server_port} 🌐",
    },
    {
        "icon": "🏷️",
        "title": "Server Name",
        "get_text": _ip_row_server_name_text,
        "send": lambda: f"Server Name : {_get_server_name() or '—'} 🏷️",
    },
]


class _IpPanelWindow:
    def __init__(self):
        w = IP_PANEL_WIDTH
        h = IP_PANEL_HEIGHT
        self._width = w
        self._height = h

        try:
            sw, sh = bui.get_virtual_screen_size()
        except Exception:
            sw, sh = w, h
        pos_x = (sw - w) / 2
        pos_y = (sh - h) / 2

        self.root_widget = bui.containerwidget(
            parent=gsw("overlay_stack"),
            position=(pos_x, pos_y),
            size=(w, h),
            transition="in_scale",
            scale=1.0,
            color=_panel_colors["ip"],
        )
        self._root_widget = self.root_widget
        _live_panels["ip"] = self.root_widget

        margin = 20

        bui.textwidget(
            parent=self._root_widget,
            position=(0, h - 34),
            size=(w, 24),
            text="🌐 IP / Server Name",
            h_align="center",
            v_align="center",
            scale=1.1,
            color=(1, 1, 1),
        )

        close_btn = bw(
            parent=self._root_widget,
            position=(w - margin - 22, h - 36),
            size=(22, 22),
            button_type="square",
            label="✕",
            text_scale=0.8,
            color=CALC_CLOSE_COLOR,
            textcolor=(1, 1, 1),
            autoselect=True,
            on_activate_call=bui.WeakCall(self._close),
        )

        bui.containerwidget(
            edit=self._root_widget,
            cancel_button=close_btn,
            on_outside_click_call=bui.WeakCall(self._close),
        )

        self._auto_btn = bw(
            parent=self._root_widget,
            position=(margin, 12),
            size=(w - 2 * margin, 32),
            button_type="square",
            label=self._auto_label(),
            text_scale=0.8,
            color=self._auto_color(),
            textcolor=(1, 1, 1),
            autoselect=True,
            on_activate_call=bui.WeakCall(self._toggle_auto),
        )

        bottom_bar_h = 52
        scroll_y = bottom_bar_h
        scroll_h = h - 60 - bottom_bar_h
        scroll_w = w - 2 * margin

        row_h = 78
        content_h = max(scroll_h, 20 + len(_IP_PANEL_ROWS) * row_h)

        try:
            self._scroll = bui.scrollwidget(
                parent=self._root_widget,
                position=(margin, scroll_y),
                size=(scroll_w, scroll_h),
                highlight=False,
                capture_arrows=True,
            )
            self._content = bui.containerwidget(
                parent=self._scroll,
                size=(scroll_w, content_h),
                background=False,
            )
        except Exception:
            self._scroll = None
            self._content = self._root_widget

        self._value_labels = {}
        top = content_h - 14
        for index, row in enumerate(_IP_PANEL_ROWS):
            self._build_row(index, row, 6, top, scroll_w - 12)
            top -= row_h

    def _build_row(self, index, row, x, top, width):
        bui.textwidget(
            parent=self._content,
            position=(x, top),
            size=(width, 20),
            text=f"{row['icon']} {row['title']}",
            h_align="left",
            v_align="center",
            scale=0.85,
            color=(0.85, 0.85, 0.9),
        )
        value_widget = bui.textwidget(
            parent=self._content,
            position=(x, top - 22),
            size=(width, 20),
            text=row["get_text"](),
            h_align="left",
            v_align="center",
            scale=0.8,
            color=(1, 1, 0.6),
            maxwidth=width,
        )
        self._value_labels[index] = value_widget

        bw(
            parent=self._content,
            position=(x, top - 50),
            size=(width, 26),
            button_type="square",
            label="Send to Chat",
            text_scale=0.8,
            color=(0.25, 0.35, 0.55),
            textcolor=(1, 1, 1),
            autoselect=True,
            on_activate_call=bui.WeakCall(self._send_row, index, row),
        )

    def _auto_label(self):
        return "Auto Send IP: ON ✅" if _ip_auto_send_enabled else "Auto Send IP: OFF ❌"

    def _auto_color(self):
        return (0.2, 0.5, 0.25) if _ip_auto_send_enabled else (0.5, 0.2, 0.2)

    def _toggle_auto(self):
        global _ip_auto_send_enabled
        _ip_auto_send_enabled = not _ip_auto_send_enabled
        _save_ip_auto_send_enabled()
        if _widget_exists(self._auto_btn):
            try:
                bw(edit=self._auto_btn, label=self._auto_label(), color=self._auto_color())
            except Exception:
                pass

    def _send_row(self, index, row):
        try:
            bs.chatmessage(row["send"]())
        except Exception as e:
            try:
                push(f"PingMod error: {e}", color=(1, 0.3, 0.3))
            except Exception:
                pass
        widget = self._value_labels.get(index)
        if widget is not None and _widget_exists(widget):
            try:
                bui.textwidget(edit=widget, text=row["get_text"]())
            except Exception:
                pass

    def _close(self):
        try:
            bui.containerwidget(edit=self._root_widget, transition="out_scale")
        except Exception:
            pass
        global _ip_window
        _ip_window = None
        _live_panels["ip"] = None


def _open_ip_panel():
    global _ip_window
    try:
        if _ip_window is not None and _widget_exists(_ip_window.root_widget):
            return
        _ip_window = _IpPanelWindow()
    except Exception as e:
        try:
            push(f"PingMod error: {e}", color=(1, 0.3, 0.3))
        except Exception:
            pass


def _on_ip_press():
    _open_ip_panel()


_WEEKDAY_EN = [
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
]


def _gregorian_to_jalali(g_y, g_m, g_d):
    g_days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    j_days_in_month = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]

    gy = g_y - 1600
    gm = g_m - 1
    gd = g_d - 1

    g_day_no = 365 * gy + (gy + 3) // 4 - (gy + 99) // 100 + (gy + 399) // 400
    for i in range(gm):
        g_day_no += g_days_in_month[i]
    if gm > 1 and ((g_y % 4 == 0 and g_y % 100 != 0) or (g_y % 400 == 0)):
        g_day_no += 1
    g_day_no += gd

    j_day_no = g_day_no - 79

    j_np = j_day_no // 12053
    j_day_no %= 12053

    jy = 979 + 33 * j_np + 4 * (j_day_no // 1461)
    j_day_no %= 1461

    if j_day_no >= 366:
        jy += (j_day_no - 1) // 365
        j_day_no = (j_day_no - 1) % 365

    jm = 12
    jd = j_day_no + 1
    for i in range(11):
        if j_day_no < j_days_in_month[i]:
            jm = i + 1
            jd = j_day_no + 1
            break
        j_day_no -= j_days_in_month[i]

    return jy, jm, jd


def _clock_shamsi_text():
    now = time.localtime()
    current_time = time.strftime("%H:%M:%S", now)
    icon = "☀️" if 6 <= now.tm_hour < 18 else "🌑"
    weekday_en = _WEEKDAY_EN[now.tm_wday]
    jy, jm, jd = _gregorian_to_jalali(now.tm_year, now.tm_mon, now.tm_mday)
    return f"{icon} {weekday_en}, {jy}.{jm:02d}.{jd:02d}  |  {current_time}"


def _on_clock_press():
    try:
        bs.chatmessage(_clock_shamsi_text())
    except Exception as e:
        try:
            push(f"PingMod error: {e}", color=(1, 0.3, 0.3))
        except Exception:
            pass


_OP_MAP = {"÷": "/", "×": "*", "−": "-"}
_calc_window = None


class _CalcWindow:
    def __init__(self, party_window):
        self._expr = ""
        self._problem = ""
        self._confirm_armed = False

        w = CALC_PANEL_WIDTH
        h = CALC_PANEL_HEIGHT
        self._width = w
        self._height = h

        try:
            sw, sh = bui.get_virtual_screen_size()
        except Exception:
            sw, sh = party_window._width, party_window._height
        pos_x = (sw - w) / 2 + CALC_PANEL_X_OFFSET
        pos_y = (sh - h) / 2

        self.root_widget = bui.containerwidget(
            parent=gsw("overlay_stack"),
            position=(pos_x, pos_y),
            size=(w, h),
            transition="in_scale",
            scale=1.0,
            color=_panel_colors["calc"],
        )
        self._root_widget = self.root_widget
        _live_panels["calc"] = self.root_widget

        margin = 16

        bui.textwidget(
            parent=self._root_widget,
            position=(0, h - 32),
            size=(w, 24),
            text="🧮 Calculator",
            h_align="center",
            v_align="center",
            scale=1.1,
            color=(1, 1, 1),
        )

        close_btn = bw(
            parent=self._root_widget,
            position=(w - margin - 22, h - 36),
            size=(22, 22),
            button_type="square",
            label="✕",
            text_scale=0.8,
            color=CALC_CLOSE_COLOR,
            textcolor=(1, 1, 1),
            autoselect=True,
            on_activate_call=bui.WeakCall(self._close),
        )

        bui.containerwidget(
            edit=self._root_widget,
            cancel_button=close_btn,
            on_outside_click_call=bui.WeakCall(self._close),
        )

        self._display_margin = margin + 22
        self._display = bui.textwidget(
            parent=self._root_widget,
            position=(self._display_margin, h - 88),
            size=(w - 2 * self._display_margin, 40),
            text="0",
            h_align="right",
            v_align="center",
            scale=1.2,
            maxwidth=w - 2 * self._display_margin,
            color=(1, 1, 0.6),
        )

        rows = [
            ["7", "8", "9", "÷"],
            ["4", "5", "6", "×"],
            ["1", "2", "3", "−"],
            ["C", "0", ".", "+"],
        ]
        btn_w, btn_h, gap = 58, 44, 10
        grid_left = (w - (4 * btn_w + 3 * gap)) / 2
        grid_top = h - 130

        for r, row in enumerate(rows):
            for c, label in enumerate(row):
                x = grid_left + c * (btn_w + gap)
                y = grid_top - r * (btn_h + gap)
                bw(
                    parent=self._root_widget,
                    position=(x, y),
                    size=(btn_w, btn_h),
                    button_type="square",
                    label=label,
                    text_scale=1.1,
                    color=CALC_KEY_COLOR,
                    textcolor=(1, 1, 1),
                    autoselect=True,
                    on_activate_call=bui.WeakCall(self._append, label),
                )

        last_row_bottom = grid_top - (len(rows) - 1) * (btn_h + gap)
        equals_y = last_row_bottom - gap - 36
        self._equals_btn = bw(
            parent=self._root_widget,
            position=(grid_left, equals_y),
            size=(4 * btn_w + 3 * gap, 36),
            button_type="square",
            label="=",
            text_scale=1.2,
            color=CALC_EQUALS_COLOR,
            textcolor=(1, 1, 1),
            autoselect=True,
            on_activate_call=bui.WeakCall(self._on_equals_press),
        )


    def _append(self, ch):
        if self._confirm_armed:
            self._reset_confirm_state()
        if ch == "C":
            self._expr = ""
        else:
            self._expr += _OP_MAP.get(ch, ch)
        self._update_display()

    def _update_display(self):
        text = self._expr if self._expr else "0"
        n = len(text)
        if n <= 6:
            scale = 1.2
        elif n <= 9:
            scale = 1.0
        elif n <= 12:
            scale = 0.8
        elif n <= 15:
            scale = 0.65
        elif n <= 19:
            scale = 0.52
        else:
            scale = 0.42
        try:
            bui.textwidget(
                edit=self._display,
                text=text,
                scale=scale,
                maxwidth=self._width - 2 * self._display_margin,
            )
        except Exception:
            pass

    def _show_error(self, msg):
        try:
            bui.textwidget(edit=self._display, text=msg)
        except Exception:
            pass
        self._expr = ""

    def _calculate(self):
        expr = self._expr.strip()
        if not expr:
            return False
        if not re.fullmatch(r"[0-9+\-*/(). ]+", expr):
            self._show_error("Invalid expression")
            return False
        try:
            result = eval(expr, {"__builtins__": {}}, {})
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            self._problem = expr
            self._expr = str(result)
            self._update_display()
            return True
        except ZeroDivisionError:
            self._show_error("Division by zero!")
            return False
        except Exception:
            self._show_error("Calculation error")
            return False

    def _on_equals_press(self):
        if not self._confirm_armed:
            if self._calculate():
                self._confirm_armed = True
                try:
                    bw(edit=self._equals_btn, label="Tap to Send ✅", color=CALC_EQUALS_ARMED_COLOR)
                except Exception:
                    pass
                teck(CALC_CONFIRM_TIMEOUT, bui.WeakCall(self._confirm_timeout))
        else:
            self._send_to_chat()
            self._reset_confirm_state()

    def _confirm_timeout(self):
        if _widget_exists(self._root_widget):
            self._reset_confirm_state()

    def _reset_confirm_state(self):
        self._confirm_armed = False
        try:
            bw(edit=self._equals_btn, label="=", color=CALC_EQUALS_COLOR)
        except Exception:
            pass

    def _send_to_chat(self):
        try:
            problem = self._problem if self._problem else self._expr
            bs.chatmessage(f"🧮 {problem} = {self._expr}")
        except Exception as e:
            try:
                push(f"CalcMod error: {e}", color=(1, 0.3, 0.3))
            except Exception:
                pass

    def _close(self):
        try:
            bui.containerwidget(edit=self._root_widget, transition="out_scale")
        except Exception:
            pass
        global _calc_window
        _calc_window = None
        _live_panels["calc"] = None


def _on_calc_press(party_window):
    global _calc_window
    try:
        if _calc_window is not None and _widget_exists(_calc_window.root_widget):
            return
        _calc_window = _CalcWindow(party_window)
    except Exception as e:
        try:
            push(f"CalcMod error: {e}", color=(1, 0.3, 0.3))
        except Exception:
            pass


_PALETTE = [
    (0.0, 0.0, 0.0),
    (1.0, 1.0, 1.0),
    (0.5, 0.5, 0.5),
    (1.0, 0.2, 0.2),
    (1.0, 0.55, 0.1),
    (1.0, 0.85, 0.1),
    (0.3, 0.85, 0.3),
    (0.2, 0.85, 0.85),
    (0.3, 0.5, 1.0),
    (0.7, 0.3, 1.0),
]

SETTINGS_PANEL_WIDTH = 560
SETTINGS_PANEL_HEIGHT = 460
SETTINGS_PANEL_COLOR = (0.12, 0.12, 0.17)

SWATCH_SIZE = 32
SWATCH_GAP = 12

_SECTION_ORDER = ["ping", "ip", "clock", "calc", "notes", "party"]
_color_window = None


class _ColorSettingsWindow:
    def __init__(self):
        w = SETTINGS_PANEL_WIDTH
        h = SETTINGS_PANEL_HEIGHT
        self._width = w
        self._height = h
        self._previews = {}

        try:
            sw, sh = bui.get_virtual_screen_size()
        except Exception:
            sw, sh = w, h
        pos_x = (sw - w) / 2
        pos_y = (sh - h) / 2

        self.root_widget = bui.containerwidget(
            parent=gsw("overlay_stack"),
            position=(pos_x, pos_y),
            size=(w, h),
            transition="in_scale",
            scale=1.0,
            color=SETTINGS_PANEL_COLOR,
        )
        self._root_widget = self.root_widget

        bui.textwidget(
            parent=self._root_widget,
            position=(0, h - 34),
            size=(w, 24),
            text="🎨 Settings 1 - Icon Colors",
            h_align="center",
            v_align="center",
            scale=1.1,
            color=(1, 1, 1),
        )

        margin = 20
        bottom_bar_h = 56
        scroll_y = bottom_bar_h
        scroll_h = h - 60 - bottom_bar_h
        scroll_w = w - 2 * margin

        sec_h = 140
        content_h = max(scroll_h, 20 + len(_SECTION_ORDER) * sec_h)

        try:
            self._scroll = bui.scrollwidget(
                parent=self._root_widget,
                position=(margin, scroll_y),
                size=(scroll_w, scroll_h),
                highlight=False,
                capture_arrows=True,
            )
            self._content = bui.containerwidget(
                parent=self._scroll,
                size=(scroll_w, content_h),
                background=False,
            )
        except Exception:
            self._scroll = None
            self._content = self._root_widget

        sec_top = content_h - 20
        for key in _SECTION_ORDER:
            self._build_section(key, 10, sec_top)
            sec_top -= sec_h

        bw(
            parent=self._root_widget,
            position=(margin, 14),
            size=(160, 34),
            button_type="square",
            label="Reset All",
            text_scale=0.8,
            color=(0.35, 0.35, 0.4),
            textcolor=(1, 1, 1),
            autoselect=True,
            on_activate_call=bui.WeakCall(self._reset_all),
        )
        close_btn = bw(
            parent=self._root_widget,
            position=(w - margin - 160, 14),
            size=(160, 34),
            button_type="square",
            label="Close",
            text_scale=0.85,
            color=(0.2, 0.45, 0.25),
            textcolor=(1, 1, 1),
            autoselect=True,
            on_activate_call=bui.WeakCall(self._close),
        )

        bui.containerwidget(
            edit=self._root_widget,
            cancel_button=close_btn,
            on_outside_click_call=bui.WeakCall(self._close),
        )

    def _build_section(self, key, x, top):
        c = _colors[key]
        label = _LABELS[key]

        bui.textwidget(
            parent=self._content,
            position=(x, top),
            size=(70, 22),
            text=label,
            h_align="left",
            v_align="center",
            scale=1.0,
            color=(1, 1, 1),
        )

        preview = bw(
            parent=self._content,
            position=(x + 60, top - 4),
            size=(54, 28),
            button_type="square",
            label=label,
            text_scale=0.8,
            color=c["bg"],
            textcolor=c["text"],
            autoselect=True,
            on_activate_call=lambda: None,
        )
        self._previews[key] = preview

        self._add_swatch_row(x, top - 44, "Background", key, "bg")
        self._add_swatch_row(x, top - 44 - (SWATCH_SIZE + 16), "Text", key, "text")

    def _add_swatch_row(self, x, y, row_label, key, which):
        bui.textwidget(
            parent=self._content,
            position=(x, y + SWATCH_SIZE / 2 - 8),
            size=(52, 18),
            text=row_label,
            h_align="left",
            v_align="center",
            scale=0.75,
            color=(0.8, 0.8, 0.85),
        )
        sx = x + 56
        for color in _PALETTE:
            bw(
                parent=self._content,
                position=(sx, y),
                size=(SWATCH_SIZE, SWATCH_SIZE),
                button_type="square",
                label="",
                color=color,
                autoselect=True,
                on_activate_call=bui.WeakCall(self._pick, key, which, color),
            )
            sx += SWATCH_SIZE + SWATCH_GAP

    def _pick(self, key, which, color):
        _apply_color(key, which, color)
        preview = self._previews.get(key)
        if preview is not None and _widget_exists(preview):
            try:
                if which == "bg":
                    bw(edit=preview, color=color)
                else:
                    bw(edit=preview, textcolor=color)
            except Exception:
                pass

    def _reset_all(self):
        for key, default in _DEFAULT_COLORS.items():
            _apply_color(key, "bg", default["bg"])
            _apply_color(key, "text", default["text"])
            preview = self._previews.get(key)
            if preview is not None and _widget_exists(preview):
                try:
                    bw(edit=preview, color=default["bg"], textcolor=default["text"])
                except Exception:
                    pass

    def _close(self):
        try:
            bui.containerwidget(edit=self._root_widget, transition="out_scale")
        except Exception:
            pass
        global _color_window
        _color_window = None


def _open_color_settings():
    global _color_window
    try:
        if _color_window is not None and _widget_exists(_color_window.root_widget):
            return
        _color_window = _ColorSettingsWindow()
    except Exception as e:
        try:
            push(f"PingMod settings error: {e}", color=(1, 0.3, 0.3))
        except Exception:
            pass


_panel_color_window = None


class _PanelColorSettingsWindow:
    def __init__(self):
        w = SETTINGS_PANEL_WIDTH
        h = SETTINGS_PANEL_HEIGHT
        self._width = w
        self._height = h
        self._previews = {}

        try:
            sw, sh = bui.get_virtual_screen_size()
        except Exception:
            sw, sh = w, h
        pos_x = (sw - w) / 2
        pos_y = (sh - h) / 2

        self.root_widget = bui.containerwidget(
            parent=gsw("overlay_stack"),
            position=(pos_x, pos_y),
            size=(w, h),
            transition="in_scale",
            scale=1.0,
            color=SETTINGS_PANEL_COLOR,
        )
        self._root_widget = self.root_widget

        bui.textwidget(
            parent=self._root_widget,
            position=(0, h - 34),
            size=(w, 24),
            text="🖌️ Settings 2 - Panel Colors",
            h_align="center",
            v_align="center",
            scale=1.1,
            color=(1, 1, 1),
        )

        margin = 20
        bottom_bar_h = 56
        scroll_y = bottom_bar_h
        scroll_h = h - 60 - bottom_bar_h
        scroll_w = w - 2 * margin

        sec_h = 110
        content_h = max(scroll_h, 20 + len(_PANEL_SECTION_ORDER) * sec_h)

        try:
            self._scroll = bui.scrollwidget(
                parent=self._root_widget,
                position=(margin, scroll_y),
                size=(scroll_w, scroll_h),
                highlight=False,
                capture_arrows=True,
            )
            self._content = bui.containerwidget(
                parent=self._scroll,
                size=(scroll_w, content_h),
                background=False,
            )
        except Exception:
            self._scroll = None
            self._content = self._root_widget

        sec_top = content_h - 20
        for key in _PANEL_SECTION_ORDER:
            self._build_section(key, 10, sec_top)
            sec_top -= sec_h

        bw(
            parent=self._root_widget,
            position=(margin, 14),
            size=(160, 34),
            button_type="square",
            label="Reset All",
            text_scale=0.8,
            color=(0.35, 0.35, 0.4),
            textcolor=(1, 1, 1),
            autoselect=True,
            on_activate_call=bui.WeakCall(self._reset_all),
        )
        close_btn = bw(
            parent=self._root_widget,
            position=(w - margin - 160, 14),
            size=(160, 34),
            button_type="square",
            label="Close",
            text_scale=0.85,
            color=(0.2, 0.45, 0.25),
            textcolor=(1, 1, 1),
            autoselect=True,
            on_activate_call=bui.WeakCall(self._close),
        )

        bui.containerwidget(
            edit=self._root_widget,
            cancel_button=close_btn,
            on_outside_click_call=bui.WeakCall(self._close),
        )

    def _build_section(self, key, x, top):
        color = _panel_colors[key]
        label = _PANEL_LABELS[key]

        bui.textwidget(
            parent=self._content,
            position=(x, top),
            size=(220, 22),
            text=label,
            h_align="left",
            v_align="center",
            scale=1.0,
            color=(1, 1, 1),
        )

        preview = bw(
            parent=self._content,
            position=(x + 230, top - 4),
            size=(60, 28),
            button_type="square",
            label="Preview",
            text_scale=0.7,
            color=color,
            textcolor=(1, 1, 1),
            autoselect=True,
            on_activate_call=lambda: None,
        )
        self._previews[key] = preview

        sx = x
        sy = top - 44
        for c in _PALETTE:
            bw(
                parent=self._content,
                position=(sx, sy),
                size=(SWATCH_SIZE, SWATCH_SIZE),
                button_type="square",
                label="",
                color=c,
                autoselect=True,
                on_activate_call=bui.WeakCall(self._pick, key, c),
            )
            sx += SWATCH_SIZE + SWATCH_GAP

    def _pick(self, key, color):
        _apply_panel_color(key, color)
        preview = self._previews.get(key)
        if preview is not None and _widget_exists(preview):
            try:
                bw(edit=preview, color=color)
            except Exception:
                pass

    def _reset_all(self):
        for key, default in _DEFAULT_PANEL_COLORS.items():
            _apply_panel_color(key, default)
            preview = self._previews.get(key)
            if preview is not None and _widget_exists(preview):
                try:
                    bw(edit=preview, color=default)
                except Exception:
                    pass

    def _close(self):
        try:
            bui.containerwidget(edit=self._root_widget, transition="out_scale")
        except Exception:
            pass
        global _panel_color_window
        _panel_color_window = None


def _open_panel_color_settings():
    global _panel_color_window
    try:
        if _panel_color_window is not None and _widget_exists(_panel_color_window.root_widget):
            return
        _panel_color_window = _PanelColorSettingsWindow()
    except Exception as e:
        try:
            push(f"PingMod settings error: {e}", color=(1, 0.3, 0.3))
        except Exception:
            pass


LAYOUT_PANEL_WIDTH = SETTINGS_PANEL_WIDTH
LAYOUT_PANEL_HEIGHT = SETTINGS_PANEL_HEIGHT
LAYOUT_PANEL_COLOR = SETTINGS_PANEL_COLOR

_layout_window = None


class _LayoutSettingsWindow:
    def __init__(self):
        w = LAYOUT_PANEL_WIDTH
        h = LAYOUT_PANEL_HEIGHT
        self._width = w
        self._height = h
        self._previews = {}
        self._preview_pos = {}
        self._value_labels = {}
        self._shape_buttons = {}

        try:
            sw, sh = bui.get_virtual_screen_size()
        except Exception:
            sw, sh = w, h
        pos_x = (sw - w) / 2
        pos_y = (sh - h) / 2

        self.root_widget = bui.containerwidget(
            parent=gsw("overlay_stack"),
            position=(pos_x, pos_y),
            size=(w, h),
            transition="in_scale",
            scale=1.0,
            color=LAYOUT_PANEL_COLOR,
        )
        self._root_widget = self.root_widget

        bui.textwidget(
            parent=self._root_widget,
            position=(0, h - 34),
            size=(w, 24),
            text="📐 Settings 3 - Icon Position/Size/Shape",
            h_align="center",
            v_align="center",
            scale=1.1,
            color=(1, 1, 1),
        )

        margin = 20
        bottom_bar_h = 56
        scroll_y = bottom_bar_h
        scroll_h = h - 60 - bottom_bar_h
        scroll_w = w - 2 * margin

        self._row_w = scroll_w - 20
        sec_h = 205
        content_h = max(scroll_h, 20 + len(_SECTION_ORDER) * sec_h)

        try:
            self._scroll = bui.scrollwidget(
                parent=self._root_widget,
                position=(margin, scroll_y),
                size=(scroll_w, scroll_h),
                highlight=False,
                capture_arrows=True,
            )
            self._content = bui.containerwidget(
                parent=self._scroll,
                size=(scroll_w, content_h),
                background=False,
            )
        except Exception:
            self._scroll = None
            self._content = self._root_widget

        sec_top = content_h - 20
        for key in _SECTION_ORDER:
            self._build_section(key, 10, sec_top)
            sec_top -= sec_h

        bw(
            parent=self._root_widget,
            position=(margin, 14),
            size=(160, 34),
            button_type="square",
            label="Reset All",
            text_scale=0.8,
            color=(0.35, 0.35, 0.4),
            textcolor=(1, 1, 1),
            autoselect=True,
            on_activate_call=bui.WeakCall(self._reset_all),
        )
        close_btn = bw(
            parent=self._root_widget,
            position=(w - margin - 160, 14),
            size=(160, 34),
            button_type="square",
            label="Close",
            text_scale=0.85,
            color=(0.2, 0.45, 0.25),
            textcolor=(1, 1, 1),
            autoselect=True,
            on_activate_call=bui.WeakCall(self._close),
        )

        bui.containerwidget(
            edit=self._root_widget,
            cancel_button=close_btn,
            on_outside_click_call=bui.WeakCall(self._close),
        )

    def _build_section(self, key, x, top):
        cfg = _layout[key]
        label = _LABELS[key]
        row_w = self._row_w

        bui.textwidget(
            parent=self._content,
            position=(x, top),
            size=(70, 22),
            text=label,
            h_align="left",
            v_align="center",
            scale=1.0,
            color=(1, 1, 1),
        )

        preview_pos = (x + 60, top - 4)
        self._preview_pos[key] = preview_pos
        preview = bw(
            parent=self._content,
            position=preview_pos,
            size=(44, 44),
            button_type=_shape_button_type(cfg["shape"]),
            label=label,
            text_scale=0.7,
            color=_colors[key]["bg"],
            textcolor=_colors[key]["text"],
            autoselect=True,
            on_activate_call=lambda: None,
        )
        self._previews[key] = preview

        row1_y = top - 56
        self._build_stepper(key, "x", "X", x, row1_y, row_w / 2 - 10)
        self._build_stepper(key, "y", "Y", x + row_w / 2 + 10, row1_y, row_w / 2 - 10)

        row2_y = row1_y - 42
        self._build_stepper(key, "size", "Size", x, row2_y, row_w)

        row3_y = row2_y - 48
        self._build_shape_row(key, x, row3_y, row_w)

    def _build_stepper(self, key, field, label, x, y, width):
        cfg = _layout[key]
        btn_size = 26
        minus_x = x + width - (btn_size * 2 + 6)
        plus_x = x + width - btn_size
        text_w = max(40, width - 2 * btn_size - 14)

        value_widget = bui.textwidget(
            parent=self._content,
            position=(x, y + 4),
            size=(text_w, 18),
            text=f"{label}: {cfg[field]}",
            h_align="left",
            v_align="center",
            scale=0.8,
            color=(0.85, 0.85, 0.9),
        )
        self._value_labels[f"{key}_{field}"] = value_widget

        bw(
            parent=self._content,
            position=(minus_x, y),
            size=(btn_size, btn_size),
            button_type="square",
            label="-",
            text_scale=1.0,
            color=(0.3, 0.3, 0.38),
            textcolor=(1, 1, 1),
            autoselect=True,
            on_activate_call=bui.WeakCall(self._step, key, field, -1, label),
        )
        bw(
            parent=self._content,
            position=(plus_x, y),
            size=(btn_size, btn_size),
            button_type="square",
            label="+",
            text_scale=1.0,
            color=(0.3, 0.3, 0.38),
            textcolor=(1, 1, 1),
            autoselect=True,
            on_activate_call=bui.WeakCall(self._step, key, field, 1, label),
        )

    def _build_shape_row(self, key, x, y, width):
        btn_w = (width - 2 * 10) / 3
        bx = x
        self._shape_buttons[key] = {}
        for shape in _SHAPES:
            selected = _layout[key]["shape"] == shape
            btn = bw(
                parent=self._content,
                position=(bx, y),
                size=(btn_w, 30),
                button_type="square",
                label=_SHAPE_LABELS[shape],
                text_scale=0.75,
                color=(0.25, 0.55, 0.3) if selected else (0.25, 0.25, 0.32),
                textcolor=(1, 1, 1),
                autoselect=True,
                on_activate_call=bui.WeakCall(self._pick_shape, key, shape),
            )
            self._shape_buttons[key][shape] = btn
            bx += btn_w + 10


    def _step(self, key, field, direction, label):
        step = _LAYOUT_STEP[field]
        current = _layout[key][field]
        _apply_layout(key, **{field: current + direction * step})
        new_val = _layout[key][field]
        widget = self._value_labels.get(f"{key}_{field}")
        if widget is not None and _widget_exists(widget):
            try:
                bui.textwidget(edit=widget, text=f"{label}: {new_val}")
            except Exception:
                pass

    def _pick_shape(self, key, shape):
        _apply_layout(key, shape=shape)
        for s, btn in self._shape_buttons.get(key, {}).items():
            if _widget_exists(btn):
                try:
                    bw(edit=btn, color=(0.25, 0.55, 0.3) if s == shape else (0.25, 0.25, 0.32))
                except Exception:
                    pass
        self._rebuild_preview(key)

    def _rebuild_preview(self, key):
        old = self._previews.get(key)
        pos = self._preview_pos.get(key)
        if old is None or pos is None or not _widget_exists(old):
            return
        cfg = _layout[key]
        try:
            bui.widget(edit=old, delete=True)
        except Exception:
            return
        try:
            new_preview = bw(
                parent=self._content,
                position=pos,
                size=(44, 44),
                button_type=_shape_button_type(cfg["shape"]),
                label=_LABELS[key],
                text_scale=0.7,
                color=_colors[key]["bg"],
                textcolor=_colors[key]["text"],
                autoselect=True,
                on_activate_call=lambda: None,
            )
            self._previews[key] = new_preview
        except Exception:
            pass

    def _reset_all(self):
        field_labels = {"x": "X", "y": "Y", "size": "Size"}
        for key, default in _DEFAULT_LAYOUT.items():
            _apply_layout(
                key,
                x=default["x"],
                y=default["y"],
                size=default["size"],
                shape=default["shape"],
            )
            for field, flabel in field_labels.items():
                widget = self._value_labels.get(f"{key}_{field}")
                if widget is not None and _widget_exists(widget):
                    try:
                        bui.textwidget(edit=widget, text=f"{flabel}: {default[field]}")
                    except Exception:
                        pass
            for s, btn in self._shape_buttons.get(key, {}).items():
                if _widget_exists(btn):
                    try:
                        bw(edit=btn, color=(0.25, 0.55, 0.3) if s == default["shape"] else (0.25, 0.25, 0.32))
                    except Exception:
                        pass
            self._rebuild_preview(key)

    def _close(self):
        try:
            bui.containerwidget(edit=self._root_widget, transition="out_scale")
        except Exception:
            pass
        global _layout_window
        _layout_window = None


def _open_layout_settings():
    global _layout_window
    try:
        if _layout_window is not None and _widget_exists(_layout_window.root_widget):
            return
        _layout_window = _LayoutSettingsWindow()
    except Exception as e:
        try:
            push(f"PingMod settings error: {e}", color=(1, 0.3, 0.3))
        except Exception:
            pass


_CONFIG_KEY_NOTES_TEXT = "PingMod Notes Text"


def _load_notes_text():
    try:
        val = babase.app.config.get(_CONFIG_KEY_NOTES_TEXT)
        if isinstance(val, str):
            return val
    except Exception:
        pass
    return ""


_notes_text = _load_notes_text()


def _save_notes_text():
    try:
        babase.app.config[_CONFIG_KEY_NOTES_TEXT] = _notes_text
        babase.app.config.commit()
    except Exception as e:
        try:
            push(f"PingMod: Error saving note: {e}", color=(1, 0.3, 0.3))
        except Exception:
            pass


def _read_textwidget(widget, fallback=""):
    if widget is None or not _widget_exists(widget):
        return fallback
    try:
        val = bui.textwidget(query=widget)
        if isinstance(val, str):
            return val
    except Exception:
        pass
    try:
        val = bui.textwidget(edit=widget)
        if isinstance(val, str):
            return val
    except Exception:
        pass
    return fallback


def _wrap_notes_paragraphs(text, width):
    paragraphs = []
    for para in (text or "").split("\n"):
        if para == "":
            paragraphs.append([""])
            continue
        wrapped = textwrap.wrap(
            para, width=width, break_long_words=True, replace_whitespace=False
        )
        paragraphs.append(wrapped if wrapped else [""])
    return paragraphs or [[""]]


_notes_window = None


class _NotesPanelWindow:
    def __init__(self):
        w = NOTES_PANEL_WIDTH
        h = NOTES_PANEL_HEIGHT
        self._width = w
        self._height = h

        try:
            sw, sh = bui.get_virtual_screen_size()
        except Exception:
            sw, sh = w, h
        pos_x = (sw - w) / 2
        pos_y = (sh - h) / 2

        self.root_widget = bui.containerwidget(
            parent=gsw("overlay_stack"),
            position=(pos_x, pos_y),
            size=(w, h),
            transition="in_scale",
            scale=1.0,
            color=_panel_colors["notes"],
        )
        self._root_widget = self.root_widget
        _live_panels["notes"] = self.root_widget

        margin = 10

        bui.textwidget(
            parent=self._root_widget,
            position=(0, h - 32),
            size=(w, 24),
            text="📝 Notebook",
            h_align="center",
            v_align="center",
            scale=1.1,
            color=(1, 1, 1),
        )

        close_btn = bw(
            parent=self._root_widget,
            position=(w - margin - 22, h - 36),
            size=(22, 22),
            button_type="square",
            label="✕",
            text_scale=0.8,
            color=CALC_CLOSE_COLOR,
            textcolor=(1, 1, 1),
            autoselect=True,
            on_activate_call=bui.WeakCall(self._close),
        )

        title_bottom = h - 8 - 24
        bottom_margin = 8
        btn_row_h = 34
        edit_h = 34
        gap = 6
        scroll_bottom = bottom_margin + btn_row_h + gap + edit_h + gap
        scroll_top = title_bottom - 4
        scroll_h = max(scroll_top - scroll_bottom, 40)
        scroll_w = w - 2 * margin

        self._scroll_w = scroll_w
        self._scroll_h = scroll_h
        self._line_h = 26
        try:
            self._scroll = bui.scrollwidget(
                parent=self._root_widget,
                position=(margin, scroll_bottom),
                size=(scroll_w, scroll_h),
                highlight=False,
                capture_arrows=True,
            )
            self._content = bui.containerwidget(
                parent=self._scroll,
                size=(scroll_w, scroll_h),
                background=False,
            )
        except Exception:
            self._scroll = None
            self._content = None

        edit_bottom = bottom_margin + btn_row_h + gap
        self._text_field = bui.textwidget(
            parent=self._root_widget,
            position=(margin, edit_bottom),
            size=(scroll_w, edit_h),
            text=_notes_text,
            editable=True,
            max_chars=NOTES_MAX_CHARS,
            maxwidth=scroll_w - 10,
            v_align="center",
            h_align="left",
            scale=0.8,
            color=(1, 1, 0.9),
            description="Edit note",
        )

        half_w = (scroll_w - 10) / 2
        bw(
            parent=self._root_widget,
            position=(margin, bottom_margin),
            size=(half_w, btn_row_h),
            button_type="square",
            label="Save",
            text_scale=0.85,
            color=(0.2, 0.45, 0.25),
            textcolor=(1, 1, 1),
            autoselect=True,
            on_activate_call=bui.WeakCall(self._save),
        )
        bw(
            parent=self._root_widget,
            position=(margin + half_w + 10, bottom_margin),
            size=(half_w, btn_row_h),
            button_type="square",
            label="Send to Chat",
            text_scale=0.8,
            color=(0.25, 0.35, 0.55),
            textcolor=(1, 1, 1),
            autoselect=True,
            on_activate_call=bui.WeakCall(self._send),
        )

        bui.containerwidget(
            edit=self._root_widget,
            cancel_button=close_btn,
            on_outside_click_call=bui.WeakCall(self._close),
        )

        self._last_preview_text = None
        self._refresh_preview(_notes_text)
        self._auto_tick()

    def _auto_tick(self):
        if not _widget_exists(self._root_widget):
            return
        try:
            current = _read_textwidget(self._text_field, _notes_text)
            self._refresh_preview(current)
        except Exception:
            pass
        teck(1.0, bui.WeakCall(self._auto_tick))

    def _refresh_preview(self, text):
        if self._content is None or not _widget_exists(self._content):
            return
        if text == self._last_preview_text:
            return
        self._last_preview_text = text

        try:
            for child in self._content.get_children():
                child.delete()
        except Exception:
            pass

        paragraphs = _wrap_notes_paragraphs(text, NOTES_WRAP_CHARS)
        rows = []
        for i, para_lines in enumerate(paragraphs):
            if i > 0:
                rows.append(None)
            rows.extend(para_lines)

        line_h = self._line_h
        scroll_h = self._scroll_h
        total_h = len(rows) * line_h
        content_h = max(scroll_h, total_h + 8)

        try:
            bui.containerwidget(edit=self._content, size=(self._scroll_w, content_h))
        except Exception:
            pass

        if total_h <= scroll_h:
            top = (content_h + total_h) / 2 - line_h
        else:
            top = content_h - line_h - 4

        for row in rows:
            if row is not None:
                bui.textwidget(
                    parent=self._content,
                    position=(2, top),
                    size=(self._scroll_w - 4, line_h),
                    text=row if row else " ",
                    h_align="center",
                    v_align="center",
                    scale=0.85,
                    color=(1, 1, 0.9),
                )
            top -= line_h

    def _save(self):
        global _notes_text
        _notes_text = _read_textwidget(self._text_field, _notes_text)
        _save_notes_text()
        self._refresh_preview(_notes_text)

    def _send(self):
        self._save()
        text = _notes_text.strip()
        if not text:
            return
        try:
            bs.chatmessage(f"📝 {text}")
        except Exception as e:
            try:
                push(f"PingMod error: {e}", color=(1, 0.3, 0.3))
            except Exception:
                pass

    def _close(self):
        self._save()
        try:
            bui.containerwidget(edit=self._root_widget, transition="out_scale")
        except Exception:
            pass
        global _notes_window
        _notes_window = None
        _live_panels["notes"] = None


def _open_notes_panel():
    global _notes_window
    try:
        if _notes_window is not None and _widget_exists(_notes_window.root_widget):
            return
        _notes_window = _NotesPanelWindow()
    except Exception as e:
        try:
            push(f"PingMod error: {e}", color=(1, 0.3, 0.3))
        except Exception:
            pass


def _on_notes_press():
    _open_notes_panel()


_DEFAULT_ICON_ENABLED = {"ping": True, "ip": True, "clock": True, "calc": True, "notes": True, "party": True}
_CONFIG_KEY_ICON_ENABLED = "PingMod Icon Enabled"


def _load_icon_enabled():
    saved = {}
    try:
        raw = babase.app.config.get(_CONFIG_KEY_ICON_ENABLED)
        if isinstance(raw, dict):
            saved = raw
    except Exception:
        saved = {}
    enabled = {}
    for key, default in _DEFAULT_ICON_ENABLED.items():
        val = saved.get(key, default)
        enabled[key] = bool(val) if isinstance(val, bool) else default
    return enabled


_icon_enabled = _load_icon_enabled()


def _save_icon_enabled():
    try:
        babase.app.config[_CONFIG_KEY_ICON_ENABLED] = dict(_icon_enabled)
        babase.app.config.commit()
    except Exception as e:
        try:
            push(f"PingMod: Error saving icon states: {e}", color=(1, 0.3, 0.3))
        except Exception:
            pass


def _set_icon_enabled(key, enabled):
    _icon_enabled[key] = enabled
    _save_icon_enabled()
    if enabled:
        widget = _live_buttons.get(key)
        if widget is None or not _widget_exists(widget):
            _create_icon_button(key)
    else:
        widget = _live_buttons.get(key)
        if widget is not None and _widget_exists(widget):
            try:
                bui.widget(edit=widget, delete=True)
            except Exception:
                pass
        _live_buttons[key] = None


ICON_TOGGLE_PANEL_WIDTH = SETTINGS_PANEL_WIDTH
ICON_TOGGLE_PANEL_COLOR = SETTINGS_PANEL_COLOR

_icon_toggle_window = None


class _IconToggleSettingsWindow:
    def __init__(self):
        w = ICON_TOGGLE_PANEL_WIDTH
        h = max(300, 130 + len(_SECTION_ORDER) * 52)
        self._width = w
        self._height = h
        self._row_buttons = {}

        try:
            sw, sh = bui.get_virtual_screen_size()
        except Exception:
            sw, sh = w, h
        pos_x = (sw - w) / 2
        pos_y = (sh - h) / 2

        self.root_widget = bui.containerwidget(
            parent=gsw("overlay_stack"),
            position=(pos_x, pos_y),
            size=(w, h),
            transition="in_scale",
            scale=1.0,
            color=ICON_TOGGLE_PANEL_COLOR,
        )
        self._root_widget = self.root_widget

        margin = 20

        bui.textwidget(
            parent=self._root_widget,
            position=(0, h - 34),
            size=(w, 24),
            text="🧩 Settings 4 - Add/Remove Icons",
            h_align="center",
            v_align="center",
            scale=1.1,
            color=(1, 1, 1),
        )

        close_btn = bw(
            parent=self._root_widget,
            position=(w - margin - 22, h - 38),
            size=(22, 22),
            button_type="square",
            label="✕",
            text_scale=0.8,
            color=CALC_CLOSE_COLOR,
            textcolor=(1, 1, 1),
            autoselect=True,
            on_activate_call=bui.WeakCall(self._close),
        )

        row_top = h - 80
        row_h = 52
        for key in _SECTION_ORDER:
            self._build_row(key, margin, row_top, w - 2 * margin)
            row_top -= row_h

        bui.containerwidget(
            edit=self._root_widget,
            cancel_button=close_btn,
            on_outside_click_call=bui.WeakCall(self._close),
        )

    def _row_label(self, key):
        state = "ON ✅" if _icon_enabled.get(key, True) else "OFF ❌"
        return f"{_LABELS[key]}  —  {state}"

    def _row_color(self, key):
        return (0.2, 0.5, 0.25) if _icon_enabled.get(key, True) else (0.5, 0.2, 0.2)

    def _build_row(self, key, x, top, width):
        btn = bw(
            parent=self._root_widget,
            position=(x, top - 40),
            size=(width, 40),
            button_type="square",
            label=self._row_label(key),
            text_scale=0.9,
            color=self._row_color(key),
            textcolor=(1, 1, 1),
            autoselect=True,
            on_activate_call=bui.WeakCall(self._toggle, key),
        )
        self._row_buttons[key] = btn

    def _toggle(self, key):
        _set_icon_enabled(key, not _icon_enabled.get(key, True))
        btn = self._row_buttons.get(key)
        if btn is not None and _widget_exists(btn):
            try:
                bw(edit=btn, label=self._row_label(key), color=self._row_color(key))
            except Exception:
                pass

    def _close(self):
        try:
            bui.containerwidget(edit=self._root_widget, transition="out_scale")
        except Exception:
            pass
        global _icon_toggle_window
        _icon_toggle_window = None


def _open_icon_toggle_settings():
    global _icon_toggle_window
    try:
        if _icon_toggle_window is not None and _widget_exists(_icon_toggle_window.root_widget):
            return
        _icon_toggle_window = _IconToggleSettingsWindow()
    except Exception as e:
        try:
            push(f"PingMod settings error: {e}", color=(1, 0.3, 0.3))
        except Exception:
            pass


ADS_INTERVAL = 180.0
ADS_CHECK_INTERVAL = 5.0

_CONFIG_KEY_ADS = "PingMod Ads Enabled"

_ADS_MESSAGES = [
    "🔥 Using PoyaMod! Get it and more BombSquad mods on Telegram: @AzraelMods",
    "⚡ PoyaMod - a handy toolkit for your party window. Download: @AzraelMods",
    "📢 Best mods for BombSquad? Join our Telegram channel: @AzraelMods",
    "☄️ Want this mod? Find it on our Telegram channel: @AzraelMods",
]

_ads_state = {"next_time": 0.0, "last_index": -1, "last_sent": 0.0, "chain": 0}


def _load_ads_enabled():
    try:
        val = babase.app.config.get(_CONFIG_KEY_ADS)
        if isinstance(val, bool):
            return val
    except Exception:
        pass
    return False


_ads_enabled = _load_ads_enabled()


def _save_ads_enabled():
    try:
        babase.app.config[_CONFIG_KEY_ADS] = _ads_enabled
        babase.app.config.commit()
    except Exception as e:
        try:
            push(f"PingMod: Error saving ads setting: {e}", color=(1, 0.3, 0.3))
        except Exception:
            pass


def _set_ads_enabled(enabled):
    global _ads_enabled
    _ads_enabled = bool(enabled)
    _ads_state["next_time"] = 0.0
    _save_ads_enabled()


def _ads_connected():
    if _server_ip != "127.0.0.1":
        return True
    for fn_name in ("get_connection_to_host_info_2", "get_connection_to_host_info"):
        fn = getattr(bs, fn_name, None)
        if fn is None:
            continue
        try:
            info = fn()
        except Exception:
            continue
        if info:
            return True
    return False


def _ads_shared_last_sent():
    try:
        return float(getattr(bs, "_poyamod_ads_last_sent", 0.0))
    except Exception:
        return 0.0


def _ads_mark_sent(now):
    _ads_state["last_sent"] = now
    try:
        setattr(bs, "_poyamod_ads_last_sent", now)
    except Exception:
        pass


def _ads_schedule_next():
    _ads_state["next_time"] = time.time() + ADS_INTERVAL


def _ads_pick_message():
    count = len(_ADS_MESSAGES)
    index = random.randrange(count)
    if count > 1 and index == _ads_state["last_index"]:
        index = (index + 1) % count
    _ads_state["last_index"] = index
    return _ADS_MESSAGES[index]


def _ads_send():
    now = time.time()
    last = max(_ads_state["last_sent"], _ads_shared_last_sent())
    if 0.0 <= now - last < ADS_INTERVAL:
        return None
    message = _ads_pick_message()
    try:
        bs.chatmessage(message)
    except Exception as e:
        try:
            push(f"PingMod ads error: {e}", color=(1, 0.3, 0.3))
        except Exception:
            pass
        return None
    _ads_mark_sent(now)
    return message


def _ads_status_text():
    if not _ads_enabled:
        return "Status: OFF"
    if not _ads_connected():
        return "Status: waiting for a server connection"
    next_time = _ads_state["next_time"]
    if next_time <= 0.0:
        return "Status: starting..."
    remaining = max(0, int(next_time - time.time()))
    return f"Status: next ad in {remaining // 60}:{remaining % 60:02d}"


def _ads_start():
    _ads_state["chain"] += 1
    _ads_tick(_ads_state["chain"])


def _ads_tick(chain_id):
    if chain_id != _ads_state["chain"]:
        return
    try:
        if _ads_enabled and _ads_connected():
            if _ads_state["next_time"] <= 0.0:
                _ads_schedule_next()
            elif time.time() >= _ads_state["next_time"]:
                _ads_send()
                _ads_schedule_next()
        else:
            _ads_state["next_time"] = 0.0
    except Exception as e:
        try:
            push(f"PingMod ads error: {e}", color=(1, 0.3, 0.3))
        except Exception:
            pass
    teck(ADS_CHECK_INTERVAL, lambda c=chain_id: _ads_tick(c))


ADS_PANEL_WIDTH = 420
ADS_PANEL_HEIGHT = 300
ADS_PANEL_COLOR = SETTINGS_PANEL_COLOR

_ads_window = None


class _AdsSettingsWindow:
    def __init__(self):
        w = ADS_PANEL_WIDTH
        h = ADS_PANEL_HEIGHT
        self._width = w
        self._height = h

        try:
            sw, sh = bui.get_virtual_screen_size()
        except Exception:
            sw, sh = w, h
        pos_x = (sw - w) / 2
        pos_y = (sh - h) / 2

        self.root_widget = bui.containerwidget(
            parent=gsw("overlay_stack"),
            position=(pos_x, pos_y),
            size=(w, h),
            transition="in_scale",
            scale=1.0,
            color=ADS_PANEL_COLOR,
        )
        self._root_widget = self.root_widget

        margin = 20

        bui.textwidget(
            parent=self._root_widget,
            position=(0, h - 34),
            size=(w, 24),
            text="📣 Settings 5 - Ads",
            h_align="center",
            v_align="center",
            scale=1.1,
            color=(1, 1, 1),
        )

        close_btn = bw(
            parent=self._root_widget,
            position=(w - margin - 22, h - 38),
            size=(22, 22),
            button_type="square",
            label="✕",
            text_scale=0.8,
            color=CALC_CLOSE_COLOR,
            textcolor=(1, 1, 1),
            autoselect=True,
            on_activate_call=bui.WeakCall(self._close),
        )

        info_lines = [
            ("Help promote PoyaMod!", 0.95, (1, 1, 0.6)),
            ("When ON, a short message about @AzraelMods is", 0.75, (0.85, 0.85, 0.9)),
            ("sent to the party chat every 3 minutes while", 0.75, (0.85, 0.85, 0.9)),
            ("you are connected to a server.", 0.75, (0.85, 0.85, 0.9)),
            ("When OFF, nothing is sent.", 0.75, (0.85, 0.85, 0.9)),
        ]
        line_top = h - 66
        for text, scale, color in info_lines:
            bui.textwidget(
                parent=self._root_widget,
                position=(margin, line_top - 20),
                size=(w - 2 * margin, 20),
                text=text,
                h_align="center",
                v_align="center",
                scale=scale,
                color=color,
                maxwidth=w - 2 * margin,
            )
            line_top -= 26

        self._status_text = bui.textwidget(
            parent=self._root_widget,
            position=(margin, line_top - 24),
            size=(w - 2 * margin, 20),
            text=_ads_status_text(),
            h_align="center",
            v_align="center",
            scale=0.8,
            color=(0.6, 1, 0.8),
            maxwidth=w - 2 * margin,
        )

        self._toggle_btn = bw(
            parent=self._root_widget,
            position=(margin, 24),
            size=(w - 2 * margin, 44),
            button_type="square",
            label=self._toggle_label(),
            text_scale=0.95,
            color=self._toggle_color(),
            textcolor=(1, 1, 1),
            autoselect=True,
            on_activate_call=bui.WeakCall(self._toggle),
        )

        bui.containerwidget(
            edit=self._root_widget,
            cancel_button=close_btn,
            on_outside_click_call=bui.WeakCall(self._close),
        )

        self._tick()

    def _toggle_label(self):
        return "Help Promote: ON ✅" if _ads_enabled else "Help Promote: OFF ❌"

    def _toggle_color(self):
        return (0.2, 0.5, 0.25) if _ads_enabled else (0.5, 0.2, 0.2)

    def _toggle(self):
        _set_ads_enabled(not _ads_enabled)
        if _widget_exists(self._toggle_btn):
            try:
                bw(edit=self._toggle_btn, label=self._toggle_label(), color=self._toggle_color())
            except Exception:
                pass

    def _tick(self):
        if not _widget_exists(self._root_widget):
            return
        try:
            bui.textwidget(edit=self._status_text, text=_ads_status_text())
        except Exception:
            pass
        teck(1.0, bui.WeakCall(self._tick))

    def _close(self):
        try:
            bui.containerwidget(edit=self._root_widget, transition="out_scale")
        except Exception:
            pass
        global _ads_window
        _ads_window = None


def _open_ads_settings():
    global _ads_window
    try:
        if _ads_window is not None and _widget_exists(_ads_window.root_widget):
            return
        _ads_window = _AdsSettingsWindow()
    except Exception as e:
        try:
            push(f"PingMod settings error: {e}", color=(1, 0.3, 0.3))
        except Exception:
            pass


_SETTINGS_MODULES = [
    {"title": "Icon Colors", "icon": "🎨", "open": _open_color_settings},
    {"title": "Panel Colors", "icon": "🖌️", "open": _open_panel_color_settings},
    {"title": "Icon Position/Size/Shape", "icon": "📐", "open": _open_layout_settings},
    {"title": "Add/Remove Icons", "icon": "🧩", "open": _open_icon_toggle_settings},
    {"title": "Ads", "icon": "📣", "open": _open_ads_settings},
]

HUB_PANEL_WIDTH = 420
HUB_PANEL_HEIGHT = 300
HUB_PANEL_COLOR = (0.12, 0.12, 0.17)

_hub_window = None


class _SettingsHubWindow:
    def __init__(self):
        w = HUB_PANEL_WIDTH
        h = max(HUB_PANEL_HEIGHT, 110 + len(_SETTINGS_MODULES) * 56)
        self._width = w
        self._height = h

        try:
            sw, sh = bui.get_virtual_screen_size()
        except Exception:
            sw, sh = w, h
        pos_x = (sw - w) / 2
        pos_y = (sh - h) / 2

        self.root_widget = bui.containerwidget(
            parent=gsw("overlay_stack"),
            position=(pos_x, pos_y),
            size=(w, h),
            transition="in_scale",
            scale=1.0,
            color=HUB_PANEL_COLOR,
        )
        self._root_widget = self.root_widget

        bui.textwidget(
            parent=self._root_widget,
            position=(0, h - 34),
            size=(w, 24),
            text="⚙️ PingMod Settings",
            h_align="center",
            v_align="center",
            scale=1.1,
            color=(1, 1, 1),
        )

        close_btn = bw(
            parent=self._root_widget,
            position=(w - 16 - 26, h - 40),
            size=(26, 26),
            button_type="square",
            label="✕",
            text_scale=0.8,
            color=CALC_CLOSE_COLOR,
            textcolor=(1, 1, 1),
            autoselect=True,
            on_activate_call=bui.WeakCall(self._close),
        )

        bui.containerwidget(
            edit=self._root_widget,
            cancel_button=close_btn,
            on_outside_click_call=bui.WeakCall(self._close),
        )

        margin = 20
        row_top = h - 74
        row_h = 56
        for i, module in enumerate(_SETTINGS_MODULES, start=1):
            self._build_row(i, module, margin, row_top)
            row_top -= row_h

    def _build_row(self, number, module, margin, top):
        icon = module.get("icon", "🔧")
        label = f"{number}. {icon}  {module['title']}"
        bw(
            parent=self._root_widget,
            position=(margin, top - 40),
            size=(self._width - 2 * margin, 40),
            button_type="square",
            label=label,
            text_scale=0.95,
            color=(0.2, 0.2, 0.28),
            textcolor=(1, 1, 1),
            autoselect=True,
            on_activate_call=bui.WeakCall(self._open_module, module),
        )

    def _open_module(self, module):
        self._close()
        module["open"]()

    def _close(self):
        try:
            bui.containerwidget(edit=self._root_widget, transition="out_scale")
        except Exception:
            pass
        global _hub_window
        _hub_window = None


def _open_settings_hub():
    global _hub_window
    try:
        if _hub_window is not None and _widget_exists(_hub_window.root_widget):
            return
        _hub_window = _SettingsHubWindow()
    except Exception as e:
        try:
            push(f"PingMod settings error: {e}", color=(1, 0.3, 0.3))
        except Exception:
            pass


PARTY_TINT_INTERVAL = 3.0

_CONFIG_KEY_PARTY_TINT = "PingMod Party Tint Enabled"

_party_tint_state = {"chain": 0}


def _load_bool_setting(key, default=False):
    try:
        val = babase.app.config.get(key)
        if isinstance(val, bool):
            return val
    except Exception:
        pass
    return default


def _save_bool_setting(key, value):
    try:
        babase.app.config[key] = bool(value)
        babase.app.config.commit()
    except Exception as e:
        try:
            push(f"PingMod: Error saving setting: {e}", color=(1, 0.3, 0.3))
        except Exception:
            pass


_party_tint_enabled = _load_bool_setting(_CONFIG_KEY_PARTY_TINT, False)


def _set_party_tint_enabled(enabled):
    global _party_tint_enabled
    _party_tint_enabled = bool(enabled)
    _save_bool_setting(_CONFIG_KEY_PARTY_TINT, _party_tint_enabled)
    if _party_tint_enabled:
        _party_tint_state["chain"] += 1
        _party_tint_tick(_party_tint_state["chain"])


# A curated set of visually distinct, saturated tints (each channel 0-9).
# Random-per-channel picks tended to cluster on muddy/grayish colors and
# could repeat a similar shade back-to-back. Instead we shuffle this whole
# palette and hand tints out one at a time, so every color in a cycle is
# used exactly once and neighboring colors are guaranteed to look distinct.
_PARTY_TINT_PALETTE = [
    (9, 0, 0),  # red
    (0, 9, 0),  # green
    (0, 0, 9),  # blue
    (9, 9, 0),  # yellow
    (0, 9, 9),  # cyan
    (9, 0, 9),  # magenta
    (9, 5, 0),  # orange
    (5, 0, 9),  # purple
    (0, 9, 5),  # mint
    (9, 0, 5),  # pink/rose
    (5, 9, 0),  # lime
    (0, 5, 9),  # sky blue
    (9, 9, 9),  # white
    (5, 9, 9),  # light cyan
    (9, 9, 5),  # pale yellow
    (9, 5, 9),  # light magenta
]

_party_tint_queue = []
_party_tint_last = None


def _party_tint_pick():
    # server command example: /T 6 9 1
    global _party_tint_queue, _party_tint_last

    if not _party_tint_queue:
        pool = list(_PARTY_TINT_PALETTE)
        random.shuffle(pool)
        # Don't let the first tint of a new cycle match the last tint
        # sent at the end of the previous cycle.
        if _party_tint_last is not None and pool[0] == _party_tint_last and len(pool) > 1:
            swap_at = random.randint(1, len(pool) - 1)
            pool[0], pool[swap_at] = pool[swap_at], pool[0]
        _party_tint_queue = pool

    r, g, b = _party_tint_queue.pop(0)
    _party_tint_last = (r, g, b)
    return f"/T {r} {g} {b}"


def _party_tint_tick(chain_id):
    if chain_id != _party_tint_state["chain"] or not _party_tint_enabled:
        return
    try:
        if _ads_connected():
            bs.chatmessage(_party_tint_pick())
    except Exception as e:
        try:
            push(f"PingMod tint error: {e}", color=(1, 0.3, 0.3))
        except Exception:
            pass
    teck(PARTY_TINT_INTERVAL, lambda c=chain_id: _party_tint_tick(c))


PARTY_PANEL_COLOR = SETTINGS_PANEL_COLOR

_party_window = None


class _PartyPanelWindow:
    def __init__(self):
        w = PARTY_PANEL_WIDTH
        h = PARTY_PANEL_HEIGHT
        self._width = w
        self._height = h

        try:
            sw, sh = bui.get_virtual_screen_size()
        except Exception:
            sw, sh = w, h
        pos_x = (sw - w) / 2
        pos_y = (sh - h) / 2

        self.root_widget = bui.containerwidget(
            parent=gsw("overlay_stack"),
            position=(pos_x, pos_y),
            size=(w, h),
            transition="in_scale",
            scale=1.0,
            color=PARTY_PANEL_COLOR,
        )
        self._root_widget = self.root_widget

        margin = 20

        bui.textwidget(
            parent=self._root_widget,
            position=(0, h - 34),
            size=(w, 24),
            text="🎉 Party",
            h_align="center",
            v_align="center",
            scale=1.1,
            color=(1, 1, 1),
        )

        close_btn = bw(
            parent=self._root_widget,
            position=(w - margin - 22, h - 38),
            size=(22, 22),
            button_type="square",
            label="✕",
            text_scale=0.8,
            color=CALC_CLOSE_COLOR,
            textcolor=(1, 1, 1),
            autoselect=True,
            on_activate_call=bui.WeakCall(self._close),
        )

        bui.textwidget(
            parent=self._root_widget,
            position=(margin, 90),
            size=(w - 2 * margin, 20),
            text="Color/Tint: sends a random /T tint every 3s",
            h_align="center",
            v_align="center",
            scale=0.72,
            color=(0.85, 0.85, 0.9),
            maxwidth=w - 2 * margin,
        )

        self._tint_btn = bw(
            parent=self._root_widget,
            position=(margin, 35),
            size=(w - 2 * margin, 44),
            button_type="square",
            label=self._tint_label(),
            text_scale=0.9,
            color=self._tint_color(),
            textcolor=(1, 1, 1),
            autoselect=True,
            on_activate_call=bui.WeakCall(self._toggle_tint),
        )

        bui.containerwidget(
            edit=self._root_widget,
            cancel_button=close_btn,
            on_outside_click_call=bui.WeakCall(self._close),
        )

    def _tint_label(self):
        return "Color/Tint: ON ✅" if _party_tint_enabled else "Color/Tint: OFF ❌"

    def _tint_color(self):
        return (0.2, 0.5, 0.25) if _party_tint_enabled else (0.5, 0.2, 0.2)

    def _toggle_tint(self):
        _set_party_tint_enabled(not _party_tint_enabled)
        if _widget_exists(self._tint_btn):
            try:
                bw(edit=self._tint_btn, label=self._tint_label(), color=self._tint_color())
            except Exception:
                pass

    def _close(self):
        try:
            bui.containerwidget(edit=self._root_widget, transition="out_scale")
        except Exception:
            pass
        global _party_window
        _party_window = None


def _open_party_panel():
    global _party_window
    try:
        if _party_window is not None and _widget_exists(_party_window.root_widget):
            return
        _party_window = _PartyPanelWindow()
    except Exception as e:
        try:
            push(f"PingMod party panel error: {e}", color=(1, 0.3, 0.3))
        except Exception:
            pass


def _on_party_press():
    _open_party_panel()


_BUTTON_CALLBACKS = {
    "ping": _on_ping_press,
    "ip": _on_ip_press,
    "clock": _on_clock_press,
    "calc": lambda: _on_calc_press(_get_live_party_window()) if _get_live_party_window() is not None else None,
    "notes": _on_notes_press,
    "party": _on_party_press,
}

def _party_tint_start():
    if _party_tint_enabled:
        _party_tint_state["chain"] += 1
        _party_tint_tick(_party_tint_state["chain"])

_orig_party_init = party.PartyWindow.__init__


def _patched_party_init(self, *args, **kwargs):
    _orig_party_init(self, *args, **kwargs)

    global _live_party_window_ref, _live_party_root, _live_party_dims
    _live_party_window_ref = weakref.ref(self)
    _live_party_root = self._root_widget
    _live_party_dims = (self._width, self._height)

    for key in _SECTION_ORDER:
        if not _icon_enabled.get(key, True):
            continue
        try:
            if _create_icon_button(key) is None:
                raise RuntimeError("couldn't create button widget")
        except Exception as e:
            try:
                push(f"PingMod error: {e}", color=(1, 0.3, 0.3))
            except Exception:
                pass
            print(f"PingMod: couldn't add {key} button: {e}")


party.PartyWindow.__init__ = _patched_party_init


def _announce_loaded():
    try:
        push("PingMod loaded ✅ (Party > Ping/IP/Time/Calc/Notes)", color=(0.3, 1, 0.3))
    except Exception:
        pass


# ba_meta require api 9


# ba_meta export plugin
class PingMod(Plugin):

    def on_app_running(self) -> None:
        teck(1.5, _announce_loaded)
        teck(2.0, _ping_alert_tick)
        teck(3.0, _ads_start)
        teck(3.0, _party_tint_start)

    def has_settings_ui(self) -> bool:
        return True

    def show_settings_ui(self, source_widget) -> None:
        _open_settings_hub()

    def __del__(self):
        try:
            _ping_thread.stop()
        except Exception:
            pass
