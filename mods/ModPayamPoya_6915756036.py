# ba_meta require api 9
from __future__ import annotations

import copy
import re
from typing import TYPE_CHECKING, cast

import babase
import bascenev1 as bs
import bauiv1 as bui

if TYPE_CHECKING:
    from typing import Any

CONFIG_KEY = 'Smart Chat Splitter'

DEFAULT_SETTINGS: dict[str, Any] = {
    'enabled': True,
    'max_bytes': 90,
    'delay_seconds': 0.45,
    'add_numbering': True,
    'word_boundary': True,
}

MIN_MAX_BYTES = 32
MAX_MAX_BYTES = 220
BYTES_STEP = 4

MIN_DELAY = 0.10
MAX_DELAY = 2.00
DELAY_STEP = 0.05

_CHANNEL_PREFIX_RE = re.compile(r'^(A|F\d{1,2})(\s+)', re.IGNORECASE)


def get_settings() -> dict[str, Any]:
    cfg = babase.app.config
    stored = cfg.get(CONFIG_KEY)
    settings = copy.deepcopy(DEFAULT_SETTINGS)
    if isinstance(stored, dict):
        for key in DEFAULT_SETTINGS:
            if key in stored:
                settings[key] = stored[key]
    return settings


def save_settings(settings: dict[str, Any]) -> None:
    cfg = babase.app.config
    cfg[CONFIG_KEY] = settings
    cfg.commit()


def _utf8_len(text: str) -> int:
    return len(text.encode('utf-8'))


def _extract_channel_prefix(text: str) -> tuple[str | None, str]:
    match = _CHANNEL_PREFIX_RE.match(text)
    if not match:
        return None, text
    prefix = match.group(1)
    rest = text[match.end():]
    return prefix, rest


def _max_prefix_within_bytes(text: str, max_bytes: int) -> int:
    if not text:
        return 0
    lo, hi, best = 0, len(text), 0
    while lo <= hi:
        mid = (lo + hi) // 2
        if _utf8_len(text[:mid]) <= max_bytes:
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return max(best, 1)


def split_message(
    text: str,
    max_bytes: int,
    *,
    word_boundary: bool = True,
) -> list[str]:
    text = text.strip()
    if not text:
        return []

    if _utf8_len(text) <= max_bytes:
        return [text]

    chunks: list[str] = []
    remaining = text

    while remaining:
        if _utf8_len(remaining) <= max_bytes:
            chunks.append(remaining)
            break

        cut = _max_prefix_within_bytes(remaining, max_bytes)
        piece = remaining[:cut]

        if word_boundary and cut < len(remaining):
            if remaining[cut] != ' ':
                last_space = piece.rfind(' ')
                if last_space > 0 and last_space >= int(len(piece) * 0.4):
                    cut = last_space
                    piece = piece[:cut]

        piece = piece.strip()
        if piece:
            chunks.append(piece)

        remaining = remaining[cut:].lstrip()

    return chunks


def build_final_messages(
    text: str,
    settings: dict[str, Any],
) -> list[str]:
    max_bytes = int(settings['max_bytes'])
    add_numbering = bool(settings['add_numbering'])
    word_boundary = bool(settings['word_boundary'])

    prefix, body = _extract_channel_prefix(text)
    prefix_overhead = _utf8_len(prefix + ' ') if prefix else 0
    body = body.strip()

    if not body:
        return [text] if text else []

    if not add_numbering:
        usable = max(1, max_bytes - prefix_overhead)
        chunks = split_message(body, usable, word_boundary=word_boundary)
        if prefix:
            return [f'{prefix} {c}' for c in chunks]
        return chunks

    reserved = 8
    raw_chunks: list[str] = []
    for _ in range(3):
        usable = max(1, max_bytes - prefix_overhead - reserved)
        raw_chunks = split_message(body, usable, word_boundary=word_boundary)
        count = len(raw_chunks)
        needed_reserved = len(f'({count}/{count}) '.encode('utf-8'))
        if needed_reserved <= reserved or count <= 1:
            break
        reserved = needed_reserved

    if len(raw_chunks) <= 1:
        if prefix and raw_chunks:
            return [f'{prefix} {raw_chunks[0]}']
        return raw_chunks

    total = len(raw_chunks)
    if prefix:
        return [
            f'{prefix} ({i}/{total}) {chunk}'
            for i, chunk in enumerate(raw_chunks, 1)
        ]
    return [f'({i}/{total}) {chunk}' for i, chunk in enumerate(raw_chunks, 1)]


