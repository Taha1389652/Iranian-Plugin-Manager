import babase
import bascenev1 as bs

# متن مورد نظر برای تکرار در چت
msg = "@Beoworldمرجع دانلود فیلم های دژمنان در تلگرام🎌🐲"

# زمان تکرار متن به ثانیه
time_ad = 30

# وضعیت تغییر متن (برای جلوگیری از تکرار یکسان)
state_msg = True


def handle_msg() -> None:
    """ارسال پیام در چت و زمانبندی مجدد با apptimer"""
    global state_msg

    if state_msg:
        bs.chatmessage(msg)
        state_msg = False
    else:
        bs.chatmessage(msg + ".")
        state_msg = True

    # استفاده از apptimer برای زمانبندی بعدی (در سطح اپلیکیشن)
    babase.apptimer(time_ad, handle_msg)


# شروع تایمر اولیه پس از ۸ ثانیه
babase.apptimer(8, handle_msg)

# ba_meta require api 9
# ba_meta export babase.Plugin
class Mod(babase.Plugin):
    """کلاس پلاگین برای BombSquad API 9"""
    pass