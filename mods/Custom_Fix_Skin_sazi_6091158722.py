# ba_meta require api 9

from __future__ import annotations

import bascenev1 as ba
import babase
import bauiv1 as bui


# ============================================================
# رنگ‌ها
# ============================================================

PURPLE_DARK = (0.22, 0.04, 0.35)
TEXT_COLOR = (1.0, 1.0, 1.0)


# ============================================================
# ارسال مستقیم به چت
# ============================================================

def _send_chat(text: str) -> None:
    try:
        ba.chatmessage(text)
    except Exception as exc:
        print('SEND CHAT ERROR:', repr(exc))


# ============================================================
# مدیریت پنجره‌ها
# ============================================================

_main_window = None
_sub_window = None
_input_window = None


def _close_widget(widget):
    try:
        bui.containerwidget(edit=widget, transition='out_scale')
    except Exception:
        pass


def _close_main():
    global _main_window
    if _main_window is not None:
        _close_widget(_main_window)
        _main_window = None


def _close_sub():
    global _sub_window
    if _sub_window is not None:
        _close_widget(_sub_window)
        _sub_window = None


def _close_input():
    global _input_window
    if _input_window is not None:
        _close_widget(_input_window)
        _input_window = None


def _back_to_main():
    global _sub_window
    _close_sub()
    _sub_window = None
    _open_main_menu()


# ============================================================
# پنجره شبیه‌سازی کادر چت (SEND + CANCEL)
# ============================================================

def _open_input_window(default_text=''):
    global _input_window

    _close_input()

    size = (480, 220)

    _input_window = bui.containerwidget(
        size=size,
        transition='in_scale',
        color=PURPLE_DARK,
    )

    bui.textwidget(
        parent=_input_window,
        position=(0, size[1] - 40),
        size=(size[0], 30),
        text='متن را وارد کن:',
        h_align='center',
        v_align='center',
        scale=0.7,
        color=TEXT_COLOR,
    )

    text_field = bui.textwidget(
        parent=_input_window,
        position=(30, 100),
        size=(420, 60),
        text=default_text,
        editable=True,
        h_align='left',
        v_align='center',
        scale=0.8,
        color=(1.0, 1.0, 0.5),
        max_chars=200,
        padding=6.0,
    )

    bui.buttonwidget(
        parent=_input_window,
        position=(30, 30),
        size=(180, 50),
        label='SEND',
        button_type='square',
        autoselect=True,
        text_scale=0.8,
        color=PURPLE_DARK,
        textcolor=(0.3, 1.0, 0.3),
        on_activate_call=bui.Call(_do_send_from_input, text_field),
    )

    close_btn = bui.buttonwidget(
        parent=_input_window,
        position=(270, 30),
        size=(180, 50),
        label='CANCEL',
        button_type='square',
        autoselect=True,
        text_scale=0.8,
        color=PURPLE_DARK,
        textcolor=(1.0, 0.4, 0.4),
        on_activate_call=bui.Call(_close_input),
    )

    try:
        bui.containerwidget(
            edit=_input_window,
            cancel_button=close_btn,
        )
    except Exception:
        pass

    try:
        bui.containerwidget(
            edit=_input_window,
            selected_child=text_field,
        )
    except Exception:
        pass


def _do_send_from_input(text_field):
    try:
        text = str(bui.textwidget(query=text_field)).strip()
    except Exception as e:
        print('READ FIELD ERROR:', repr(e))
        _close_input()
        return

    if text:
        _send_chat(text)

    _close_input()


# ============================================================
# پنجره پایه منوهای فرعی
# ============================================================

