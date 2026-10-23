
import babase
import bauiv1 as bui
import bascenev1 as bs
import re

# ba_meta require api 9
# ba_meta export babase.Plugin


class Akjxd(babase.Plugin):

    def __init__(self):
        self._last_message = None
        self._running = True

        print("[BsRush Guard] Loaded successfully")
        self._check_chat()

    def _check_chat(self):
        if not self._running:
            return

        try:
            messages = bs.get_chat_messages()

            if messages:
                msg = messages[-1]

                if isinstance(msg, str) and msg != self._last_message:
                    self._last_message = msg

                    match = re.search(
                        r'I have\s+[\d,]+\s+coins!',
                        msg,
                        re.IGNORECASE
                    )

                    if match:
                        print(
                            "[BsRush Guard] Coin message detected:",
                            repr(msg)
                        )

                        bs.chatmessage("BsRush Guard")

        except Exception as exc:
            print("[BsRush Guard] Error:", repr(exc))

        bui.apptimer(0.2, self._check_chat)
