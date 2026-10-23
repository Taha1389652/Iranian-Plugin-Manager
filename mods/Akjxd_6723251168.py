
# ba_meta require api 9
# ba_meta export babase.Plugin

import babase
import bauiv1 as bui
import bascenev1 as bs


class BsRushGuard(babase.Plugin):

    def __init__(self):
        self._last_message = None
        self._timer = None
        self._check()

    def _check(self):
        try:
            messages = bs.get_chat_messages()
            if messages:
                msg = messages[-1]

                if msg != self._last_message:
                    self._last_message = msg

                    if msg.strip().lower() == 'x':
                        bui.screenmessage(
                            'BsRush Guard: Suspicious trigger detected!',
                            color=(1.0, 0.2, 0.2),
                            transient=False,
                        )
                        print(
                            '[BsRush Guard] Trigger detected:',
                            repr(msg)
                        )
        except Exception as exc:
            print('[BsRush Guard] Error:', exc)

        self._timer = bui.apptimer(0.2, self._check)
