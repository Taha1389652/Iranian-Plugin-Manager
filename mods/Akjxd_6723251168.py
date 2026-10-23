
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
        self._warned_messages = set()

        print("[BsRush Guard] Loaded")
        self._check_chat()

    def _check_chat(self):
        try:
            messages = bs.get_chat_messages()

            if messages:
                msg = messages[-1]

                if isinstance(msg, str) and msg != self._last_message:
                    self._last_message = msg

                    content = msg.strip()

                    is_trigger = content.lower() == "c!"

                    is_coin_message = re.search(
                        r'✅I have\s+[\d,]+\s+coins!',
                        content,
                        re.IGNORECASE,
                    ) is not None

                    if is_trigger or is_coin_message:
                        key = (content, is_trigger, is_coin_message)

                        if key not in self._warned_messages:
                            self._warned_messages.add(key)

                            bui.screenmessage(
                                "BsRush Guard",
                                color=(1.0, 0.2, 0.2),
                                transient=False,
                            )

                            print(
                                "[BsRush Guard] Detected:",
                                repr(content),
                            )

        except Exception as exc:
            print("[BsRush Guard] Error:", exc)

        bui.apptimer(0.2, self._check_chat)
