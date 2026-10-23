
# ba_meta require api 9

import re
import babase
import bauiv1 as bui
import bascenev1 as bs


# ba_meta export babase.Plugin
class Akjxd(babase.Plugin):
    def __init__(self):
        super().__init__()

        self._last_messages = []
        self._initialized = False
        self._last_send_time = 0.0

        print("[BsRush Guard] Plugin loaded")

        bui.apptimer(0.5, self._check_chat)

    def _check_chat(self):
        try:
            messages = bs.get_chat_messages() or []
            messages = [
                msg for msg in messages
                if isinstance(msg, str)
            ]

            # بار اول فقط پیام‌های فعلی را ذخیره کن
            if not self._initialized:
                self._last_messages = messages[-30:]
                self._initialized = True
            else:
                old = self._last_messages
                current = messages[-30:]

                # پیدا کردن پیام‌های جدید با استفاده از هم‌پوشانی
                overlap = min(len(old), len(current))
                while overlap > 0:
                    if old[-overlap:] == current[:overlap]:
                        break
                    overlap -= 1

                new_messages = current[overlap:]

                # اگر تاریخچه عوض شده باشد، فقط آخرین پیام را بررسی کن
                if not new_messages and current != old and current:
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
                            "[BsRush Guard] Coin message:",
                            repr(msg)
                        )

                    if gift_match:
                        print(
                            "[BsRush Guard] Gift message:",
                            repr(msg)
                        )

                        # جلوگیری از ارسال پشت‌سرهم
                        import time
                        now = time.monotonic()

                        if now - self._last_send_time >= 3.0:
                            bs.chatmessage("BsRush Guard")
                            self._last_send_time = now
                            print("[BsRush Guard] Alert sent")

        except Exception as exc:
            print("[BsRush Guard] Chat check error:", repr(exc))

        bui.apptimer(0.5, self._check_chat)