class _SubMenuWindow:

    def __init__(self, title: str, size=(360, 520)):
        global _sub_window

        self._root = bui.containerwidget(
            size=size,
            transition='in_scale',
            color=PURPLE_DARK,
        )

        bui.textwidget(
            parent=self._root,
            position=(0, size[1] - 50),
            size=(size[0], 40),
            text=title,
            h_align='center',
            v_align='center',
            scale=1.0,
            color=TEXT_COLOR,
        )

        bui.buttonwidget(
            parent=self._root,
            position=(20, 12),
            size=(110, 40),
            label='BACK',
            button_type='square',
            autoselect=True,
            text_scale=0.6,
            color=PURPLE_DARK,
            textcolor=TEXT_COLOR,
            on_activate_call=bui.Call(_back_to_main),
        )

        close_btn = bui.buttonwidget(
            parent=self._root,
            position=(size[0] - 130, 12),
            size=(110, 40),
            label='CLOSE',
            button_type='square',
            autoselect=True,
            text_scale=0.6,
            color=PURPLE_DARK,
            textcolor=TEXT_COLOR,
            on_activate_call=bui.Call(self._close),
        )

        try:
            bui.containerwidget(
                edit=self._root,
                cancel_button=close_btn,
            )
        except Exception:
            pass

        _sub_window = self._root

    def _close(self):
        global _sub_window
        _close_widget(self._root)
        _sub_window = None


# ============================================================
# منوی Fix
# ============================================================

class FixWindow(_SubMenuWindow):

    def __init__(self):
        super().__init__('Fix', size=(360, 520))

        items = [
            ('fix 0', 'send'),
            ('fix i', 'send'),
            ('fix c', 'input'),
            ('fix c sell', 'input'),
            ('fix c delete', 'input'),
            ('fix c free', 'input'),
            ('fix c pv', 'input'),
            ('fix Poook', 'send'),
        ]

        y = 400
        for label, mode in items:
            bui.buttonwidget(
                parent=self._root,
                position=(40, y),
                size=(280, 38),
                label=label,
                button_type='square',
                autoselect=True,
                text_scale=0.6,
                color=PURPLE_DARK,
                textcolor=TEXT_COLOR,
                on_activate_call=bui.Call(self._on_click, label, mode),
            )
            y -= 44

    def _on_click(self, label, mode):
        if mode == 'send':
            _send_chat(label)
        else:
            _close_sub()
            _open_input_window(label)


# ============================================================
# منوی Rang
# ============================================================

class RangWindow(_SubMenuWindow):

    def __init__(self):
        super().__init__('Rang', size=(420, 520))

        items = [
            '",-1,-1111,-1,-1',
            '",-1,-50,-50,-1',
            '1c-1,99999,-1,-1',
            '",-12,10000,10,9',
            '",10,10,10,11',
            'اسکین سازم خواستی چت بده!',
            'کد رنگ میفروشم بهترین کد رنگ ها !',
            'اسکین ساز حرفه ای هستم چت بده!',
        ]

        y = 400
        for label in items:
            bui.buttonwidget(
                parent=self._root,
                position=(30, y),
                size=(360, 38),
                label=label,
                button_type='square',
                autoselect=True,
                text_scale=0.5,
                color=PURPLE_DARK,
                textcolor=TEXT_COLOR,
                on_activate_call=bui.Call(_send_chat, label),
            )
            y -= 44


# ============================================================
# منوی Cod test (۱۶ کد) - testb3 اصلاح شد
# ============================================================

class CodTestWindow(_SubMenuWindow):

    def __init__(self):
        super().__init__('Cod test', size=(480, 520))

        codes = [
            'testb', 'testh', 'testf',
            'testb1', 'testh1', 'testf1',
            'testb2', 'testh2', 'testf2',
            'testb3', 'testh3', 'testf3',
            'tests', 'testt', 'testm',
            'test',
        ]

        start_x = 30
        start_y = 400
        btn_w = 135
        btn_h = 38
        gap_x = 12
        gap_y = 12

        for i, code in enumerate(codes):
            col = i % 3
            row = i // 3
            x = start_x + col * (btn_w + gap_x)
            y = start_y - row * (btn_h + gap_y)

            bui.buttonwidget(
                parent=self._root,
                position=(x, y),
                size=(btn_w, btn_h),
                label=code,
                button_type='square',
                autoselect=True,
                text_scale=0.55,
                color=PURPLE_DARK,
                textcolor=TEXT_COLOR,
                on_activate_call=bui.Call(_send_chat, code),
            )


