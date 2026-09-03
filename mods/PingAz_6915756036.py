import ba
import _ba

class PingDisplay(ba.Widget):
    def __init__(self):
        # ساخت ویجت متنی در موقعیت مشخص شده (با توجه به اسکرین‌شات شما)
        self.text = ba.textwidget(
            parent=ba.get_special_widget('party_window'),
            position=(700, 350), # مختصات تقریبی بر اساس عکس شما
            size=(100, 30),
            text="Ping: --",
            h_align='center',
            v_align='center',
            color=(1, 1, 1),
            click_activate=True,
            on_activate_call=self.send_ping_to_chat
        )
        # تایمر برای آپدیت هر ۱ ثانیه
        self.timer = ba.Timer(1.0, self.update_ping, repeat=True)

    def update_ping(self):
        ping = _ba.get_ping()
        
        # تعیین رنگ بر اساس پینگ
        if ping < 100:
            color = (0, 1, 0) # سبز
        elif ping < 300:
            color = (1, 1, 0) # زرد
        else:
            color = (1, 0, 0) # قرمز
            
        ba.textwidget(edit=self.text, text=f"Ping: {ping}ms", color=color)

    def send_ping_to_chat(self):
        ping = _ba.get_ping()
        # ارسال پیام به چت (نیاز به دسترسی به چت سیستم)
        _ba.chatmessage(f"My Ping : {ping} ms")

# اجرای ماد
def ba_app_get_plugin():
    return PingDisplay()
