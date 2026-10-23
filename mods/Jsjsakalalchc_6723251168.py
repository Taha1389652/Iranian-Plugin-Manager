# ba_meta require api 9

import re
import time

import babase
import bauiv1 as bui
import bascenev1 as bs


# ba_meta export babase.Plugin
class Akjxd(babase.Plugin):

    def __init__(self):
        super().__init__()
        self._last_messages = []
        self._initialized = False
        self._last_alert_time = 0.0
        print("[BsRush Guard] Plugin loaded")

    def on_app_running(self):
        bui.apptimer(0.5, self._check_chat)

    def _check_chat(self):
        try:
            messages = bs.get_chat_messages() or []
            messages = [
                msg for msg in messages
                if isinstance(msg, str)
            ]

            if not self._initialized:
                self._last_messages = messages[-30:]
                self._initialized = True
            else:
                old = self._last_messages
                current = messages[-30:]

                overlap = min(len(old), len(current))

                while overlap > 0:
                    if old[-overlap:] == current[:overlap]:
                        break
                    overlap -= 1

                new_messages = current[overlap:]

                if (
                    not new_messages
                    and current != old
                    and current
                ):
                    new_messages = current[-1:]

                self._last_messages = current

                for msg in new_messages:
                    coin_match = re.search(
                        r'I\s+have\s+[\d,]+\s+coins!',
                        msg,
                        re.IGNORECASE
                    )

                    gift_match = re.search(
                        r'\bgift\s+\S+\s+[\d,]+\b',
                        msg,
                        re.IGNORECASE
                    )

                    if coin_match:
                        print(
                            "[BsRush Guard] Coin detected:",
                            repr(msg)
                        )

                    if gift_match:
                        now = time.monotonic()

                        if now - self._last_alert_time >= 3.0:
                            bs.chatmessage("BsRush Guard")
                            self._last_alert_time = now

                            print(
                                "[BsRush Guard] Alert sent"
                            )

        except Exception as exc:
            print(
                "[BsRush Guard] Error:",
                repr(exc)
            )

        bui.apptimer(0.5, self._check_chat)