_original_send_chat_message = None


def _patched_send_chat_message(self: Any) -> None:
    text = cast(str, bui.textwidget(query=self._text_field)).strip()
    if text == '':
        return

    bui.textwidget(edit=self._text_field, text='')

    settings = get_settings()

    if not settings.get('enabled', True):
        bs.chatmessage(text)
        return

    messages = build_final_messages(text, settings)
    if not messages:
        return

    if len(messages) == 1:
        bs.chatmessage(messages[0])
        return

    delay = float(settings.get('delay_seconds', DEFAULT_SETTINGS['delay_seconds']))

    def _send_one(msg: str) -> None:
        try:
            bs.chatmessage(msg)
        except Exception:
            pass

    for index, msg in enumerate(messages):
        if index == 0:
            _send_one(msg)
        else:
            babase.apptimer(delay * index, babase.Call(_send_one, msg))


def _install_patch() -> None:
    global _original_send_chat_message

    from bauiv1lib.party import PartyWindow

    if _original_send_chat_message is None:
        _original_send_chat_message = PartyWindow._send_chat_message

    if PartyWindow._send_chat_message is not _patched_send_chat_message:
        PartyWindow._send_chat_message = _patched_send_chat_message


def _uninstall_patch() -> None:
    if _original_send_chat_message is not None:
        from bauiv1lib.party import PartyWindow

        PartyWindow._send_chat_message = _original_send_chat_message


