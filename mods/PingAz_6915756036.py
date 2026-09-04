# Released under the MIT License.
#
# Ping Meter - BombSquad / Ballistica plugin (API 9)
# ---------------------------------------------------
# Shows a small floating button in the top-right corner of the screen
# (in the toolbar overlay, so it's visible in the main menu AND in-game).
# The button updates every second with your current ping (ms) and is
# color coded:
#   green  -> 0   to 100 ms
#   yellow -> 100 to 300 ms
#   red    -> 300+ ms
# Tapping the button sends "My Ping : XX.XX ms" to the in-game chat.
#
# Install: put this file in your mods folder
# (Settings -> Advanced -> Show Mods Folder) and restart the game.

# ba_meta require api 9

from __future__ import annotations

import logging
from typing import Any

import babase
import bascenev1 as bs
import bauiv1 as bui


class _PingMeter:
    """Owns the on-screen ping button and keeps it updated."""

    def __init__(self) -> None:
        self._container: bui.Widget | None = None
        self._button: bui.Widget | None = None
        self._text: bui.Widget | None = None
        self._update_timer: bui.AppTimer | None = None
        self._last_ping: float | None = None
        self._build()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build(self) -> None:
        self.destroy()

        try:
            overlay = bui.get_special_widget('overlay_stack')
        except Exception:
            logging.exception('PingMeter: could not get overlay_stack.')
            return

        try:
            screen_w, screen_h = babase.get_virtual_screen_size()
        except Exception:
            screen_w, screen_h = 1280.0, 720.0

        btn_w = 62.0
        btn_h = 36.0
        # Sit just under the top-right toolbar buttons (party/currency/etc).
        btn_x = screen_w - btn_w - 10.0
        btn_y = screen_h - btn_h - 90.0

        self._container = bui.containerwidget(
            parent=overlay,
            size=(screen_w, screen_h),
            transition='in_right',
            background=False,
            claims_left_right=False,
            claims_tab=False,
        )

        self._button = bui.buttonwidget(
            parent=self._container,
            position=(btn_x, btn_y),
            size=(btn_w, btn_h),
            label='',
            color=(0.4, 0.4, 0.4),
            button_type='square',
            autoselect=True,
            repeat=False,
            on_activate_call=babase.WeakCall(self._send_to_chat),
        )

        self._text = bui.textwidget(
            parent=self._container,
            position=(btn_x + btn_w * 0.5, btn_y + btn_h * 0.5),
            size=(0, 0),
            h_align='center',
            v_align='center',
            scale=0.65,
            color=(1, 1, 1),
            shadow=1.0,
            flatness=1.0,
            text='--',
        )

        self._update_timer = bui.AppTimer(
            1.0, babase.WeakCall(self._update), repeat=True
        )
        self._update()

    def destroy(self) -> None:
        self._update_timer = None
        if self._container is not None:
            try:
                self._container.delete()
            except Exception:
                pass
        self._container = None
        self._button = None
        self._text = None

    # ------------------------------------------------------------------
    # Ping lookup
    # ------------------------------------------------------------------
    def _get_ping(self) -> float | None:
        """Best-effort lookup of our current ping (RTT) in milliseconds.

        Uses bascenev1.get_client_ping() (added in a recent engine build)
        with a few different calling conventions, since it's designed
        primarily for a host to query a connected client's ping. We try
        a no-arg self-ping call first, then fall back to scanning the
        party roster for a usable client id.
        """
        fn = getattr(bs, 'get_client_ping', None)
        if fn is None:
            return None

        # 1) Try calling with no arguments (some builds treat this as
        #    "my own connection to the host").
        try:
            val = fn()
            if isinstance(val, (int, float)):
                return float(val)
        except TypeError:
            pass
        except Exception:
            logging.exception('PingMeter: error calling get_client_ping().')

        # 2) Try client id -1 (commonly used to mean "the host" or "self").
        for cid in (-1, 0):
            try:
                val = fn(cid)
                if isinstance(val, (int, float)):
                    return float(val)
            except Exception:
                pass

        # 3) Scan the party roster for any client id and use the first
        #    one that returns a usable ping value.
        try:
            roster: Any = bs.get_game_roster()
        except Exception:
            roster = None

        if roster:
            for entry in roster:
                cid = entry.get('client_id')
                if cid is None:
                    continue
                try:
                    val = fn(cid)
                except Exception:
                    continue
                if isinstance(val, (int, float)):
                    return float(val)

        return None

    # ------------------------------------------------------------------
    # Periodic update
    # ------------------------------------------------------------------
    def _update(self) -> None:
        if self._text is None or self._button is None:
            return

        ping = self._get_ping()
        self._last_ping = ping

        if ping is None:
            bui.textwidget(edit=self._text, text='--')
            bui.buttonwidget(edit=self._button, color=(0.4, 0.4, 0.4))
            return

        if ping < 100.0:
            color = (0.15, 0.75, 0.15)  # green
        elif ping < 300.0:
            color = (0.85, 0.75, 0.10)  # yellow
        else:
            color = (0.85, 0.15, 0.15)  # red

        bui.textwidget(edit=self._text, text=f'{ping:.0f}')
        bui.buttonwidget(edit=self._button, color=color)

    # ------------------------------------------------------------------
    # Tap action
    # ------------------------------------------------------------------
    def _send_to_chat(self) -> None:
        if self._last_ping is None:
            babase.screenmessage('Ping not available yet.', color=(1, 0.6, 0))
            return

        msg = f'My Ping : {self._last_ping:.2f} ms'
        try:
            bs.chatmessage(msg)
        except Exception:
            # Not in a session (e.g. main menu) - just show it locally.
            babase.screenmessage(msg, color=(0.6, 1.0, 0.6))


_meter: _PingMeter | None = None
_retry_timer: babase.AppTimer | None = None


def _try_attach() -> None:
    """Try to build the meter; keep retrying until the overlay exists.

    On current builds the toolbar overlay only exists while
    ClassicAppMode is the active app mode, and it may not be active yet
    (or ever, e.g. on non-classic app modes) at the moment
    on_app_running fires. A single fixed delay is a race condition -
    if the UI isn't ready yet at that exact moment, get_special_widget()
    raises and the meter silently never appears. Polling every second
    and stopping once it succeeds is more reliable.
    """
    global _meter, _retry_timer

    if _meter is not None:
        _retry_timer = None
        return

    try:
        bui.get_special_widget('overlay_stack')
    except Exception:
        # Not ready yet (e.g. ClassicAppMode inactive) - try again
        # on the next tick instead of giving up.
        return

    _meter = _PingMeter()
    # Dropping our reference to the retry timer stops it from firing
    # again.
    _retry_timer = None


def _teardown_meter() -> None:
    global _meter, _retry_timer
    _retry_timer = None
    if _meter is not None:
        _meter.destroy()
        _meter = None


# ba_meta export babase.Plugin
class PingMeterPlugin(babase.Plugin):
    """Plugin entry point."""

    def on_app_running(self) -> None:
        global _retry_timer
        # Poll once a second until the toolbar overlay is actually
        # available, instead of assuming it exists after a fixed delay.
        _retry_timer = babase.AppTimer(1.0, _try_attach, repeat=True)

    def on_app_shutdown(self) -> None:
        _teardown_meter()