# ============================================================
# منوی اصلی 🪐
# ============================================================

class MainMenuWindow:

    def __init__(self):
        global _main_window

        size = (300, 420)

        self._root = bui.containerwidget(
            size=size,
            transition='in_scale',
            color=PURPLE_DARK,
        )

        bui.textwidget(
            parent=self._root,
            position=(0, 340),
            size=(300, 60),
            text='🪐',
            h_align='center',
            v_align='center',
            scale=2.4,
            color=TEXT_COLOR,
        )

        bui.buttonwidget(
            parent=self._root,
            position=(40, 260),
            size=(220, 48),
            label='Fix',
            button_type='square',
            autoselect=True,
            text_scale=0.7,
            color=PURPLE_DARK,
            textcolor=TEXT_COLOR,
            on_activate_call=bui.Call(self._open_fix),
        )

        bui.buttonwidget(
            parent=self._root,
            position=(40, 195),
            size=(220, 48),
            label='Rang',
            button_type='square',
            autoselect=True,
            text_scale=0.7,
            color=PURPLE_DARK,
            textcolor=TEXT_COLOR,
            on_activate_call=bui.Call(self._open_rang),
        )

        bui.buttonwidget(
            parent=self._root,
            position=(40, 130),
            size=(220, 48),
            label='Cod test',
            button_type='square',
            autoselect=True,
            text_scale=0.7,
            color=PURPLE_DARK,
            textcolor=TEXT_COLOR,
            on_activate_call=bui.Call(self._open_codtest),
        )

        close_btn = bui.buttonwidget(
            parent=self._root,
            position=(90, 30),
            size=(120, 40),
            label='CLOSE',
            button_type='square',
            autoselect=True,
            text_scale=0.6,
            color=PURPLE_DARK,
            textcolor=TEXT_COLOR,
            on_activate_call=bui.Call(self._close),
        )

        try:
            bui.containerwidget(
                edit=self._root,
                cancel_button=close_btn,
            )
        except Exception:
            pass

        _main_window = self._root

    def _close_main_then(self, opener):
        _close_main()
        opener()

    def _open_fix(self):
        self._close_main_then(FixWindow)

    def _open_rang(self):
        self._close_main_then(RangWindow)

    def _open_codtest(self):
        self._close_main_then(CodTestWindow)

    def _close(self):
        _close_main()


def _open_main_menu():
    global _main_window
    if _main_window is not None:
        return
    MainMenuWindow()


# ============================================================
# دکمه 🪐 داخل پنجره Party (بالای بالا)
# ============================================================

_original_party_init = None

try:
    from bauiv1lib import party
    _original_party_init = party.PartyWindow.__init__
except Exception:
    pass


def _patched_party_init(self, origin=(0, 0)):
    if _original_party_init:
        _original_party_init(self, origin)

    if getattr(self, '_custom_menu_added', False):
        return
    self._custom_menu_added = True

    try:
        bui.buttonwidget(
            parent=self._root_widget,
            position=(425, 250),
            size=(55, 28),
            label='🪐',
            button_type='square',
            autoselect=True,
            text_scale=0.7,
            color=PURPLE_DARK,
            textcolor=TEXT_COLOR,
            on_activate_call=bui.Call(_open_main_menu),
        )
    except Exception as exc:
        print('CUSTOM MENU PARTY BUTTON ERROR:', repr(exc))


# ba_meta export babase.Plugin
class CustomMenu(babase.Plugin):

    def __init__(self):
        if _original_party_init and not getattr(
            party.PartyWindow, '_custom_menu_patched', False
        ):
            party.PartyWindow.__init__ = _patched_party_init
            party.PartyWindow._custom_menu_patched = True

        ba.screenmessage(
            '🪐 Custom Menu Loaded (API 9)',
            color=(0.8, 0.3, 1.0),
        )