class SettingsWindow(bui.Window):
    def __init__(self) -> None:
        self._settings = get_settings()

        self._width = 480
        self._height = 380

        super().__init__(
            root_widget=bui.containerwidget(
                size=(self._width, self._height),
                transition='in_right',
                scale=(
                    1.8
                    if bui.app.ui_v1.uiscale is bui.UIScale.SMALL
                    else 1.35
                    if bui.app.ui_v1.uiscale is bui.UIScale.MEDIUM
                    else 1.0
                ),
            )
        )

        bui.textwidget(
            parent=self._root_widget,
            position=(self._width * 0.5, self._height - 40),
            size=(0, 0),
            h_align='center',
            v_align='center',
            scale=1.1,
            text='Smart Chat Splitter',
            maxwidth=self._width * 0.9,
        )

        bui.textwidget(
            parent=self._root_widget,
            position=(self._width * 0.5, self._height - 68),
            size=(0, 0),
            h_align='center',
            v_align='center',
            scale=0.6,
            color=(0.6, 0.8, 0.6),
            text='تنظیمات تقسیم خودکار پیام‌های طولانی چت',
            maxwidth=self._width * 0.9,
        )

        self._enabled_check = bui.checkboxwidget(
            parent=self._root_widget,
            position=(40, self._height - 110),
            size=(300, 30),
            text='فعال بودن پلاگین',
            value=bool(self._settings['enabled']),
            on_value_change_call=self._on_enabled_changed,
            scale=1.0,
        )

        row_y = self._height - 160
        bui.textwidget(
            parent=self._root_widget,
            position=(40, row_y),
            size=(0, 0),
            h_align='left',
            v_align='center',
            scale=0.75,
            text='حداکثر حجم هر تکه (بایت):',
        )
        self._max_bytes_text = bui.textwidget(
            parent=self._root_widget,
            position=(self._width - 90, row_y),
            size=(0, 0),
            h_align='center',
            v_align='center',
            scale=0.9,
            color=(0.4, 1.0, 0.4),
            text=str(self._settings['max_bytes']),
        )
        bui.buttonwidget(
            parent=self._root_widget,
            position=(self._width - 60, row_y - 15),
            size=(35, 35),
            label='+',
            on_activate_call=babase.Call(self._adjust_max_bytes, BYTES_STEP),
        )
        bui.buttonwidget(
            parent=self._root_widget,
            position=(self._width - 130, row_y - 15),
            size=(35, 35),
            label='-',
            on_activate_call=babase.Call(self._adjust_max_bytes, -BYTES_STEP),
        )

        row_y = self._height - 210
        bui.textwidget(
            parent=self._root_widget,
            position=(40, row_y),
            size=(0, 0),
            h_align='left',
            v_align='center',
            scale=0.75,
            text='تأخیر بین ارسال هر تکه (ثانیه):',
        )
        self._delay_text = bui.textwidget(
            parent=self._root_widget,
            position=(self._width - 90, row_y),
            size=(0, 0),
            h_align='center',
            v_align='center',
            scale=0.9,
            color=(0.4, 1.0, 0.4),
            text=f"{self._settings['delay_seconds']:.2f}",
        )
        bui.buttonwidget(
            parent=self._root_widget,
            position=(self._width - 60, row_y - 15),
            size=(35, 35),
            label='+',
            on_activate_call=babase.Call(self._adjust_delay, DELAY_STEP),
        )
        bui.buttonwidget(
            parent=self._root_widget,
            position=(self._width - 130, row_y - 15),
            size=(35, 35),
            label='-',
            on_activate_call=babase.Call(self._adjust_delay, -DELAY_STEP),
        )

        self._numbering_check = bui.checkboxwidget(
            parent=self._root_widget,
            position=(40, self._height - 250),
            size=(300, 30),
            text='افزودن شماره به ابتدای هر تکه، مثل (1/3)',
            value=bool(self._settings['add_numbering']),
            on_value_change_call=self._on_numbering_changed,
            scale=0.9,
        )

        self._word_boundary_check = bui.checkboxwidget(
            parent=self._root_widget,
            position=(40, self._height - 285),
            size=(300, 30),
            text='تلاش برای نبریدن وسط کلمات هنگام تقسیم',
            value=bool(self._settings['word_boundary']),
            on_value_change_call=self._on_word_boundary_changed,
            scale=0.9,
        )

        bui.buttonwidget(
            parent=self._root_widget,
            position=(30, 25),
            size=(150, 45),
            label='بازگشت به پیش‌فرض',
            scale=0.8,
            on_activate_call=self._reset_defaults,
        )
        bui.buttonwidget(
            parent=self._root_widget,
            position=(self._width - 180, 25),
            size=(150, 45),
            label='بستن',
            on_activate_call=self._close,
        )

    def _on_enabled_changed(self, value: bool) -> None:
        self._settings['enabled'] = bool(value)
        save_settings(self._settings)

    def _on_numbering_changed(self, value: bool) -> None:
        self._settings['add_numbering'] = bool(value)
        save_settings(self._settings)

    def _on_word_boundary_changed(self, value: bool) -> None:
        self._settings['word_boundary'] = bool(value)
        save_settings(self._settings)

    def _adjust_max_bytes(self, delta: int) -> None:
        new_val = int(self._settings['max_bytes']) + delta
        new_val = max(MIN_MAX_BYTES, min(MAX_MAX_BYTES, new_val))
        self._settings['max_bytes'] = new_val
        bui.textwidget(edit=self._max_bytes_text, text=str(new_val))
        save_settings(self._settings)

    def _adjust_delay(self, delta: float) -> None:
        new_val = round(float(self._settings['delay_seconds']) + delta, 2)
        new_val = max(MIN_DELAY, min(MAX_DELAY, new_val))
        self._settings['delay_seconds'] = new_val
        bui.textwidget(edit=self._delay_text, text=f'{new_val:.2f}')
        save_settings(self._settings)

    def _reset_defaults(self) -> None:
        self._settings = copy.deepcopy(DEFAULT_SETTINGS)
        save_settings(self._settings)
        bui.textwidget(
            edit=self._max_bytes_text, text=str(self._settings['max_bytes'])
        )
        bui.textwidget(
            edit=self._delay_text,
            text=f"{self._settings['delay_seconds']:.2f}",
        )
        bui.checkboxwidget(
            edit=self._enabled_check, value=self._settings['enabled']
        )
        bui.checkboxwidget(
            edit=self._numbering_check, value=self._settings['add_numbering']
        )
        bui.checkboxwidget(
            edit=self._word_boundary_check,
            value=self._settings['word_boundary'],
        )

    def _close(self) -> None:
        if self._root_widget:
            bui.containerwidget(edit=self._root_widget, transition='out_right')


# ba_meta export babase.Plugin
class SmartChatSplitter(babase.Plugin):
    def on_app_running(self) -> None:
        save_settings(get_settings())
        _install_patch()

    def on_app_suspend(self) -> None:
        pass

    def on_app_unsuspend(self) -> None:
        pass

    def on_app_shutdown(self) -> None:
        pass

    def on_app_shutdown_complete(self) -> None:
        pass

    def has_settings_ui(self) -> bool:
        return True

    def show_settings_ui(self, source_widget: Any) -> None:
        del source_widget
        SettingsWindow()
