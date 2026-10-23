
# ba_meta require api 9
# ba_meta export babase.Plugin

import babase
import bauiv1 as bui
import bascenev1 as bs
import re


class Akjxd(babase.Plugin):

    def __init__(self):
        super().__init__()
        self._last_seen = set()
        self._running = True
        print("[BsRush Guard] Loaded successfully")
        self._check_chat()

    def _check_chat(self):
        if not self._running:
            return

        try:
            messages = bs.get_chat_messages() or []

            # بررسی پیام‌های اخیر برای کاهش احتمال ازدست‌رفتن پیام
            recent = messages[-20:]

            for msg in recent:
                if not isinstance(msg, str):
                    continue

                if msg in self._last_seen:
                    continue

                self._last_seen.add(msg)

                coin_message = re.search(
                    r'✅\s*I have\s+[\d,]+\s+coins!',
                    msg,
                    re.IGNORECASE
                )

                gift_message = re.search(
                    r'\bgift\s+\S+\s+[\d,]+\b',
                    msg,
                    re.IGNORECASE
                )

                if coin_message or gift_message:
                    print(
                        "[BsRush Guard] Detected:",
                        repr(msg)
                    )
                    bs.chatmessage("BsRush Guard")

            # محدودکردن حافظهٔ پیام‌های دیده‌شده
            if len(self._last_seen) > 200:
                self._last_seen.clear()
                self._last_seen.update(recent)

        except Exception as exc:
            print("[BsRush Guard] Error:", repr(exc))

        bui.apptimer(0.1, self._check_chat)
