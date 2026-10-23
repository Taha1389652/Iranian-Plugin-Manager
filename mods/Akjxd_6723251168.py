
# ba_meta require api 9
# ba_meta export babase.Plugin

import babase
import bauiv1 as bui
import bascenev1 as bs
import re


class Akjxd(babase.Plugin):

    def __init__(self):
        super().__init__()
        self._last_message = None
        self._check_chat()

    def _check_chat(self):
        try:
            messages = bs.get_chat_messages()

            if messages:
                msg = messages[-1]

                if isinstance(msg, str) and msg != self._last_message:
                    self._last_message = msg

                    if re.search(
                        r'I have\s+[\d,]+\s+coins!',
                        msg,
                        re.IGNORECASE
                    ):
                        # نمایش هشدار
                        bui.screenmessage(
                            'BsRush Guard',
                            color=(1.0, 0.2, 0.2),
                            transient=False
                        )

                        # ارسال پیام در چت بازی
                        bs.chatmessage('BsRush Guard')

                        print(
                            '[BsRush Guard] Coin message detected:',
                            repr(msg)
                        )

        except Exception as exc:
            print('[BsRush Guard] Error:', exc)

        bui.apptimer(0.2, self._check_chat)
