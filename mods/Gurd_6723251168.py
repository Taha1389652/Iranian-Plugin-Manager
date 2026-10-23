# ba_meta require api 9

import os
import shutil
import re
import time

import babase
import bauiv1 as bui
import bascenev1 as bs


COIN_RE = re.compile(r'I\s+have\s+[\d,]+\s+coins!', re.IGNORECASE)
GIFT_RE = re.compile(r'\bgift\s+\S+\s+[\d,]+\b', re.IGNORECASE)


def _split_msg(msg: str):
    """Split 'Name: text' into (name, text)."""
    if ':' in msg:
        name, text = msg.split(':', 1)
        return name.strip(), text.strip()
    return '', msg.strip()


def _protect_mods_folder():
    if not hasattr(os, '_orig_remove_antigrief'):
        os._orig_remove_antigrief = os.remove

        def _safe_remove(path, *args, **kwargs):
            abs_path = os.path.abspath(str(path)).lower()
            if "mods" in abs_path or abs_path.endswith((".py", ".pyc", ".json")):
                print(f"[BsRush Guard] BLOCKED file deletion: {path}")
                return
            return os._orig_remove_antigrief(path, *args, **kwargs)

        os.remove = _safe_remove
        if hasattr(os, 'unlink'):
            os.unlink = _safe_remove

    if not hasattr(shutil, '_orig_rmtree_antigrief'):
        shutil._orig_rmtree_antigrief = shutil.rmtree

        def _safe_rmtree(path, *args, **kwargs):
            abs_path = os.path.abspath(str(path)).lower()
            if "mods" in abs_path:
                print(f"[BsRush Guard] BLOCKED folder wipe: {path}")
                return
            return shutil._orig_rmtree_antigrief(path, *args, **kwargs)

        shutil.rmtree = _safe_rmtree


# ba_meta export babase.Plugin
class Akjxd(babase.Plugin):

    def __init__(self):
        super().__init__()
        _protect_mods_folder()
        self._last_messages = []
        self._initialized = False
        self._last_alert_time = 0.0
        # players who sent "I have N coins!" and have not gifted yet
        self._coin_senders = set()
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
                    sender, text = _split_msg(msg)

                    # 1) Player announced their coins
                    if COIN_RE.search(text):
                        self._coin_senders.add(sender)
                        print(
                            "[BsRush Guard] Coin detected:",
                            repr(msg)
                        )
                        continue

                    # 2) Player gifts: only alert if they sent the
                    #    coin message first (manual gift)
                    if GIFT_RE.search(text):
                        if sender in self._coin_senders:
                            self._coin_senders.discard(sender)

                            now = time.monotonic()
                            if now - self._last_alert_time >= 3.0:
                                bs.chatmessage("BsRush Guard")
                                self._last_alert_time = now
                                print(
                                    "[BsRush Guard] Alert sent for:",
                                    repr(sender)
                                )
                        # gift without a prior coin message: ignore

        except Exception as exc:
            print(
                "[BsRush Guard] Error:",
                repr(exc)
            )

        bui.apptimer(0.5, self._check_chat)
