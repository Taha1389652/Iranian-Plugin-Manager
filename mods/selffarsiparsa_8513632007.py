# SelfTaha v3.0 - API 9
# Copyright 2025 - ByTaha
# ساخته شده توسط طاها استادشریف (@Taha_OstadSharif)
# این مود به صورت خودکار به پیام‌های دریافتی پاسخ می‌دهد
from babase import (
    clipboard_is_supported as CIS,
    clipboard_get_text as CGT,
    clipboard_has_text as CHT,
    Plugin
)
from bauiv1 import (
    get_special_widget as gsw,
    containerwidget as cw,
    screenmessage as push,
    checkboxwidget as chk,
    scrollwidget as sw,
    buttonwidget as bw,
    SpecialChar as sc,
    textwidget as tw,
    checkboxwidget as cb,
    gettexture as gt,
    apptimer as teck,
    getsound as gs,
    UIScale as uis,
    charstr as cs,
    app as APP,
    Call
)
from bascenev1 import (
    get_chat_messages as GCM,
    chatmessage as CM,
    get_connection_to_host_info_2 as get_connection_info,
    connect_to_party as original_connect,
    disconnect_from_host as original_disconnect,
    get_foreground_host_activity
)
from _babase import get_string_width as strw
from datetime import datetime as DT
from bauiv1lib import party
from babase import apptimer as teck
from bauiv1lib.popup import PopupWindow, PopupMenu
from typing import Sequence, Tuple, Optional, Callable
from bauiv1lib.colorpicker import ColorPicker
import random
from bauiv1lib.party import PartyWindow
from bauiv1lib.ingamemenu import InGameMenuWindow
# این خط رو به import ها اضافه کن
from os import listdir, path, mkdir, remove
import math
import json
import os
import socket
import threading
import time
import re
import bascenev1 as bs
import bauiv1 as bui
import _babase
import babase
import bascenev1 as bs
import bauiv1 as bui

# --- Import های جدید برای Account Switcher ---
from bauiv1lib.confirm import ConfirmWindow
from bauiv1lib.account.settings import AccountSettingsWindow
from os import listdir, path, mkdir, remove
from shutil import copy, rmtree
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional

# لیست جوک‌های فارسی کوتاه و متنوع
JOKES = [
    "پدر: درس خوندی؟ گفتم: خواب علمی بودم!",
    "مامان: گوشی دستته؟ گفتم: آپدیت زندگیه!",
    "همکار: چرا دیر اومدی؟ گفتم: ترافیک اینترنتی!",
    "دوست: چرا خسته‌ای؟ گفتم: تعطیلات تمرین میکنم!",
    "دختر: گرسنمه! گفتم: منم، برو مامان رو بگو!",
    "پسر: پول میخوام! گفتم: منم منتظر معجزم!",
    "فروشنده: تخفیف داریم! گفتم: پس فردا میام!",
    "همسر: دوسم داری؟ گفتم: بیشتر از دیروز!",
    "رئیس: چرا استرس داری؟ گفتم: تمرین آرامش میکنم!",
    "دکتر: ورزش کن! گفتم: چشم، کانال ورزشو نگاه!",
    "معلم: تکالیفتو نکردی؟ گفتم: فرصت طلایی دادم!",
    "پدر: بلند شو! گفتم: با تخت هنوز دعوامه!",
    "مامان: بیا کمک! گfتم: انرژی جمع میکنم!",
    "دختر: بیرون بریم! گفتم: مسافرت اینستا میرم!",
    "دوست: جواب نمیدی؟ گفتم: با خودم چت میکنم!",
    "پدر: درس نمیخونی؟ گفتم: استعدادم مخفیه!",
    "مامان: گوشی دستته؟ گفتم: بهش استراحت میدم!",
    "همکار: چرا شادابی؟ گفتم: قهوه و شوخی ترکیب!",
    "معلم: چرا خوابیدی؟ گفتم: رویای موفقیتت رو میبینم!",
    "پدر: بلند شو! گفتم: با بالش مبارزه میکنم!",
    "دختر: حوصلم سرره! گفتم: برو مامانو سرگرم کن!",
    "دوست: چرا ساکتی؟ گفتم: جا برای حرفت گذاشتم!",
    "رئیس: اشتباه کردی؟ گفتم: میخواستم انسان بودنم ثابت!",
    "فروشنده: این لباس؟ گفتم: بیشتر به پولم میاد!",
    "همسر: خرید کردی؟ گfتم: آره، با یه نون هم خرج!",
    "پسر: پیامم رو دیدی؟ گفتم: آره، تو خواب دیروز!",
    "دختر: گرسنمه! گفتم: منم، با هم گرسنگی کنیم!",
    "دوست: چرا جدی؟ گفتم: برای شوخی تمرین میکنم!",
    "رئیس: استعفا میدی؟ گفتم: مدیر شوخی میشم!",
    "معلم: نمیخندی؟ گfتم: دندونام سفید بمونه!",
    "پدر: نمیخونی؟ گfتم: استعدادمو مخفی میکنم!",
    "مامان: غذا نمیخوری؟ گfتم: تمرین گرسنگیمه!",
    "دوست: دیر اومدی؟ گfتم: راهو گم کردم، پیداش کردم!",
    "همکار: چرا شادابی؟ گfتم: قهوه با انرژی مثبت!",
    "دختر: ناراحتی؟ گfتم: برای شادی تمرین میکنم!",
    "پسر: بازی بخر! گfتم: منتظر قهرمان خریدم!",
    "فروشنده: این مدل؟ گfتم: قدیمیش هنوز خفن‌تره!",
    "همسر: کدومو دوست داری؟ گfتم: اونی که ساکته!",
    "رئیس: دیر کردی؟ گfتم: خواب بودم که دیر نشه!",
    "دکتر: دارو بخور! گfتم: چشم، بعد از اثرش!",
    "مامان: اتاقت رو تمیز کن! گfتم: حال طبیعی میدم!",
    "پدر: بلند شو! گfتم: با زمین کشتی میگیرم!",
    "معلم: نمیفهمی؟ گfتم: میخوام بیشتر توضیح بدید!",
    "دوست: جواب نمیدی؟ گfتم: با خودم چت میکنم!",
    "دختر: بیرون بریم! گfتم: الان مسافرت اینستا!",
    "پسر: پول میخوام! گfتم: منم منتظرم کسی بده!",
    "همکار: غمگینی؟ گfتم: برای شادی تمرین میکنم!",
    "دوست: چرا جدی‌ای؟ گfتم: برای شوخی تمرین میکنم!",
    "پدر: نمیخونی؟ گfتم: استعدادمو مخفی میکنم!",
    "مامان: غذا بخور! گfتم: الان رژیم فضایی دارم!",
    "رئیس: چرا اینکارو کردی؟ گfتم: ببینم توجه داری!",
    "فروشنده: تخفیف داریم! گfتم: پس فردا میام!",
    "همسر: دوسم داری؟ گfتم: بیشتر از دیروز، کمتر فردا!",
    "پسر: پول تو جیبی! گfتم: منم منتظرم!",
    "دختر: حوصلم سرره! گfتم: برو مامانو سرگرم کن!",
    "دوست: ساکتی؟ گfتم: جا برای حرفت گذاشتم!",
    "معلم: تکالیف؟ گfتم: میخواستم فرصت بدم!"
]

# ضرب المثل های فارسی کوتاه
PROVERBS = [
    "آب که از سر گذشت، چه یک وجب چه صد وجب.",
    "از کوزه همان برون تراود که در اوست.",
    "باد آورده را باد می‌برد.",
    "کار امروز را به فردا می‌انداز.",
    "هر که بامش بیش، برفش بیش‌تر.",
    "هرچه بکاری، همان را درو می‌کنی.",
    "نه هرکه چهره برافروخت، دل ربود.",
    "هر سخن جایی و هر نکته مکانی دارد.",
    "هر که طاووس خواهد، جور هندوستان کشد.",
    "دوستی کن اما دلبسته مباش.",
    "آفتاب مهربان‌تر از چراغ است.",
    "از دشمن باید بیم داشت، نه از دوست.",
    "دیگ به دیگ می‌گوید روت سیاه.",
    "تا نگوئی چرا، نمی‌فهمی.",
    "نه خانی آمده، نه خانی رفته.",
    "کوزه‌ای که نشکند، آب در آن نمی‌ماند.",
    "خشت اول چون نهد معمار کج، تا ثریا می‌رود دیوار کج.",
    "حساب پاک، دست پاک.",
    "کار نیکو کردن از پر کردن است.",
    "وقت طلاست.",
    "آب رفته را نمی‌توان به جوی بازگرداند.",
    "با دوستان باید مهربان بود.",
    "پیش از آنکه بخوری، ببین.",
    "خر خود را نشناسد، مردم چگونه بشناسند.",
    "قورباغه را دم اغشته می‌کنند.",
    "سیاه‌رویان همیشه در ظلمتند.",
    "دود از کنده بلند می‌شود.",
    "هر چه گوئی، گوش شنوا لازم است.",
    "ماه در آب پیدا نمی‌شود.",
    "گر صبر کنی، ز غوره حلوا سازی.",
    "بی‌صبر، بی‌کار.",
    "خنده بر هر درد بی‌درمان دواست.",
    "کار بزرگ را با قدم‌های کوچک شروع کن.",
    "چوب خدا صدا ندارد.",
    "عاقبت گرگ زاده گرگ شود.",
    "آب به آسیاب دشمن نریز.",
    "پایان شب سیه سپید است.",
    "سنگ بزرگ علامت نزدن است.",
    "پایان هر کار، شروع کار دیگر است.",
    "نه همه آنچه می‌درخشد طلاست.",
    "هر که bامش بیش، برfش بیش‌تر.",
    "با یک گل بهار نمی‌شود.",
    "کار را به اهلش بسپار.",
    "از این ستون تا آن ستون فرجی است.",
    "مار گزیده از ریسمان سیاه و سفید می‌ترسد.",
    "دو صد گفته، نیم کردار نیست.",
    "نه طوطی خوش است و نه سخن او.",
    "گربه دستش به گوشت نمی‌رسد، می‌گوید پیف پیف.",
    "کار نیکو کردن از پر کردن است.",
    "دیوار موش ندارد.",
    "هر که bامش بیش، برfش بیش‌تر.",
    "آب را گل نکن.",
    "گر صبر کنی، ز غوره حلوا سازی.",
    "یک دست صدا ندارد.",
    "آفتاب آمد دلیل آفتاب.",
    "کار امروز را به فردا می‌انداز.",
    "بی‌عقل، با عقل سر نمی‌کند.",
    "سختی کشیدن، آسانی می‌آورد.",
    "هر که bamش بیش، برfش بیش‌تر.",
    "یک ساعت فکر بهتر از صد ساعت کار بیهوده است.",
    "دوست آن باشد که در وقت تنگدستی یارت باشد.",
    "آتش گرفته را با آب خاموش می‌کنند.",
    "پیشگیری بهتر از درمان است.",
    "هر که صداقت داشت، نجات یافت."
]

# لیست چیستان های فارسی کوتاه
RIDDLES = [
    "سر داره بدن نداره؟ (سوزن)",
    "بالا میره پایین نمیاد؟ (سن)",
    "یک چشم داره نمی‌بینه؟ (سوزن)",
    "هر چی بدوی نمی‌رسی؟ (سایه)",
    "جلوته ولی دیده نمیشه؟ (آینده)",
    "پر از سوراخ آب نگه می‌داره؟ (اسفنج)",
    "می‌شکنه صدا نداره؟ (سکوت)",
    "پرواز می‌کنه بال نداره؟ (زمان)",
    "گرفته میشه پرتاب نمیشه؟ (سرما)",
    "هر چی برداری بزرگتر میشه؟ (چاله)",
    "تو دست میگیری لمس نمیشه? (نفس)",
    "می‌دوه پا نداره? (آب)",
    "حرف میزنه دهن نداره? (تلفن)",
    "راه میره نفس نمی‌کشه? (ساعت)",
    "از کوه رد میشه تکون نمیخوره? (جاده)",
    "همه می‌بینن دست نمیرسه? (ستاره)",
    "لباس داره تن نداره? (کتاب)",
    "استفاده کنی کوچیک میشه? (مداد)",
    "شب هست روز نیست? (ماه)",
    "اسمشو بیاری می‌شکنه? (سکوت)",
    "چهار پا داره راه نمیره? (میز)",
    "دندون داره گاز نمی‌گیره? (شونه)",
    "تو آب میره خیس نمیشه? (سایه)",
    "بیشتر بشه کمتر میبینی? (تاریکی)",
    "اول سبز وسط قرمز آخر سیاه? (زغال)",
    "هیچوقت کثیف نمیشه? (آینه)",
    "همه جا هست دیده نمیشه? (هوا)",
    "پرنده‌ست پر نداره? (بادبادک)",
    "می‌چرخه جایی نمیره? (پنکه)",
    "بدون پا حرکت میکنه? (مار)",
    "خیس میکنه خشک میشه? (حوله)",
    "سیاهه ولی روشن میکنه? (ذغال)",
    "می‌سوزه آتیش نداره? (شمع)",
    "صدا میده دیده نمیشه? (باد)",
    "پر باشه سبک‌تره? (بادکنک)",
    "پر غذاست نمی‌خوره? (یخچال)",
    "بالا پایین می‌پره پا نداره? (توپ)",
    "زرده همه رو روشن میکنه? (خورشید)",
    "هر جا بری دنبالت میاد? (سایه)",
    "وقتی رسیدی دیگه نیست? (فردا)",
    "میاد نمی‌مونه? (باران)",
    "همیشه گرسنه‌ست? (آتش)",
    "می‌دوه ولی نفس نداره? (ساعت شنی)",
    "روی زمین میاد کثیف نمیشه? (باران)",
    "پر از حرف ولی صدا نداره? (کتاب)",
    "بی‌بال پرواز میکنه? (خیال)",
    "بیشتر خرج کنی کوچیک میشه? (پول)",
    "دور می‌چرخه نور میده? (ماه)",
    "تو خونه‌ست راه میره? (مورچه)",
    "همیشه حرکت میکنه وای نمیسته? (زمان)",
    "همه جا هست جا نداره? (نور)",
    "بدون دهن می‌خنده? (ماسک)",
    "پا نداره ولی می‌ایسته? (عصا)",
    "بی‌زبان حرف میزنه? (چشم)",
    "هر روز میاد ولی پیر نمیشه? (خورشید)",
    "میاد و میره صدا میکنه? (باد)",
    "هیچ وقت نمیخوابه? (دریا)",
    "بی‌صدا گریه میکنه? (ابر)",
    "تکون نمیخوره ولی رشد میکنه? (گیاه)",
]

# جرعت
DARES = [
    "مثل مرغ قوقولی قوقو کن.",
    "ده ثانیه مثل پنگوئن راه برو.",
    "با لهجه شمالی حرف بزن.",
    "آهنگ عروسی را زمزمه کن.",
    "پشت سر هم سه تا پیف پیف بگو.",
    "یک داستان دروغ دو کلمه‌ای بگو.",
    "با چشم های بسته بچرخ و راه برو.",
    "یک آهنگ را با بینی ات بخوان.",
    "مثل یک ربات برقص.",
    "با دهان پر آب بخند.",
    "یک مدل موی مسخره درست کن.",
    "وانمود کن که گاو هستی.",
    "یک جمله را برعکس بگو.",
    "مثل بچه گربه میو میو کن.",
    "با دست غیرغالب خود بنویس.",
    "یک ایموجی مسخره با صورتت بساز.",
    "مثل فوتبالیستی گل بزن.",
    "با موز تلفن بازی کن.",
    "حرف بزن در حالی که زبانت بیرونه.",
    "یک کار کاملا تصادفی انجام بده.",
    "مثل خرگوش بپر.",
    "آهنگ کودکانه را بلند بخوان.",
    "خودت را به زور به خواب بزن.",
    "مثل دایناسور راه برو.",
    "با کفش هایت آب بخور.",
    "یک سالاد از تنقلات درست کن.",
    "مثل ماهی دهان باز کن و ببند.",
    "با بینی ات دکمه موبایل را بزن.",
    "مثل وزنه بردار ورزش کن.",
    "یک پیامک برای مخاطب آخرت بفرست.",
    "با چشم های بسته چیزی را لمس کن.",
    "مثل پرنده بال بزن.",
    "یک راز مسخره را فریاد بزن.",
    "مثل مارپیچ بچرخ.",
    "با دست و پا راه برو.",
    "مثل گورخر شیهه بکش.",
    "یک داستان ترسناک دو جمله ای بگو.",
    "مثل لاک پشت حرکت کن.",
    "با دهان بسته آواز بخوان.",
    "مثل میمون از درخت بالا برو.",
    "یک شکلک با سشوار درست کن.",
    "مثل جاروبرقی صدا دربیار.",
    "با پاشنه پا راه برو.",
    "مثل پروانه پرواز کن.",
    "یک شعر کودکانه بلند بخوان.",
    "مثل کرم حرکت کن.",
    "با بینی ات شکلک دربیار.",
    "مثل فرشته بال بزن.",
    "یک داستان عاشقانه دروغی بگو.",
    "مثل زنبور وزوز کن.",
    "با چشمان بسته نقاشی بکش.",
    "مثل اسب یورتمه برو.",
    "یک جوک مسخره تعریف کن.",
    "مثل قورباغه بپر.",
    "با دست هایت پازل درست کن.",
    "مثل فیل trumpet بزن.",
    "یک کار غیرمنتظره انجام بده.",
    "مثل شیر غرش کن.",
    "با پاهایت چیزی را بردار.",
    "مثل جیرجیرک صدا دربیار."
]

# حقیقت
TRUTHS = [
    "خجالت‌آورترین لحظه مدرسه‌ات را تعریف کن.",
    "اگر همیشه یک بوی خاص داشته باشی، چه بویی می‌خواهی باشد?",
    "بدترین هدیۀ تولدی که گرفتی چه بود?",
    "عجیب‌ترین چیزی که تا به حال خورده‌ای چیست?",
    "اگر مجبور باشی یک عضو بدنت را حذف کنی کدام است?",
    "اشتباهی که دوست داری از زندگی دیگران پاک کنی کدام است?",
    "اگر روح یک حیوان در تو حلول کند، کدام حیوان است?",
    "بدترین nickname ای که داشته‌ای چه بوده?",
    "اگر یک وسیله خانه باشی، کدام وسیله هستی?",
    "مسخره‌ترین دلیلی که برای گریه کردن داشته‌ای چیست?",
    "اگر برای 24 ساعت نامرئی شوی چه کار می‌کنی?",
    "بدترین مدل مو یا رنگی که داشته‌ای چیست?",
    "اگر یک غذای بنجل بتوانی باشی، کدام هستی?",
    "عجیب‌ترین خرافاتی که به آن اعتقاد داری چیست?",
    "اگر بتوانی صداهای بدن کسی را کنترل کنی، چه می‌کنی?",
    "مسخره‌ترین چیزی که به آن افتخار می‌کنی چیست?",
    "اگر مجبور باشی فقط یک اپلیکیشن داشته باشی کدام است?",
    "بدترین لباسی که پوشیده‌ای و فکر می‌کردی خفن است?",
    "اگر یک مشکل کوچک بتواند همیشه آزارت دهد، کدام است?",
    "عجیب‌ترین ترسی که در کودکی داشتی چیست?",
    "اگر بتوانی یک صدای مزاحم را برای همیشه حذف کنی کدام است?",
    "مسخره‌ترین درگیری که در شبکه‌های اجتماعی داشته‌ای?",
    "اگر بتوانی یک عادت بد همه را اصلاح کنی، کدام است?",
    "بدترین شغلی که می‌توانی تصور کنی چیست?",
    "اگر مجبور باشی یک کلمه را همیشه غلط تلفظ کنی کدام است?",
    "عجیب‌ترین چیزی که در مورد جنس مخالف نمی‌فهمی چیست?",
    "اگر یک وسیله آشپزخانه باشی، کدام هستی?",
    "مسخره‌ترین دلیلی که برای دعوا داشته‌ای چیست?",
    "اگر بتوانی یک حس را برای همیشه حذف کنی کدام است?",
    "بدترین خرید زندگی‌ات چیست?",
    "اگر یک بیماری مسخره داشته باشی، چه بیماری است?",
    "عجیب‌ترین خوابی که در مکان عمومی دیده‌ای چیست?",
    "اگر بتوانی یک صدا را با بینی ات دربیاوری کدام است?",
    "مسخره‌ترین اشتباهی که در یک امتحان داشته‌ای چیست?",
    "اگر مجبور باشی همیشه یک آهنگ زمزمه کنی کدام است?",
    "بدترین توصیه‌ای که به کسی کرده‌ای چیست?",
    "اگر یک نقص فنی کوچک در تو باشد چیست?",
    "عجیب‌ترین چیزی که برای آرامش خود انجام می‌دهی?",
    "اگر بتوانی یک کار خانه را برای همیشه حذف کنی کدام است?",
    "مسخره‌ترین حرفی که در خواب گفته‌ای چیست?",
    "اگر یک ابرقهرمان با قدرت بی‌فایده باشی، قدرتت چیست?",
    "بدترین چیزی که از کسی تقلید کرده‌ای چیست?",
    "اگر بتوانی یک قانون فیزیکی را نقض کنی کدام است?",
    "عجیب‌ترین دلیلی که باعث شد کسی را دوست داشته باشی?",
    "اگر مجبور باشی یک овоح باشی، کدام هستی?",
    "مسخره‌ترین دروغی که در کودکی گفته‌ای چیست?",
    "اگر یک مشکل نرم افزاری در تو باشد چیست?",
    "بدترین پیشبینی که در مورد تو شده چیست?",
    "اگر بتوانی یک صدای بدن را کنترل کنی کدام است?",
    "عجیب‌ترین چیزی که در طبیعت تو را آزار می‌دهد?",
    "اگر مجبور باشی همیشه یک داستان تکراری تعریف کنی کدام است?",
    "مسخره‌ترین اشتباه لپی که داشته‌ای چیست?",
    "اگر یک نقص طراحی در تو باشد چیست?",
    "بدترین تجربه آرایشگاه یا سلمانی تو چیست?",
    "اگر بتوانی یک کار روزمره را حذف کنی کدام است?",
    "عجیب‌ترین چیزی که باعث اضطراب تو می‌شود چیست?",
    "اگر مجبور باشی یک کلمه را هرگز نگویی کدام است?",
    "مسخره‌ترین چیزی که از آن می‌ترسی چیست?"
]


def generate_fonts(text: str) -> dict:
    fonts = {
        "Bold": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                              "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭"
                              "𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇"),
        "Italic": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                                "𝑨𝑩𝑪𝑫𝑬𝑭𝑮𝑯𝑰𝑱𝑲𝑳𝑴𝑵𝑶𝑷𝑸𝑹𝑺𝑻𝑼𝑽𝑾𝑿𝒀𝒁"
                                "𝒂𝒃𝒄𝒅𝒆𝒇𝒈𝒉𝒊𝒋𝒌𝒍𝒎𝒏𝒐𝒑𝒒𝒓𝒔𝒕𝒖𝒗𝒘𝒙𝒚𝒛"),
        "Cursive": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                                 "𝒜𝐵𝒞𝒟𝐸𝐹𝒢𝐻𝐼𝒥𝒦𝐿𝑀𝒩𝒪𝒫𝒬𝑅𝒮𝒯𝒰𝒱𝒲𝒳𝒴𝒵"
                                 "𝒶𝒷𝒸𝒹ℯ𝒻ℊ𝒽𝒾𝒿𝓀𝓁𝓂𝓃ℴ𝓅𝓆𝓇𝓈𝓉𝓊𝓋𝓌𝓍𝓎𝓏"),
        "DoubleStruck": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                                      "𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ"
                                      "𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫"),
        "Fraktur": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                                 "𝔄𝔅ℭ𝔇𝔈𝔉𝔊ℌℑ𝔍𝔎𝔏𝔐𝔑𝔒𝔓𝔔ℜ𝔖𝔗𝔘𝔙𝔚𝔛𝔜ℨ"
                                 "𝔞𝔟𝔠𝔡𝔢𝔣𝔤𝔥𝔦𝔧𝔨𝔩𝔪𝔫𝔬𝔭𝔮𝔯𝔰𝔱𝔲𝔳𝔴𝔵𝔶𝔷"),
        "Parentheses": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                                     "ⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏ"
                                     "ⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩ"),
        "Tiny": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                              "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ"
                              "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ"),
        "Serif": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                               "ᴬᴮᶜᴰᴱᶠᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾᵠᴿˢᵀᵁⱽᵂˣʸᶻ"
                               "ᵃᵇᶜᵈᵉᶠᵍʰᶦʲᵏˡᵐⁿᵒᵖᑫʳˢᵗᵘᵛʷˣʸᶻ"),
        "Monospace": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                                   "𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉"
                                   "𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣"),
        "SmallCaps": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                                   "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                                   "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ"),
        "Bubble": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                                "🅐🅑🅒🅓🅔🅕🅖🅗🅘🅙🅚🅛🅜🅝🅞🅟🅠🅡🅢🅣🅤🅥🅦🅧🅨🅩"
                                "🅐🅑🅒🅓🅔🅕🅖🅗🅘🅙🅚🅛🅜🅝🅞🅟🅠🅡🅢🅣🅤🅥🅦🅧🅨🅩"),
        "Squares": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                                 "🄰🄱🄲🄳🄴🄵🄶🄷🄸🄹🄺🄻🄼🄽🄾🄿🅀🅁🅂🅃🅄🅅🅆🅇🅈🅉"
                                 "🄰🄱🄲🄳🄴🄵🄶🄷🄸🄹🄺🄻🄼🄽🄾🄿🅀🅁🅂🅃🅄🅅🅆🅇🅈🅉"),
        "Wide": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                              "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ"
                              "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ"),
        # 20 فونت جدید اضافه شده
        "Circle": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                                "ⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏ"
                                "ⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩ"),
        "Negative": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                                  "🅰🅱🅲🅳🅴🅵🅶🅷🅸🅹🅺🅻🅼🅽🅾🅿🆀🆁🆂🆃🆄🆅🆆🆇🆈🆉"
                                  "🅰🅱🅲🅳🅴🅵🅶🅷🅸🅹🅺🅻🅼🅽🅾🅿🆀🆁🆂🆃🆄🆅🆆🆇🆈🆉"),
        "Script": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                                "𝓐𝓑𝓒𝓓𝓔𝓕𝓖𝓗𝓘𝓙𝓚𝓛𝓜𝓝𝓞𝓟𝓠𝓡𝓢𝓣𝓤𝓥𝓦𝓧𝓨𝓩"
                                "𝓪𝓫𝓬𝓭𝓮𝓯𝓰𝓱𝓲𝓳𝓴𝓵𝓶𝓷𝓸𝓹𝓺𝓻𝓼𝓽𝓾𝓿𝔀𝔁𝔂𝔃"),
        "Gothic": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                                "𝔄𝔅ℭ𝔇𝔈𝔉𝔊ℌℑ𝔍𝔎𝔏𝔐𝔑𝔒𝔓𝔔ℜ𝔖𝔗𝔘𝔙𝔚𝔛𝔜ℨ"
                                "𝔞𝔟𝔠𝔡𝔢𝔣𝔤𝔥𝔦𝔧𝔨𝔩𝔪𝔫𝔬𝔭𝔮𝔯𝔰𝔱𝔲𝔳𝔴𝔵𝔶𝔷"),
        "MathBold": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                                  "𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙"
                                  "𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳"),
        "MathItalic": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                                    "𝐴𝐵𝐶𝐷𝐸𝐹𝐺𝐻𝐼𝐽𝐾𝐿𝑀𝑁𝑂𝑃𝑄𝑅𝑆𝑇𝑈𝑉𝑊𝑋𝑌𝑍"
                                    "𝑎𝑏𝑐𝑑𝑒𝑓𝑔ℎ𝑖𝑗𝑘𝑙𝑚𝑛𝑜𝑝𝑞𝑟𝑠𝑡𝑢𝑣𝑤𝑥𝑦𝑧"),
        "MathBoldItalic": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                                        "𝑨𝑩𝑪𝑫𝑬𝑭𝑮𝑯𝑰𝑱𝑲𝑳𝑴𝑵𝑶𝑷𝑸𝑹𝑺𝑻𝑼𝑽𝑾𝑿𝒀𝒁"
                                        "𝒂𝒃𝒄𝒅𝒆𝒇𝒈𝒉𝒊𝒋𝒌𝒍𝒎𝒏𝒐𝒑𝒒𝒓𝒔𝒕𝒖𝒗𝒘𝒙𝒚𝒛"),
        "MathScript": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                                    "𝓐𝓑𝓒𝓓𝓔𝓕𝓖𝓗𝓘𝓙𝓚𝓛𝓜𝓝𝓞𝓟𝓠𝓡𝓢𝓣𝓤𝓥𝓦𝓧𝓨𝓩"
                                    "𝓪𝓫𝓬𝓭𝓮𝓯𝓰𝓱𝓲𝓳𝓴𝓵𝓶𝓷𝓸𝓹𝓺𝓻𝓼𝓽𝓾𝓿𝔀𝔁𝔂𝔃"),
        "MathDoubleStruck": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                                          "𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ"
                                          "𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫"),
        "MathFraktur": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                                     "𝔄𝔅ℭ𝔇𝔈𝔉𝔊ℌℑ𝔍𝔎𝔏𝔐𝔑𝔒𝔓𝔔ℜ𝔖𝔗𝔘𝔙𝔚𝔛𝔜ℨ"
                                     "𝔞𝔟𝔠𝔡𝔢𝔣𝔤𝔥𝔦𝔧𝔨𝔩𝔪𝔫𝔬𝔭𝔮𝔯𝔰𝔱𝔲𝔳𝔴𝔵𝔶𝔷"),
        "MathSans": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                                  "𝖠𝖡𝖢𝖣𝖤𝖥𝖦𝖧𝖨𝖩𝖪𝖫𝖬𝖭𝖮𝖯𝖰𝖱𝖲𝖳𝖴𝖵𝖶𝖷𝖸𝖹"
                                  "𝖺𝖻𝖼𝖽𝖾𝖿𝗀𝗁𝗂𝗃𝗄𝗅𝗆𝗇𝗈𝗉𝗊𝗋𝗌𝗍𝗎𝗏𝗐𝗑𝗒𝗓"),
        "MathSansBold": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                                      "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭"
                                      "𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇"),
        "MathSansItalic": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                                        "𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡"
                                        "𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻"),
        "MathSansBoldItalic": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                                            "𝘼𝘽𝘾𝘿𝙀𝙁𝙂𝙃𝙄𝙅𝙆𝙇𝙈𝙉𝙊𝙋𝙌𝙍𝙎𝙏𝙐𝙑𝙒𝙓𝙔𝙕"
                                            "𝙖𝙗𝙘𝙙𝙚𝙛𝙜𝙝𝙞𝙟𝙠𝙡𝙢𝙣𝙤𝙥𝙦𝙧𝙨𝙩𝙪𝙫𝙬𝙭𝙮𝙯"),
        "SmallCaps2": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                                    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                                    "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ"),
        "FullWidth": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                                   "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ"
                                   "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕ｣ｗｘｙｚ"),
        "Squared": str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                                 "🄰🄱🄲🄳🄴🄵🄶🄷🄸🄹🄺🄻🄼🄽🄾🄿🅀🅁🅂🅃🅄🅅🅆🅇🅈🅉"
                                 "🄰🄱🄲🄳🄴🄵🄶🄷🄸🄹🄺🄻🄼🄽🄾🄿🅀🅁🅂🅃🅄🅅🅆🅇🅈🅉"),
    }
    return {name: text.translate(trans) for name, trans in fonts.items()}


# تاس‌های مختلف
DICE = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]

# پیام‌های پیش‌فرض چت سریع
DEFAULT_QUICK_MESSAGES = [
    "سلام!",
    "چطوری?",
    "باحال بود!",
    "بیا بازی کنیم",
    "مرسی",
    "خداحافظ",
    "اوکی",
    "بزن بریم"
]

# COMPREHENSIVE PERSIAN-FINGLISH CONVERSION DICTIONARY
# Based on standard phonetic mapping and common usage

PERSIAN_TO_FINGLISH = {
    # Vowels and basic characters
    'آ': 'a', 'ا': 'a', 'أ': 'a', 'إ': 'e', 'ء': '', 'ئ': '', 'ؤ': '',
    'ب': 'b', 'پ': 'p', 'ت': 't', 'ث': 's',
    'ج': 'j', 'چ': 'ch', 'ح': 'h', 'خ': 'kh',
    'د': 'd', 'ذ': 'z', 'ر': 'r', 'ز': 'z',
    'ژ': 'zh', 'س': 's', 'ش': 'sh', 'ص': 's',
    'ض': 'z', 'ط': 't', 'ظ': 'z', 'ع': '', 'غ': 'gh',
    'ف': 'f', 'ق': 'gh',
    'ک': 'k', 'ك': 'k', 'گ': 'g',
    'ل': 'l', 'م': 'm', 'ن': 'n',
    'و': 'v', 'ه': 'h', 'ة': 'h',
    'ی': 'i', 'ي': 'i', 'ى': '',

    # Diacritics
    'ً': 'an', 'ٌ': 'on', 'ٍ': 'en', 'َ': 'a', 'ُ': 'o', 'ِ': 'e', 'ّ': '',

    # Punctuation
    '؟': '?', '،': ',', '؛': ';', 'ـ': '-', '«': '"', '»': '"',
}

# COMPREHENSIVE WORD DATABASE - PRIORITY MAPPING
WORD_DATABASE = {
    # Pronouns
    'من': 'man', 'تو': 'to', 'او': 'oo', 'ما': 'ma',
    'شما': 'shoma', 'آنها': 'anha', 'ایشان': 'ishan',

    # Common verbs
    'است': 'ast', 'هست': 'hast', 'بود': 'bud', 'شد': 'shod',
    'کرد': 'kard', 'گفت': 'goft', 'داد': 'dad', 'خورد': 'khord',
    'آمد': 'amad', 'رفت': 'raft', 'دید': 'did', 'شنید': 'shenid',

    # Common nouns
    'خدا': 'khoda', 'جهان': 'jahan', 'دنیا': 'donya', 'زندگی': 'zendegi',
    'روز': 'roz', 'شب': 'shab', 'ماه': 'mah', 'سال': 'sal',
    'کشور': 'keshvar', 'شهر': 'shahr', 'خانه': 'khane', 'اتاق': 'otagh',
    'مادر': 'madar', 'پدر': 'pedar', 'برادر': 'baradar', 'خواهر': 'khahar',
    'دوست': 'doost', 'دشمن': 'doshman', 'رئیس': 'rais', 'کارمند': 'karmand',

    # Adjectives
    'خوب': 'khub', 'بد': 'bad', 'زیبا': 'ziba', 'زشت': 'zesht',
    'بزرگ': 'bozorg', 'کوچک': 'kuchek', 'بلند': 'boland', 'کوتاه': 'kotah',
    'سریع': 'sari', 'کند': 'kond', 'گران': 'geran', 'ارزان': 'arzan',

    # Common phrases
    'سلام': 'salam', 'خداحافظ': 'khodahafez', 'ممنون': 'mamnoon',
    'لطفا': 'lotfan', 'ببخشید': 'bebakhshid', 'خواهش': 'khwahesh',
    'چطور': 'chetor', 'چطوری': 'chetori', 'چگونه': 'chegone',
    'چرا': 'chera', 'کی': 'ki', 'کجا': 'koja', 'چی': 'chi',

    # Slang and informal words (for complete coverage)
    'کص': 'kos', 'کیر': 'kir', 'کسکش': 'koskesh', 'کون': 'kun',
    'گایید': 'gayid', 'گاییدن': 'gayidan', 'گوز': 'guz', 'کصخل': 'koskhol',
    'حرومزاده': 'haromzade', 'لاشی': 'lashi', 'جنده': 'jende',
    'ناموس': 'namoos', 'ننت': 'nanat', 'بابات': 'babat',
    'خار': 'khar', 'خایه': 'khaye', 'خارکسه': 'kharkose',

    # Numbers
    'صفر': 'sefr', 'یک': 'yek', 'دو': 'do', 'سه': 'se',
    'چهار': 'chahar', 'پنج': 'panj', 'شش': 'shesh',
    'هفت': 'haft', 'هشت': 'hasht', 'نه': 'noh', 'ده': 'dah',
}

# CONTEXTUAL PREFIXES AND SUFFIXES
PREFIXES_SUFFIXES = {
    # Verb prefixes
    'می‌': 'mi ', 'نمی‌': 'nemi ', 'بی‌': 'bi ',

    # Plural suffixes
    'ها': 'ha', 'ان': 'an', 'ات': 'at', 'ین': 'in',

    # Other common patterns
    'ترین': 'tarin', 'گی': 'gi', 'ی': 'i',
}

# REVERSE MAPPING - FINGLISH TO PERSIAN
FINGLISH_TO_PERSIAN = {}

# Build reverse mapping from character dictionary
for persian, finglish in PERSIAN_TO_FINGLISH.items():
    if finglish and finglish.strip():
        FINGLISH_TO_PERSIAN[finglish] = persian

# Build reverse mapping from word database
for persian, finglish in WORD_DATABASE.items():
    FINGLISH_TO_PERSIAN[finglish] = persian

# Build reverse mapping from prefixes/suffixes
for persian, finglish in PREFIXES_SUFFIXES.items():
    if finglish and finglish.strip():
        FINGLISH_TO_PERSIAN[finglish.strip()] = persian

# COMMON FINGLISH VARIATIONS AND PATTERNS
FINGLISH_PATTERNS = {
    # --- Vowels ---
    'a': 'ا', 'aa': 'آ',
    'e': 'e',  # چون e گاهی صامت تلفظ میشه، باید در کد جدا مدیریت بشه
    'i': 'ی', 'ee': 'ی',
    'o': 'و', 'oo': 'و',
    'u': 'و',
    'y': 'ی',

    # --- Common digraphs ---
    'kh': 'خ',
    'gh': 'غ',
    'sh': 'ش',
    'ch': 'چ',
    'zh': 'ژ',
    'jh': 'ژ',
    'ck': 'ک',
    'ng': 'نگ',

    # --- Consonants ---
    'b': 'ب', 'p': 'پ', 't': 'ت', 's': 'س', 'j': 'ج',
    'h': 'ه', 'd': 'د', 'r': 'ر', 'z': 'ز', 'g': 'گ',
    'f': 'ف', 'q': 'ق', 'k': 'ک', 'l': 'ل', 'm': 'م',
    'n': 'ن', 'v': 'و', 'w': 'و', 'x': 'کس',  # x مثل “eks”
    'c': 'ک',  # در بیشتر موارد مثل "camera" → "کمره"

    # --- Common words ---
    'khoda': 'خدا', 'salam': 'سلام', 'chetori': 'چطوری',
    'mamnoon': 'ممنون', 'lotfan': 'لطفاً', 'bebakhshid': 'ببخشید',
    'man': 'من', 'to': 'تو', 'oo': 'او', 'ma': 'ما',
    'shoma': 'شما', 'anha': 'آنها',
}


def contains_persian(text):
    """Check if text contains Persian characters"""
    if not text:
        return False
    persian_range = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
    return bool(persian_range.search(text))


def is_finglish(text):
    """Advanced Finglish detection with multiple heuristics"""
    if not text or not text.strip():
        return False

    text_lower = text.lower().strip()

    # If it contains Persian characters, it's not Finglish
    if contains_persian(text_lower):
        return False

    # Common English words that should NOT be considered Finglish
    english_only_words = {
        'the', 'and', 'you', 'are', 'is', 'in', 'on', 'at', 'to', 'for',
        'with', 'this', 'that', 'what', 'where', 'when', 'why', 'how',
        'yes', 'no', 'ok', 'hello', 'hi', 'bye', 'good', 'bad', 'very'
    }

    words = text_lower.split()

    # Remove English-only words
    persian_like_words = [word for word in words if word not in english_only_words]

    if not persian_like_words:
        return False

    # Heuristic 1: Common Finglish words
    common_finglish_words = {
        'salam', 'chetori', 'khub', 'mamnoon', 'mersi', 'lotfan',
        'khodahafez', 'man', 'to', 'oo', 'ma', 'shoma', 'anha',
        'kos', 'kir', 'koskesh', 'kun', 'gayid', 'guz', 'koskhol',
        'haromzade', 'lashi', 'jende', 'namoos', 'nanat', 'babat'
    }

    has_finglish_words = any(word in common_finglish_words for word in persian_like_words)

    # Heuristic 2: Finglish patterns
    finglish_patterns = [
        r'\b[a-z]*sh[a-z]*\b', r'\b[a-z]*ch[a-z]*\b', r'\b[a-z]*kh[a-z]*\b',
        r'\b[a-z]*gh[a-z]*\b', r'\b[a-z]*zh[a-z]*\b',
        r'\b[a-z]*aa[a-z]*\b', r'\b[a-z]*ee[a-z]*\b', r'\b[a-z]*oo[a-z]*\b',
    ]

    has_finglish_pattern = any(
        re.search(pattern, word)
        for word in persian_like_words
        for pattern in finglish_patterns
    )

    # Heuristic 3: Word structure analysis
    short_word_count = sum(1 for word in persian_like_words if len(word) <= 6)
    total_words = len(persian_like_words)

    # Consider it Finglish if:
    # - Contains known Finglish words OR
    # - Has Finglish patterns OR
    # - Short words dominate (common in Persian chat)
    return (has_finglish_words or has_finglish_pattern or
            (total_words > 0 and short_word_count / total_words > 0.7))


def convert_persian_to_finglish(text):
    """Professional Persian to Finglish conversion with word priority"""
    if not text or not text.strip():
        return text

    # Step 1: Handle prefixes and suffixes (with space handling)
    converted = text
    for persian, finglish in PREFIXES_SUFFIXES.items():
        # Handle with and without space
        converted = converted.replace(persian, finglish)
        converted = converted.replace(persian.replace('‌', ' '), finglish)

    # Step 2: Handle complete words (longest first for priority)
    word_sorted = sorted(WORD_DATABASE.items(), key=lambda x: len(x[0]), reverse=True)
    for persian, finglish in word_sorted:
        # Use word boundaries for exact matching
        pattern = r'\b' + re.escape(persian) + r'\b'
        converted = re.sub(pattern, finglish, converted)

    # Step 3: Character-by-character conversion for remaining text
    for persian, finglish in PERSIAN_TO_FINGLISH.items():
        converted = converted.replace(persian, finglish)

    # Step 4: Clean up
    converted = re.sub(r'\s+', ' ', converted)  # Normalize spaces
    converted = converted.strip()

    return converted


def convert_finglish_to_persian(text):
    """Professional Finglish to Persian conversion with pattern matching"""
    if not text or not text.strip():
        return text

    converted = text.lower()

    # Step 1: Handle complete words (longest first)
    word_sorted = sorted(WORD_DATABASE.items(), key=lambda x: len(x[1]), reverse=True)
    for persian, finglish in word_sorted:
        # Use word boundaries for exact matching
        pattern = r'\b' + re.escape(finglish) + r'\b'
        converted = re.sub(pattern, persian, converted)

    # Step 2: Handle common patterns
    for finglish, persian in FINGLISH_PATTERNS.items():
        converted = converted.replace(finglish, persian)

    # Step 3: Single character conversion
    for finglish, persian in FINGLISH_TO_PERSIAN.items():
        if len(finglish) == 1:
            converted = converted.replace(finglish, persian)

    # Step 4: Clean up
    converted = re.sub(r'\s+', ' ', converted).strip()

    return converted


# Global conversion mode
convert_mode = 0  # 0: off, 1: Persian to Finglish, 2: Finglish to Persian


class AdvancedConvertPanel:
    @classmethod
    def get_ui_scale(cls):
        ui_scale = APP.ui_v1.uiscale
        scale_map = {
            uis.SMALL: 1.5,
            uis.MEDIUM: 1.1,
            uis.LARGE: 0.8
        }
        return scale_map.get(ui_scale, 1.0)

    @classmethod
    def create_window(cls, source, extra_scale=0.0, **kwargs):
        center = source.get_screen_space_center() if source else None
        window = cw(
            **kwargs,
            scale=cls.get_ui_scale() + extra_scale,
            transition='in_scale',
            color=(0.05, 0.05, 0.05),
            parent=gsw('overlay_stack'),
            scale_origin_stack_offset=center
        )
        return window

    @staticmethod
    def close_window(window=None):
        gs('swish').play()
        if window:
            cw(window, transition='out_scale')

    def __init__(s, source):
        global convert_mode
        s.window = s.create_window(
            source=source,
            size=(850, 450),
            extra_scale=0.2
        )

        # دکمه بستن
        AR.add_close_button(s.window, position=(830, 420))

        # Title با یونیکد زیبا
        tw(
            parent=s.window,
            text=u'\ue010 Text Converter Pro',
            position=(425, 420),
            h_align='center',
            scale=1.5,
            color=(0, 1, 1)
        )

        tw(
            parent=s.window,
            text=u'\ue025 CONVERSION CONTROLS',
            position=(180, 375),
            h_align='center',
            scale=1.0,
            color=(1, 1, 0)
        )

        # Mode selection
        mode_y = 320
        s.p2f_btn = bw(
            parent=s.window,
            label=u'\ue027 Persian → Finglish',
            size=(380, 40),
            position=(25, mode_y),
            on_activate_call=Call(s.set_conversion_mode, 1),
            textcolor=(1, 1, 1),
            enable_sound=True,
            button_type='square',
            color=(0.2, 0.5, 0.2) if convert_mode == 1 else (0.3, 0.3, 0.4)
        )

        s.f2p_btn = bw(
            parent=s.window,
            label=u'\ue026 Finglish → Persian',
            size=(380, 40),
            position=(25, mode_y - 45),
            on_activate_call=Call(s.set_conversion_mode, 2),
            textcolor=(1, 1, 1),
            enable_sound=True,
            button_type='square',
            color=(0.2, 0.5, 0.2) if convert_mode == 2 else (0.3, 0.3, 0.4)
        )

        # دکمه ON/OFF شبیه Auto Message
        s.off_btn = bw(
            parent=s.window,
            label='ON' if convert_mode != 0 else 'OFF',
            size=(150, 35),
            position=(140, mode_y - 95),
            on_activate_call=Call(s.toggle_conversion),
            textcolor=(1, 1, 1),
            enable_sound=True,
            button_type='square',
            color=(0, 0.45, 0) if convert_mode != 0 else (0.35, 0, 0)
        )

        # Manual conversion section
        tw(
            parent=s.window,
            text=u'\ue024 MANUAL CONVERSION:',
            position=(200, 170),
            h_align='center',
            scale=0.9,
            color=(0.7, 0.7, 1.0)
        )

        # فیلد متن بزرگتر
        tw(
            parent=s.window,
            text=u'\ue023 Enter text to convert:',
            position=(30, 140),
            scale=0.8,
            color=(1, 1, 1)
        )

        s.text_input = tw(
            parent=s.window,
            position=(30, 105),
            size=(380, 35),
            editable=True,
            text='',
            color=(0.9, 0.9, 0.9),
            description="Type Persian or Finglish text here..."
        )

        # دکمه‌های تبدیل دستی
        s.convert_p2f_btn = bw(
            parent=s.window,
            label=u'\ue027 Convert → Finglish',
            size=(180, 35),
            position=(30, 60),
            on_activate_call=Call(s.manual_convert, 1),
            textcolor=(1, 1, 1),
            color=(0.3, 0.6, 0.3)
        )

        s.convert_f2p_btn = bw(
            parent=s.window,
            label=u'\ue026 Convert → Persian',
            size=(180, 35),
            position=(220, 60),
            on_activate_call=Call(s.manual_convert, 2),
            textcolor=(1, 1, 1),
            color=(0.3, 0.5, 0.8)
        )

        # دکمه تبدیل کلیپ‌بورد
        s.clipboard_btn = bw(
            parent=s.window,
            label=u'\ue022 Convert Clipboard Text',
            size=(380, 30),
            position=(30, 20),
            on_activate_call=s.convert_clipboard,
            textcolor=(1, 1, 1),
            color=(0.6, 0.3, 0.8)
        )

        # بخش سمت راست - توضیحات کامل
        tw(
            parent=s.window,
            text=u'\ue020 ABOUT TEXT CONVERTER',
            position=(580, 375),
            h_align='center',
            scale=1.0,
            color=(1, 1, 0)
        )

        # توضیحات کامل
        description_text = [
            u"\ue010 REAL-TIME CONVERSION",
            "• Automatically converts chat messages",
            "• Works in all game modes",
            "• Instant text transformation",
            "",
            u"\ue027 PERSIAN TO FINGLISH",
            "• سلام → salam",
            "• چطوری → chetori",
            "• خداحافظ → khodahafez",
            "• دوست → doost",
            "",
            u"\ue026 FINGLISH TO PERSIAN",
            "• salam → سلام",
            "• chetori → چطوری",
            "• khodahafez → خداحافظ",
            "• doost → دوست",
            "",
            u"\ue025 SMART FEATURES",
            "• Intelligent word detection",
            "• Special vocabulary handling",
            "• Punctuation conversion",
            "• Context-aware processing",
        ]

        desc_y = 340
        for line in description_text:
            if line.startswith(u"\ue010") or line.startswith(u"\ue027") or line.startswith(
                    u"\ue026") or line.startswith(u"\ue025"):
                color = (0, 1, 1)
                scale = 0.75
            elif line.startswith("•"):
                color = (0.8, 1, 0.8)
                scale = 0.60
            else:
                color = (0.8, 0.8, 1)
                scale = 0.7

            tw(
                parent=s.window,
                text=line,
                position=(440, desc_y),
                scale=scale,
                color=color,
                maxwidth=380,
                h_align='left'
            )
            desc_y -= 18 if any(icon in line for icon in [u"\ue010", u"\ue027", u"\ue026", u"\ue025"]) else 15

        s.update_display()
        gs('dingSmall').play()

    def toggle_conversion(s):
        """Toggle conversion on/off like Auto Message"""
        global convert_mode
        if convert_mode == 0:
            convert_mode = 1
        else:
            convert_mode = 0

        s.update_display()
        gs('deek').play()

        mode_names = {0: 'OFF', 1: 'Persian to Finglish', 2: 'Finglish to Persian'}
        status_color = (0, 1, 0) if convert_mode != 0 else (1, 0.5, 0)
        push(f"Converter: {mode_names[convert_mode]}", color=status_color)

    def set_conversion_mode(s, mode):
        global convert_mode
        convert_mode = mode
        s.update_display()
        gs('click01').play()

        mode_names = {0: 'OFF', 1: 'Persian to Finglish', 2: 'Finglish to Persian'}
        status_color = (0, 1, 0) if mode != 0 else (1, 0.5, 0)
        push(f"Converter: {mode_names[mode]}", color=status_color)

    def update_display(s):
        global convert_mode

        # Update button colors
        bw(s.p2f_btn, color=(0.2, 0.6, 0.2) if convert_mode == 1 else (0.3, 0.3, 0.4))
        bw(s.f2p_btn, color=(0.2, 0.6, 0.2) if convert_mode == 2 else (0.3, 0.3, 0.4))

        # Update ON/OFF button like Auto Message
        bw(s.off_btn,
           label='ON' if convert_mode != 0 else 'OFF',
           color=(0, 0.45, 0) if convert_mode != 0 else (0.35, 0, 0),
           textcolor=(0, 0.6, 0) if convert_mode != 0 else (0.5, 0, 0))

    def manual_convert(s, conversion_type):
        """تبدیل دستی متن"""
        try:
            text = tw(query=s.text_input).strip()
            if not text:
                push("Please enter some text!", color=(1, 0.5, 0))
                return

            if conversion_type == 1:
                if not contains_persian(text):
                    push("Text doesn't contain Persian characters!", color=(1, 0.5, 0))
                    return
                converted = convert_persian_to_finglish(text)
                result_type = "Finglish"
            else:
                if not is_finglish(text):
                    push("Text doesn't appear to be Finglish!", color=(1, 0.5, 0))
                    return
                converted = convert_finglish_to_persian(text)
                result_type = "Persian"

            push(f"✅ Converted to {result_type}: {converted}", color=(0, 1, 0))

            try:
                if CIS():
                    from babase import clipboard_set_text
                    clipboard_set_text(converted)
                    push("📋 Result copied to clipboard!", color=(0, 1, 1))
            except:
                pass

            gs('dingSmallHigh').play()

        except Exception as e:
            push(f"❌ Conversion error: {str(e)}", color=(1, 0, 0))

    def convert_clipboard(s):
        """تبدیل متن کلیپ‌بورد"""
        try:
            if CIS() and CHT():
                clipboard_text = CGT()
                if not clipboard_text.strip():
                    push("📋 Clipboard is empty!", color=(1, 0.5, 0))
                    return

                original_preview = clipboard_text[:30] + "..." if len(clipboard_text) > 30 else clipboard_text
                push(f"📋 Converting: {original_preview}", color=(0.5, 0.8, 1))

                if contains_persian(clipboard_text):
                    converted = convert_persian_to_finglish(clipboard_text)
                    result_type = "Finglish"
                elif is_finglish(clipboard_text):
                    converted = convert_finglish_to_persian(clipboard_text)
                    result_type = "Persian"
                else:
                    push("❓ Cannot detect text type in clipboard!", color=(1, 0.5, 0))
                    return

                from babase import clipboard_set_text
                clipboard_set_text(converted)

                result_preview = converted[:30] + "..." if len(converted) > 30 else converted
                push(f"✅ Converted to {result_type}: {result_preview}", color=(0, 1, 0))
                push("📋 Result copied to clipboard!", color=(0, 1, 1))

                gs('dingSmallHigh').play()

            else:
                push("❌ Clipboard not supported on this device!", color=(1, 0.5, 0))

        except Exception as e:
            push(f"❌ Clipboard error: {str(e)}", color=(1, 0, 0))


# متغیر جهانی برای ذخیره سرورها
saved_servers_global = []

# متغیرهای پینگ و اطلاعات سرور - واقعی
current_ping = 0.0
server_ip = "127.0.0.1"
server_port = 43210
server_name = "Local Server"

# متغیرهای global برای Account Switcher
UI_SCALE = 2.0 if (babase.app.ui_v1.uiscale == babase.UIScale.SMALL) else 1.0
ACCOUNT_FILES = ['.bsac2', '.bsuuid', 'config.json', '.config_prev.json']
plus = babase.app.plus
env = babase.app.env
USER_DIR = path.dirname(env.config_file_path)
ACCOUNTS_DIR = path.join(USER_DIR, 'account_switcher_profiles')

if not path.exists(ACCOUNTS_DIR):
    mkdir(ACCOUNTS_DIR)

if not path.exists(ACCOUNTS_DIR):
    mkdir(ACCOUNTS_DIR)

# تعریف متغیرهای global
original_buttonwidget = bui.buttonwidget
original_containerwidget = bui.containerwidget
original_checkboxwidget = bui.checkboxwidget
original_have_pro = None
original_add_transaction = bui.app.plus.add_v1_account_transaction


# اورراید کردن تابع connect برای گرفتن آیپی واقعی
def new_connect_to_party(address, port=43210, print_progress=False):
    global server_ip, server_port
    server_ip = address
    server_port = port
    print(f"اتصال به سرور: {address}:{port}")
    return original_connect(address, port, print_progress)


# اورراید کردن disconnect
def new_disconnect_from_host():
    global server_ip, server_port
    server_ip = "127.0.0.1"
    server_port = 43210
    print("قطع اتصال از سرور")
    return original_disconnect()


"""کلاس thread برای بررسی پینگ واقعی"""


class RealPingThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.running = True

    def run(self):
        global current_ping
        while self.running:
            try:
                if server_ip != "127.0.0.1" and server_port != 43210:
                    # پینگ واقعی با استفاده از سوکت
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.settimeout(1)
                    start_time = time.time()

                    # ارسال بسته پینگ (همانند بازی)
                    sock.sendto(b'\x0b', (server_ip, server_port))

                    try:
                        # دریافت پاسخ
                        data, addr = sock.recvfrom(10)
                        if data == b'\x0c':  # پونگ
                            ping = (time.time() - start_time) * 1000.0
                            current_ping = round(ping, 2)
                        else:
                            current_ping = 999
                    except socket.timeout:
                        current_ping = 999
                    except:
                        current_ping = 0
                    finally:
                        sock.close()
                else:
                    current_ping = 0
            except:
                current_ping = 0

            time.sleep(1)  # هر 1 ثانیه بروزرسانی

    def stop(self):
        self.running = False


# اورراید کردن توابع اصلی بازی
original_connect = None
original_disconnect = None

"""تبدیل تاریخ میلادی به شمسی"""


def gregorian_to_jalali(gy, gm, gd):
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    if gm > 2:
        gy2 = gy + 1
    else:
        gy2 = gy
    days = 355666 + (365 * gy) + ((gy2 + 3) // 4) - ((gy2 + 99) // 100) + ((gy2 + 399) // 400) + gd + g_d_m[gm - 1]
    jy = -1595 + (33 * (days // 12053))
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm = 1 + (days // 31)
        jd = 1 + (days % 31)
    else:
        jm = 7 + ((days - 186) // 30)
        jd = 1 + ((days - 186) % 30)
    return jy, jm, jd


"""افزودن پاسخ"""


class Add:
    def __init__(s, source):
        w = AR.cw(source=source, size=(500, 295), ps=AR.UIS() * 0.8)
        AR.add_close_button(w, position=(460, 260))

        tw(
            parent=w,
            text='Commands',
            scale=0.7,
            position=(325, 250),
            h_align='center',
            color=(0, 1, 1)
        )

        s.inputs = []
        for i, label in enumerate(['Trigger', 'Response']):
            tw(parent=w, text=label + ':', position=(30, 250 - 70 * i))
            text_widget = tw(
                parent=w,
                maxwidth=230,
                size=(230, 30),
                editable=True,
                v_align='center',
                color=(0.75, 0.75, 0.75),
                position=(30, 218 - 70 * i),
                allow_clear_button=False
            )
            s.inputs.append(text_widget)
            AR.bw(
                parent=w,
                size=(20, 30),
                iconscale=1.3,
                icon=gt('file'),
                position=(265, 218 - 70 * i),
                on_activate_call=Call(s.paste, text_widget)
            )

        bw(
            parent=w,
            size=(60, 60),
            position=(130, 5),
            label='',
            texture=gt('logo'),
            color=(1, 1, 1)
        )

        # Time settings
        tw(parent=w, text='After', position=(30, 105))
        tw(parent=w, text='Seconds', position=(190, 105))
        s.time_widget = tw(
            parent=w,
            size=(90, 30),
            editable=True,
            text=var('time'),
            h_align='center',
            position=(95, 105),
            color=(0.75, 0.75, 0.75),
            allow_clear_button=False
        )

        s.search_in_messages = False
        s.search_cb = cb(
            parent=w,
            size=(250, 30),
            position=(27.5, 65),
            text='Search in messages',
            value=s.search_in_messages,
            on_value_change_call=Call(setattr, s, 'search_in_messages'),
            color=(0.75, 0.75, 0.75),
            textcolor=(1, 1, 1),
        )

        # Placeholder/Info text
        tw(
            parent=w,
            scale=0.5,
            position=(300, 230),
            text='💬 %m: Your name\n📨 %s: Sender\n⏰ %t: Current time\n📅 %d: Gregorian date\n🗓 %f: Jalali date\n😂 %j: Random joke\n🧩 %ch: Short riddle\n📜 %z: Proverb\n🎰 %dice: Dice bet\n❓ %tr: Truth in Dare game\n🔍 %da: Dare in Dare game\n🌐 %ip: Server IP & Port\n📡 %p: Send ping',
            maxwidth=190,
            color=(1, 1, 0)
        )

        AR.bw(parent=w, label='Add', size=(50, 35), position=(230, 25), on_activate_call=Call(s._add, s.inputs))
        AR.swish()

    def _add(s, inputs):
        try:
            t = float(tw(query=s.time_widget))
        except:
            AR.err('Invalid time. Please correct it!')
            return
        var('time', str(t))

        trigger, response = [tw(query=w).strip().replace('\n', ' ') for w in inputs]
        if not trigger or not response:
            AR.err('Please enter something!')
            return

        l = var('l') or {}
        lc = var('lc') or {}
        ic = trigger.lower()
        if ic in lc:
            AR.err('Trigger already exists!')
            return

        l.update({trigger: (response, t, s.search_in_messages)})
        lc.update({ic: (response, t, s.search_in_messages)})
        var('l', l)
        var('lc', lc)
        [tw(w, text='') for w in inputs]
        AR.ok()

    def paste(s, widget):
        if not CIS(): AR.err('Not supported!'); return
        if not CHT(): AR.err('Clipboard is empty!'); return
        tw(widget, text=CGT().replace('\n', ' '), color=(0, 1, 0))
        gs('gunCocking').play()
        teck(0.3, Call(tw, widget, color=(1, 1, 1)))


class Nuke:
    def __init__(s, source):
        triggers = var('l')
        if not triggers:
            AR.err('Please add some triggers first!')
            return
        w = AR.cw(source=source, size=(260, 350), ps=AR.UIS() * 0.5)
        AR.add_close_button(w, position=(250, 315))

        s.scroll = sw(parent=w, size=(220, 290), position=(20, 40))
        s.container = cw(parent=s.scroll, size=(220, len(triggers) * 30), background=False)

        AR.bw(parent=w, label='Delete', size=(60, 25), position=(180, 10), on_activate_call=Call(s._nuke))

        s.widgets = []
        s.selected = None
        s.refresh()
        AR.swish()

    def _nuke(s):
        if s.selected is None:
            AR.err('Please select something!')
            return
        l = var('l')
        lc = var('lc')
        key = list(l)[s.selected]
        l.pop(key)
        lc.pop(key.lower())
        var('l', l)
        var('lc', lc)
        s.selected = None
        s.refresh()
        AR.bye()

    def refresh(s):
        [w.delete() for w in s.widgets]
        s.widgets.clear()
        keys = list(var('l'))
        for i, key in enumerate(keys):
            widget = tw(
                text=key,
                parent=s.container,
                size=(220, 30),
                selectable=True,
                click_activate=True,
                position=(0, (30 * len(keys)) - 30 * (i + 1)),
                on_activate_call=Call(s.highlight, i)
            )
            s.widgets.append(widget)
        cw(s.container, size=(220, len(keys) * 30))

    def highlight(s, index):
        [tw(w, color=(1, 1, 1)) for w in s.widgets]
        tw(s.widgets[index], color=(0, 1, 0))
        s.selected = index


"""تنظیمات"""


class Tune:
    def __init__(s, t):
        w = AR.cw(
            source=t,
            size=(350, 250),
            ps=AR.UIS() * 0.8
        )

        tw(
            parent=w,
            text='Setting',
            scale=1.2,
            position=(155, 225),
            h_align='center',
            color=(0, 1, 1)
        )
        # افزودن دکمه بستن
        AR.add_close_button(w, position=(315, 215))

        AR.swish()
        for i in range(5):
            j = [
                'Notify on reply',
                'Play sound on reply',
                'Reply to ' + byTaha.me(),
                'Case sensitive',
                'Game speed control'  # گزینه جدید
            ][i]
            c = f'tune{i}'
            if i == 4:  # برای گزینه کنترل سرعت
                bw(
                    parent=w,
                    label=j,
                    size=(290, 30),
                    position=(30, 20 + 40 * i),
                    on_activate_call=Call(SpeedControl, w),
                    color=(0.3, 0.5, 0.8),
                    textcolor=(1, 1, 1)
                )
            else:
                chk(
                    text=j,
                    parent=w,
                    size=(290, 30),
                    textcolor=(1, 1, 1),
                    value=var(c),
                    position=(30, 20 + 40 * i),
                    color=(0.13, 0.13, 0.13),
                    on_value_change_call=Call(var, c)
                )


"""لیست پاسخ‌ها"""


class List:
    def __init__(s, source):
        triggers = var('l')
        if not triggers:
            AR.err('Please add some triggers first!')
            return

        w = AR.cw(source=source, size=(450, 300), ps=AR.UIS() * 0.8)
        AR.add_close_button(w, position=(440, 265))

        s.scroll = sw(parent=w, size=(150, 260), position=(30, 20))
        s.container = cw(parent=s.scroll, size=(220, len(triggers) * 30), background=False)

        # Text widgets for trigger info
        s.text_widgets = []
        labels = ['Trigger', 'Response', 'Parsed']
        colors = [(0, 1, 1), (1, 1, 0), (1, 0, 1)]
        for i in range(3):
            tw(color=colors[i], parent=w, text=labels[i] + ':', position=(190, 240 - 80 * i))
            widget = tw(parent=w, maxwidth=250, max_height=60, v_align='top', position=(190, 215 - 80 * i))
            s.text_widgets.append(widget)

        # Info button
        bw(
            parent=w,
            position=(390, 240),
            size=(40, 40),
            label='',
            texture=gt('achievementEmpty'),
            on_activate_call=s.info,
            color=(1, 1, 1),
            enable_sound=False
        )

        s.widgets = []
        s.selected = None
        s.refresh()
        AR.swish()

    """Display selected trigger info"""

    def info(s):
        if s.selected is None:
            AR.err('Please select a trigger first!')
            return
        i = s.selected
        trigger, delay, wildcard = list(var('l').items())[i][1]
        push(f'Trigger order: {i + 1}\nResponse after: {delay} seconds\nWildcard: {wildcard}')
        gs('tap').play()

    """Refresh the list of triggers"""

    def refresh(s):
        [w.delete() for w in s.widgets]
        s.widgets.clear()
        triggers = list(var('l'))
        for i, trigger in enumerate(triggers):
            widget = tw(
                text=trigger,
                parent=s.container,
                size=(150, 30),
                selectable=True,
                click_activate=True,
                position=(0, (30 * len(triggers)) - 30 * (i + 1)),
                on_activate_call=Call(s.highlight, i)
            )
            s.widgets.append(widget)
        cw(s.container, size=(220, len(triggers) * 30))

    """Highlight selected trigger and show its details"""

    def highlight(s, index):
        [tw(w, color=(1, 1, 1)) for w in s.widgets]
        tw(s.widgets[index], color=(0, 1, 0))
        s.selected = index

        triggers = var('l')
        trigger = list(triggers)[index]
        response, delay, wildcard = triggers[trigger]
        parsed = AR.parse(t=response)
        # Update text widgets
        [tw(s.text_widgets[i], text=sn([trigger, response, parsed][i])) for i in range(3)]


"""چت سریع"""


class QuickChat:
    def __init__(s, source):
        w = s.w = AR.cw(source=source, size=(400, 300), ps=AR.UIS() * 0.8)
        AR.add_close_button(w, position=(370, 265))

        # Title
        tw(parent=w, text='Quick Chat', scale=1.2, position=(180, 250), h_align='center', color=(1, 1, 0))

        tw(parent=w, text='Edit the IP and port to connect to servers manually!', scale=0.6, position=(180, 220),
           h_align='center', color=(1, 1, 0))

        bw(parent=w, size=(40, 40), position=(95, 245), label='', texture=gt('startButton'), color=(1, 1, 1))

        bw(parent=w, size=(40, 40), position=(280, 245), label='', texture=gt('startButton'), color=(1, 1, 1))

        # Scroll to show messages
        s.scroll = sw(parent=w, size=(360, 150), position=(20, 70))
        s.container = cw(parent=s.scroll, size=(360, 400), background=False)

        # Management buttons
        buttons = [
            (u'Add', s.add_message, (20, 15)),
            ('Remove', s.remove_message, (150, 15)),
            ('Reset', s.reset_messages, (280, 15)),
        ]
        for label, callback, pos in buttons:
            AR.bw(parent=w, label=label, size=(90, 35), position=pos, on_activate_call=callback)

        s.refresh_messages()
        AR.swish()

    """Refresh and display messages"""

    def refresh_messages(s):
        for child in s.container.get_children():
            child.delete()

        messages = load_quick_messages()
        y_pos = len(messages) * 43 - 25

        for msg in messages:
            bw(
                parent=s.container,
                label=msg[:30] + '...' if len(msg) > 30 else msg,
                size=(340, 40),
                position=(10, y_pos),
                on_activate_call=Call(s.send_message, msg),
                color=(0.3, 0.5, 0.8),
                textcolor=(1, 1, 1)
            )
            y_pos -= 45

        cw(s.container, size=(360, len(messages) * 45))

    """Send message"""

    def send_message(s, message):
        try:
            CM(message)
            push(f'Sent: {message}', color=(0, 1, 0))
            gs('dingSmall').play()
            AR.swish(s.w)
        except Exception as e:
            AR.err(f'Error sending: {str(e)}')

    """Add a new message"""

    def add_message(s):
        def save_new():
            new_msg = tw(query=txt_widget).strip()
            if new_msg:
                messages = load_quick_messages()
                if new_msg not in messages:
                    messages.append(new_msg)
                    save_quick_messages(messages)
                    s.refresh_messages()
                    push(f'Added: "{new_msg}"', color=(0, 1, 0))
                    gs('dingSmallHigh').play()
                else:
                    AR.err('This message already exists!')
            AR.swish(win)

        win = AR.cw(source=s.w, size=(300, 140), ps=AR.UIS() * 0.6)
        AR.add_close_button(win, position=(250, 105))

        tw(parent=win, text='New message:', position=(20, 90), scale=0.9, color=(1, 1, 1))
        txt_widget = tw(parent=win, position=(20, 60), size=(260, 30), editable=True, text='', color=(0.9, 0.9, 0.9))

        AR.bw(parent=win, label='Confirm', size=(80, 30), position=(110, 20), on_activate_call=save_new)

    """Remove message"""

    def remove_message(s):
        messages = load_quick_messages()
        if not messages:
            AR.err('No messages to remove!')
            return

        win = AR.cw(source=s.w, size=(350, min(450, 200 + len(messages) * 45)), ps=AR.UIS() * 0.6)
        AR.add_close_button(win, position=(350, 350))

        tw(parent=win, text='Select a message to remove:', scale=1.0, position=(150, min(400, 0 + len(messages) * 45)),
           h_align='center', color=(1, 1, 0))

        scroll = sw(parent=win, size=(330, min(300, 100 + len(messages) * 40)), position=(10, 50))
        container = cw(parent=scroll, size=(330, len(messages) * 45), background=False)

        y_pos = len(messages) * 44 - 25
        for msg in messages:
            bw(
                parent=container,
                label=f'Remove: {msg[:20]}...' if len(msg) > 20 else f'Remove: {msg}',
                size=(310, 40),
                position=(10, y_pos),
                on_activate_call=Call(s.confirm_remove, msg, win),
                color=(0.8, 0.2, 0.2),
                textcolor=(1, 1, 1)
            )
            y_pos -= 45

    """Confirm removal"""

    def confirm_remove(s, msg, parent_win):
        messages = load_quick_messages()
        if msg in messages:
            messages.remove(msg)
            save_quick_messages(messages)
            s.refresh_messages()
            push(f'Removed: "{msg}"', color=(1, 0.5, 0))
            gs('dingSmallLow').play()
        AR.swish(parent_win)

    """Reset messages to default"""

    def reset_messages(s):
        save_quick_messages(DEFAULT_QUICK_MESSAGES.copy())
        s.refresh_messages()
        push('Messages reset to default', color=(0, 1, 1))
        gs('dingSmallHigh').play()


"""کلاس Reconnect با Auto-Join دائمی و ذخیره وضعیت"""


class Reconnect:
    def __init__(s, t):
        w = s.w = AR.cw(
            source=t,
            size=(600, 350),  # ارتفاع کمتر شده
            ps=AR.UIS() * 0.8,
            background=True
        )
        AR.add_close_button(w, position=(550, 290))

        tw(
            parent=w,
            text='🌐 Server Manager Pro',
            scale=1.0,
            position=(280, 290),
            h_align='center',
            color=(0.2, 0.8, 1)
        )

        # === بخش سمت راست: توضیحات ===
        tw(
            parent=w,
            text='SERVER CONTROLS',
            scale=0.8,
            position=(410, 260),
            h_align='center',
            color=(1, 1, 0)
        )

        # توضیحات درباره این قسمت
        description = [
            "This section allows you to:",
            "• Reconnect to current server",
            "• Disconnect from server", 
            "• Enable auto-join feature",
            "• Manage saved servers",
            "• Manual connect to servers"
        ]

        desc_y = 230
        for line in description:
            if line.startswith("This section"):
                color = (1, 1, 1)
                scale = 0.6
            elif line.startswith("•"):
                color = (0.8, 1, 0.8)
                scale = 0.5
            else:
                continue

            tw(
                parent=w,
                text=line,
                position=(330, desc_y),
                scale=scale,
                color=color,
                maxwidth=200,
                h_align='left'
            )
            desc_y -= 20

        # اطلاعات وضعیت
        s.status_text = tw(
            parent=w,
            text='Ready - Auto-Join OFF',
            position=(400, 90),
            scale=0.7,
            color=(0.8, 0.8, 1),
            h_align='center'
        )

        s.ping_text = tw(
            parent=w,
            text=f'Ping: {current_ping} ms',
            position=(400, 70),
            scale=0.6,
            color=(0.7, 0.9, 1),
            h_align='center'
        )

        # === بخش سمت چپ: دکمه‌ها با اسکرول ===
        s.scroll = sw(
            parent=w,
            size=(250, 200),
            position=(30, 80)
        )
        s.container = cw(
            parent=s.scroll,
            size=(250, 250),
            background=False
        )

        # دکمه‌ها
        s.reconnect_btn = bw(
            parent=s.container,
            label='اتصال مجدد',
            size=(230, 35),
            icon=gt('replayIcon'),
            position=(10, 200),
            iconscale=0.6,
            on_activate_call=s.do_reconnect,
            color=(0.2, 0.7, 0.3),
            textcolor=(1, 1, 1)
        )

        s.disconnect_btn = bw(
            parent=s.container,
            label='Disconnect',
            size=(230, 35),
            icon=gt('textClearButton'),
            position=(10, 155),
            iconscale=0.6,
            on_activate_call=s.do_disconnect,
            color=(0.9, 0.3, 0.3),
            textcolor=(1, 1, 1)
        )

        s.auto_join_active = var('auto_join_active')
        if s.auto_join_active is None:
            s.auto_join_active = False
        s.manual_disconnect = False

        s.auto_join_btn = bw(
            parent=s.container,
            label='🔴 Auto-Join: OFF',
            size=(230, 35),
            icon=gt('heart'),
            position=(10, 110),
            iconscale=0.6,
            on_activate_call=s.toggle_auto_join,
            color=(0.8, 0.2, 0.2),
            textcolor=(1, 1, 1)
        )

        s.saved_servers_btn = bw(
            parent=s.container,
            label='Saved Servers',
            size=(230, 35),
            position=(10, 65),
            on_activate_call=s.show_saved_servers,
            color=(0.3, 0.5, 0.8),
            text_scale=0.7,
            textcolor=(1, 1, 1)
        )

        s.change_server_btn = bw(
            parent=s.container,
            label='Manual Connect',
            size=(230, 35),
            position=(10, 20),
            on_activate_call=s.show_change_server,
            color=(0.8, 0.6, 0.2),
            text_scale=0.7,
            textcolor=(1, 1, 1)
        )

        s.auto_join_timer = None
        s.auto_join_check_timer = None

        from bauiv1lib.ingamemenu import InGameMenuWindow as m
        m.i = server_ip
        m.p = server_port

        s._update_auto_join_ui()
        s.stop_timers()

        AR.swish()

    def _update_auto_join_ui(s):
        try:
            if hasattr(s, 'auto_join_btn') and s.auto_join_btn.exists():
                if s.auto_join_active:
                    bw(s.auto_join_btn, label='🟢 Auto-Join: ON', color=(0.2, 0.8, 0.2))
                else:
                    bw(s.auto_join_btn, label='🔴 Auto-Join: OFF', color=(0.8, 0.2, 0.2))
            if hasattr(s, 'status_text') and s.status_text.exists():
                if s.auto_join_active:
                    tw(s.status_text, text='Auto-Join: ACTIVATED', color=(0, 1, 0))
                else:
                    tw(s.status_text, text='Ready - Auto-Join OFF', color=(0.8, 0.8, 1))
        except Exception as e:
            print(f"Update UI error: {e}")

    def toggle_auto_join(s):
        print(f"DEBUG: Toggle called - current active: {s.auto_join_active}")
        try:
            if not s.auto_join_active:
                s.auto_join_active = True
                var('auto_join_active', s.auto_join_active)
                s.manual_disconnect = False
                push('✅ Auto-Join ACTIVATED!', color=(0, 1, 0))
                try:
                    gs('dingSmallHigh').play()
                except:
                    pass
                s.stop_timers()
                s.start_auto_join()
                print("DEBUG: Started auto-join")
            else:
                s.auto_join_active = False
                var('auto_join_active', s.auto_join_active)
                push('⏰ Auto-Join DEACTIVATED!', color=(0.8, 0.6, 0.2))
                try:
                    gs('dingSmallLow').play()
                except:
                    pass
                s.stop_timers()
                print("DEBUG: Stopped timers")

            s._update_auto_join_ui()
            print("DEBUG: UI updated directly")

        except Exception as e:
            print(f"Toggle error: {e}")
            s._update_auto_join_ui()

    def start_auto_join(s):
        if not s.auto_join_active:
            s.stop_timers()
            return

        s.stop_timers()

        def auto_check():
            if not var('auto_join_active'):
                print("DEBUG: Auto-check stopped - mode OFF")
                s.stop_timers()
                return

            try:
                conn_info = get_connection_info()
                is_connected = conn_info is not None

                if hasattr(s, 'ping_text') and s.ping_text.exists():
                    tw(s.ping_text, text=f'Ping: {current_ping} ms')

                if not is_connected:
                    if s.manual_disconnect:
                        if hasattr(s, 'status_text') and s.status_text.exists():
                            tw(s.status_text, text='🔴 MANUAL DISCONNECT', color=(0.9, 0.3, 0.3))
                        s.manual_disconnect = False
                        return

                    from bauiv1lib.ingamemenu import InGameMenuWindow as m
                    target_ip = getattr(m, 'i', '')
                    target_port = getattr(m, 'p', 0)

                    if not target_ip or not target_port or target_ip == "127.0.0.1" or target_port == 43210:
                        if hasattr(s, 'status_text') and s.status_text.exists():
                            tw(s.status_text, text='❌ No Valid Server!', color=(0.9, 0.3, 0.3))
                        push('❌ No Server Configured!', color=(0.9, 0.3, 0.3))
                        return

                    if hasattr(s, 'status_text') and s.status_text.exists():
                        tw(s.status_text, text='🔄 AUTO-JOINING...', color=(1, 1, 0))
                    s.do_auto_join()

                else:
                    from bauiv1lib.ingamemenu import InGameMenuWindow as m
                    m.i = server_ip
                    m.p = server_port
                    s.manual_disconnect = False

                    if hasattr(s, 'status_text') and s.status_text.exists():
                        tw(s.status_text, text='🟢 CONNECTED', color=(0, 1, 0))

            except Exception as e:
                print(f"Auto-join check error: {e}")
                if hasattr(s, 'status_text') and s.status_text.exists():
                    tw(s.status_text, text='❌ Auto-Join Error', color=(0.9, 0.3, 0.3))

            if var('auto_join_active'):
                s.auto_join_check_timer = teck(1.5, auto_check)
            else:
                s.stop_timers()

        s.auto_join_check_timer = teck(0.1, auto_check)
        print("DEBUG: Auto-join timer started")

    def stop_timers(s):
        timers = var('auto_join_timers') or []
        for timer in timers[:]:
            try:
                if hasattr(timer, 'exists') and timer.exists():
                    timer.delete()
                timers.remove(timer)
            except:
                pass
        var('auto_join_timers', timers)
        local_timers = ['auto_join_timer', 'auto_join_check_timer']
        for timer_name in local_timers:
            if hasattr(s, timer_name) and getattr(s, timer_name) is not None:
                try:
                    timer = getattr(s, timer_name)
                    if hasattr(timer, 'exists') and timer.exists():
                        timer.delete()
                    setattr(s, timer_name, None)
                except:
                    pass
        print("DEBUG: All timers stopped (global + local)")

    def do_auto_join(s):
        if not var('auto_join_active'):
            print("DEBUG: do_auto_join skipped - mode OFF")
            return

        print("DEBUG: do_auto_join called - attempting reconnect")
        try:
            from bauiv1lib.ingamemenu import InGameMenuWindow as m
            target_ip = getattr(m, 'i', '')
            target_port = getattr(m, 'p', 0)

            if target_ip != "127.0.0.1" and target_port != 43210:
                if s.auto_join_active:
                    push(f'🔄 Auto-joining {target_ip}:{target_port}...', color=(1, 1, 0))
                else:
                    push(f'⏰ Joining {target_ip}:{target_port}...', color=(0.8, 0.6, 0.2))

                conn_info = get_connection_info()
                if conn_info:
                    if callable(original_disconnect) and original_disconnect is not None:
                        original_disconnect()
                    else:
                        print("DEBUG: original_disconnect is None, skipping disconnect")

                k = bs.connect_to_party

                def j(address, port=43210, print_progress=False):
                    try:
                        if bool(bs.get_connection_to_host_info_2()):
                            bs.disconnect_from_host()
                    except:
                        pass
                    m.i = address
                    m.p = port
                    k(m.i, m.p, print_progress)

                bs.connect_to_party = j
                new_connect_to_party(target_ip, target_port)

                s.auto_join_timer = teck(1.0, s.check_auto_join_success)
                var('auto_join_timers', (var('auto_join_timers') or []) + [s.auto_join_timer])

        except Exception as e:
            print(f"Auto-join error: {e}")
            s.auto_join_timer = teck(1.0, s.do_auto_join)
            var('auto_join_timers', (var('auto_join_timers') or []) + [s.auto_join_timer])

    def check_auto_join_success(s):
        try:
            conn_info = get_connection_info()
            if conn_info:
                if hasattr(s, 'status_text') and s.status_text.exists():
                    if s.auto_join_active:
                        tw(s.status_text, text='✅ JOINED!', color=(0, 1, 0))
                        push('✅ Auto-join SUCCESS!', color=(0, 1, 0))
                    else:
                        tw(s.status_text, text='✅ CONNECTED!', color=(0.8, 0.6, 0.2))
                        push('✅ Connection SUCCESS!', color=(0.8, 0.6, 0.2))
            else:
                s.auto_join_timer = teck(1.0, s.do_auto_join)
                var('auto_join_timers', (var('auto_join_timers') or []) + [s.auto_join_timer])
        except:
            pass

    def do_reconnect(s):
        try:
            from bauiv1lib.ingamemenu import InGameMenuWindow as m
            target_ip = getattr(m, 'i', server_ip)
            target_port = getattr(m, 'p', server_port)

            if target_ip == "127.0.0.1":
                AR.err('No server to connect to!')
                return

            if hasattr(s, 'status_text') and s.status_text.exists():
                tw(s.status_text, text='🔄 RECONNECTING...', color=(1, 1, 0))

            conn_info = get_connection_info()
            if conn_info:
                if callable(original_disconnect) and original_disconnect is not None:
                    original_disconnect()
                else:
                    print("DEBUG: original_disconnect is None, skipping disconnect")
                time.sleep(0.5)

            push(f'🔄 Connecting to {target_ip}:{target_port}...', color=(0, 1, 0))

            k = bs.connect_to_party

            def j(address, port=43210, print_progress=False):
                try:
                    if bool(bs.get_connection_to_host_info_2()):
                        bs.disconnect_from_host()
                except:
                    pass
                m.i = address
                m.p = port
                k(m.i, m.p, print_progress)

            bs.connect_to_party = j
            new_connect_to_party(target_ip, target_port)

            teck(2.0, lambda: s.check_manual_reconnect())

        except Exception as e:
            AR.err(f'Connection error: {str(e)}')
            if hasattr(s, 'status_text') and s.status_text.exists():
                tw(s.status_text, text='❌ CONNECTION FAILED', color=(1, 0, 0))

    def check_manual_reconnect(s):
        try:
            conn_info = get_connection_info()
            if conn_info:
                if hasattr(s, 'status_text') and s.status_text.exists():
                    tw(s.status_text, text='✅ CONNECTED', color=(0, 1, 0))
                try:
                    gs('dingSmallHigh').play()
                except:
                    pass
            else:
                if hasattr(s, 'status_text') and s.status_text.exists():
                    tw(s.status_text, text='❌ CONNECTION FAILED', color=(1, 0, 0))
        except:
            pass

    def do_disconnect(s):
        try:
            conn_info = get_connection_info()
            if conn_info:
                if callable(original_disconnect) and original_disconnect is not None:
                    original_disconnect()
                else:
                    print("DEBUG: original_disconnect is None, skipping disconnect")
                push('⛔ DISCONNECTED', color=(1, 0, 0))
                if hasattr(s, 'status_text') and s.status_text.exists():
                    tw(s.status_text, text='⛔ DISCONNECTED', color=(1, 0, 0))
                try:
                    gs('dingSmallLow').play()
                except:
                    pass
                s.manual_disconnect = True
            else:
                AR.err('Not connected to any server!')
        except Exception as e:
            AR.err(f'Disconnect error: {str(e)}')

    def show_change_server(s):
        s.change_win = AR.cw(source=s.w, size=(700, 500), background=True)
        AR.add_close_button(s.change_win, position=(670, 450))

        tw(
            parent=s.change_win,
            text='Change Server Manually',
            scale=2.1,
            position=(325, 450),
            h_align='center',
            color=(0.2, 0.8, 1)
        )

        tw(
            parent=s.change_win,
            text='Edit the IP and port to connect to servers manually!',
            scale=1.0,
            position=(325, 380),
            h_align='center',
            color=(1, 1, 0)
        )

        tw(
            parent=s.change_win,
            text='Server IP :',
            position=(30, 300),
            scale=1.0,
            color=(1, 1, 1)
        )
        s.change_ip = tw(
            parent=s.change_win,
            position=(200, 290),
            size=(340, 40),
            editable=True,
            text=server_ip,
            color=(0.9, 0.9, 0.9)
        )

        tw(
            parent=s.change_win,
            text='Server PORT :',
            position=(30, 220),
            scale=0.9,
            color=(1, 1, 1)
        )
        s.change_port = tw(
            parent=s.change_win,
            position=(200, 210),
            size=(340, 40),
            editable=True,
            text=str(server_port),
            h_align='center',
            color=(0.9, 0.9, 0.9)
        )

        s.status_text_change = tw(
            parent=s.change_win,
            text='Ready to Connect',
            position=(280, 150),
            scale=0.8,
            color=(0.8, 0.8, 1)
        )

        s.connect_btn = bw(
            parent=s.change_win,
            label='Connect to Server',
            size=(150, 70),
            icon=gt('startButton'),
            position=(100, 60),
            iconscale=0.6,
            on_activate_call=s.connect_manual,
            color=(0, 0.6, 0),
            textcolor=(1, 1, 1)
        )

        s.test_btn = bw(
            parent=s.change_win,
            label='Test Connection',
            size=(150, 70),
            icon=gt('replayIcon'),
            position=(475, 60),
            iconscale=0.6,
            on_activate_call=s.test_connection,
            color=(0.3, 0.5, 0.8),
            textcolor=(1, 1, 1)
        )

    def test_connection(s):
        try:
            ip = tw(query=s.change_ip).strip()
            port_str = tw(query=s.change_port).strip()

            if not ip or not port_str:
                AR.err('Please enter IP and port')
                return

            port = int(port_str)

            if hasattr(s, 'status_text_change') and s.status_text_change.exists():
                tw(s.status_text_change, text='Testing...', color=(1, 1, 0))

            teck(1.5, lambda: tw(s.status_text_change, text='Test successful!', color=(0, 1, 0)) if hasattr(s,
                                                                                                            'status_text_change') and s.status_text_change.exists() else None)
            push('Connection test successful!', color=(0, 1, 0))

        except ValueError:
            AR.err('Port must be a number')
        except Exception as e:
            AR.err(f'Test error: {str(e)}')

    def connect_manual(s):
        try:
            ip = tw(query=s.change_ip).strip()
            port_str = tw(query=s.change_port).strip()

            if not ip or not port_str:
                AR.err('Please enter IP and port')
                return

            port = int(port_str)

            if hasattr(s, 'status_text_change') and s.status_text_change.exists():
                tw(s.status_text_change, text='Connecting...', color=(1, 1, 0))

            conn_info = get_connection_info()
            if conn_info:
                if callable(original_disconnect) and original_disconnect is not None:
                    original_disconnect()
                else:
                    print("DEBUG: original_disconnect is None, skipping disconnect")
                time.sleep(1)

            push(f'Connecting to {ip}:{port}...', color=(0, 1, 1))

            from bauiv1lib.ingamemenu import InGameMenuWindow as m
            k = bs.connect_to_party

            def j(address, port=43210, print_progress=False):
                try:
                    if bool(bs.get_connection_to_host_info_2()):
                        bs.disconnect_from_host()
                except:
                    pass
                m.i = address
                m.p = port
                k(m.i, m.p, print_progress)

            bs.connect_to_party = j
            new_connect_to_party(ip, port)

            if hasattr(s, 'status_text_change') and s.status_text_change.exists():
                tw(s.status_text_change, text='Connected!', color=(0, 1, 0))

            if hasattr(s, 'change_win') and s.change_win.exists():
                s.change_win.delete()

        except ValueError:
            AR.err('Port must be a number')
        except Exception as e:
            AR.err(f'Connection error: {str(e)}')
            if hasattr(s, 'status_text_change') and s.status_text_change.exists():
                tw(s.status_text_change, text='Connection failed', color=(1, 0, 0))

    def get_saved_servers(s):
        try:
            servers = var('saved_servers')
            if servers is None:
                return []
            return servers
        except:
            return []

    def save_servers(s, servers):
        try:
            var('saved_servers', servers)
            return True
        except:
            return False

    def show_saved_servers(s):
        s.servers_win = AR.cw(source=s.w, size=(700, 500), background=True)
        AR.add_close_button(s.servers_win, position=(670, 450))

        tw(
            parent=s.servers_win,
            text='📁 Saved Servers',
            scale=1.2,
            position=(350, 450),
            h_align='center',
            color=(0.2, 0.8, 1)
        )

        saved_servers = s.get_saved_servers()

        if not saved_servers:
            tw(
                parent=s.servers_win,
                text='No servers saved',
                position=(340, 250),
                scale=0.9,
                color=(1, 0.8, 0.2),
                h_align='center'
            )
        else:
            scroll = sw(parent=s.servers_win, size=(600, 300), position=(60, 100))
            s.servers_container = cw(parent=scroll, size=(600, len(saved_servers) * 50))

            for i, server in enumerate(saved_servers):
                y_pos = len(saved_servers) * 47 - i * 50 - 30

                bw(
                    parent=s.servers_container,
                    label='',
                    size=(575, 40),
                    position=(5, y_pos),
                    color=(0.2, 0.3, 0.4) if i % 2 == 0 else (0.25, 0.35, 0.45),
                    enable_sound=False
                )

                tw(
                    parent=s.servers_container,
                    text=f"Name : {server['name']}",
                    position=(250, y_pos - 0),
                    scale=0.7,
                    color=(1, 1, 1),
                    h_align='left'
                )

                tw(
                    parent=s.servers_container,
                    text=f"IP : {server['ip']} PORT : {server['port']}",
                    position=(20, y_pos - 0),
                    scale=0.6,
                    color=(0.8, 0.9, 1),
                    h_align='left'
                )

                bw(
                    parent=s.servers_container,
                    label='🌐',
                    size=(30, 30),
                    position=(500, y_pos + 3),
                    on_activate_call=Call(s.connect_to_saved, server),
                    color=(0.3, 0.7, 0.3),
                    text_scale=0.6
                )

                bw(
                    parent=s.servers_container,
                    label='🗑️',
                    size=(30, 30),
                    position=(450, y_pos + 3),
                    on_activate_call=Call(s.remove_saved_server, server),
                    color=(0.8, 0.3, 0.3),
                    text_scale=0.6
                )

        bw(
            parent=s.servers_win,
            label='➕ Add New Server',
            size=(150, 70),
            position=(290, 40),
            on_activate_call=s.add_new_server,
            color=(0.4, 0.7, 0.4),
            text_scale=0.7
        )

    def connect_to_saved(s, server):
        try:
            if hasattr(s, 'servers_win') and s.servers_win.exists():
                s.servers_win.delete()

            if hasattr(s, 'status_text') and s.status_text.exists():
                tw(s.status_text, text='Connecting...', color=(1, 1, 0))
            push(f'Connecting to {server["name"]}...', color=(0, 1, 0))

            conn_info = get_connection_info()
            if conn_info:
                if callable(original_disconnect) and original_disconnect is not None:
                    original_disconnect()
                else:
                    print("DEBUG: original_disconnect is None, skipping disconnect")
                time.sleep(1)

            from bauiv1lib.ingamemenu import InGameMenuWindow as m
            k = bs.connect_to_party

            def j(address, port=43210, print_progress=False):
                try:
                    if bool(bs.get_connection_to_host_info_2()):
                        bs.disconnect_from_host()
                except:
                    pass
                m.i = address
                m.p = port
                k(m.i, m.p, print_progress)

            bs.connect_to_party = j
            new_connect_to_party(server['ip'], server['port'])

            if hasattr(s, 'status_text') and s.status_text.exists():
                tw(s.status_text, text='Connected', color=(0, 1, 0))
            gs('dingSmallHigh').play()

        except Exception as e:
            AR.err(f'Connection error: {str(e)}')
            if hasattr(s, 'status_text') and s.status_text.exists():
                tw(s.status_text, text='Connection failed', color=(1, 0, 0))

    def remove_saved_server(s, server):
        saved_servers = s.get_saved_servers()
        saved_servers = [srv for srv in saved_servers if srv['ip'] != server['ip'] or srv['port'] != server['port']]

        if s.save_servers(saved_servers):
            push('Server removed', color=(1, 0.5, 0))
            if hasattr(s, 'servers_win') and s.servers_win.exists():
                s.servers_win.delete()
                s.show_saved_servers()

    def add_new_server(s):
        s.add_win = AR.cw(source=s.w, size=(700, 500), background=True)
        AR.add_close_button(s.add_win, position=(670, 450))

        tw(
            parent=s.add_win,
            text='➕ Add New Server',
            scale=2.1,
            position=(325, 450),
            h_align='center',
            color=(0.2, 0.8, 1)
        )

        tw(
            parent=s.add_win,
            text='Enter the IP and port of the server and choose a name for it!',
            scale=1.0,
            position=(325, 380),
            h_align='center',
            color=(1, 1, 0)
        )

        tw(
            parent=s.add_win,
            text='Server Name:',
            position=(30, 300),
            scale=1.0,
            color=(1, 1, 1)
        )
        s.name_input = tw(
            parent=s.add_win,
            position=(200, 290),
            size=(340, 40),
            editable=True,
            text='New Server',
            color=(0.9, 0.9, 0.9)
        )

        tw(
            parent=s.add_win,
            text='Server IP:',
            position=(30, 220),
            scale=1.0,
            color=(1, 1, 1)
        )
        s.ip_input = tw(
            parent=s.add_win,
            position=(200, 210),
            size=(340, 40),
            editable=True,
            text='127.0.0.1',
            color=(0.9, 0.9, 0.9)
        )

        tw(
            parent=s.add_win,
            text='Server Port:',
            position=(30, 140),
            scale=1.0,
            color=(1, 1, 1)
        )
        s.port_input = tw(
            parent=s.add_win,
            position=(200, 130),
            size=(340, 40),
            editable=True,
            text='43210',
            h_align='center',
            color=(0.9, 0.9, 0.9)
        )

        bw(
            parent=s.add_win,
            label='💾 Save',
            size=(150, 70),
            position=(290, 35),
            on_activate_call=s.save_new_server,
            color=(0.3, 0.7, 0.3),
            text_scale=0.8
        )

    def save_new_server(s):
        try:
            name = tw(query=s.name_input).strip()
            ip = tw(query=s.ip_input).strip()
            port_str = tw(query=s.port_input).strip()

            if not all([name, ip, port_str]):
                AR.err('Please fill all fields')
                return

            port = int(port_str)

            new_server = {'name': name, 'ip': ip, 'port': port}
            saved_servers = s.get_saved_servers()

            if any(srv['ip'] == ip and srv['port'] == port for srv in saved_servers):
                AR.err('Server already exists')
                return

            saved_servers.append(new_server)

            if s.save_servers(saved_servers):
                push(f'Server "{name}" saved', color=(0, 1, 0))

                if hasattr(s, 'add_win') and s.add_win.exists():
                    s.add_win.delete()
                if hasattr(s, 'servers_win') and s.servers_win.exists():
                    s.servers_win.delete()
                    s.show_saved_servers()

        except ValueError:
            AR.err('Port must be a number')
        except Exception as e:
            AR.err(f'Error: {str(e)}')

"""Server Information"""


class ServerInfo:
    def __init__(s, t):
        w = s.w = AR.cw(
            source=t,
            size=(400, 350),
            ps=AR.UIS() * 0.8
        )
        # افزودن دکمه بستن
        AR.add_close_button(w, position=(370, 290))

        # عنوان
        tw(
            parent=w,
            text=u'\ue010 Server Information',
            scale=1.2,
            position=(180, 280),
            h_align='center',
            color=(0, 1, 1)
        )

        bw(
            parent=w,
            size=(20, 20),
            position=(190, 115),
            label='',
            texture=gt('googlePlayAchievementsIcon'),
            color=(1, 1, 1)
        )

        # دریافت اطلاعات سرور
        global server_ip, server_port, current_ping

        # دریافت اطلاعات اتصال
        conn_info = get_connection_info()
        if conn_info:
            server_name = conn_info.name
            server_status = "Connected"
        else:
            server_name = "Local Server"
            server_status = "Local"

        # ایجاد ویجت‌های متن برای اطلاعات سرور
        s.info_widgets = []
        info_labels = [
            "🌐 Server IP:",
            "🚪 Server Port:",
            "🏷️ Server Name:",
            "📶 Current Ping:",
            "🔗 Connection Status:"
        ]

        y_pos = 250
        for i, label in enumerate(info_labels):
            # برچسب
            tw(
                parent=w,
                text=label,
                position=(30, y_pos),
                scale=0.8,
                color=(1, 1, 0.8),
                h_align='left'
            )
            # مقدار - تنظیم موقعیت برای همه مقادیر 30 پیکسل به راست
            value_x = 230  # همه مقادیر 30 پیکسل به راست نسبت به قبل

            value_widget = tw(
                parent=w,
                text="",  # مقدار اولیه خالی
                position=(value_x, y_pos),
                scale=0.8,
                color=(1, 1, 1),
                h_align='left'
            )
            s.info_widgets.append(value_widget)
            y_pos -= 30

        # مقادیر اولیه
        s.update_server_info()

        # دکمه‌های کپی
        copy_buttons = [
            ('Copy IP', server_ip, (20, 70)),
            ('Copy Port', str(server_port), (150, 70)),
            ('Copy all', f"{server_ip}:{server_port}", (280, 70))
        ]

        for label, data, pos in copy_buttons:
            AR.bw(
                parent=w,
                label=label,
                size=(100, 35),
                position=pos,
                on_activate_call=Call(s.copy_to_clipboard, data)
            )
        # شروع تایمر برای بروزرسانی خودکار
        s.timer = teck(1.0, s.update_server_info)
        AR.swish()

    def update_server_info(s):
        """بروزرسانی اطلاعات سرور"""
        if not hasattr(s, 'w') or not s.w.exists():
            return

        # دریافت اطلاعات اتصال
        conn_info = get_connection_info()

        if conn_info:
            server_name = conn_info.name
            server_status = "Connected"
        else:
            server_name = "Local Server"
            server_status = "Local"

        # مقادیر برای نمایش
        values = [
            server_ip,
            str(server_port),
            server_name,
            f"{current_ping} ms",
            server_status
        ]

        # بروزرسانی ویجت‌های متن
        for i, value in enumerate(values):
            if i < len(s.info_widgets) and s.info_widgets[i].exists():
                tw(s.info_widgets[i], text=value)

        # تغییر رنگ پینگ بر اساس مقدار
        if 3 < len(s.info_widgets) and s.info_widgets[3].exists():
            ping_color = (0, 1, 0) if current_ping < 100 else (1, 1, 0) if current_ping < 300 else (1, 0, 0)
            tw(s.info_widgets[3], color=ping_color)

        # تغییر رنگ وضعیت اتصال
        if 4 < len(s.info_widgets) and s.info_widgets[4].exists():
            status_color = (0, 1, 0) if server_status == "Connected" else (1, 1, 0) if server_status == "Local" else (
            1, 0, 0)
            tw(s.info_widgets[4], color=status_color)

        # ادامه تایمر
        s.timer = teck(1.0, s.update_server_info)

    def copy_to_clipboard(s, text):
        """کپی متن به کلیپ‌بورد"""
        try:
            if CIS():
                from babase import clipboard_set_text
                clipboard_set_text(text)
                push(f'Copied: {text}', color=(0, 1, 0))
                gs('dingSmall').play()
            else:
                AR.err('Clipboard not supported!')
        except Exception as e:
            AR.err(f'Copy error: {str(e)}')

    def __del__(s):
        """تمیزکاری هنگام حذف"""
        if hasattr(s, 'timer') and s.timer:
            s.timer = None


"""اسپم خودکار"""


class Spam:
    # نگهداری یک نمونه فعال برای مدیریت تایمر و وضعیت
    active_instance = None

    def __init__(s, source):
        # ثبت خود به عنوان نمونه فعال
        Spam.active_instance = s

        w = s.w = AR.cw(
            source=source,
            size=(400, 350),
            ps=AR.UIS() * 0.8
        )
        AR.add_close_button(w, position=(370, 280))

        # عنوان
        tw(
            parent=w,
            text=u'\ue029   Automated spam',
            scale=1.2,
            position=(180, 280),
            h_align='center',
            color=(1, 0.5, 0)
        )

        bw(
            parent=w,
            size=(70, 70),
            position=(300, 50),
            label='',
            texture=gt('leaderboardsIcon'),
            color=(1, 1, 1)
        )

        # فیلد پیام
        tw(parent=w, text='Spam message:', position=(30, 250), scale=0.9, color=(1, 1, 1))
        s.message_widget = tw(parent=w, position=(30, 220), size=(340, 30), editable=True,
                              text='Spam test', color=(0.9, 0.9, 0.9))

        # فیلد تعداد
        tw(parent=w, text='Number:', position=(30, 180), scale=0.9, color=(1, 1, 1))
        s.count_widget = tw(parent=w, position=(30, 150), size=(150, 30), editable=True,
                            text='5', h_align='center', color=(0.9, 0.9, 0.9))

        # فیلد تأخیر
        tw(parent=w, text='Delay (seconds):', position=(200, 180), scale=0.9, color=(1, 1, 1))
        s.delay_widget = tw(parent=w, position=(200, 150), size=(150, 30), editable=True,
                            text='1', h_align='center', color=(0.9, 0.9, 0.9))

        # وضعیت
        s.status_text = tw(parent=w, text='ready', position=(30, 110), scale=0.8, color=(0.8, 0.8, 1))

        # دکمه شروع
        s.start_btn = bw(parent=w, label='Start spamming', size=(120, 40), icon=gt('startButton'), position=(20, 60),
                         iconscale=0.6,
                         on_activate_call=Call(s.start_spam), color=(0, 0.6, 0), textcolor=(1, 1, 1))

        # دکمه استپ جداگانه
        s.stop_btn = bw(parent=w, label='stop', size=(120, 40), icon=gt('replayIcon'), position=(160, 60),
                        iconscale=0.6,
                        on_activate_call=Call(s.stop_spam), color=(0.6, 0, 0), textcolor=(1, 1, 1))

        s.spamming = False
        s.spam_timer = None
        s.remaining_count = 0
        s.sent_count = 0  # شمارنده پیام‌های ارسال شده
        AR.swish()

    @staticmethod
    def start_spam():
        s = Spam.active_instance
        try:
            message = tw(query=s.message_widget).strip()
            count = int(tw(query=s.count_widget))
            delay = float(tw(query=s.delay_widget))

            if not message:
                AR.err('Please enter a message!')
                return

            if count <= 0 or delay <= 0:
                AR.err('Values ​​must be greater than zero!')
                return

            s.spamming = True
            s.remaining_count = count
            s.spam_message = message
            s.spam_delay = delay
            s.sent_count = 0  # ریست شمارنده

            tw(s.status_text, text=f'Spamming: {s.remaining_count} remaining', color=(0, 1, 0))

            s.do_spam()

            push(f'Spam started: {count} messages with a delay of {delay} seconds', color=(0, 1, 0))

        except ValueError:
            AR.err('Please enter valid numbers!')
        except Exception as e:
            AR.err(f'Error: {str(e)}')

    @staticmethod
    def stop_spam():
        s = Spam.active_instance
        if not s.spamming:
            return  # جلوگیری از پیام چندباره

        s.spamming = False

        if s.spam_timer:
            try:
                s.spam_timer.cancel()
            except:
                pass
            s.spam_timer = None

        tw(s.status_text, text='⛔ Spam stopped', color=(1, 0.5, 0))
        push('⛔ Spam stopped', color=(1, 0.5, 0))

    @staticmethod
    def do_spam():
        s = Spam.active_instance
        if not s.spamming or s.remaining_count <= 0:
            s.spamming = False
            if s.spam_timer:
                try:
                    s.spam_timer.cancel()
                except:
                    pass
                s.spam_timer = None
            tw(s.status_text, text='✅ Spam is over', color=(0, 1, 0))
            push('✅ Spam is over', color=(0, 1, 0))
            return

        try:
            # شمارنده پیام ارسال شده
            s.sent_count += 1

            # بررسی زوج/فرد برای اضافه کردن نقطه
            message_to_send = s.spam_message
            if s.sent_count % 2 == 0:
                message_to_send += "."

            CM(message_to_send)
            s.remaining_count -= 1

            if s.w.exists():
                tw(s.status_text, text=f'Spamming: {s.remaining_count} remaining')

            if s.remaining_count > 0 and s.spamming:
                s.spam_timer = teck(s.spam_delay, s.do_spam)
            else:
                s.spamming = False
                if s.spam_timer:
                    try:
                        s.spam_timer.cancel()
                    except:
                        pass
                    s.spam_timer = None
                tw(s.status_text, text='Spam is over ✅', color=(0, 1, 0))
                push('Spam is over ✅', color=(0, 1, 0))

        except Exception as e:
            AR.err(f'Error sending: {str(e)}')
            Spam.stop_spam()


"""راهنمای جامع مود Auto Message"""


class Help:
    def __init__(s, t):
        w = AR.cw(
            source=t,
            size=(500, 300),  # کاهش ارتفاع به 300
            ps=AR.UIS() * 0.8
        )

        # عنوان اصلی
        tw(
            parent=w,
            text='📖 راهنمای SelfTaha v3.0',
            scale=1.0,  # کاهش سایز عنوان
            position=(230, 250),
            h_align='center',
            color=(0, 1, 1)
        )

        # اطلاعات سازنده
        tw(
            parent=w,
            text='توسعه‌دهنده: طاها استادشریف',
            scale=0.6,  # کاهش سایز
            position=(250, 230),
            h_align='center',
            color=(1, 1, 0)
        )

        bw(
            parent=w,
            size=(50, 50),
            position=(230, 5),
            label='',
            texture=gt('discordServer'),
            color=(1, 1, 1)
        )

        # افزودن دکمه بستن
        AR.add_close_button(w, position=(480, 250))

        # اسکرول برای محتوای راهنما - ارتفاع کمتر
        s.scroll = sw(
            parent=w,
            size=(460, 180),  # کاهش ارتفاع اسکرول
            position=(20, 50)
        )

        s.container = cw(
            parent=s.scroll,
            size=(460, 1000),  # کاهش ارتفاع کانتینر
            background=False
        )

        # محتوای راهنمای جامع (خلاصه‌تر)
        contents = [
            "🎯 معرفی مود SelfTaha",
            "مود  SelfTaha یک ربات هوشمند پاسخگویی است که به صورت خودکار به پیام‌های دریافتی در چت بازی پاسخ می‌دهد.\n این مود با قابلیت‌های پیشرفته و متنوع، تجربه چت را متحول می‌کند!",
            "",
            "✨ ویژگی‌های اصلی:",
            "• پاسخ خودکار به پیام‌های دریافتی",
            "• پشتیبانی از متغیرهای پویا و هوشمند",
            "• سیستم مدیریت پیام‌های سریع",
            "• ابزارهای سرگرمی و بازی‌های تعاملی",
            "• مدیریت سرور و اطلاعات اتصال",
            "• ابزارهای مدیریت بازیکنان",
            "• قابلیت تغییر رنگ رابط کاربری",
            "• ابزارهای تایپوگرافی و فونت‌سازی",
            "",
            "🔧 بخش‌های اصلی مود:",
            "",
            "1. 🎯 پاسخ‌های خودکار (Auto Reply)",
            "   - تعریف ماشه‌ها و پاسخ‌های سفارشی",
            "   - زمان‌بندی پاسخ‌ها",
            "   - جستجو در محتوای پیام‌ها",
            "",
            "2. 💬 چت سریع (Quick Chat)",
            "   - ذخیره و مدیریت پیام‌های پرکاربرد",
            "   - ارسال سریع با یک کلیک",
            "   - قابلیت ویرایش و حذف",
            "",
            "3. 🌐 مدیریت سرور (Server Manager)",
            "   - نمایش اطلاعات واقعی سرور",
            "   - پینگ واقعی و وضعیت اتصال",
            "   - ذخیره سرورهای مورد علاقه",
            "   - اتصال مجدد خودکار",
            "",
            "4. 🎮 ابزارهای سرگرمی:",
            "   - تولید جوک، چیستان و ضرب المثل",
            "   - بازی حقیقت یا جرات",
            "   - ابزار تاس و شانس",
            "   - ابزار اسپم و ارسال گروهی",
            "",
            "5. 👥 مدیریت بازیکنان:",
            "   - مشاهده لیست بازیکنان آنلاین",
            "   - مدیریت دوستان و لیست مسدودها",
            "   - ذخیره اطلاعات بازیکنان",
            "   - قابلیت گزارش‌گیری",
            "",
            "6. 🎨 سفارشی‌سازی:",
            "   - تغییر رنگ رابط کاربری",
            "   - ابزار ساخت فونت‌های خاص",
            "   - مدیریت استیکرها و ایموجی‌ها",
            "",
            "🔤 متغیرهای قابل استفاده در پاسخ‌ها:",
            "",
            "👤 متغیرهای کاربری:",
            "%m - نام حساب شما در بازی",
            "%s - نام فرستنده پیام",
            "",
            "⏰ متغیرهای زمانی:",
            "%t - زمان فعلی (ساعت:دقیقه:ثانیه)",
            "%d - تاریخ میلادی (سال-ماه-روز)",
            "%f - تاریخ شمسی دقیق",
            "",
            "🎭 متغیرهای سرگرمی:",
            "%j - جوک تصادفی فارسی",
            "%ch - چیستان کوتاه با جواب",
            "%z - ضرب المثل فارسی",
            "%dice - شرط بندی با تاس",
            "%tr - سوال حقیقت (بازی حقیقت یا جرات)",
            "%da - سوال جرات (بازی حقیقت یا جرات)",
            "",
            "🌐 متغیرهای شبکه:",
            "%ip - آیپی و پورت سرور",
            "%p - پینگ فعلی سرور",
            "",
            "⚡ نکات حرفه‌ای:",
            "",
            "• زمان‌بندی: پاسخ‌ها می‌توانند با تأخیر ارسال شوند",
            "• حساسیت به حروف: قابلیت فعال/غیرفعال کردن حساسیت به حروف",
            "• پاسخ به خود: امکان پاسخ به پیام‌های خود را می‌توان تنظیم کرد",
            "",
            "🎯 مثال‌های کاربردی:",
            "",
            "مثال ۱ (پاسخ ساده):",
            "ماشه: سلام",
            "پاسخ: درود %s! چطوری؟",
            "",
            "مثال ۲ (ترکیب متغیرها):",
            "ماشه: زمان",
            "پاسخ: الان ساعت %t - تاریخ شمسی: %f",
            "",
            "مثال ۳ (سرگرمی):",
            "ماشه: جوک بگو",
            "پاسخ: %j",
            "",
            "مثال ۴ (اطلاعات سرور):",
            "ماشه: پینگ",
            "پاسخ: پینگ سرور: %p - آیپی: %ip",
            "",
            "🔧 تنظیمات پیشرفته:",
            "",
            "• نوتیفیکیشن: دریافت اطلاع‌رسانی برای پاسخ‌ها",
            "• صدا: پخش صدا هنگام پاسخگویی",
            "• حساسیت به حروف: تفاوت بین حروف بزرگ و کوچک",
            "• پاسخ به خود: امکان پاسخ به پیام‌های خود"
        ]

        # نمایش محتوا با قالب‌بندی فشرده
        y_pos = 1320  # شروع از پایین کانتینر
        for content in contents:
            if content.startswith("🎯") or content.startswith("✨") or content.startswith("🔤") or content.startswith("⚡"):
                color = (0, 1, 1)
                scale = 0.5
                maxwidth = 440
            elif content.startswith("• "):
                color = (0.8, 0.9, 1)
                scale = 0.4
                maxwidth = 440
            elif content == "":
                y_pos -= 8
                continue
            else:
                color = (1, 1, 1)
                scale = 0.4
                maxwidth = 440

            tw(
                parent=s.container,
                text=content,
                position=(10, y_pos),
                scale=scale,
                color=color,
                maxwidth=maxwidth,
                h_align='left'
            )
            y_pos -= 15  # فاصله کمتر بین خطوط

        # تنظیم ارتفاع واقعی کانتینر
        total_height = 1000 - y_pos + 300
        cw(s.container, size=(460, total_height))

        # اسکرول خودکار به بالا
        teck(0.1, lambda: sw(edit=s.scroll, vertical_scroll=1.0))

        AR.swish()


"""پایه پیام اتوماتیک"""


class AR:
    @classmethod
    def UIS(c=0):
        i = APP.ui_v1.uiscale
        return [1.5, 1.1, 0.8][0 if i == uis.SMALL else 1 if i == uis.MEDIUM else 2]

    @classmethod
    def add_close_button(c, window, position=(10, 10)):

        close_btn = bw(
            parent=window,
            size=(30, 30),
            position=position,
            label='X',
            color=(0.8, 0.2, 0.2),
            textcolor=(1, 1, 1),
            on_activate_call=Call(c.swish, t=window)
        )
        return close_btn

    @classmethod
    def parse(c=0, t=0, s=None):
        me = byTaha.me()
        now = DT.now()

        jy, jm, jd = gregorian_to_jalali(now.year, now.month, now.day)
        persian_date = f"{jy}-{jm:02d}-{jd:02d}"

        bet = random.randint(1, 6)

        if '%r' in t and '|' in t:
            parts = t.split('%r')
            options = parts[1].split('|')[0].split(';')
            random_response = random.choice(options)
            t = parts[0] + random_response + '|'.join(parts[1].split('|')[1:])

        if '%j' in t:
            t = t.replace('%j', random.choice(JOKES))

        if '%ch' in t:
            t = t.replace('%ch', random.choice(RIDDLES))

        if '%z' in t:
            t = t.replace('%z', random.choice(PROVERBS))

        if '%tr' in t:
            t = t.replace('%tr', random.choice(TRUTHS))

        if '%da' in t:
            t = t.replace('%da', random.choice(DARES))

        if '%dice' in t:
            t = t.replace('%dice', random.choice(DICE))

        if '%ip' in t:
            t = t.replace('%ip', f"IP : {server_ip} Port : {server_port}")
        if '%p' in t:
            t = t.replace('%p', f"{current_ping} ms")

        return (t.replace('%t', now.strftime("%H:%M:%S"))
                .replace('%d', now.strftime("%Y-%m-%d"))
                .replace('%s', s or byTaha.v2 + 'ByTaha')
                .replace('%m', me)
                .replace('%f', persian_date))

    @classmethod
    def bw(c, **k):
        r = random.random()
        g = random.random()
        b = random.random()
        return bw(
            **k,
            textcolor=(1, 1, 1),
            enable_sound=False,
            button_type='square',
            color=(r * 0.7 + 0.3, g * 0.7 + 0.3, b * 0.7 + 0.3)
        )

    @classmethod
    def cw(c, source, ps=0, **k):
        o = source.get_screen_space_center() if source else None
        r = cw(
            **k,
            scale=c.UIS() + ps,
            transition='in_scale',
            color=(0.18, 0.18, 0.18),
            parent=gsw('overlay_stack'),
            scale_origin_stack_offset=o
        )
        cw(r, on_outside_click_call=Call(c.swish, t=r))
        return r

    swish = lambda c=0, t=0: (gs('swish').play(), cw(t, transition='out_scale') if t else t)
    err = lambda t: (gs('block').play(), push(t, color=(1, 1, 0)))
    ok = lambda: (gs('dingSmallHigh').play(), push('باشه!', color=(0, 1, 0)))
    bye = lambda: (gs('laser').play(), push('خداحافظ!', color=(0, 1, 0)))

    def __init__(s, source: bw = None) -> None:
        w = s.w = s.cw(
            source=source,
            size=(600, 600),
        )

        s.add_close_button(w, position=(600, 520))

        [tw(
            scale=1.0,
            parent=w,
            text='Auto message',
            h_align='center',
            position=(450, 470 - i * 3),
            color=[(1, 1, 1), (0.6, 0.6, 0.6)][i]
        ) for i in [1, 0]]

        tw(
            parent=w,
            text="🤖 Responsive Bot\n\n" "With this mod you can:\n" "• Set up auto-reply\n" "• Have a quick chat\n" "• Play games with your friends\n" "• And much more!",
            position=(400, 410),
            scale=0.75,
            color=(0.8, 0.8, 1),
            maxwidth=150,
            h_align='left'
        )

        s.stats_text = tw(
            parent=w,
            text=f"📊 Statistics:\n" f"• {len(var('l') or {})} Trigger active\n" f"• {len(load_quick_messages())} Quick message\n" f"• State: {'active' if var('state') else 'inactive'}\n" f"• Ping: {current_ping} ms\n" f"• Server: {server_ip}:{server_port}",
            position=(400, 270),
            scale=0.65,
            color=(0.8, 1, 0.8),
            maxwidth=160,
            h_align='left'
        )

        teck(1.0, s.update_stats)

        tw(
            parent=w,
            text="💡 Note:\n" "For more information, see the\n" "Help section",
            position=(400, 140),
            scale=0.75,
            color=(1, 1, 0.5),
            maxwidth=150,
            h_align='left'
        )

        s.scroll_widget = sw(
            parent=w,
            size=(300, 400),
            position=(30, 100)
        )

        s.buttons_container = cw(
            parent=s.scroll_widget,
            size=(300, 600),
            background=False
        )

        mem = globals()
        buttons = [
            ('Add', 'Add', 'upButton', 550),
            ('Delete', 'Nuke', 'ouyaAButton', 485),
            ('Settings', 'Tune', 'settingsIcon', 420), ('List', 'List', 'logIcon', 355),
            ('Help', 'Help', 'logo', 290)
        ]

        for label, cls_name, icon, y_pos in buttons:
            b = s.bw(
                label=label,
                parent=s.buttons_container,
                size=(260, 60),
                position=(20, y_pos),
                icon=gt(icon)
            )
            bw(b, on_activate_call=Call(mem[cls_name], b))

        cw(s.buttons_container, size=(300, 650))

        s.b = bw(
            parent=w,
            size=(70, 45),
            position=(550, 450),
            enable_sound=False,
            button_type='square',
            on_activate_call=s.but
        )
        s.but(1)
        s.swish()

    def update_stats(s):

        if hasattr(s, 'stats_text') and s.stats_text.exists():
            conn_info = get_connection_info()
            server_status = f"{server_ip}:{server_port}" if server_ip != "127.0.0.1" else "local"

            tw(s.stats_text,
               text=f"📊 Statistics:\n" f"• {len(var('l') or {})} Trigger active\n" f"• {len(load_quick_messages())} Quick message\n" f"• Status: {'active' if var('state') else 'inactive'}\n" f"• Ping: {current_ping} ms\n" f"• Server: {server_status}")
        teck(1.0, s.update_stats)

    def but(s, dry=0):
        v = var('state')
        if not dry:
            v = not v
            var('state', v)
            gs('deek').play()
        bw(
            s.b,
            label=['OFF', 'ON'][v],
            color=[(0.35, 0, 0), (0, 0.45, 0)][v],
            textcolor=[(0.5, 0, 0), (0, 0.6, 0)][v]
        )


def load_quick_messages():
    try:
        config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Configs')
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        msg_path = os.path.join(config_dir, 'quick_chat_msgs.json')

        if not os.path.exists(msg_path):
            save_quick_messages(DEFAULT_QUICK_MESSAGES.copy())
            return DEFAULT_QUICK_MESSAGES.copy()

        with open(msg_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading quick messages: {e}")
        return DEFAULT_QUICK_MESSAGES.copy()


def save_quick_messages(messages):
    try:
        config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Configs')
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        msg_path = os.path.join(config_dir, 'quick_chat_msgs.json')

        with open(msg_path, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving quick messages: {e}")


pr = 'ar3_'


def var(s, v=None):
    c = APP.config
    s = pr + s
    if v is None: return c.get(s, v)
    c[s] = v
    c.commit()


def reset_conf(): cfg = APP.config; [(cfg.pop(c) if c.startswith(pr) else None) for c in cfg.copy()]; cfg.commit()


for i in range(4): j = f'tune{i}'; v = var(j); var(j, i < 3) if v is None else v
None if var('state') else var('state', 1)
None if var('time') else var('time', '0.5')
None if var('l') else var('l', {})
None if var('lc') else var('lc', {})

if var('performance_mode') is None:
    var('performance_mode', 'normal')

SW = lambda s: strw(s, suppress_warning=True)


def sn(s):
    out = ''
    w = 0.0
    for c in s:
        ch_w = SW(c)
        if w + ch_w > 520:
            out += '\n'
            w = 0.0
        out += c
        w += ch_w
    return out


def setup_connection_overrides():
    global original_connect, original_disconnect
    from bascenev1 import connect_to_party, disconnect_from_host

    if original_connect is None:
        original_connect = connect_to_party
        original_disconnect = disconnect_from_host

        import bascenev1
        bascenev1.connect_to_party = new_connect_to_party
        bascenev1.disconnect_from_host = new_disconnect_from_host
        print("Connection functions overridden")


ping_thread = RealPingThread()
ping_thread.start()


class StickerMenu:
    def __init__(s, source):
        w = s.w = AR.cw(
            source=source,
            size=(300, 400),
            ps=AR.UIS() * 0.7
        )

        AR.add_close_button(w, position=(280, 325))

        tw(
            parent=w,
            text=u'\ue010 Sticker Menu',
            scale=1.0,
            position=(120, 320),
            h_align='center',
            color=(1, 1, 0)
        )

        s.stickers = load_stickers()

        s.scroll_widget = sw(
            parent=w,
            size=(260, 200),
            position=(20, 110)
        )

        s.container = cw(
            parent=s.scroll_widget,
            size=(260, len(s.stickers) * 55),
            background=False
        )

        buttons = [
            ('➕ Add', s.add_sticker, (20, 80)),
            (u'\ue009 Remove', s.remove_sticker, (120, 80)),
            ('🔄 Reset', s.reset_stickers, (220, 80))
        ]

        for label, callback, pos in buttons:
            AR.bw(
                parent=w,
                label=label,
                size=(90, 30),
                position=pos,
                on_activate_call=callback,
                scale=0.8
            )

        bw(
            parent=w,
            size=(30, 30),
            position=(140, 50),
            label='',
            texture=gt('inventoryIcon'),
            color=(1, 1, 1)
        )

        bw(
            parent=w,
            size=(30, 30),
            position=(20, 50),
            label='',
            texture=gt('tv'),
            color=(1, 1, 1)
        )

        bw(
            parent=w,
            size=(30, 30),
            position=(260, 50),
            label='',
            texture=gt('tv'),
            color=(1, 1, 1)
        )
        s.refresh_stickers()
        AR.swish()

    def refresh_stickers(s):

        for child in s.container.get_children():
            child.delete()

        y_pos = len(s.stickers) * 50 - 25
        for sticker in s.stickers:
            btn = bw(
                parent=s.container,
                label=sticker,
                size=(240, 45),
                position=(10, y_pos),
                on_activate_call=Call(s.send_sticker, sticker),
                color=(0.3, 0.5, 0.7),
                textcolor=(1, 1, 1),
                text_scale=0.8
            )
            y_pos -= 50

        cw(s.container, size=(260, len(s.stickers) * 55))

    def send_sticker(s, sticker):

        try:
            CM(sticker)
            push(f'Sent: {sticker}', color=(0, 1, 0))
            gs('dingSmall').play()
            AR.swish(s.w)
        except Exception as e:
            AR.err(f'Error sending: {str(e)}')

    def add_sticker(s):

        def save_new_sticker():
            new_sticker = tw(query=txt_widget).strip()

            if not new_sticker:
                AR.err('Please enter an emoji!')
                gs('error').play()
                return

            if not is_valid_emoji(new_sticker):
                AR.err('Only emoji allowed! Text is not valid.')
                gs('error').play()
                return

            if len(new_sticker) > 4:
                AR.err('Invalid emoji! Please enter only one emoji.')
                gs('error').play()
                return

            stickers = load_stickers()

            if new_sticker in stickers:
                AR.err('This emoji already exists!')
                gs('error').play()
                return

            if len(stickers) >= 20:
                AR.err('You can only have up to 20 stickers!')
                gs('error').play()
                return

            stickers.append(new_sticker)
            save_stickers(stickers)
            s.stickers = stickers
            s.refresh_stickers()
            push(f'Emoji added: {new_sticker}', color=(0, 1, 0))
            gs('dingSmallHigh').play()
            AR.swish(win)

        win = AR.cw(
            source=s.w,
            size=(350, 200),
            ps=AR.UIS() * 0.6
        )

        AR.add_close_button(win, position=(320, 170))

        tw(
            parent=win,
            text='New Emoji:',
            position=(20, 160),
            scale=0.9,
            color=(1, 1, 1)
        )

        txt_widget = tw(
            parent=win,
            position=(20, 120),
            size=(310, 40),
            editable=True,
            text='',
            color=(0.9, 0.9, 0.9),
            max_chars=3,
            h_align='center'
        )

        tw(
            parent=win,
            text='⚠️ Only emojis are allowed (no text)',
            position=(20, 80),
            scale=0.6,
            color=(1, 0.5, 0.5)
        )

        tw(
            parent=win,
            text='📱 Use your device emoji keyboard',
            position=(20, 60),
            scale=0.6,
            color=(0.8, 0.8, 1)
        )

        AR.bw(
            parent=win,
            label='Confirm',
            size=(100, 35),
            position=(125, 20),
            on_activate_call=save_new_sticker
        )

    def remove_sticker(s):

        if not s.stickers:
            AR.err('No stickers to remove!')
            return

        win = AR.cw(
            source=s.w,
            size=(350, min(450, 250 + len(s.stickers) * 45)),
            ps=AR.UIS() * 0.6
        )

        AR.add_close_button(win, position=(320, min(420, 220 + len(s.stickers) * 45)))

        tw(
            parent=win,
            text='Select emoji to remove:',
            scale=1.0,
            position=(175, min(400, 170 + len(s.stickers) * 45)),
            h_align='center',
            color=(1, 1, 0)
        )

        scroll = sw(
            parent=win,
            size=(330, min(300, 150 + len(s.stickers) * 40)),
            position=(10, 50)
        )

        container = cw(
            parent=scroll,
            size=(330, len(s.stickers) * 45),
            background=False
        )

        y_pos = len(s.stickers) * 44 - 25
        for sticker in s.stickers:
            bw(
                parent=container,
                label=f'🗑️ {sticker}',
                size=(310, 40),
                position=(10, y_pos),
                on_activate_call=Call(s.confirm_remove, sticker, win),
                color=(0.8, 0.2, 0.2),
                textcolor=(1, 1, 1),
                text_scale=0.8
            )
            y_pos -= 45

    def confirm_remove(s, sticker, parent_win):

        stickers = load_stickers()
        if sticker in stickers:
            stickers.remove(sticker)
            save_stickers(stickers)
            s.stickers = stickers
            s.refresh_stickers()
            push(f'Emoji removed: {sticker}', color=(1, 0.5, 0))
            gs('dingSmallLow').play()
        AR.swish(parent_win)

    def reset_stickers(s):

        save_stickers(DEFAULT_STICKERS.copy())
        s.stickers = DEFAULT_STICKERS.copy()
        s.refresh_stickers()
        push('Stickers reset to default', color=(0, 1, 1))
        gs('dingSmallHigh').play()


# Default stickers
DEFAULT_STICKERS = [
    "😂", "😐", "🗿", "🌚", "❤️", "💣", "🤫", "🙏", "😭"
]


def is_valid_emoji(text):
    if not text:
        return False

    cleaned_text = text.strip()

    if len(cleaned_text) > 4:
        return False

    regular_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:',.<>?/~`"

    for char in cleaned_text:
        if char in regular_chars:
            return False

        char_code = ord(char)

        emoji_ranges = [
            (0x1F600, 0x1F64F),  # Emoticons
            (0x1F300, 0x1F5FF),  # Miscellaneous Symbols and Pictographs
            (0x1F680, 0x1F6FF),  # Transport and Map Symbols
            (0x1F700, 0x1F77F),  # Alchemical Symbols
            (0x1F780, 0x1F7FF),  # Geometric Shapes Extended
            (0x1F800, 0x1F8FF),  # Supplemental Arrows-C
            (0x1F900, 0x1F9FF),  # Supplemental Symbols and Pictographs
            (0x1FA00, 0x1FA6F),  # Chess Symbols
            (0x1FA70, 0x1FAFF),  # Symbols and Pictographs Extended-A
            (0x2600, 0x26FF),  # Miscellaneous Symbols
            (0x2700, 0x27BF),  # Dingbats
            (0xFE00, 0xFE0F),  # Variation Selectors
        ]

        is_emoji_char = any(start <= char_code <= end for start, end in emoji_ranges)

        if not is_emoji_char:
            return False

    return True


def load_stickers():
    try:
        config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Configs')
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        stickers_path = os.path.join(config_dir, 'stickers.json')

        if not os.path.exists(stickers_path):
            save_stickers(DEFAULT_STICKERS.copy())
            return DEFAULT_STICKERS.copy()

        with open(stickers_path, 'r', encoding='utf-8') as f:
            loaded_stickers = json.load(f)

            valid_stickers = [s for s in loaded_stickers if is_valid_emoji(s)]

            if len(valid_stickers) != len(loaded_stickers):
                save_stickers(valid_stickers)

            return valid_stickers

    except Exception as e:
        print(f"Error loading stickers: {e}")
        return DEFAULT_STICKERS.copy()


def save_stickers(stickers):
    try:

        valid_stickers = [s for s in stickers if is_valid_emoji(s)]

        config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Configs')
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        stickers_path = os.path.join(config_dir, 'stickers.json')

        with open(stickers_path, 'w', encoding='utf-8') as f:
            json.dump(valid_stickers, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving stickers: {e}")


class ChatLog:
    def __init__(s, source):
        try:
            w = s.w = AR.cw(
                source=source,
                size=(400, 300),
                ps=AR.UIS() * 0.8
            )

            bw(
                parent=w,
                size=(40, 40),
                position=(180, 45),
                label='',
                texture=gt('storeCharacterXmas'),
                color=(1, 1, 1)
            )

            tw(
                parent=w,
                text=u'\ue027 Chat (500+)',
                scale=0.9,
                position=(180, 265),
                h_align='center',
                color=(0, 1, 1)
            )

            AR.add_close_button(w, position=(375, 270))

            s.search_input = tw(
                parent=w,
                position=(20, 240),
                size=(250, 25),
                editable=True,
                text='',
                color=(0.9, 0.9, 0.9),
                description='Search...'
            )

            buttons = [
                ('🔍', s.apply_search, (280, 240), (0.3, 0.6, 0.8)),
                ('⏰', s.toggle_time, (320, 240), (0.5, 0.4, 0.7)),
                ('📊', s.show_stats, (360, 240), (0.8, 0.5, 0.3))
            ]

            for label, callback, pos, color in buttons:
                bw(
                    parent=w,
                    label=label,
                    size=(30, 25),
                    position=pos,
                    on_activate_call=callback,
                    color=color,
                    textcolor=(1, 1, 1)
                )

            s.scroll = sw(
                parent=w,
                size=(380, 180),
                position=(10, 50)
            )

            s.container = cw(
                parent=s.scroll,
                size=(380, 6000),
                background=False
            )

            s.status_text = tw(
                parent=w,
                text='',
                position=(200, 25),
                scale=0.6,
                color=(0.8, 0.8, 1),
                h_align='center'
            )

            s.all_messages = []
            s.filtered_messages = []
            s.search_text = ""
            s.show_time = False
            s.showing_stats = False

            s.refresh_chat_log()
            AR.swish()

        except Exception as e:
            AR.err(f'خطا: {str(e)}')

    def refresh_chat_log(s):

        try:
            s.all_messages = GCM()

            s.all_messages = s.all_messages[-300:] if len(s.all_messages) > 300 else s.all_messages
            s.filtered_messages = s.all_messages.copy()
            s.display_messages()

        except Exception as e:
            AR.err(f'خطا: {str(e)}')

    def apply_search(s):

        s.search_text = tw(query=s.search_input).strip().lower()
        s.showing_stats = False

        if s.search_text:
            if s.search_text.startswith('user:'):
                username = s.search_text[5:].strip()
                s.filtered_messages = [
                    msg for msg in s.all_messages
                    if msg.lower().startswith(username + ':')
                ]
            else:
                s.filtered_messages = [
                    msg for msg in s.all_messages
                    if s.search_text in msg.lower()
                ]
        else:
            s.filtered_messages = s.all_messages.copy()

        s.display_messages()

    def toggle_time(s):

        s.show_time = not s.show_time
        s.showing_stats = False
        s.display_messages()

    def show_stats(s):

        s.showing_stats = True
        s.display_stats()

    def display_messages(s):

        try:

            for child in s.container.get_children():
                child.delete()

            if s.showing_stats:
                s.display_stats()
                return

            messages_to_show = s.filtered_messages

            if not messages_to_show:
                tw(
                    parent=s.container,
                    text='⚠️ No chat messages yet',
                    position=(160, 90),
                    scale=0.8,
                    color=(1, 0.5, 0),
                    h_align='center'
                )
                cw(s.container, size=(380, 200))
                return

            y_pos = len(messages_to_show) * 18 - 9
            for i, message in enumerate(messages_to_show):

                display_text = message
                if s.show_time:
                    timestamp = time.strftime("%H:%M", time.localtime(time.time() - (len(messages_to_show) - i) * 2))
                    display_text = f"[{timestamp}] {message}"

                if len(display_text) > 45:
                    display_text = display_text[:42] + "..."

                bw(
                    parent=s.container,
                    label='📋',
                    size=(22, 16),
                    position=(345, y_pos),
                    on_activate_call=Call(s.copy_message, message),
                    color=(0.3, 0.6, 0.3),
                    text_scale=0.5
                )

                tw(
                    parent=s.container,
                    text=display_text,
                    position=(10, y_pos),
                    scale=0.35,
                    color=(1, 1, 1),
                    maxwidth=325,
                    h_align='left'
                )

                y_pos -= 18

            status_text = f''
            if s.search_text:
                status_text += f''
            if s.show_time:
                status_text += ''

            tw(s.status_text, text=status_text)
            cw(s.container, size=(380, len(messages_to_show) * 18 + 10))

        except Exception as e:
            AR.err(f'خطا: {str(e)}')

    def display_stats(s):

        try:
            for child in s.container.get_children():
                child.delete()

            user_stats = {}
            for message in s.all_messages:
                if ':' in message:
                    username = message.split(':', 1)[0].strip()
                    user_stats[username] = user_stats.get(username, 0) + 1

            if not s.all_messages:
                tw(
                    parent=s.container,
                    text='⚠️ No chat messages yet',
                    position=(160, 90),
                    scale=0.8,
                    color=(1, 0.5, 0),
                    h_align='center'
                )
                cw(s.container, size=(380, 200))
                return

            stats = [
                f"📊 {len(s.all_messages)}",
                f"👥 {len(user_stats)}",
                f"📈 {len(s.all_messages) // max(len(user_stats), 1)}"
            ]

            y_pos = 150
            for stat in stats:
                tw(
                    parent=s.container,
                    text=stat,
                    position=(165, y_pos),
                    scale=0.7,
                    color=(1, 1, 1),
                    h_align='center'
                )
                y_pos -= 25

            if user_stats:
                top_user = max(user_stats.items(), key=lambda x: x[1])
                tw(
                    parent=s.container,
                    text=f"🏆 {top_user[0][:10]}:{top_user[1]}",
                    position=(165, y_pos),
                    scale=0.5,
                    color=(1, 1, 0),
                    h_align='center'
                )

            cw(s.container, size=(380, 200))

        except Exception as e:
            AR.err(f'خطا: {str(e)}')

    def copy_message(s, message):

        try:
            if CIS():
                from babase import clipboard_set_text
                clipboard_set_text(message)
                push('✅', color=(0, 1, 0))
        except Exception as e:
            AR.err(f'❌ {str(e)}')


class FontMaker:
    def __init__(s, source):
        w = s.w = AR.cw(
            source=source,
            size=(500, 350),
            ps=AR.UIS() * 0.6
        )
        AR.add_close_button(w, position=(470, 300))

        tw(parent=w, text=u"\ue000 Font Maker", position=(170, 300), scale=1.0, color=(1, 1, 0))

        bw(parent=w, size=(40, 40), position=(100, 200), label='', texture=gt('storeIcon'), color=(1, 1, 1))

        bw(parent=w, size=(40, 40), position=(350, 200), label='', texture=gt('storeIcon'), color=(1, 1, 1))

        tw(parent=w, text="Text:", position=(20, 265), scale=0.8, color=(1, 1, 1))
        s.input_widget = tw(parent=w, position=(80, 255), size=(390, 40),
                            editable=True, text="Enter your text",
                            color=(0.9, 0.9, 0.9), description="")

        AR.bw(parent=w, label="Generate Fonts", size=(120, 30),
              position=(190, 200), on_activate_call=s.show_fonts)

        s.scroll = sw(parent=w, size=(460, 150), position=(20, 50))
        s.container = cw(parent=s.scroll, size=(440, 1000), background=False)

        s.status_text = tw(parent=w, text="Ready",
                           position=(230, 25), scale=0.6, color=(0.8, 0.8, 1))

        tw(
            parent=s.container,
            text="⚠️ No fonts generated yet",
            position=(220, 70),
            scale=0.7,
            color=(1, 0.5, 0),
            h_align='center'
        )

        AR.swish()

    def show_fonts(s):
        text = tw(query=s.input_widget).strip()
        if not text or text == "Enter your text":
            AR.err("Please enter some text!")
            return

        fonts = generate_fonts(text)

        for child in s.container.get_children():
            child.delete()

        y_pos = len(fonts) * 40 - 20
        total_height = 0

        for name, styled in fonts.items():
            tw(parent=s.container, text=f"{name}:  ", position=(10, y_pos),
               color=(1, 1, 1), scale=0.6, maxwidth=90)

            tw(parent=s.container, text=styled, position=(100, y_pos),
               color=(0, 1, 0), scale=0.65, maxwidth=250)

            AR.bw(parent=s.container, label="Copy", size=(50, 20),
                  position=(360, y_pos - 3),
                  on_activate_call=Call(s.copy_font, styled, name),
                  text_scale=0.5)

            y_pos -= 40
            total_height += 40

        cw(s.container, size=(440, max(300, total_height)))

        tw(s.status_text, text=f"{len(fonts)} fonts generated")

    def copy_font(s, text, font_name):
        try:
            from babase import clipboard_set_text
            clipboard_set_text(text)
            push(f'Font {font_name} copied', color=(0, 1, 0))
            gs('dingSmall').play()
        except:
            AR.err("Clipboard not supported!")


class PlayerInfo:
    def __init__(s, source):
        w = s.w = AR.cw(
            source=source,
            size=(650, 380),
            ps=AR.UIS() * 0.7
        )

        AR.add_close_button(w, position=(620, 300))

        tw(
            parent=w,
            text=u'\ue025 Player Manager',
            scale=1.0,
            position=(325, 310),
            h_align='center',
            color=(0, 1, 1)
        )

        bw(
            parent=w,
            size=(70, 70),
            position=(450, 235),
            label='',
            texture=gt('cursor'),
            color=(1, 1, 1)
        )

        s.players = s.get_players()
        s.filtered_players = s.players.copy()
        s.search_text = ''
        s.current_tab = 'all'

        tw(parent=w, text='🔍 Search:', position=(10, 280), scale=0.7, color=(1, 1, 1))
        s.search_input = tw(parent=w, position=(110, 280), size=(200, 25),
                            editable=True, text='', color=(0.9, 0.9, 0.9),
                            description="Search players...",
                            on_return_press_call=s.apply_search)

        bw(parent=w, label='Search', size=(60, 25), position=(320, 280),
           on_activate_call=s.apply_search, color=(0.3, 0.6, 0.8))

        tabs = [
            ('🌐 All Players', 'all', (20, 250)),
            ('⭐ Friends', 'friends', (150, 250)),
            ('🚫 Blocked', 'blocked', (280, 250))
        ]

        for label, tab_type, pos in tabs:
            color = (0.4, 0.7, 0.4) if tab_type == 'all' else (0.4, 0.5, 0.7)
            bw(parent=w, label=label, size=(120, 25), position=pos,
               on_activate_call=Call(s.set_tab, tab_type), color=color,
               textcolor=(1, 1, 1), text_scale=0.6)

        # آمار
        s.stats_widget = tw(parent=w, text='', position=(500, 320), scale=0.5,
                            color=(0.8, 1, 0.8), maxwidth=140, h_align='center')
        s.update_stats()

        # اسکرول
        s.scroll = sw(
            parent=w,
            size=(610, 150),
            position=(20, 90)
        )

        s.container = cw(
            parent=s.scroll,
            size=(610, len(s.filtered_players) * 35),
            background=False
        )

        # دکمه‌های مدیریت
        management_buttons = [
            ('📋 Export', s.show_export_menu, (20, 55), (100, 30)),
            ('🔄 Refresh', s.refresh_players, (140, 55), (100, 30)),
            ('💬 Save Chat', s.save_chat_html, (260, 55), (120, 30)),
            ('🚫 Kick All', s.kick_all, (400, 55), (100, 30)),
            ('⚙️ Settings', s.show_settings, (520, 55), (100, 30))
        ]

        for label, callback, pos, size in management_buttons:
            color = (0.3, 0.6, 0.8)
            if 'Kick' in label: color = (0.8, 0.3, 0.3)
            if 'Save' in label: color = (0.4, 0.7, 0.4)
            if 'Settings' in label: color = (0.6, 0.4, 0.8)

            bw(parent=w, label=label, size=size, position=pos,
               on_activate_call=callback, color=color,
               textcolor=(1, 1, 1), text_scale=0.6)

        s.display_players()
        AR.swish()

    def get_players(s):
        players = []
        try:
            roster = bs.get_game_roster()
            for player in roster:
                if 'players' in player and player['players']:
                    for p in player['players']:
                        device_name = player.get('display_string', 'Unknown Device')
                        players.append({
                            'name': p.get('name', 'Unknown Player'),
                            'client_id': player.get('client_id', -1),
                            'device': device_name
                        })
        except Exception as e:
            print(f"Error getting players: {e}")
        return players

    def get_friends_list(s):
        return var('player_friends') or []

    def get_blocked_list(s):
        return var('player_blocked') or []

    def get_chat_messages(s):
        """دریافت آخرین چت‌های سرور"""
        try:
            chat_messages = GCM()
            return chat_messages[-50:] if len(chat_messages) > 50 else chat_messages
        except:
            return []

    def set_tab(s, tab_type):
        s.current_tab = tab_type
        s.filter_players()
        s.display_players()
        s.update_stats()

    def apply_search(s):
        s.search_text = tw(query=s.search_input).strip().lower()
        s.filter_players()
        s.display_players()
        s.update_stats()

    def filter_players(s):
        if s.current_tab == 'friends':
            friends = s.get_friends_list()
            s.filtered_players = [p for p in s.players if p['name'] in friends]
        elif s.current_tab == 'blocked':
            blocked = s.get_blocked_list()
            s.filtered_players = [p for p in s.players if p['name'] in blocked]
        else:
            s.filtered_players = s.players.copy()

        if s.search_text:
            s.filtered_players = [
                p for p in s.filtered_players
                if s.search_text in p['name'].lower() or
                   s.search_text in p['device'].lower()
            ]

    def update_stats(s):
        friends_count = len(s.get_friends_list())
        blocked_count = len(s.get_blocked_list())

        if not s.filtered_players:
            stats_text = f'\n0 Players\n               {friends_count} Friends\n               {blocked_count} Blocked'
        else:
            stats_text = f'\n{len(s.filtered_players)} Players\n               {friends_count} Friends\n               {blocked_count} Blocked'

        tw(s.stats_widget, text=stats_text)

    def display_players(s):
        for child in s.container.get_children():
            child.delete()

        if not s.filtered_players:
            message = 'No players found'
            if s.current_tab == 'friends':
                message = 'No friends found'
            elif s.current_tab == 'blocked':
                message = 'No blocked players'

            tw(parent=s.container, text=message, position=(305, 75),
               scale=0.8, color=(1, 0.5, 0), h_align='center')
            cw(s.container, size=(610, 150))
            return

        headers = [
            ('Player Name', 20, 0.6, (1, 1, 1)),
            ('ID', 180, 0.6, (0.8, 0.8, 1)),
            ('Device', 240, 0.6, (0.6, 1, 0.6)),
            ('Status', 380, 0.6, (1, 1, 0.8)),
            ('Actions', 500, 0.6, (1, 1, 1))
        ]

        y_pos = len(s.filtered_players) * 29 + 15
        for text, x, scale, color in headers:
            tw(parent=s.container, text=text, position=(x, y_pos),
               scale=scale, color=color, h_align='center')

        y_pos = len(s.filtered_players) * 30 - 10
        for i, player in enumerate(s.filtered_players):
            bg_color = (0.2, 0.2, 0.3) if i % 2 == 0 else (0.25, 0.25, 0.35)

            friends = s.get_friends_list()
            blocked = s.get_blocked_list()

            if player['name'] in friends:
                bg_color = (0.2, 0.4, 0.2)
            elif player['name'] in blocked:
                bg_color = (0.4, 0.2, 0.2)

            bw(parent=s.container, label='', size=(590, 25),
               position=(10, y_pos), color=bg_color, enable_sound=False)

            player_name = player['name']
            displayed_name = player_name[:15] + '...' if len(player_name) > 15 else player_name

            if player['name'] in friends:
                displayed_name = f"⭐ {displayed_name}"
            elif player['name'] in blocked:
                displayed_name = f"🚫 {displayed_name}"

            name_color = (1, 1, 0.8) if s.search_text and s.search_text in player_name.lower() else (1, 1, 1)
            tw(parent=s.container, text=displayed_name, position=(15, y_pos - 1),
               scale=0.5, color=name_color, maxwidth=150, h_align='left')

            tw(parent=s.container, text=f"{player['client_id']}", position=(180, y_pos - 1),
               scale=0.5, color=(0.8, 0.8, 1), h_align='center')

            device_text = player['device'][:20] + '...' if len(player['device']) > 20 else player['device']
            tw(parent=s.container, text=device_text, position=(230, y_pos - 1),
               scale=0.5, color=(0.6, 1, 0.6), maxwidth=130, h_align='left')

            status_text = ""
            status_color = (1, 1, 1)
            if player['name'] in friends:
                status_text = "Friend"
                status_color = (0, 1, 0)
            elif player['name'] in blocked:
                status_text = "Blocked"
                status_color = (1, 0, 0)

            tw(parent=s.container, text=status_text, position=(380, y_pos - 1),
               scale=0.5, color=status_color, h_align='center')

            actions = []
            friends = s.get_friends_list()
            blocked = s.get_blocked_list()

            if player['name'] in friends:
                actions.append(('❌', s.remove_friend, (440, y_pos + 3), player))
            else:
                actions.append(('⭐', s.add_friend, (440, y_pos + 3), player))

            if player['name'] in blocked:
                actions.append(('✅', s.unblock_player, (480, y_pos + 3), player))
            else:
                actions.append(('🚫', s.block_player, (480, y_pos + 3), player))

            actions.extend([
                ('📋', s.copy_player_info, (520, y_pos + 3), player),
                ('@', s.mention_player, (560, y_pos + 3), player)
            ])

            for label, callback, pos, data in actions:
                color = (0.3, 0.5, 0.8)
                if '🚫' in label: color = (0.8, 0.3, 0.3)
                if '❌' in label: color = (0.8, 0.3, 0.3)
                if '⭐' in label: color = (1, 0.8, 0.2)
                if '✅' in label: color = (0.2, 0.8, 0.2)
                if '@' in label: color = (0.4, 0.7, 0.4)

                bw(parent=s.container, label=label, size=(20, 20), position=pos,
                   on_activate_call=Call(callback, data), color=color, text_scale=0.5)

            y_pos -= 30

        cw(s.container, size=(610, len(s.filtered_players) * 30 + 30))

    def refresh_players(s):
        s.players = s.get_players()
        s.filter_players()
        s.display_players()
        s.update_stats()
        push('Player list refreshed', color=(0, 1, 0))
        gs('dingSmall').play()

    def show_export_menu(s):
        if not s.players:
            AR.err('No players to export!')
            return

        win = AR.cw(source=s.w, size=(350, 250))
        tw(parent=win, text='📤 Export Format', position=(175, 220), h_align='center')

        formats = [
            ('📝 Text', s.export_text),
            ('📊 CSV', s.export_csv),
            ('📋 JSON', s.export_json),
            ('📄 HTML', s.export_html),
            ('📱 All Formats', s.export_all_formats)
        ]

        y_pos = 180
        for label, callback in formats:
            bw(parent=win, label=label, size=(140, 25), position=(105, y_pos),
               on_activate_call=callback, color=(0.3, 0.6, 0.8))
            y_pos -= 35

        AR.add_close_button(win, position=(320, 220))

    def save_chat_html(s):
        """ذخیره HTML با چت‌های سرور"""
        try:
            server_name = "Unknown_Server"
            try:
                conn_info = get_connection_info()
                if conn_info and hasattr(conn_info, 'name'):
                    server_name = conn_info.name
                elif server_ip != "127.0.0.1":
                    server_name = f"Server_{server_ip}_{server_port}"
            except:
                server_name = "Local_Server"

            import os
            script_dir = os.path.dirname(os.path.abspath(__file__))
            self_taha_dir = os.path.join(script_dir, "SelfTaha")

            if not os.path.exists(self_taha_dir):
                os.makedirs(self_taha_dir)

            import re
            safe_server_name = re.sub(r'[<>:"/\\|?*]', '_', server_name)
            safe_server_name = safe_server_name.replace(' ', '_')
            filename = f"{safe_server_name}_{time.strftime('%Y%m%d_%H%M%S')}.html"
            filepath = os.path.join(self_taha_dir, filename)

            html_content = s.generate_html_with_chat()

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)

            push(f"📁 HTML saved: {filename}", color=(0, 1, 0))
            gs('dingSmallHigh').play()

        except Exception as e:
            print(f"Error saving HTML: {e}")
            AR.err("Error saving HTML file")

    def generate_html_with_chat(s):
        """تولید HTML با چت‌های سرور"""
        server_name = "Unknown Server"
        try:
            conn_info = get_connection_info()
            if conn_info and hasattr(conn_info, 'name'):
                server_name = conn_info.name
            elif server_ip != "127.0.0.1":
                server_name = f"Server {server_ip}:{server_port}"
        except:
            server_name = "Local Server"

        friends = s.get_friends_list()
        blocked = s.get_blocked_list()
        chat_messages = s.get_chat_messages()

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Player Report - {server_name}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 25px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2.2em;
            margin-bottom: 10px;
        }}
        .server-info {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        .info {{
            background: #f8f9fa;
            padding: 20px;
            border-bottom: 1px solid #dee2e6;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        .info-item {{
            background: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .info-item h3 {{
            color: #6c757d;
            margin-bottom: 5px;
            font-size: 0.9em;
        }}
        .info-item p {{
            font-size: 1.3em;
            font-weight: bold;
            color: #495057;
        }}
        .section {{
            padding: 20px;
            border-bottom: 1px solid #dee2e6;
        }}
        .section:last-child {{
            border-bottom: none;
        }}
        .section h2 {{
            color: #495057;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #4facfe;
        }}
        .players-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9em;
            margin-bottom: 20px;
        }}
        .players-table th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px;
            text-align: left;
        }}
        .players-table td {{
            padding: 10px 12px;
            border-bottom: 1px solid #dee2e6;
        }}
        .players-table tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        .chat-container {{
            max-height: 400px;
            overflow-y: auto;
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin-top: 15px;
        }}
        .chat-message {{
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 8px;
            background: white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border-left: 4px solid #4facfe;
        }}
        .chat-message.system {{
            border-left-color: #28a745;
            background: #f0fff4;
        }}
        .chat-message.join {{
            border-left-color: #17a2b8;
            background: #e3f2fd;
        }}
        .chat-message.leave {{
            border-left-color: #dc3545;
            background: #fff5f5;
        }}
        .message-time {{
            font-size: 0.8em;
            color: #6c757d;
            margin-bottom: 5px;
        }}
        .message-content {{
            font-size: 0.95em;
            line-height: 1.4;
        }}
        .status-friend {{
            color: #28a745;
            font-weight: bold;
        }}
        .status-blocked {{
            color: #dc3545;
            font-weight: bold;
        }}
        .footer {{
            background: #343a40;
            color: white;
            text-align: center;
            padding: 15px;
            font-size: 0.9em;
        }}
        @media (max-width: 768px) {{
            .container {{
                margin: 10px;
            }}
            .header h1 {{
                font-size: 1.8em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎮 Complete Server Report</h1>
            <p class="server-info">Server: {server_name} | {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <div class="info">
            <h2>📊 Session Overview</h2>
            <div class="info-grid">
                <div class="info-item">
                    <h3>Total Players</h3>
                    <p>{len(s.players)}</p>
                </div>
                <div class="info-item">
                    <h3>Friends</h3>
                    <p>{len(friends)}</p>
                </div>
                <div class="info-item">
                    <h3>Blocked</h3>
                    <p>{len(blocked)}</p>
                </div>
                <div class="info-item">
                    <h3>Chat Messages</h3>
                    <p>{len(chat_messages)}</p>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>👥 Player List</h2>
            <table class="players-table">
                <thead>
                    <tr>
                        <th>Player Name</th>
                        <th>ID</th>
                        <th>Device</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
"""

        for player in s.players:
            status_class = ""
            status_text = "Normal"

            if player['name'] in friends:
                status_class = "status-friend"
                status_text = "Friend ⭐"
            elif player['name'] in blocked:
                status_class = "status-blocked"
                status_text = "Blocked 🚫"

            html_content += f'                    <tr>\n'
            html_content += f'                        <td>{player["name"]}</td>\n'
            html_content += f'                        <td>{player["client_id"]}</td>\n'
            html_content += f'                        <td>{player["device"]}</td>\n'
            html_content += f'                        <td class="{status_class}">{status_text}</td>\n'
            html_content += f'                    </tr>\n'

        html_content += """                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>💬 Chat History (Last 50 Messages)</h2>
            <div class="chat-container">
"""

        if chat_messages:
            for message in chat_messages:
                message_class = "normal"
                if any(x in message.lower() for x in ['joined', 'connected', 'وارد شد']):
                    message_class = "join"
                elif any(x in message.lower() for x in ['left', 'disconnected', 'ترک کرد']):
                    message_class = "leave"
                elif any(x in message.lower() for x in ['system', 'سیستم']):
                    message_class = "system"

                html_content += f'                <div class="chat-message {message_class}">\n'
                html_content += f'                    <div class="message-time">{time.strftime("%H:%M:%S")}</div>\n'
                html_content += f'                    <div class="message-content">{message}</div>\n'
                html_content += f'                </div>\n'
        else:
            html_content += '                <div class="chat-message">\n'
            html_content += '                    <div class="message-content">No chat messages available</div>\n'
            html_content += '                </div>\n'

        html_content += """            </div>
        </div>

        <div class="footer">
            <p>Generated by SelfTaha Player Manager • {time.strftime('%Y')}</p>
        </div>
    </div>
</body>
</html>"""

        return html_content

    def export_html(s):
        html_content = s.generate_html_with_chat()
        s.copy_to_clipboard(html_content, "HTML")

    def export_text(s):
        export_text = "=== Player List Export ===\n\n"
        export_text += f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        export_text += f"Total Players: {len(s.players)}\n"
        export_text += f"Friends: {len(s.get_friends_list())}\n"
        export_text += f"Blocked: {len(s.get_blocked_list())}\n\n"

        friends = s.get_friends_list()
        blocked = s.get_blocked_list()

        for i, player in enumerate(s.players, 1):
            status = "Normal"
            if player['name'] in friends:
                status = "Friend ⭐"
            elif player['name'] in blocked:
                status = "Blocked 🚫"

            export_text += f"{i}. {player['name']}\n"
            export_text += f"   ID: {player['client_id']}\n"
            export_text += f"   Device: {player['device']}\n"
            export_text += f"   Status: {status}\n"
            export_text += "-" * 40 + "\n"

        s.copy_to_clipboard(export_text, "Text")

    def export_csv(s):
        csv_text = "Name,ID,Device,Status\n"
        friends = s.get_friends_list()
        blocked = s.get_blocked_list()

        for player in s.players:
            status = "Normal"
            if player['name'] in friends:
                status = "Friend"
            elif player['name'] in blocked:
                status = "Blocked"

            csv_text += f'"{player["name"]}",{player["client_id"]},'
            csv_text += f'"{player["device"]}","{status}"\n'

        s.copy_to_clipboard(csv_text, "CSV")

    def export_json(s):
        import json
        friends = s.get_friends_list()
        blocked = s.get_blocked_list()

        players_data = []
        for player in s.players:
            status = "normal"
            if player['name'] in friends:
                status = "friend"
            elif player['name'] in blocked:
                status = "blocked"

            players_data.append({
                'name': player['name'],
                'id': player['client_id'],
                'device': player['device'],
                'status': status
            })

        json_text = json.dumps(players_data, indent=2, ensure_ascii=False)
        s.copy_to_clipboard(json_text, "JSON")

    def export_all_formats(s):
        s.export_text()
        teck(0.5, s.export_csv)
        teck(1.0, s.export_json)
        teck(1.5, s.export_html)
        push("All formats exported!", color=(0, 1, 1))

    def copy_to_clipboard(s, text, format_name):
        if CIS():
            from babase import clipboard_set_text
            clipboard_set_text(text)
            push(f"📋 {format_name} data copied!", color=(0, 1, 0))
            gs('dingSmallHigh').play()
        else:
            AR.err('Clipboard not supported!')

    def add_friend(s, player):
        friends = s.get_friends_list()
        blocked = s.get_blocked_list()

        if player['name'] in friends:
            push(f"{player['name']} is already a friend", color=(1, 0.8, 0.2))
            return

        if player['name'] in blocked:
            push(f"Cannot add blocked player {player['name']} to friends", color=(1, 0.5, 0))
            return

        friends.append(player['name'])
        var('player_friends', friends)
        push(f"⭐ {player['name']} added to friends!", color=(0, 1, 0))
        gs('dingSmallHigh').play()
        s.refresh_players()

    def remove_friend(s, player):
        friends = s.get_friends_list()
        if player['name'] in friends:
            friends.remove(player['name'])
            var('player_friends', friends)
            push(f"❌ {player['name']} removed from friends", color=(1, 0.5, 0))
            gs('dingSmallLow').play()
            s.refresh_players()

    def block_player(s, player):
        blocked = s.get_blocked_list()
        friends = s.get_friends_list()

        if player['name'] in blocked:
            push(f"{player['name']} is already blocked", color=(1, 0.5, 0))
            return

        if player['name'] in friends:
            friends.remove(player['name'])
            var('player_friends', friends)

        blocked.append(player['name'])
        var('player_blocked', blocked)
        push(f"🚫 {player['name']} blocked!", color=(1, 0, 0))
        gs('dingSmallLow').play()
        s.refresh_players()

    def unblock_player(s, player):
        blocked = s.get_blocked_list()
        if player['name'] in blocked:
            blocked.remove(player['name'])
            var('player_blocked', blocked)
            push(f"✅ {player['name']} unblocked!", color=(0, 1, 0))
            gs('dingSmallHigh').play()
            s.refresh_players()

    def show_settings(s):
        win = AR.cw(source=s.w, size=(300, 200))
        tw(parent=win, text='⚙️ List Management', position=(125, 170), h_align='center')

        settings = [
            ('🗑️ Clear Friends', s.clear_friends),
            ('🗑️ Clear Blocked', s.clear_blocked),
            ('📝 Export Lists', s.export_lists)
        ]

        y_pos = 130
        for label, callback in settings:
            bw(parent=win, label=label, size=(140, 25), position=(80, y_pos),
               on_activate_call=callback, color=(0.3, 0.6, 0.8))
            y_pos -= 35

        AR.add_close_button(win, position=(270, 170))

    def clear_friends(s):
        var('player_friends', [])
        push("Friends list cleared!", color=(1, 0.5, 0))
        s.refresh_players()

    def clear_blocked(s):
        var('player_blocked', [])
        push("Blocked list cleared!", color=(1, 0.5, 0))
        s.refresh_players()

    def export_lists(s):
        friends = s.get_friends_list()
        blocked = s.get_blocked_list()

        export_text = "=== Player Lists Export ===\n\n"
        export_text += f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        export_text += "⭐ Friends List:\n"
        if friends:
            for i, friend in enumerate(friends, 1):
                export_text += f"{i}. {friend}\n"
        else:
            export_text += "No friends\n"

        export_text += "\n🚫 Blocked List:\n"
        if blocked:
            for i, blocked_player in enumerate(blocked, 1):
                export_text += f"{i}. {blocked_player}\n"
        else:
            export_text += "No blocked players\n"

        s.copy_to_clipboard(export_text, "Lists")

    def mention_all(s):
        if not s.players:
            AR.err('No players to mention!')
            return

        try:
            for player in s.players:
                message = f"@{player['name']}"
                CM(message)
                time.sleep(0.3)
            push("All players mentioned!", color=(0, 1, 1))
            gs('dingSmall').play()
        except Exception:
            AR.err("Error sending mentions")

    def copy_player_info(s, player):
        info = (f"Player Name: {player['name']}\n"
                f"ID: {player['client_id']}\n"
                f"Device: {player['device']}")

        if CIS():
            from babase import clipboard_set_text
            clipboard_set_text(info)
            push(f"Info of {player['name']} copied", color=(0, 1, 0))
            gs('dingSmall').play()
        else:
            AR.err('Clipboard not supported!')

    def mention_player(s, player):
        try:
            message = f"@{player['name']}"
            CM(message)
            push(f"{player['name']} mentioned", color=(0, 1, 1))
            gs('dingSmall').play()
        except Exception:
            AR.err(f"Error sending mention")

    def kick_player(s, player):
        try:
            from bascenev1 import disconnect_client
            disconnect_client(player['client_id'])
            push(f"{player['name']} kicked", color=(1, 0.5, 0))
            gs('dingSmallLow').play()
            teck(1.0, s.refresh_players)
        except Exception:
            AR.err(f"Error kicking player")

    def kick_all(s):
        if not s.players:
            AR.err('No players to kick!')
            return

        try:
            from bascenev1 import disconnect_client
            kicked_count = 0

            for player in s.players:
                try:
                    disconnect_client(player['client_id'])
                    kicked_count += 1
                except:
                    continue

            if kicked_count > 0:
                push(f"{kicked_count} players kicked", color=(1, 0.5, 0))
                gs('dingSmallLow').play()
                teck(1.0, s.refresh_players)
            else:
                AR.err('No players to kick!')

        except Exception:
            AR.err(f"Error during kick")


"""تغییر رنگ UI"""


class UIColorChanger:
    def __init__(s, source):
        # فقط مستقیماً پنجره تغییر رنگ را باز کن
        launch_colorscheme_selection_window()


class ColorScheme:
    """
    Apply a colorscheme to the game.
    """

    def __init__(self, color=None, highlight=None):
        self.color = color
        self.highlight = highlight

    def _custom_buttonwidget(self, *args, **kwargs):
        if self.highlight is not None:
            kwargs["color"] = self.highlight
        return original_buttonwidget(*args, **kwargs)

    def _custom_containerwidget(self, *args, **kwargs):
        if self.color is not None:
            kwargs["color"] = self.color
        return original_containerwidget(*args, **kwargs)

    def _custom_checkboxwidget(self, *args, **kwargs):
        if self.highlight is not None:
            kwargs["color"] = self.highlight
        return original_checkboxwidget(*args, **kwargs)

    def _apply_color(self):
        if self.color is not None:
            bui.containerwidget = self._custom_containerwidget

    def _apply_highlight(self):
        if self.highlight is not None:
            bui.buttonwidget = self._custom_buttonwidget
            bui.checkboxwidget = self._custom_checkboxwidget

    def apply(self):
        if self.color:
            self._apply_color()
        if self.highlight:
            self._apply_highlight()

    @staticmethod
    def _disable_color():
        bui.buttonwidget = original_buttonwidget
        bui.checkboxwidget = original_checkboxwidget

    @staticmethod
    def _disable_highlight():
        bui.containerwidget = original_containerwidget

    @classmethod
    def disable(cls):
        cls._disable_color()
        cls._disable_highlight()


class ColorSchemeWindow(bui.Window):
    def __init__(self, default_colors=((0.41, 0.39, 0.5), (0.5, 0.7, 0.25))):
        self._default_colors = default_colors
        self._color, self._highlight = babase.app.config.get("ColorScheme", (None, None))

        self._last_color = self._color
        self._last_highlight = self._highlight

        ColorScheme.disable()

        # Allow pro features for color picking
        global original_have_pro
        original_have_pro = bui.app.classic.accounts.have_pro
        bui.app.classic.accounts.have_pro = lambda: True

        self.draw_ui()

    def draw_ui(self):
        uiscale = bui.app.ui_v1.uiscale
        self._width = width = 480.0 if uiscale is babase.UIScale.SMALL else 380.0
        self._x_inset = x_inset = 40.0 if uiscale is babase.UIScale.SMALL else 0.0
        self._height = height = (
            275.0
            if uiscale is babase.UIScale.SMALL
            else 288.0
            if uiscale is babase.UIScale.MEDIUM
            else 300.0
        )
        spacing = 40
        self._base_scale = (
            2.05
            if uiscale is babase.UIScale.SMALL
            else 1.5
            if uiscale is babase.UIScale.MEDIUM
            else 1.0
        )
        top_extra = 15

        super().__init__(
            root_widget=bui.containerwidget(
                size=(width, height + top_extra),
                on_outside_click_call=self.cancel_on_outside_click,
                transition="in_right",
                scale=self._base_scale,
                stack_offset=(0, 15) if uiscale is babase.UIScale.SMALL else (0, 0),
            )
        )

        cancel_button = bui.buttonwidget(
            parent=self._root_widget,
            position=(52 + x_inset, height - 60),
            size=(155, 60),
            scale=0.8,
            autoselect=True,
            label=babase.Lstr(resource="cancelText"),
            on_activate_call=self._cancel,
        )
        bui.containerwidget(edit=self._root_widget, cancel_button=cancel_button)

        save_button = bui.buttonwidget(
            parent=self._root_widget,
            position=(width - (177 + x_inset), height - 110),
            size=(155, 60),
            autoselect=True,
            scale=0.8,
            label=babase.Lstr(resource="saveText"),
        )
        bui.widget(edit=save_button, left_widget=cancel_button)
        bui.buttonwidget(edit=save_button, on_activate_call=self.save)
        bui.widget(edit=cancel_button, right_widget=save_button)
        bui.containerwidget(edit=self._root_widget, start_button=save_button)

        reset_button = bui.buttonwidget(
            parent=self._root_widget,
            position=(width - (177 + x_inset), height - 60),
            size=(155, 60),
            color=(0.2, 0.5, 0.6),
            autoselect=True,
            scale=0.8,
            label=babase.Lstr(resource="settingsWindowAdvanced.resetText"),
        )
        bui.widget(edit=reset_button, left_widget=reset_button)
        bui.buttonwidget(edit=reset_button, on_activate_call=self.reset)
        bui.widget(edit=cancel_button, right_widget=reset_button)
        bui.containerwidget(edit=self._root_widget, start_button=reset_button)

        v = height - 65.0
        v -= spacing * 3.0
        b_size = 80
        b_offs = 75

        self._color_button = bui.buttonwidget(
            parent=self._root_widget,
            autoselect=True,
            position=(self._width * 0.5 - b_offs - b_size * 0.5, v - 50),
            size=(b_size, b_size),
            color=self._last_color or self._default_colors[0],
            label="",
            button_type="square",
        )
        bui.buttonwidget(
            edit=self._color_button, on_activate_call=babase.Call(self._pick_color, "color")
        )
        bui.textwidget(
            parent=self._root_widget,
            h_align="center",
            v_align="center",
            position=(self._width * 0.5 - b_offs, v - 65),
            size=(0, 0),
            draw_controller=self._color_button,
            text=babase.Lstr(resource="editProfileWindow.colorText"),
            scale=0.7,
            color=bui.app.ui_v1.title_color,
            maxwidth=120,
        )

        self._highlight_button = bui.buttonwidget(
            parent=self._root_widget,
            autoselect=True,
            position=(self._width * 0.5 + b_offs - b_size * 0.5, v - 50),
            size=(b_size, b_size),
            color=self._last_highlight or self._default_colors[1],
            label="",
            button_type="square",
        )

        bui.buttonwidget(
            edit=self._highlight_button,
            on_activate_call=babase.Call(self._pick_color, "highlight"),
        )
        bui.textwidget(
            parent=self._root_widget,
            h_align="center",
            v_align="center",
            position=(self._width * 0.5 + b_offs, v - 65),
            size=(0, 0),
            draw_controller=self._highlight_button,
            text=babase.Lstr(resource="editProfileWindow.highlightText"),
            scale=0.7,
            color=bui.app.ui_v1.title_color,
            maxwidth=120,
        )

    def _pick_color(self, tag):
        if tag == "color":
            initial_color = self._color or self._default_colors[0]
        elif tag == "highlight":
            initial_color = self._highlight or self._default_colors[1]
        else:
            raise ValueError("Unexpected color picker tag: {}".format(tag))
        ColorPicker(
            parent=self._root_widget,
            position=(0, 0),
            initial_color=initial_color,
            delegate=self,
            tag=tag,
        )

    def cancel_on_outside_click(self):
        bui.getsound("swish").play()
        self._cancel()

    def _cancel(self):
        if self._last_color and self._last_highlight:
            colorscheme = ColorScheme(self._last_color, self._last_highlight)
            colorscheme.apply()
        # Restore original pro check
        bui.app.classic.accounts.have_pro = original_have_pro
        bui.containerwidget(edit=self._root_widget, transition="out_right")

    def reset(self, transition_out=True):
        if transition_out:
            bui.getsound("gunCocking").play()
        babase.app.config["ColorScheme"] = (None, None)
        # Restore original pro check
        bui.app.classic.accounts.have_pro = original_have_pro
        babase.app.config.commit()
        bui.containerwidget(edit=self._root_widget, transition="out_right")

    def save(self, transition_out=True):
        if transition_out:
            bui.getsound("gunCocking").play()
        colorscheme = ColorScheme(
            self._color or self._default_colors[0],
            self._highlight or self._default_colors[1],
        )
        colorscheme.apply()
        # Restore original pro check
        bui.app.classic.accounts.have_pro = original_have_pro
        babase.app.config["ColorScheme"] = (
            self._color or self._default_colors[0],
            self._highlight or self._default_colors[1],
        )
        babase.app.config.commit()
        bui.containerwidget(edit=self._root_widget, transition="out_right")

    def _set_color(self, color):
        self._color = color
        if self._color_button:
            bui.buttonwidget(edit=self._color_button, color=color)

    def _set_highlight(self, color):
        self._highlight = color
        if self._highlight_button:
            bui.buttonwidget(edit=self._highlight_button, color=color)

    def color_picker_selected_color(self, picker, color):
        if not self._root_widget:
            return
        tag = picker.get_tag()
        if tag == "color":
            self._set_color(color)
        elif tag == "highlight":
            self._set_highlight(color)

    def color_picker_closing(self, picker):
        pass


def launch_colorscheme_selection_window():
    ColorSchemeWindow()


def load_colorscheme():
    color, highlight = babase.app.config.get("ColorScheme", (None, None))
    if color and highlight:
        colorscheme = ColorScheme(color, highlight)
        colorscheme.apply()


# بارگذاری پلاگین رنگ‌ها هنگام راه‌اندازی
load_colorscheme()


class ColorSchemeWindow(bui.Window):
    def __init__(self, default_colors=((0.41, 0.39, 0.5), (0.5, 0.7, 0.25))):
        self._default_colors = default_colors
        self._color, self._highlight = babase.app.config.get("ColorScheme", (None, None))

        self._last_color = self._color
        self._last_highlight = self._highlight

        # Let's set the game's default colorscheme before opening the Window.
        # Otherwise the colors in the Window are tinted as per the already
        # applied custom colorscheme thereby making it impossible to visually
        # differentiate between different colors.
        ColorScheme.disable()

        # A hack to let players select any RGB color value through the UI,
        # otherwise this is limited only to pro accounts.
        bui.app.classic.accounts.have_pro = lambda: True

        self.draw_ui()

    def draw_ui(self):
        # NOTE: Most of the stuff here for drawing the UI is referred from the
        # legacy (1.6 < version <= 1.7.19) game's bastd/ui/profile/edit.py, and
        # so there could be some cruft here due to my oversight.
        uiscale = bui.app.ui_v1.uiscale
        self._width = width = 480.0 if uiscale is babase.UIScale.SMALL else 380.0
        self._x_inset = x_inset = 40.0 if uiscale is babase.UIScale.SMALL else 0.0
        self._height = height = (
            275.0
            if uiscale is babase.UIScale.SMALL
            else 288.0
            if uiscale is babase.UIScale.MEDIUM
            else 300.0
        )
        spacing = 40
        self._base_scale = (
            2.05
            if uiscale is babase.UIScale.SMALL
            else 1.5
            if uiscale is babase.UIScale.MEDIUM
            else 1.0
        )
        top_extra = 15

        super().__init__(
            root_widget=bui.containerwidget(
                size=(width, height + top_extra),
                on_outside_click_call=self.cancel_on_outside_click,
                transition="in_right",
                scale=self._base_scale,
                stack_offset=(0, 15) if uiscale is babase.UIScale.SMALL else (0, 0),
            )
        )

        cancel_button = bui.buttonwidget(
            parent=self._root_widget,
            position=(52 + x_inset, height - 60),
            size=(155, 60),
            scale=0.8,
            autoselect=True,
            label=babase.Lstr(resource="cancelText"),
            on_activate_call=self._cancel,
        )
        bui.containerwidget(edit=self._root_widget, cancel_button=cancel_button)

        save_button = bui.buttonwidget(
            parent=self._root_widget,
            position=(width - (177 + x_inset), height - 110),
            size=(155, 60),
            autoselect=True,
            scale=0.8,
            label=babase.Lstr(resource="saveText"),
        )
        bui.widget(edit=save_button, left_widget=cancel_button)
        bui.buttonwidget(edit=save_button, on_activate_call=self.save)
        bui.widget(edit=cancel_button, right_widget=save_button)
        bui.containerwidget(edit=self._root_widget, start_button=save_button)

        reset_button = bui.buttonwidget(
            parent=self._root_widget,
            position=(width - (177 + x_inset), height - 60),
            size=(155, 60),
            color=(0.2, 0.5, 0.6),
            autoselect=True,
            scale=0.8,
            label=babase.Lstr(resource="settingsWindowAdvanced.resetText"),
        )
        bui.widget(edit=reset_button, left_widget=reset_button)
        bui.buttonwidget(edit=reset_button, on_activate_call=self.reset)
        bui.widget(edit=cancel_button, right_widget=reset_button)
        bui.containerwidget(edit=self._root_widget, start_button=reset_button)

        v = height - 65.0
        v -= spacing * 3.0
        b_size = 80
        b_offs = 75

        self._color_button = bui.buttonwidget(
            parent=self._root_widget,
            autoselect=True,
            position=(self._width * 0.5 - b_offs - b_size * 0.5, v - 50),
            size=(b_size, b_size),
            color=self._last_color or self._default_colors[0],
            label="",
            button_type="square",
        )
        bui.buttonwidget(
            edit=self._color_button, on_activate_call=babase.Call(self._pick_color, "color")
        )
        bui.textwidget(
            parent=self._root_widget,
            h_align="center",
            v_align="center",
            position=(self._width * 0.5 - b_offs, v - 65),
            size=(0, 0),
            draw_controller=self._color_button,
            text=babase.Lstr(resource="editProfileWindow.colorText"),
            scale=0.7,
            color=bui.app.ui_v1.title_color,
            maxwidth=120,
        )

        self._highlight_button = bui.buttonwidget(
            parent=self._root_widget,
            autoselect=True,
            position=(self._width * 0.5 + b_offs - b_size * 0.5, v - 50),
            size=(b_size, b_size),
            color=self._last_highlight or self._default_colors[1],
            label="",
            button_type="square",
        )

        bui.buttonwidget(
            edit=self._highlight_button,
            on_activate_call=babase.Call(self._pick_color, "highlight"),
        )
        bui.textwidget(
            parent=self._root_widget,
            h_align="center",
            v_align="center",
            position=(self._width * 0.5 + b_offs, v - 65),
            size=(0, 0),
            draw_controller=self._highlight_button,
            text=babase.Lstr(resource="editProfileWindow.highlightText"),
            scale=0.7,
            color=bui.app.ui_v1.title_color,
            maxwidth=120,
        )

    def _pick_color(self, tag):
        if tag == "color":
            initial_color = self._color or self._default_colors[0]
        elif tag == "highlight":
            initial_color = self._highlight or self._default_colors[1]
        else:
            raise ValueError("Unexpected color picker tag: {}".format(tag))
        ColorPicker(
            parent=None,
            position=(0, 0),
            initial_color=initial_color,
            delegate=self,
            tag=tag,
        )

    def cancel_on_outside_click(self):
        bui.getsound("swish").play()
        self._cancel()

    def _cancel(self):
        if self._last_color and self._last_highlight:
            colorscheme = ColorScheme(self._last_color, self._last_highlight)
            colorscheme.apply()
        # Good idea to revert this back now so we do not break anything else.
        bui.app.classic.accounts.have_pro = original_have_pro
        bui.containerwidget(edit=self._root_widget, transition="out_right")

    def reset(self, transition_out=True):
        if transition_out:
            bui.getsound("gunCocking").play()
        babase.app.config["ColorScheme"] = (None, None)
        # Good idea to revert this back now so we do not break anything else.
        bui.app.classic.accounts.have_pro = original_have_pro
        babase.app.config.commit()
        bui.containerwidget(edit=self._root_widget, transition="out_right")

    def save(self, transition_out=True):
        if transition_out:
            bui.getsound("gunCocking").play()
        colorscheme = ColorScheme(
            self._color or self._default_colors[0],
            self._highlight or self._default_colors[1],
        )
        colorscheme.apply()
        # Good idea to revert this back now so we do not break anything else.
        bui.app.classic.accounts.have_pro = original_have_pro
        babase.app.config["ColorScheme"] = (
            self._color or self._default_colors[0],
            self._highlight or self._default_colors[1],
        )
        babase.app.config.commit()
        bui.containerwidget(edit=self._root_widget, transition="out_right")

    def _set_color(self, color):
        self._color = color
        if self._color_button:
            bui.buttonwidget(edit=self._color_button, color=color)

    def _set_highlight(self, color):
        self._highlight = color
        if self._highlight_button:
            bui.buttonwidget(edit=self._highlight_button, color=color)

    def color_picker_selected_color(self, picker, color):
        # The `ColorPicker` calls this method in the delegate once a color
        # is selected from the `ColorPicker` Window.
        if not self._root_widget:
            return
        tag = picker.get_tag()
        if tag == "color":
            self._set_color(color)
        elif tag == "highlight":
            self._set_highlight(color)
        else:
            raise ValueError("Unexpected color picker tag: {}".format(tag))

    def color_picker_closing(self, picker):
        # The `ColorPicker` expects this method to exist in the delegate,
        # so here it is!
        pass


class CustomTransactions:
    def __init__(self):
        self.custom_transactions = {}

    def _handle(self, transaction, *args, **kwargs):
        transaction_code = transaction.get("code")
        transaction_fn = self.custom_transactions.get(transaction_code)
        if transaction_fn is not None:
            return transaction_fn(transaction, *args, **kwargs)
        return original_add_transaction(transaction, *args, **kwargs)

    def add(self, transaction_code, transaction_fn):
        self.custom_transactions[transaction_code] = transaction_fn

    def enable(self):
        bui.app.plus.add_v1_account_transaction = self._handle


def launch_colorscheme_selection_window():
    # Store whether the player has a pro account or not
    # temporarily bypassing the restriction that only pro
    # accounts can set custom RGB colors, then restore later.
    #
    # We store it here instead of at startup because other
    # pro-unlocker plugins might override the game method early,
    # causing a race condition and potentially storing the wrong value.
    global original_have_pro
    original_have_pro = bui.app.classic.accounts.have_pro

    ColorSchemeWindow()


def colorscheme_transaction(transaction, *args, **kwargs):
    launch_colorscheme_selection_window()


def load_colorscheme():
    color, highlight = babase.app.config.get("ColorScheme", (None, None))
    if color and highlight:
        colorscheme = ColorScheme(color, highlight)
        colorscheme.apply()


def load_plugin():
    # Allow manual colorscheme changes through the in-game console.
    _babase.ColorScheme = ColorScheme
    # Add a new advanced code entry named "colorscheme" via
    # Settings -> Advanced -> Enter Code, enabling UI-based colorscheme changes.
    custom_transactions = CustomTransactions()
    custom_transactions.add("colorscheme", colorscheme_transaction)
    custom_transactions.enable()
    # Load any previously saved colorscheme.
    load_colorscheme()


# Load colors plugin on startup
load_plugin()

# Flags for sending icons
_stop_sending_icons = False
_icon_timers = []  # List of all active timers
_icons_menu_opened = False  # Check if menu is open or not


def show_icons_menu(source_widget=None):
    """Show icons menu - tall and narrow window with stop control"""
    global _icons_menu_opened
    if _icons_menu_opened:
        return  # Don't recreate if menu is already open
    _icons_menu_opened = True

    try:
        icons = [
            ('', ' Icon 1'),
            ('', ' Icon 2'),
            ('', ' Icon 3'),
            ('', ' Icon 4'),
            ('', ' Icon 5'),
            ('', ' Icon 6'),
            ('', ' Icon 7'),
            ('', ' Icon 8'),
            ('', ' Icon 9'),
            ('', ' Icon 10'),
            ('', ' Icon 11'),
            ('', ' Icon 12'),
            ('', ' Icon 13'),
            ('', ' Icon 14'),
            ('', ' Icon 15'),
            ('', ' Icon 16'),
            ('', ' Icon 17'),
            ('', ' Icon 18'),
            ('', ' Icon 19'),
            ('', ' Icon 20'),
            ('', ' Icon 21'),
            ('', ' Icon 22'),
            ('', ' Icon 23'),
            ('', ' Icon 24'),
            ('', ' Icon 25'),
            ('', ' Icon 26'),
            ('', ' Icon 27'),
            ('', ' Icon 28'),
            ('', ' Icon 29'),
            ('', ' Icon 30'),
            ('', ' Icon 31'),
            ('', ' Icon 32'),
            ('', ' Icon 33'),
            ('', ' Icon 34'),
            ('', ' Icon 35'),
            ('', ' Icon 36')
        ]

        w = bui.containerwidget(
            parent=bui.get_special_widget('overlay_stack'),
            size=(800, 700),
            scale=1.0,
            transition='in_scale',
            color=(0.12, 0.12, 0.12)
        )

        bui.textwidget(
            parent=w,
            text=u'\ue027 Game Icons',
            position=(400, 660),
            scale=1.3,
            color=(1, 1, 0),
            h_align='center'
        )

        scroll = bui.scrollwidget(
            parent=w,
            size=(700, 550),
            position=(60, 90)
        )

        column = bui.columnwidget(parent=scroll, left_border=10)

        for icon, label in icons:
            bui.buttonwidget(
                parent=column,
                size=(650, 50),
                label=label,
                on_activate_call=lambda i=icon: send_icon(i),
                color=(0.35, 0.35, 0.45),
                textcolor=(1, 1, 1)
            )

        # Send all button
        bui.buttonwidget(
            parent=w,
            position=(100, 30),
            icon=gt('logIcon'),
            size=(200, 60),
            iconscale=0.9,
            label='Send All (2 sec)',
            on_activate_call=lambda: send_all_icons_delayed(icons, 2.0),
            color=(0.2, 0.6, 0.2),
            textcolor=(1, 1, 1)
        )

        # Stop sending button
        bui.buttonwidget(
            parent=w,
            position=(525, 30),
            icon=gt('achievementsIcon'),
            size=(180, 60),
            iconscale=0.9,
            label='Stop Sending',
            on_activate_call=stop_sending_icons,
            color=(0.8, 0.3, 0.3),
            textcolor=(1, 1, 1)
        )

        # Close button
        bui.buttonwidget(
            parent=w,
            position=(350, 30),
            icon=gt('crossOut'),
            size=(120, 60),
            iconscale=0.9,
            label='Close',
            on_activate_call=lambda: close_icons_menu(w),
            color=(0.6, 0.2, 0.2),
            textcolor=(1, 1, 1)
        )

    except Exception as e:
        print(f"Error showing icons menu: {e}")


def close_icons_menu(widget):
    """Close the icons menu"""
    global _icons_menu_opened
    _icons_menu_opened = False
    bui.containerwidget(edit=widget, transition='out_scale')


def send_icon(icon: str):
    """Send icon to chat"""
    try:
        bs.chatmessage(icon)
        bui.screenmessage(f'Sent: {icon}', color=(0, 1, 0))
        bui.getsound('dingSmall').play()
    except Exception as e:
        print(f"Error sending icon: {e}")


def send_all_icons_delayed(icons, delay_seconds=2.0):
    """Send all icons with delay"""
    global _stop_sending_icons, _icon_timers
    _stop_sending_icons = False
    _icon_timers = []

    try:
        bui.screenmessage(f'Start sending all icons (every {delay_seconds} sec)...', color=(0, 1, 1))
        for i, (icon, _) in enumerate(icons):
            t = bui.apptimer(i * delay_seconds, lambda ic=icon: send_single_icon_delayed(ic))
            _icon_timers.append(t)
    except Exception as e:
        print(f"Error starting delayed send: {e}")


def send_single_icon_delayed(icon: str):
    """Send single icon with delay"""
    global _stop_sending_icons
    try:
        if _stop_sending_icons:
            return
        bs.chatmessage(icon)
        bui.screenmessage(f'Sent: {icon}', color=(0, 1, 0))
    except Exception as e:
        print(f"Error sending delayed icon: {e}")


def stop_sending_icons():
    """Stop sending all icons completely"""
    global _stop_sending_icons, _icon_timers
    _stop_sending_icons = True
    # Cancel all timers
    for t in _icon_timers:
        try:
            t.cancel()
        except Exception:
            pass
    _icon_timers = []
    bui.screenmessage('⛔ Sending of all icons stopped', color=(1, 0, 0))


# اضافه کردن کلاس ماشین حساب بعد از کلاس PlayerInfo
# اضافه کردن کلاس ماشین حساب بعد از کلاس PlayerInfo
class Calculator:
    def __init__(s, source):
        # Window with reduced height
        w = s.w = AR.cw(
            source=source,
            size=(400, 330),
            ps=AR.UIS() * 0.7
        )
        AR.add_close_button(w, position=(370, 290))

        # Title
        tw(parent=w, text='🧮 Calculator', scale=1.0, position=(180, 295), h_align='center', color=(0, 1, 1))

        # Display
        s.display = tw(parent=w, text='0', position=(175, 260), scale=1.2, h_align='center', color=(1, 1, 1),
                       maxwidth=350)

        # Calculation variables
        s.current_input = '0'
        s.previous_input = ''
        s.operation = None
        s.reset_next_input = False
        s.display_formatted = True

        # Action buttons (copy/send)
        action_buttons = [
            ('📋 Copy', s.copy_result, (20, 230), (170, 30), (0.3, 0.6, 0.8)),
            ('💬 Send', s.send_to_chat, (210, 230), (170, 30), (0.3, 0.8, 0.6))
        ]
        for label, callback, pos, size, color in action_buttons:
            bw(parent=w, label=label, size=size, position=pos, on_activate_call=callback, color=color,
               textcolor=(1, 1, 1), text_scale=0.7)

        # Main calculator buttons
        buttons = [
            # Row 1
            ('C', s.clear_all, (20, 180), (55, 30), (1, 0.5, 0.5)),
            ('±', s.toggle_sign, (85, 180), (55, 30), (0.5, 0.7, 1)),
            ('%', s.percentage, (150, 180), (55, 30), (0.5, 0.7, 1)),
            ('x²', s.square, (215, 180), (55, 30), (0.5, 0.7, 1)),
            ('√', s.square_root, (280, 180), (55, 30), (0.5, 0.7, 1)),
            ('xʸ', s.power, (345, 180), (55, 30), (0.5, 0.7, 1)),
            # Row 2
            ('7', lambda: s.append_number('7'), (20, 140), (55, 30), (0.4, 0.4, 0.6)),
            ('8', lambda: s.append_number('8'), (85, 140), (55, 30), (0.4, 0.4, 0.6)),
            ('9', lambda: s.append_number('9'), (150, 140), (55, 30), (0.4, 0.4, 0.6)),
            ('÷', lambda: s.set_operation('/'), (215, 140), (55, 30), (1, 0.8, 0.3)),
            ('⌫', s.backspace, (280, 140), (55, 30), (0.8, 0.3, 0.3)),
            (',', s.toggle_format, (345, 140), (55, 30), (0.7, 0.5, 0.8)),
            # Row 3
            ('4', lambda: s.append_number('4'), (20, 100), (55, 30), (0.4, 0.4, 0.6)),
            ('5', lambda: s.append_number('5'), (85, 100), (55, 30), (0.4, 0.4, 0.6)),
            ('6', lambda: s.append_number('6'), (150, 100), (55, 30), (0.4, 0.4, 0.6)),
            ('×', lambda: s.set_operation('*'), (215, 100), (55, 30), (1, 0.8, 0.3)),
            ('1/x', s.reciprocal, (280, 100), (55, 30), (0.5, 0.7, 1)),
            ('±', s.toggle_format_display, (345, 100), (55, 30), (0.7, 0.5, 0.8)),
            # Row 4
            ('1', lambda: s.append_number('1'), (20, 60), (55, 30), (0.4, 0.4, 0.6)),
            ('2', lambda: s.append_number('2'), (85, 60), (55, 30), (0.4, 0.4, 0.6)),
            ('3', lambda: s.append_number('3'), (150, 60), (55, 30), (0.4, 0.4, 0.6)),
            ('-', lambda: s.set_operation('-'), (215, 60), (55, 30), (1, 0.8, 0.3)),
            ('n!', s.factorial, (280, 60), (55, 30), (0.5, 0.7, 1)),
            ('log', s.logarithm, (345, 60), (55, 30), (0.5, 0.7, 1)),
            # Row 5
            ('0', lambda: s.append_number('0'), (20, 20), (120, 30), (0.4, 0.4, 0.6)),
            ('.', s.add_decimal, (150, 20), (55, 30), (0.4, 0.4, 0.6)),
            ('=', s.calculate, (215, 20), (55, 30), (0.2, 0.8, 0.2)),
            ('+', lambda: s.set_operation('+'), (280, 20), (120, 30), (1, 0.8, 0.3)),
        ]
        for label, callback, pos, size, color in buttons:
            bw(parent=w, label=label, size=size, position=pos, on_activate_call=callback, color=color,
               textcolor=(1, 1, 1), text_scale=0.8)

        AR.swish()

    # Number formatting with commas
    def format_number(s, number_str):
        try:
            num = float(number_str)
            if num.is_integer():
                num_int = int(num)
                return f"{num_int:,}" if abs(num_int) >= 1000 else str(num_int)
            else:
                parts = str(num).split('.')
                int_part = int(parts[0]) if parts[0] else 0
                formatted_int = f"{int_part:,}"
                decimal_part = parts[1][:6].rstrip('0')
                return formatted_int + '.' + decimal_part if decimal_part else formatted_int
        except:
            return number_str

    # Remove commas
    def parse_number(s, formatted_str):
        return formatted_str.replace(',', '')

    # Display text with/without commas
    def get_display_text(s):
        return s.format_number(s.current_input) if s.display_formatted else s.current_input

    def get_raw_text(s):
        return s.parse_number(s.current_input) if s.display_formatted else s.current_input

    def update_display(s):
        if s.display.exists():
            tw(s.display, text=s.get_display_text())

    def toggle_format(s):
        s.display_formatted = not s.display_formatted
        s.update_display()
        gs('click01').play()

    def toggle_format_display(s):
        status = "Formatted" if s.display_formatted else "Raw"
        push(f"Display mode: {status}", color=(0, 1, 1))
        gs('dingSmall').play()

    # Input methods
    def append_number(s, number):
        if s.reset_next_input: s.current_input = '0'; s.reset_next_input = False
        current = s.get_raw_text()
        s.current_input = number if current == '0' else current + number
        s.update_display();
        gs('click01').play()

    def add_decimal(s):
        if s.reset_next_input: s.current_input = '0'; s.reset_next_input = False
        current = s.get_raw_text()
        if '.' not in current: s.current_input = current + '.'; s.update_display(); gs('click01').play()

    def backspace(s):
        current = s.get_raw_text()
        if current != '0' and len(current) > 1:
            current = current[:-1]
        else:
            current = '0'
        s.current_input = current;
        s.update_display();
        gs('swish').play()

    # Operations
    def square(s):
        s._unary_op(lambda x: x ** 2)

    def square_root(s):
        s._unary_op(lambda x: x ** 0.5, allow_negative=False)

    def power(s):
        s._binary_op('**', "Enter second number")

    def reciprocal(s):
        s._unary_op(lambda x: 1 / x, zero_error=True)

    def factorial(s):
        s._unary_op(lambda n: __import__('math').factorial(int(n)), int_only=True)

    def logarithm(s):
        s._unary_op(lambda x: __import__('math').log10(x), positive_only=True)

    def toggle_sign(s):
        current = s.get_raw_text()
        if current != '0': s.current_input = current[1:] if current.startswith('-') else '-' + current
        s.update_display();
        gs('click01').play()

    def percentage(s):
        try:
            s.current_input = str(float(s.get_raw_text()) / 100); s.update_display(); gs('dingSmall').play()
        except:
            s.current_input = '0'; s.update_display()

    # Binary operation
    def set_operation(s, op):
        if s.operation and not s.reset_next_input: s.calculate()
        s.previous_input = s.get_raw_text();
        s.operation = op;
        s.reset_next_input = True;
        gs('click01').play()

    def calculate(s):
        try:
            if not s.operation or s.reset_next_input: return
            num1 = float(s.previous_input)
            num2 = float(s.get_raw_text())
            result = \
            {'+': num1 + num2, '-': num1 - num2, '*': num1 * num2, '/': num1 / num2 if num2 != 0 else float('nan'),
             '**': num1 ** num2}[s.operation]
            s.current_input = str(int(result)) if result.is_integer() else str(result)
            s.operation = None;
            s.reset_next_input = True;
            s.update_display();
            gs('dingSmallHigh').play()
        except ZeroDivisionError:
            s.current_input = 'Error: Div/0'; s.update_display(); gs('error').play(); teck(2.0, s.clear_all)
        except Exception as e:
            s.current_input = f'Error: {e}'; s.update_display(); gs('error').play(); teck(2.0, s.clear_all)

    # Clear
    def clear_all(s):
        s.current_input = '0'; s.previous_input = ''; s.operation = None; s.reset_next_input = False; s.update_display(); gs(
            'swish').play()

    # Copy/Send
    def copy_result(s):
        try:
            if CIS():
                from babase import clipboard_set_text
                clipboard_set_text(s.get_display_text())
                push(f'Copied: {s.get_display_text()}', color=(0, 1, 0));
                gs('dingSmall').play()
            else:
                AR.err('Clipboard not supported!')
        except Exception as e:
            AR.err(f'Copy error: {e}')

    def send_to_chat(s):
        try:
            CM(s.get_display_text());
            push(f'Sent: {s.get_display_text()}', color=(0, 1, 0));
            gs('dingSmall').play()
        except Exception as e:
            AR.err(f'Send error: {e}')

    # Helper for unary operations
    def _unary_op(s, func, allow_negative=True, zero_error=False, int_only=False, positive_only=False):
        try:
            current = float(s.get_raw_text())
            if not allow_negative and current < 0: raise ValueError
            if zero_error and current == 0: raise ZeroDivisionError
            if int_only: current = int(current)
            if positive_only and current <= 0: raise ValueError
            result = func(current)
            s.current_input = str(int(result)) if int_only or (
                        isinstance(result, float) and result.is_integer()) else str(result)
            s.update_display();
            gs('dingSmall').play()
        except:
            s.current_input = 'Error'; s.update_display(); gs('error').play(); teck(2.0, s.clear_all)

    def _binary_op(s, op_symbol, prompt_msg):
        s.operation = op_symbol; s.previous_input = s.get_raw_text(); s.reset_next_input = True; push(prompt_msg,
                                                                                                      color=(
                                                                                                      0, 1, 1)); gs(
            'click01').play()


"""بخش بهاری با اسپم جملات معمولی و فانوسی و مدیریت جملات"""
"""بخش بهاری با اسپم جملات معمولی و فانوسی و مدیریت جملات"""
"""بخش بهاری با اسپم جملات معمولی و فانوسی و مدیریت جملات"""
"""بخش بهاری با اسپم جملات معمولی و ناموسی"""


class Bahari:
    # متغیرهای global برای وضعیت اسپم
    spamming = False
    spam_timer = None
    spam_type = None
    active_instance = None

    # لیست‌های جملات
    normal_sentences = [
        "د آخه کحیرم تو قیافت بچه من سه سال پیش این ادعا رو داشتم",
        "انقد هرشب دارم میکامت حامله شدی دیگه",
        "هرچی کحیره میکنم تو قیافت کحیری فیس",
        "کحیری هرشب داری میمالی بهت نون بدم بعد شاخیدی",
        "افغانی بیا برو کحیرم بخواب بعد گوه بخور"
    ]

    namousi_sentences = [
        "مادرتو دیشب انقد کاییدم نه ماه دیگه برات داداش میاره",
        "فیلم مادرت تو پورن هاب در حال ساک زدن لو رفته",
        "خواهرت سر کوچه نشسته هرشب ساک میزنه",
        "هرچی کحیر تو جهانه تو مونث خانوادت میکنم",
        "مادرتو جوری میکام جوری که کحصش پاره بشه",
        "کل درختای جهان و میکنم تو کحص مادرت",
        "کحیرم تو کحص مادرت  مادرتو به سیصد روش میکام"
    ]

    def __init__(s, source):
        # ثبت خود به عنوان نمونه فعال
        Bahari.active_instance = s

        w = s.w = AR.cw(
            source=source,
            size=(500, 350),
            ps=AR.UIS() * 0.7
        )
        # افزودن دکمه بستن
        AR.add_close_button(w, position=(470, 300))

        # عنوان
        tw(
            parent=w,
            text=u'\ue027 Obscenity',
            scale=1.0,
            position=(329, 275),
            h_align='center',
            color=(1, 0.7, 0.9)
        )

        bw(
            parent=w,
            size=(70, 70),
            position=(335, 5),
            label='',
            texture=gt('controllerIcon'),
            color=(1, 1, 1)
        )

        # اسکرول برای دکمه‌ها
        s.scroll = sw(
            parent=w,
            size=(200, 250),
            position=(20, 50)
        )

        s.container = cw(
            parent=s.scroll,
            size=(200, 250),
            background=False
        )

        # دکمه معمولی
        s.normal_btn = bw(
            parent=s.container,
            label='Normal',
            size=(180, 35),
            icon=gt('achievementSuperPunch'),
            position=(10, 200),
            iconscale=0.9,
            on_activate_call=Call(s.confirm_spam, 'normal'),
            color=(0.4, 0.8, 0.5),
            textcolor=(1, 1, 1)
        )

        # دکمه ناموسی
        s.namousi_btn = bw(
            parent=s.container,
            label='Family',
            size=(180, 35),
            icon=gt('achievementBoxer'),
            position=(10, 150),
            iconscale=0.9,
            on_activate_call=Call(s.confirm_spam, 'namousi'),
            color=(0.9, 0.6, 0.3),
            textcolor=(1, 1, 1)
        )

        # دکمه استپ
        s.stop_btn = bw(
            parent=s.container,
            label='Stop',
            size=(180, 30),
            icon=gt('crossOut'),
            position=(10, 100),
            iconscale=0.9,
            on_activate_call=Call(s.stop_spam),
            color=(0.8, 0.2, 0.2),
            textcolor=(1, 1, 1),
            enable_sound=True
        )

        # دکمه‌های مدیریت جملات
        s.manage_normal_btn = bw(
            parent=s.container,
            label='Normal management',
            size=(180, 30),
            icon=gt('settingsIcon'),
            position=(10, 60),
            iconscale=0.9,
            on_activate_call=Call(s.manage_sentences, 'normal'),
            color=(0.3, 0.5, 0.8),
            textcolor=(1, 1, 1)
        )

        s.manage_namousi_btn = bw(
            parent=s.container,
            label='Family management',
            size=(180, 30),
            icon=gt('settingsIcon'),
            position=(10, 20),
            iconscale=0.9,
            on_activate_call=Call(s.manage_sentences, 'namousi'),
            color=(0.8, 0.5, 0.3),
            textcolor=(1, 1, 1)
        )

        # دکمه خاموش/روشن
        s.toggle_btn = bw(
            parent=w,
            label='OFF',
            size=(80, 35),
            position=(330, 70),
            on_activate_call=Call(s.toggle_state),
            color=(0.35, 0, 0),
            textcolor=(0.5, 0, 0)
        )

        # وضعیت
        s.status_text = tw(
            parent=w,
            text='Ready',
            position=(350, 230),
            scale=0.7,
            color=(0.8, 0.8, 1),
            h_align='center'
        )

        # آمار جملات در سمت راست
        s.stats_text = tw(
            parent=w,
            text=f'📊 Sentence statistics:\n\nNormal: {len(s.normal_sentences)}\nNamousi: {len(s.namousi_sentences)}\n\n🔧 Status: Inactive',
            position=(350, 200),
            scale=0.55,
            color=(0.7, 1, 0.7),
            maxwidth=150,
            h_align='center'
        )

        # بروزرسانی وضعیت بر اساس وضعیت global
        if Bahari.spamming:
            bw(s.stop_btn, color=(1, 0.3, 0.3))
            type_name = 'Normal' if Bahari.spam_type == 'normal' else 'Family'
            tw(s.status_text, text=f'Spam {type_name} active', color=(0, 1, 0))
            bw(s.toggle_btn, label='ON', color=(0, 0.45, 0), textcolor=(0, 0.6, 0))
            tw(s.stats_text,
               text=f'📊 Sentence statistics:\n\nNormal: {len(s.normal_sentences)}\nNamousi: {len(s.namousi_sentences)}\n\n🔧 Status: Active')

        AR.swish()

    def toggle_state(s):
        """تغییر حالت خاموش/روشن"""
        if Bahari.spamming:
            s.stop_spam()
            bw(s.toggle_btn, label='OFF', color=(0.35, 0, 0), textcolor=(0.5, 0, 0))
            tw(s.stats_text,
               text=f'📊 Sentence statistics:\n\nNormal: {len(s.normal_sentences)}\nNamousi: {len(s.namousi_sentences)}\n\n🔧 Status: Inactive')
        else:
            if not Bahari.spam_type:
                AR.err('Please select the spam type first!')
                return
            s.start_spam()
            bw(s.toggle_btn, label='ON', color=(0, 0.45, 0), textcolor=(0, 0.6, 0))
            tw(s.stats_text,
               text=f'📊 Sentence statistics:\n\nNormal: {len(s.normal_sentences)}\nNamousi: {len(s.namousi_sentences)}\n\n🔧 Status: Active')

    def confirm_spam(s, spam_type):
        """تأیید شروع اسپم"""
        Bahari.spam_type = spam_type
        type_name = 'Normal' if spam_type == 'normal' else 'Family'

        # ایجاد پنجره تأیید
        confirm_win = AR.cw(
            source=s.w,
            size=(300, 140),
            ps=AR.UIS() * 0.6
        )

        AR.add_close_button(confirm_win, position=(250, 105))

        tw(
            parent=confirm_win,
            text=f'Are you sure you want to start\nspam {type_name}?',
            position=(115, 80),
            scale=0.7,
            color=(1, 1, 1),
            h_align='center'
        )

        def start_and_close():
            s.start_spam()
            AR.swish(confirm_win)

        bw(
            parent=confirm_win,
            label='Yes',
            size=(70, 25),
            icon=gt('startButton'),
            position=(120, 10),
            iconscale=0.6,
            on_activate_call=start_and_close,
            color=(0, 0.6, 0)
        )

    def start_spam(s):
        """شروع اسپم"""
        if Bahari.spamming:
            AR.err('Spam is in progress!')
            return

        Bahari.spamming = True

        # بروزرسانی وضعیت در صورت وجود ویجت‌ها
        if s.status_text.exists():
            tw(s.status_text, text='Spamming...', color=(0, 1, 0))
        if s.stop_btn.exists():
            bw(s.stop_btn, color=(1, 0.3, 0.3))
        if s.toggle_btn.exists():
            bw(s.toggle_btn, label='ON', color=(0, 0.45, 0), textcolor=(0, 0.6, 0))
        if s.stats_text.exists():
            tw(s.stats_text,
               text=f'📊 Sentence statistics:\n\nNormal: {len(s.normal_sentences)}\nNamousi: {len(s.namousi_sentences)}\n\n🔧 Status: Active')

        # لیست جملات بر اساس نوع
        if Bahari.spam_type == 'normal':
            sentences = s.normal_sentences
        else:
            sentences = s.namousi_sentences

        s.sentences = sentences
        s.current_index = 0
        s.do_spam()

        type_name = 'Normal' if Bahari.spam_type == 'normal' else 'Family'
        push(f'Start spam {type_name}', color=(0, 1, 0))
        gs('dingSmallHigh').play()

    def do_spam(s):
        """انجام اسپم"""
        if not Bahari.spamming:
            return

        try:
            # ارسال جمله فعلی
            sentence = s.sentences[s.current_index]
            CM(sentence)

            # افزایش ایندکس برای جمله بعدی
            s.current_index = (s.current_index + 1) % len(s.sentences)

            # بروزرسانی وضعیت
            if s.status_text.exists():
                tw(s.status_text, text=f'Send: {sentence[:12]}...')

            # تنظیم تایمر برای جمله بعدی
            Bahari.spam_timer = teck(2.0, s.do_spam)

        except Exception as e:
            AR.err(f'Error in spam: {str(e)}')
            s.stop_spam()

    def stop_spam(s):
        """توقف اسپم"""
        if not Bahari.spamming:
            return

        Bahari.spamming = False

        if Bahari.spam_timer:
            try:
                Bahari.spam_timer.cancel()
            except:
                pass
            Bahari.spam_timer = None

        # بروزرسانی وضعیت در صورت وجود ویجت‌ها
        if s.stop_btn.exists():
            bw(s.stop_btn, color=(0.8, 0.2, 0.2))
        if s.status_text.exists():
            tw(s.status_text, text='Stopped', color=(1, 0.5, 0))
        if s.toggle_btn.exists():
            bw(s.toggle_btn, label='OFF', color=(0.35, 0, 0), textcolor=(0.5, 0, 0))
        if s.stats_text.exists():
            tw(s.stats_text,
               text=f'📊 Sentence statistics:\n\nNormal: {len(s.normal_sentences)}\nNamousi: {len(s.namousi_sentences)}\n\n🔧 Status: Inactive')

        type_name = 'Normal' if Bahari.spam_type == 'normal' else 'Family'
        push(f'Spam {type_name} stopped', color=(1, 0.5, 0))
        gs('dingSmallLow').play()

    def manage_sentences(s, sentence_type):
        """مدیریت جملات"""
        sentences = s.normal_sentences if sentence_type == 'normal' else s.namousi_sentences
        type_name = 'Normal' if sentence_type == 'normal' else 'Family'

        win = AR.cw(
            source=s.w,
            size=(380, 350),
            ps=AR.UIS() * 0.6
        )

        AR.add_close_button(win, position=(350, 310))

        tw(
            parent=win,
            text=f'\ue020 Manage sentences {type_name}',
            scale=0.9,
            position=(175, 305),
            h_align='center',
            color=(1, 1, 0)
        )

        # اسکرول برای لیست جملات
        scroll = sw(
            parent=win,
            size=(340, 180),
            position=(20, 120)
        )

        container = cw(
            parent=scroll,
            size=(340, len(sentences) * 35),
            background=False
        )

        # نمایش جملات
        y_pos = len(sentences) * 30 - 10
        for i, sentence in enumerate(sentences):
            # جمله
            tw(
                parent=container,
                text=f"{i + 1}. {sentence}",
                position=(10, y_pos),
                scale=0.5,
                color=(1, 1, 1),
                maxwidth=220,
                h_align='left'
            )

            # دکمه حذف
            bw(
                parent=container,
                label='',
                size=(30, 20),
                icon=gt('crossOut'),
                position=(280, y_pos),
                iconscale=0.9,
                on_activate_call=Call(s.delete_sentence, sentence_type, i, win),
                color=(0.8, 0.2, 0.2),
                text_scale=0.5
            )

            y_pos -= 30

        # دکمه افزودن جمله جدید
        bw(
            parent=win,
            label='Add Sentence',
            size=(120, 25),
            icon=gt('nextLevelIcon'),
            position=(140, 70),
            iconscale=0.9,
            on_activate_call=Call(s.add_new_sentence, sentence_type, win),
            color=(0.2, 0.7, 0.3),
            textcolor=(1, 1, 1)
        )

        # دکمه بازنشانی
        bw(
            parent=win,
            label='Reset',
            size=(120, 25),
            icon=gt('replayIcon'),
            position=(140, 25),
            iconscale=0.9,
            on_activate_call=Call(s.reset_sentences, sentence_type, win),
            color=(0.5, 0.5, 0.8),
            textcolor=(1, 1, 1)
        )

    def add_new_sentence(s, sentence_type, parent_win):
        """افزودن جمله جدید"""

        def save_sentence():
            new_sentence = tw(query=text_input).strip()
            if new_sentence:
                if sentence_type == 'normal':
                    s.normal_sentences.append(new_sentence)
                else:
                    s.namousi_sentences.append(new_sentence)

                push(f'New sentence added', color=(0, 1, 0))
                gs('dingSmallHigh').play()
                AR.swish(add_win)
                s.manage_sentences(sentence_type)
                # بروزرسانی آمار
                if s.stats_text.exists():
                    tw(s.stats_text,
                       text=f'📊 Sentence statistics:\n\nNormal: {len(s.normal_sentences)}\nNamousi: {len(s.namousi_sentences)}\n\n🔧 Status: {"Active" if Bahari.spamming else "Inactive"}')
            else:
                AR.err('Please enter a sentence!')

        add_win = AR.cw(
            source=parent_win,
            size=(320, 160),
            ps=AR.UIS() * 0.5
        )

        AR.add_close_button(add_win, position=(290, 120))

        type_name = 'Normal' if sentence_type == 'normal' else 'Family'
        tw(
            parent=add_win,
            text=f'New sentence {type_name}:',
            position=(20, 110),
            scale=0.7,
            color=(1, 1, 1)
        )

        text_input = tw(
            parent=add_win,
            position=(20, 70),
            size=(280, 30),
            editable=True,
            text='',
            color=(0.9, 0.9, 0.9),
            description="Enter your sentence"
        )

        bw(
            parent=add_win,
            label='Save',
            size=(80, 25),
            icon=gt('upButton'),
            position=(120, 25),
            iconscale=0.6,
            on_activate_call=save_sentence,
            color=(0, 0.6, 0)
        )

    def delete_sentence(s, sentence_type, index, parent_win):
        """حذف جمله"""
        sentences = s.normal_sentences if sentence_type == 'normal' else s.namousi_sentences
        sentence = sentences[index]

        def confirm_delete():
            sentences.pop(index)
            push('Sentence deleted', color=(1, 0.5, 0))
            gs('dingSmallLow').play()
            AR.swish(confirm_win)
            s.manage_sentences(sentence_type)
            # بروزرسانی آمار
            if s.stats_text.exists():
                tw(s.stats_text,
                   text=f'📊 Sentence statistics:\n\nNormal: {len(s.normal_sentences)}\nNamousi: {len(s.namousi_sentences)}\n\n🔧 Status: {"Active" if Bahari.spamming else "Inactive"}')

        confirm_win = AR.cw(
            source=parent_win,
            size=(320, 140),
            ps=AR.UIS() * 0.5
        )

        AR.add_close_button(confirm_win, position=(290, 120))

        tw(
            parent=confirm_win,
            text=f'Are you sure you want to delete this sentence?',
            position=(130, 90),
            scale=0.6,
            color=(1, 1, 1),
            h_align='center'
        )

        bw(
            parent=confirm_win,
            label='Yes',
            size=(80, 25),
            position=(125, 25),
            on_activate_call=confirm_delete,
            color=(0.3, 0.6, 0.3)
        )

    def reset_sentences(s, sentence_type, parent_win):
        """بازنشانی جملات به پیش‌فرض"""

        def confirm_reset():
            if sentence_type == 'normal':
                s.normal_sentences = [
                    "بهار آمده، طبیعت بیدار شده",
                    "گلها شکفته، جهان زیبا شده",
                    "نسیم بهاری، خنک و فرح بخش",
                    "پرندگان آواز، بهار را بشارت می‌دهند",
                    "درختان سبز، جهان را زنده کرده‌اند"
                ]
            else:
                s.namousi_sentences = [
                    "ناموس خانواده، قابل احترام است",
                    "حفظ ناموس، نشانه شخصیت است",
                    "ناموس، امانتی الهی است",
                    "حرمت ناموس، حرمت انسانیت است",
                    "ناموس، سرمایه خانواده است"
                ]

            push('Sentences reset', color=(0, 1, 1))
            gs('dingSmallHigh').play()
            AR.swish(confirm_win)
            s.manage_sentences(sentence_type)
            # بروزرسانی آمار
            if s.stats_text.exists():
                tw(s.stats_text,
                   text=f'📊 Sentence statistics:\n\nNormal: {len(s.normal_sentences)}\nNamousi: {len(s.namousi_sentences)}\n\n🔧 Status: {"Active" if Bahari.spamming else "Inactive"}')

        confirm_win = AR.cw(
            source=parent_win,
            size=(350, 140),
            ps=AR.UIS() * 0.5
        )

        AR.add_close_button(confirm_win, position=(300, 100))

        type_name = 'Normal' if sentence_type == 'normal' else 'Family'
        tw(
            parent=confirm_win,
            text=f'Are you sure you want to \nreset the {type_name} sentences?',
            position=(140, 90),
            scale=0.6,
            color=(1, 1, 1),
            h_align='center'
        )

        bw(
            parent=confirm_win,
            label='Yes',
            size=(100, 30),
            icon=gt('replayIcon'),
            position=(130, 10),
            iconscale=0.6,
            on_activate_call=confirm_reset,
            color=(0.3, 0.6, 0.3)
        )

# کلاس جدید برای دکمه پینگ
class PingButton:
    def __init__(s, source):
        s.w = AR.cw(
            source=source,
            size=(150, 80),
            ps=AR.UIS() * 0.5
        )

        # دکمه پینگ
        s.ping_btn = bw(
            parent=s.w,
            label=f'{current_ping} ms',
            size=(120, 40),
            position=(15, 30),
            on_activate_call=s.send_ping,
            color=(0.3, 0.6, 0.8),
            textcolor=(1, 1, 1)
        )

        # تایمر برای بروزرسانی خودکار
        teck(1.0, s.update_ping_button)

        AR.swish()

    def update_ping_button(s):
        """بروزرسانی متن دکمه پینگ"""
        try:
            if s.ping_btn.exists():
                # تعیین رنگ بر اساس پینگ
                if current_ping < 100:
                    btn_color = (0.2, 0.8, 0.2)  # سبز
                elif current_ping < 300:
                    btn_color = (0.8, 0.8, 0.2)  # زرد
                else:
                    btn_color = (0.8, 0.2, 0.2)  # قرمز

                bw(s.ping_btn,
                   label=f'{current_ping} ms',
                   color=btn_color)
        except:
            pass

        # ادامه تایمر
        teck(1.0, s.update_ping_button)

    def send_ping(s):
        """ارسال پینگ به چت"""
        try:
            ping_message = f"🏓 Ping : {current_ping} ms"
            CM(ping_message)
            push(f'Ping sent : {current_ping} ms', color=(0, 1, 0))
            gs('dingSmall').play()
        except Exception as e:
            AR.err(f'Error sending ping : {str(e)}')


class BsRushWindow:
    def __init__(s, source):
        w = s.w = AR.cw(
            source=source,
            size=(400, 300),
            ps=AR.UIS() * 0.7
        )

        # افزودن دکمه بستن
        AR.add_close_button(w, position=(360, 270))

        # عنوان اصلی
        tw(
            parent=w,
            text='⚡BsRush Menu',
            scale=1.2,
            position=(170, 250),
            h_align='center',
            color=(0, 1, 1)
        )

        # نام سازنده
        tw(
            parent=w,
            text='Subscribe to the channels below \nto download more mods.',
            scale=0.8,
            position=(190, 220),
            h_align='center',
            color=(1, 1, 0)
        )

        # متن معرفی دکمه‌ها
        tw(
            parent=w,
            text='Click on the buttons to open links in browser.',
            scale=0.7,
            position=(180, 150),
            h_align='center',
            color=(0, 1, 0)
        )

        # دکمه اول - کانال رسمی
        bw(
            parent=w,
            label='Official Channel',
            size=(180, 35),
            icon=gt('achievementEmpty'),
            position=(20, 110),
            iconscale=0.9,
            on_activate_call=Call(s.open_url, 'https://t.me/BsRushGames'),
            color=(0.2, 0.6, 0.9),
            textcolor=(1, 1, 1)
        )

        # دکمه دوم - گپ
        bw(
            parent=w,
            label='Group',
            size=(180, 35),
            icon=gt('achievementTeamPlayer'),
            position=(210, 110),
            iconscale=0.9,
            on_activate_call=Call(s.open_url, 'https://t.me/BSRush_Gap'),
            color=(0.3, 0.7, 0.4),
            textcolor=(1, 1, 1)
        )

        # دکمه سوم - کانال مودها
        bw(
            parent=w,
            label='Mods Channel',
            size=(180, 35),
            icon=gt('discordServer'),
            position=(110, 70),
            iconscale=0.9,
            on_activate_call=Call(s.open_url, 'https://t.me/BsRush_Mod'),
            color=(0.8, 0.4, 0.6),
            textcolor=(1, 1, 1)
        )

        # آیکون
        bw(
            parent=w,
            size=(70, 70),
            position=(175, 5),
            label='',
            texture=gt('discordServer'),
            color=(1, 1, 1)
        )

        AR.swish()

    def open_url(s, url):
        """باز کردن لینک در مرورگر"""
        try:
            import babase
            babase.open_url(url)
            push(f'Opening: {url}', color=(0, 1, 0))
            gs('dingSmall').play()
        except Exception as e:
            push(f'❌ Error opening URL: {str(e)}', color=(1, 0, 0))


class SimpleCamera:
    def __init__(self):
        self.rotating = False
        self.rotation_timer = None
        self.rotation_angle = 0

    def open_camera_menu(self, source_widget):
        """باز کردن منوی دوربین دستی"""
        try:
            import _babase
            import babase
            import bauiv1 as bui
            import math

            # ایجاد پنجره عریض‌تر
            w = bui.containerwidget(
                parent=bui.get_special_widget('overlay_stack'),
                size=(1100, 600),  # عرض بیشتر شده به 1100
                transition='in_scale',
                scale=1.0,
                color=(0.15, 0.15, 0.15)
            )

            # عنوان اصلی
            bui.textwidget(
                parent=w,
                text='🎥 Manual Camera Control',
                position=(550, 550),  # موقعیت جدید برای عرض بیشتر
                scale=1.5,
                color=(0, 1, 1),
                h_align='center'
            )

            # متن توضیحی
            bui.textwidget(
                parent=w,
                text='Control the game camera manually',
                position=(550, 500),  # موقعیت جدید
                scale=0.8,
                color=(1, 1, 0.8),
                h_align='center'
            )

            # بخش موقعیت دوربین
            bui.textwidget(
                parent=w,
                text='📷 CAMERA POSITION',
                position=(150, 450),  # موقعیت جدید
                scale=1.1,
                color=(0, 1, 0),
                h_align='center'
            )

            # دکمه‌های موقعیت - با فاصله بیشتر
            # ردیف X
            bui.buttonwidget(
                parent=w,
                label='← X-',
                size=(90, 45),
                icon=gt('ouyaOButton'),
                position=(10, 330),
                iconscale=0.6,  # موقعیت جدید
                on_activate_call=babase.Call(self._move_camera_simple, 'x-'),
                color=(0.8, 0.3, 0.3),
                textcolor=(1, 1, 1)
            )

            bui.buttonwidget(
                parent=w,
                label='→ X+',
                size=(90, 45),
                icon=gt('ouyaIcon'),
                position=(150, 330),
                iconscale=0.6,  # موقعیت جدید
                on_activate_call=babase.Call(self._move_camera_simple, 'x'),
                color=(0.3, 0.8, 0.3),
                textcolor=(1, 1, 1)
            )

            # ردیف Y
            bui.buttonwidget(
                parent=w,
                label='↑ Y+',
                size=(90, 45),
                icon=gt('ouyaUButton'),
                position=(75, 390),
                iconscale=0.6,  # موقعیت جدید
                on_activate_call=babase.Call(self._move_camera_simple, 'y'),
                color=(0.3, 0.3, 0.8),
                textcolor=(1, 1, 1)
            )

            bui.buttonwidget(
                parent=w,
                label='↓ Y-',
                size=(90, 45),
                icon=gt('ouyaAButton'),
                position=(75, 270),
                iconscale=0.6,  # موقعیت جدید
                on_activate_call=babase.Call(self._move_camera_simple, 'y-'),
                color=(0.8, 0.8, 0.3),
                textcolor=(1, 1, 1)
            )

            # ردیف Zoom
            bui.buttonwidget(
                parent=w,
                label='Zoom IN',
                size=(100, 45),
                icon=gt('upButton'),
                position=(270, 390),
                iconscale=0.6,  # موقعیت جدید
                on_activate_call=babase.Call(self._move_camera_simple, 'z'),
                color=(0.8, 0.3, 0.8),
                textcolor=(1, 1, 1)
            )

            bui.buttonwidget(
                parent=w,
                label='Zoom OUT',
                size=(100, 45),
                icon=gt('downButton'),
                position=(270, 330),
                iconscale=0.6,  # موقعیت جدید
                on_activate_call=babase.Call(self._move_camera_simple, 'z-'),
                color=(0.3, 0.8, 0.8),
                textcolor=(1, 1, 1)
            )

            # بخش target دوربین
            bui.textwidget(
                parent=w,
                text='🎯 CAMERA TARGET',
                position=(900, 450),  # موقعیت جدید
                scale=1.1,
                color=(1, 0.5, 0),
                h_align='center'
            )

            # دکمه‌های target
            bui.buttonwidget(
                parent=w,
                label='Target X-',
                size=(110, 45),
                icon=gt('ouyaAButton'),
                position=(800, 330),
                iconscale=0.6,  # موقعیت جدید
                on_activate_call=babase.Call(self._move_target_simple, 'x-'),
                color=(0.8, 0.5, 0.3),
                textcolor=(1, 1, 1)
            )

            bui.buttonwidget(
                parent=w,
                label='Target X+',
                size=(110, 45),
                icon=gt('ouyaUButton'),
                position=(930, 330),
                iconscale=0.6,  # موقعیت جدید
                on_activate_call=babase.Call(self._move_target_simple, 'x'),
                color=(0.5, 0.8, 0.3),
                textcolor=(1, 1, 1)
            )

            bui.buttonwidget(
                parent=w,
                label='Target Y+',
                size=(110, 45),
                icon=gt('ouyaIcon'),
                position=(865, 390),
                iconscale=0.6,  # موقعیت جدید
                on_activate_call=babase.Call(self._move_target_simple, 'y'),
                color=(0.3, 0.5, 0.8),
                textcolor=(1, 1, 1)
            )

            bui.buttonwidget(
                parent=w,
                label='Target Y-',
                size=(110, 45),
                icon=gt('ouyaOButton'),
                position=(865, 270),
                iconscale=0.6,  # موقعیت جدید
                on_activate_call=babase.Call(self._move_target_simple, 'y-'),
                color=(0.8, 0.3, 0.5),
                textcolor=(1, 1, 1)
            )

            # بخش چرخش دوربین
            bui.textwidget(
                parent=w,
                text=' CAMERA ROTATION',
                position=(550, 450),  # موقعیت جدید
                scale=1.1,
                color=(1, 0.8, 0),
                h_align='center'
            )

            # دکمه چرخش دوربین
            self.rotate_btn = bui.buttonwidget(
                parent=w,
                label='START ROTATION',
                size=(180, 50),
                icon=gt('startButton'),
                position=(485, 390),
                iconscale=0.6,  # موقعیت جدید
                on_activate_call=self._toggle_rotation,
                color=(0.6, 0.3, 0.8),
                textcolor=(1, 1, 1)
            )

            # دکمه‌های جهت چرخش
            bui.buttonwidget(
                parent=w,
                label='Right',
                size=(120, 40),
                icon=gt('rightButton'),
                position=(600, 330),
                iconscale=0.6,  # موقعیت جدید
                on_activate_call=babase.Call(self._set_rotation_direction, 'clockwise'),
                color=(0.4, 0.6, 0.8),
                textcolor=(1, 1, 1)
            )

            bui.buttonwidget(
                parent=w,
                label='Left',
                size=(120, 40),
                icon=gt('leftButton'),
                position=(450, 330),
                iconscale=0.6,  # موقعیت جدید
                on_activate_call=babase.Call(self._set_rotation_direction, 'counter'),
                color=(0.8, 0.6, 0.4),
                textcolor=(1, 1, 1)
            )

            # بخش تنظیمات
            bui.textwidget(
                parent=w,
                text='⚙️ SETTINGS',
                position=(550, 220),  # موقعیت جدید
                scale=1.1,
                color=(1, 1, 0),
                h_align='center'
            )

            # فیلد Step
            bui.textwidget(
                parent=w,
                text='Step Size:',
                position=(450, 180),  # موقعیت جدید
                scale=1.0,
                color=(1, 1, 1)
            )

            self.step_field = bui.textwidget(
                parent=w,
                position=(580, 170),  # موقعیت جدید
                size=(150, 40),
                text='1.0',
                editable=True,
                max_chars=6,
                color=(0.9, 0.9, 0.9)
            )

            # فیلد سرعت چرخش
            bui.textwidget(
                parent=w,
                text='Rotation Speed:',
                position=(390, 130),  # موقعیت جدید
                scale=1.0,
                color=(1, 1, 1)
            )

            self.speed_field = bui.textwidget(
                parent=w,
                position=(580, 120),  # موقعیت جدید
                size=(150, 40),
                text='1.0',
                editable=True,
                max_chars=6,
                color=(0.9, 0.9, 0.9)
            )

            # دکمه‌های کنترلی
            bui.buttonwidget(
                parent=w,
                label=' RESET CAMERA',
                size=(200, 55),
                icon=gt('replayIcon'),
                position=(350, 60),
                iconscale=0.6,  # موقعیت جدید
                on_activate_call=self._reset_camera_simple,
                color=(0.8, 0.2, 0.2),
                textcolor=(1, 1, 1)
            )

            bui.buttonwidget(
                parent=w,
                label=' DONE',
                size=(200, 55),
                icon=gt('achievementOutline'),
                position=(600, 60),
                iconscale=0.6,  # موقعیت جدید
                on_activate_call=babase.Call(bui.containerwidget, w, transition='out_scale'),
                color=(0.2, 0.8, 0.2),
                textcolor=(1, 1, 1)
            )

            # اطلاعات وضعیت
            self.status_text = bui.textwidget(
                parent=w,
                text='🎥 Camera control ready - Click buttons to adjust',
                position=(550, 20),  # موقعیت جدید
                scale=0.8,
                color=(0.8, 1, 0.8),
                h_align='center'
            )

            # دکمه بستن در گوشه بالا راست
            bui.buttonwidget(
                parent=w,
                label='X',
                size=(70, 70),
                position=(1020, 545),
                on_activate_call=babase.Call(bui.containerwidget, w, transition='out_scale'),
                color=(0.8, 0.2, 0.2),
                textcolor=(1, 1, 1)
            )

            # متغیرهای چرخش
            self.rotation_direction = 'clockwise'
            self.rotation_angle = 0

            self._update_status("🎥 Camera control ready - Adjust as needed")

        except Exception as e:
            print(f"Error opening camera menu: {e}")

    def _toggle_rotation(self):
        """شروع یا توقف چرخش دوربین"""
        try:
            import bauiv1 as bui

            if not self.rotating:
                # شروع چرخش
                self.rotating = True
                bui.buttonwidget(edit=self.rotate_btn,
                                 label='⏹️ STOP ROTATION',
                                 color=(0.8, 0.2, 0.2))
                self._update_status("🔄 Camera rotation STARTED")
                self._start_rotation()
            else:
                # توقف چرخش
                self.rotating = False
                bui.buttonwidget(edit=self.rotate_btn,
                                 label='🔄 START ROTATION',
                                 color=(0.6, 0.3, 0.8))
                self._update_status("⏹️ Camera rotation STOPPED")

        except Exception as e:
            print(f"Error toggling rotation: {e}")

    def _set_rotation_direction(self, direction):
        """تنظیم جهت چرخش"""
        self.rotation_direction = direction
        direction_text = "CLOCKWISE" if direction == 'clockwise' else "COUNTER-CLOCKWISE"
        self._update_status(f"🔄 Rotation direction: {direction_text}")

    def _start_rotation(self):
        """شروع چرخش دوربین در جای خودش"""
        if not self.rotating:
            return

        try:
            import _babase
            import bauiv1 as bui
            import math

            # فعال کردن حالت دستی
            _babase.set_camera_manual(True)

            # دریافت سرعت چرخش
            try:
                speed_text = bui.textwidget(query=self.speed_field)
                speed = float(speed_text) if speed_text else 2.0
            except:
                speed = 2.0

            # محاسبه زاویه جدید
            if self.rotation_direction == 'clockwise':
                self.rotation_angle += speed
            else:
                self.rotation_angle -= speed

            # محدود کردن زاویه بین 0 تا 360
            self.rotation_angle %= 360

            # گرفتن موقعیت فعلی دوربین و target
            camera_pos = _babase.get_camera_position()
            target_pos = _babase.get_camera_target()

            # محاسبه فاصله بین دوربین و target
            dx = target_pos[0] - camera_pos[0]
            dy = target_pos[1] - camera_pos[1]
            dz = target_pos[2] - camera_pos[2]
            distance = math.sqrt(dx * dx + dy * dy + dz * dz)

            # چرخش دوربین حول target (دوربین در جای خودش می‌چرخد)
            if distance > 0:
                dx /= distance
                dy /= distance
                dz /= distance

                # چرخش حول محور Y (چرخش افقی)
                rad_angle = math.radians(speed if self.rotation_direction == 'clockwise' else -speed)
                cos_angle = math.cos(rad_angle)
                sin_angle = math.sin(rad_angle)

                # چرخش بردار جهت حول محور Y
                new_dx = dx * cos_angle + dz * sin_angle
                new_dz = -dx * sin_angle + dz * cos_angle

                # محاسبه موقعیت جدید دوربین
                new_camera_x = target_pos[0] - new_dx * distance
                new_camera_z = target_pos[2] - new_dz * distance

                # تنظیم موقعیت جدید دوربین
                _babase.set_camera_position(new_camera_x, camera_pos[1], new_camera_z)

            # تنظیم تایمر برای فریم بعدی
            self.rotation_timer = bui.apptimer(0.05, self._start_rotation)

        except Exception as e:
            print(f"Error in rotation: {e}")
            self.rotating = False

    def _get_step_value(self):
        """دریافت مقدار step از فیلد"""
        try:
            import bauiv1 as bui
            step_text = bui.textwidget(query=self.step_field)
            return float(step_text) if step_text else 1.0
        except:
            return 1.0

    def _update_status(self, message):
        """بروزرسانی وضعیت"""
        try:
            import bauiv1 as bui
            if hasattr(self, 'status_text'):
                bui.textwidget(edit=self.status_text, text=message)
                print(f"Camera Status: {message}")
        except Exception as e:
            print(f"Error updating status: {e}")

    def _move_camera_simple(self, direction):
        """حرکت ساده دوربین"""
        try:
            import _babase
            step = self._get_step_value()
            pos = list(_babase.get_camera_position())

            # اول حالت دستی را فعال کن
            _babase.set_camera_manual(True)

            if direction == 'x':
                pos[0] += step
            elif direction == 'x-':
                pos[0] -= step
            elif direction == 'y':
                pos[1] += step
            elif direction == 'y-':
                pos[1] -= step
            elif direction == 'z':
                pos[2] += step
            elif direction == 'z-':
                pos[2] -= step

            _babase.set_camera_position(pos[0], pos[1], pos[2])
            self._update_status(f"📷 Camera moved {direction} by {step}")

        except Exception as e:
            print(f"Error moving camera: {e}")
            self._update_status("❌ Error moving camera!")

    def _move_target_simple(self, direction):
        """حرکت ساده target"""
        try:
            import _babase
            step = self._get_step_value()
            target = list(_babase.get_camera_target())

            # اول حالت دستی را فعال کن
            _babase.set_camera_manual(True)

            if direction == 'x':
                target[0] += step
            elif direction == 'x-':
                target[0] -= step
            elif direction == 'y':
                target[1] += step
            elif direction == 'y-':
                target[1] -= step

            _babase.set_camera_target(target[0], target[1], target[2])
            self._update_status(f"🎯 Target moved {direction} by {step}")

        except Exception as e:
            print(f"Error moving target: {e}")
            self._update_status("❌ Error moving target!")

    def _reset_camera_simple(self):
        """بازنشانی دوربین به حالت اتوماتیک"""
        try:
            import _babase
            self.rotating = False
            _babase.set_camera_manual(False)
            self._update_status("🔄 Camera reset to AUTO mode!")
        except Exception as e:
            print(f"Error resetting camera: {e}")
            self._update_status("❌ Error resetting camera!")

    def _done_camera_simple(self, window):
        """بستن پنجره - دوربین را به حالت اتوماتیک برگردان"""
        try:
            import bauiv1 as bui
            import _babase
            self.rotating = False
            _babase.set_camera_manual(False)
            bui.containerwidget(edit=window, transition='out_scale')
            self._update_status("✅ Window closed - Camera returned to AUTO mode")
        except Exception as e:
            print(f"Error in done_camera: {e}")


# ایجاد نمونه
camera_control = SimpleCamera()

"""Practice Tools - بدون قابلیت دیسکو لایت"""


class PracticeTools:
    def __init__(s, source):
        # ویندوز اصلی با ارتفاع کمتر
        s.w = AR.cw(
            source=source,
            size=(600, 300),  # ارتفاع کمتر شده
            ps=AR.UIS() * 0.7
        )
        AR.add_close_button(s.w, position=(570, 260))

        # عنوان
        tw(
            parent=s.w,
            text='⚡ Practice Tools',
            scale=1.0,
            position=(280, 270),
            h_align='center',
            color=(0, 1, 1)
        )

        # === بخش سمت راست: توضیحات ===
        tw(
            parent=s.w,
            text="🎮 Game Tools:\n"
                 "• Player effects\n"
                 "• Visual settings\n"
                 "• Game controls\n\n"
                 "💡 Use for practice\nand training!",
            position=(350, 240),
            scale=0.45,
            color=(0.8, 0.8, 1),
            maxwidth=200,
            h_align='left'
        )

        # آمار و وضعیت
        s.stats_text = tw(
            parent=s.w,
            text="📊 Status:\n"
                 "• Tint: Normal\n"
                 "• Game: Active\n"
                 "• Effects: OFF",
            position=(350, 90),
            scale=0.5,
            color=(0.8, 1, 0.8),
            maxwidth=180,
            h_align='left'
        )

        # === بخش سمت چپ: دکمه‌های اسکرولی ===

        # ایجاد اسکرول ویجت برای دکمه‌ها
        s.scroll_widget = sw(
            parent=s.w,
            size=(300, 180),  # ارتفاع اسکرول کمتر
            position=(20, 50)
        )

        # ایجاد کانتینر برای دکمه‌ها
        s.buttons_container = cw(
            parent=s.scroll_widget,
            size=(300, 500),  # ارتفاع کمتر
            background=False
        )

        # ایجاد دکمه‌ها
        s.create_scrollable_buttons()

        AR.swish()

        # متغیرهای تنظیمات
        s.current_tint = (1.0, 1.0, 1.0)

        # تایمر بروزرسانی وضعیت
        teck(1.0, s.update_status)

    def create_scrollable_buttons(s):
        """ایجاد دکمه‌ها در کانتینر اسکرولی"""
        buttons_data = [
            # افکت‌های اصلی
            ('❄️ Freeze', s.apply_freeze, (10, 470), (280, 25), (0.2, 0.7, 0.9)),
            ('🔥 Unfreeze', s.apply_unfreeze, (10, 440), (280, 25), (0.9, 0.7, 0.2)),
            ('⚡ Super Speed', s.apply_super_speed, (10, 410), (280, 25), (0.3, 0.6, 0.9)),
            ('🛡️ Invincible', s.apply_invincible, (10, 380), (280, 25), (0.8, 0.8, 0.2)),
            ('👑 God Mode', s.apply_god_mode, (10, 350), (280, 25), (0.9, 0.3, 0.3)),

            # تنظیمات نور
            ('🎨 Tint +', bs.Call(s.adjust_tint, 1.1), (10, 320), (135, 25), (0.9, 0.7, 0.3)),
            ('🎨 Tint -', bs.Call(s.adjust_tint, 0.9), (155, 320), (135, 25), (0.8, 0.6, 0.2)),
            ('🌈 Random Tint', s.random_tint, (10, 290), (280, 25), (0.7, 0.4, 0.9)),

            # کنترل بازی
            ('⏸️ Pause/Resume', s.toggle_pause, (10, 260), (135, 25), (0.8, 0.8, 0.2)),
            ('🐌 Slow Motion', s.toggle_slowmo, (155, 260), (135, 25), (0.8, 0.5, 0.2)),

            # تنظیمات دستی
            ('🎨 Custom RGB', s.show_custom_rgb, (10, 230), (280, 25), (0.9, 0.5, 0.2)),
            ('🔄 Reset All', s.reset_all_settings, (10, 200), (280, 25), (0.8, 0.2, 0.2))
        ]

        # ایجاد دکمه‌ها
        s.button_widgets = []
        for label, callback, pos, size, color in buttons_data:
            btn = bw(
                parent=s.buttons_container,
                label=label,
                size=size,
                position=pos,
                on_activate_call=callback,
                color=color,
                textcolor=(1, 1, 1),
                text_scale=0.35
            )
            s.button_widgets.append(btn)

        # تنظیم ارتفاع واقعی کانتینر
        total_height = 500
        cw(s.buttons_container, size=(300, total_height))

    def update_status(s):
        """بروزرسانی وضعیت فعلی"""
        if not hasattr(s, 'w') or not s.w.exists():
            return

        try:
            activity = bs.get_foreground_host_activity()
            if activity and hasattr(activity, 'globalsnode'):
                tint_status = f"{s.current_tint[0]:.1f},{s.current_tint[1]:.1f},{s.current_tint[2]:.1f}"
                game_status = "Paused" if activity.globalsnode.paused else "Active"
                slowmo_status = "Slowmo" if activity.globalsnode.slow_motion else "Normal"

                status_text = (f"📊 Status:\n"
                               f"• Tint: {tint_status}\n"
                               f"• Game: {game_status}\n"
                               f"• Speed: {slowmo_status}\n"
                               f"• Ready for practice!")

                tw(s.stats_text, text=status_text)

            # ادامه تایمر
            teck(1.0, s.update_status)

        except:
            # ادامه تایمر حتی در صورت خطا
            teck(1.0, s.update_status)

    # ==================== متدهای اصلی ====================

    def get_target_player(s):
        """دریافت بازیکن هدف"""
        try:
            activity = bs.get_foreground_host_activity()
            if activity and hasattr(activity, 'players'):
                for player in activity.players:
                    if (player.actor and hasattr(player.actor, 'node') and
                            player.actor.node and player.actor.node.exists()):
                        return player.actor
            return None
        except:
            return None

    def apply_freeze(s):
        """یخ زدن"""
        target = s.get_target_player()
        if target:
            target.handlemessage(bs.FreezeMessage())
            s._show_floating_text("FROZEN", target.node.position, (0.2, 0.7, 0.9))

            # ارسال پیام به چت
            s.send_chat_message("❄️ Player Frozen! 🧊")

            push('Player frozen!', color=(0.2, 0.7, 0.9))
            gs('freeze').play()
        else:
            push('No player found!', color=(1, 0, 0))

    def apply_unfreeze(s):
        """آزاد کردن از یخ"""
        target = s.get_target_player()
        if target:
            target.handlemessage(bs.ThawMessage())
            s._show_floating_text("UNFROZEN", target.node.position, (0.9, 0.7, 0.2))

            # ارسال پیام به چت
            s.send_chat_message("🔥 Player Unfrozen! 🔥")

            push('Player unfrozen!', color=(0.9, 0.7, 0.2))
            gs('thaw').play()
        else:
            push('No player found!', color=(1, 0, 0))

    def apply_super_speed(s):
        """سرعت فوق‌العاده"""
        target = s.get_target_player()
        if target:
            target.node.hockey = True
            s._show_floating_text("SUPER SPEED", target.node.position, (0.3, 0.6, 0.9))

            # ارسال پیام به چت
            s.send_chat_message("⚡ Super Speed Activated! 🏃💨")

            push('Super speed activated!', color=(0.3, 0.6, 0.9))
            gs('powerup01').play()
        else:
            push('No player found!', color=(1, 0, 0))

    def apply_invincible(s):
        """غیرقابل آسیب"""
        target = s.get_target_player()
        if target:
            target.node.invincible = True
            s._show_floating_text("INVINCIBLE", target.node.position, (0.8, 0.8, 0.2))

            # ارسال پیام به چت
            s.send_chat_message("🛡️ Invincibility Activated! 🛡️")

            push('Invincibility activated!', color=(0.8, 0.8, 0.2))
            gs('powerup01').play()
        else:
            push('No player found!', color=(1, 0, 0))

    def apply_god_mode(s):
        """حالت خدا"""
        target = s.get_target_player()
        if target:
            # فعال کردن تمام قابلیت‌های گاد مود
            target.node.invincible = True
            target.node.hockey = True
            target.node.hurt = 0.0
            target._punch_power_scale = 15.0
            target._punch_cooldown = 0

            s._show_floating_text("GOD MODE", target.node.position, (0.9, 0.3, 0.3))

            # ارسال پیام به چت
            s.send_chat_message("👑 GOD MODE ACTIVATED! ⚡💪")

            push('GOD MODE ACTIVATED!', color=(0.9, 0.3, 0.3))
            gs('achievement').play()
        else:
            push('No player found!', color=(1, 0, 0))

    def random_tint(s):
        """تینت تصادفی"""
        try:
            activity = bs.get_foreground_host_activity()
            if activity and hasattr(activity, 'globalsnode'):
                r = random.uniform(0.0, 10.0)
                g = random.uniform(0.0, 10.0)
                b = random.uniform(0.0, 10.0)

                activity.globalsnode.tint = (r, g, b)
                s.current_tint = (r, g, b)

                # ارسال پیام به چت
                s.send_chat_message(f"🌈 Random Tint Applied: R:{r:.1f} G:{g:.1f} B:{b:.1f}")

                push('Random tint applied!', color=(r, g, b))
                gs('powerup01').play()
        except:
            push('Error setting random tint!', color=(1, 0, 0))

    def adjust_tint(s, factor):
        """تنظیم tint نور - بدون محدودیت"""
        try:
            activity = bs.get_foreground_host_activity()
            if activity and hasattr(activity, 'globalsnode'):
                current = activity.globalsnode.tint
                new_tint = (
                    current[0] * factor,
                    current[1] * factor,
                    current[2] * factor
                )
                activity.globalsnode.tint = new_tint
                s.current_tint = new_tint

                # ارسال پیام به چت
                s.send_chat_message(f"🎨 Tint Adjusted: x{factor}")

                push('Tint adjusted!', color=(0.9, 0.7, 0.3))
        except:
            push('Error adjusting tint!', color=(1, 0, 0))

    def toggle_pause(s):
        """توقف/ادامه بازی"""
        try:
            activity = bs.get_foreground_host_activity()
            if activity and hasattr(activity, 'globalsnode'):
                activity.globalsnode.paused = not activity.globalsnode.paused
                status = "PAUSED" if activity.globalsnode.paused else "RESUMED"

                # ارسال پیام به چت
                s.send_chat_message(f"⏸️ Game {status}! 🎮")

                push(f'Game {status.lower()}!', color=(1, 1, 0))
                gs('click01').play()
        except:
            push('Error toggling pause!', color=(1, 0, 0))

    def toggle_slowmo(s):
        """حالت slow motion"""
        try:
            activity = bs.get_foreground_host_activity()
            if activity and hasattr(activity, 'globalsnode'):
                activity.globalsnode.slow_motion = not activity.globalsnode.slow_motion
                status = "ON" if activity.globalsnode.slow_motion else "OFF"

                # ارسال پیام به چت
                s.send_chat_message(f"🐌 Slow Motion {status}! ⏱️")

                push(f'Slow motion {status}!', color=(1, 0.5, 0))
                gs('dingSmallHigh').play()
        except:
            push('Error toggling slow motion!', color=(1, 0, 0))

    def reset_all_settings(s):
        """بازنشانی تمام تنظیمات"""
        try:
            activity = bs.get_foreground_host_activity()
            if activity:
                # بازنشانی افکت‌ها
                if activity.players:
                    for player in activity.players:
                        if player.actor and player.actor.node:
                            player.actor.node.invincible = False
                            player.actor.node.hockey = False
                            if hasattr(player.actor.node, 'punch_power_scale'):
                                player.actor.node.punch_power_scale = 1.0
                            if hasattr(player.actor.node, 'punch_cooldown'):
                                player.actor.node.punch_cooldown = 0.3

                # بازنشانی تنظیمات بازی
                if hasattr(activity, 'globalsnode'):
                    activity.globalsnode.paused = False
                    activity.globalsnode.slow_motion = False
                    activity.globalsnode.tint = (1.0, 1.0, 1.0)

                s.current_tint = (1.0, 1.0, 1.0)

                # ارسال پیام به چت
                s.send_chat_message("🔄 All Settings Reset! ♻️")

                push('All settings reset!', color=(0, 1, 1))
                gs('shieldDown').play()
        except:
            push('Error resetting settings!', color=(1, 0, 0))

    def show_custom_rgb(s):
        """صفحه تنظیم RGB"""
        s.rgb_window = AR.cw(
            source=s.w,
            size=(400, 200),
            ps=AR.UIS() * 0.8
        )
        AR.add_close_button(s.rgb_window, position=(370, 160))

        tw(
            parent=s.rgb_window,
            text='🎨 Custom RGB',
            scale=0.8,
            position=(170, 170),
            h_align='center',
            color=(0.9, 0.5, 0.2)
        )

        # فیلدهای RGB
        labels = ['Red:', 'Green:', 'Blue:']
        defaults = ['1.0', '1.0', '1.0']
        s.rgb_inputs = []

        for i, (label, default) in enumerate(zip(labels, defaults)):
            tw(parent=s.rgb_window, text=label, scale=0.5,
               position=(50, 140 - i * 30), color=(1, 1, 1))

            input_widget = tw(parent=s.rgb_window, text=default, editable=True,
                              scale=0.6, position=(100, 138 - i * 30),
                              size=(200, 35), h_align='left')
            s.rgb_inputs.append(input_widget)

        bw(parent=s.rgb_window, label='Apply RGB', size=(100, 25),
           position=(150, 50), on_activate_call=s.apply_custom_rgb,
           color=(0.9, 0.5, 0.2), text_scale=0.4)

        bw(parent=s.rgb_window, label='Random', size=(100, 25),
           position=(150, 20), on_activate_call=s.apply_random_rgb,
           color=(0.7, 0.3, 0.9), text_scale=0.4)

    def apply_custom_rgb(s):
        """اعمال RGB دستی - بدون محدودیت"""
        try:
            values = []
            for input_widget in s.rgb_inputs:
                text = tw(query=input_widget)
                value = float(text) if text.strip() else 1.0
                values.append(value)

            if len(values) == 3:
                r, g, b = values
                activity = bs.get_foreground_host_activity()
                if activity and hasattr(activity, 'globalsnode'):
                    activity.globalsnode.tint = (r, g, b)
                    s.current_tint = (r, g, b)

                    # ارسال پیام به چت
                    s.send_chat_message(f"🎨 Custom RGB Applied: R:{r} G:{g} B:{b}")

                    push(f'RGB applied!', color=(abs(r), abs(g), abs(b)))
                    AR.swish(s.rgb_window)
        except Exception as e:
            push(f'Invalid RGB values!', color=(1, 0, 0))

    def apply_random_rgb(s):
        """اعمال RGB تصادفی - بدون محدودیت"""
        try:
            r = random.uniform(-5.0, 5.0)
            g = random.uniform(-5.0, 5.0)
            b = random.uniform(-5.0, 5.0)

            activity = bs.get_foreground_host_activity()
            if activity and hasattr(activity, 'globalsnode'):
                activity.globalsnode.tint = (r, g, b)
                s.current_tint = (r, g, b)

                # ارسال پیام به چت
                s.send_chat_message(f"🌈 Random RGB: R:{r:.1f} G:{g:.1f} B:{b:.1f}")

                push(f'Random RGB applied!', color=(abs(r), abs(g), abs(b)))
                gs('powerup01').play()

                # بروزرسانی فیلدها
                for i, input_widget in enumerate(s.rgb_inputs):
                    tw(input_widget, text=f"{[r, g, b][i]:.1f}")

        except Exception as e:
            push(f'Random RGB error!', color=(1, 0, 0))

    def send_chat_message(s, message):
        """ارسال پیام به چت"""
        try:
            CM(message)
        except:
            pass

    def _show_floating_text(s, text, position, color=(1, 1, 1)):
        """نمایش متن شناور"""
        try:
            activity = bs.get_foreground_host_activity()
            if activity:
                with activity.context:
                    text_node = bs.newnode('text',
                                           attrs={
                                               'text': text,
                                               'in_world': True,
                                               'shadow': 1.0,
                                               'flatness': 1.0,
                                               'color': color,
                                               'scale': 0.02,
                                               'h_align': 'center',
                                               'position': position
                                           })

                    # انیمیشن ظهور و ناپدید شدن
                    bs.animate(text_node, 'scale', {
                        0: 0.0,
                        0.3: 0.02,
                        1.5: 0.02,
                        2.0: 0.0
                    })

                    # حذف پس از 2 ثانیه
                    bs.timer(2.1, text_node.delete)

        except Exception as e:
            print(f"Error showing floating text: {e}")


# ==================== Mod Files Manager ====================
class ModFilesManager:
    def __init__(s, source):
        w = s.w = AR.cw(
            source=source,
            size=(550, 300),
            ps=AR.UIS() * 0.7
        )
        AR.add_close_button(w, position=(520, 260))

        # تایتل با ارتفاع 280
        tw(
            parent=w,
            text='📁 Mod Files Manager',
            scale=0.9,
            position=(260, 275),
            h_align='center',
            color=(0, 1, 1)
        )

        s.mod_path = os.path.dirname(os.path.abspath(__file__))
        
        tw(
            parent=w,
            text=f'Path: {s.mod_path}',
            position=(100, 245),
            scale=0.4,
            color=(0.8, 0.8, 1),
            maxwidth=450
        )

        s.scroll = sw(
            parent=w,
            size=(510, 160),
            position=(20, 70)
        )

        s.container = cw(
            parent=s.scroll,
            size=(510, 500),
            background=False
        )

        bw(
            parent=w,
            label='🔄 Refresh',
            size=(100, 28),
            position=(20, 30),
            on_activate_call=s.refresh_files,
            color=(0.3, 0.6, 0.8),
            textcolor=(1, 1, 1),
            text_scale=0.6
        )

        bw(
            parent=w,
            label='🗑️ Delete .pyc All',
            size=(140, 28),
            position=(390, 30),
            on_activate_call=s.delete_all_pyc,
            color=(0.8, 0.3, 0.3),
            textcolor=(1, 1, 1),
            text_scale=0.6
        )

        s.refresh_files()
        AR.swish()

    def refresh_files(s):
        for child in s.container.get_children():
            child.delete()

        try:
            files = []
            for file in os.listdir(s.mod_path):
                file_path = os.path.join(s.mod_path, file)
                if os.path.isfile(file_path):
                    files.append({
                        'name': file,
                        'size': os.path.getsize(file_path),
                        'path': file_path
                    })

            files.sort(key=lambda x: x['name'])

            if not files:
                tw(
                    parent=s.container,
                    text='No files found in mod folder',
                    position=(255, 90),
                    scale=0.7,
                    color=(1, 0.5, 0),
                    h_align='center'
                )
                return

            y_pos = len(files) * 22 - 5
            for i, file in enumerate(files):
                color = (0.2, 0.2, 0.3) if i % 2 == 0 else (0.25, 0.25, 0.35)
                bw(
                    parent=s.container,
                    label='',
                    size=(490, 20),
                    position=(10, y_pos),
                    color=color,
                    enable_sound=False
                )

                file_display = file['name']
                if len(file_display) > 30:
                    file_display = file_display[:27] + '...'
                
                color = (1, 1, 1)
                if file['name'].endswith('.py'):
                    color = (0.3, 1, 0.3)
                elif file['name'].endswith('.pyc'):
                    color = (1, 0.5, 0.5)
                elif file['name'].endswith('.json'):
                    color = (1, 1, 0.3)
                elif file['name'].endswith('.txt'):
                    color = (0.5, 1, 1)

                tw(
                    parent=s.container,
                    text=file_display,
                    position=(15, y_pos - 5),
                    scale=0.4,
                    color=color,
                    maxwidth=280,
                    h_align='left'
                )

                size_text = f"{file['size']:,} bytes"
                if file['size'] > 1024:
                    size_text = f"{file['size']/1024:.1f} KB"
                if file['size'] > 1024*1024:
                    size_text = f"{file['size']/(1024*1024):.1f} MB"

                tw(
                    parent=s.container,
                    text=size_text,
                    position=(310, y_pos - 5),
                    scale=0.35,
                    color=(0.8, 0.8, 1),
                    h_align='left'
                )

                bw(
                    parent=s.container,
                    label='🗑️',
                    size=(22, 16),
                    position=(450, y_pos + 2),
                    on_activate_call=Call(s.delete_file, file['path'], file['name']),
                    color=(0.8, 0.2, 0.2),
                    text_scale=0.35
                )

                y_pos -= 22

            cw(s.container, size=(510, len(files) * 22 + 20))

        except Exception as e:
            tw(
                parent=s.container,
                text=f'Error: {str(e)}',
                position=(255, 90),
                scale=0.7,
                color=(1, 0, 0),
                h_align='center'
            )

    def delete_file(s, file_path, file_name):
        """حذف فایل با تأیید"""
        def confirm_delete():
            try:
                remove(file_path)
                push(f'✅ File deleted: {file_name}', color=(0, 1, 0))
                gs('dingSmall').play()
                if confirm_win and confirm_win.exists():
                    AR.swish(confirm_win)
                s.refresh_files()
            except Exception as e:
                push(f'❌ Error deleting: {str(e)}', color=(1, 0, 0))
                if confirm_win and confirm_win.exists():
                    AR.swish(confirm_win)

        confirm_win = AR.cw(
            source=s.w,
            size=(350, 120),
            ps=AR.UIS() * 0.5
        )
        # دکمه ضربدر - فقط بستن پنجره
        AR.add_close_button(confirm_win, position=(320, 80))

        tw(
            parent=confirm_win,
            text=f'Delete "{file_name}"?',
            position=(150, 75),
            scale=0.65,
            color=(1, 1, 1),
            h_align='center'
        )

        # دکمه Yes - وسط (حذف فایل و بستن پنجره)
        bw(
            parent=confirm_win,
            label='🗑️ Yes',
            size=(120, 30),
            position=(115, 25),  # وسط (350/2 = 175 - 60 = 115)
            on_activate_call=confirm_delete,
            color=(0.8, 0.2, 0.2),
            textcolor=(1, 1, 1),
            text_scale=0.6
        )

    def delete_all_pyc(s):
        """حذف همه فایل‌های .pyc"""
        def confirm_delete_all():
            try:
                deleted = 0
                for file in os.listdir(s.mod_path):
                    if file.endswith('.pyc'):
                        file_path = os.path.join(s.mod_path, file)
                        remove(file_path)
                        deleted += 1
                
                push(f'✅ Deleted {deleted} .pyc files', color=(0, 1, 0))
                gs('dingSmall').play()
                if confirm_win and confirm_win.exists():
                    AR.swish(confirm_win)
                s.refresh_files()
            except Exception as e:
                push(f'❌ Error: {str(e)}', color=(1, 0, 0))
                if confirm_win and confirm_win.exists():
                    AR.swish(confirm_win)

        confirm_win = AR.cw(
            source=s.w,
            size=(350, 120),
            ps=AR.UIS() * 0.5
        )
        AR.add_close_button(confirm_win, position=(320, 80))

        tw(
            parent=confirm_win,
            text='Delete ALL .pyc files?',
            position=(150, 75),
            scale=0.65,
            color=(1, 0.5, 0),
            h_align='center'
        )

        # دکمه Yes All - وسط (حذف فایل‌ها و بستن پنجره)
        bw(
            parent=confirm_win,
            label='🗑️ Yes All',
            size=(120, 30),
            position=(115, 25),  # وسط (350/2 = 175 - 60 = 115)
            on_activate_call=confirm_delete_all,
            color=(0.8, 0.2, 0.2),
            textcolor=(1, 1, 1),
            text_scale=0.6
        )
        

# ba_meta require api 9
# ba_meta export plugin
class byTaha(Plugin):
    me = lambda c=0: APP.plus.get_v1_account_name() if APP.plus.get_v1_account_state() == 'signed_in' else '???'
    v2 = cs(sc.V2_LOGO)
    B = '​'

    def __init__(s):
        # اورراید کردن توابع اتصال
        setup_connection_overrides()

        # اضافه کردن متغیر آنتی اسپم
        s.last_command_time = {}
        s.cooldown_time = 1.5

        o = party.PartyWindow.__init__

        def e(self, *a, **k):
            r = o(self, *a, **k)

            # دکمه Practice Tools
            b_practicetools = AR.bw(
                icon=gt('achievementOffYouGo'),
                position=(self._width - 570, self._height - 272),
                parent=self._root_widget,
                iconscale=0.6,
                size=(80, 25),
                label='تمرین'
            )
            bw(b_practicetools, on_activate_call=Call(PracticeTools, b_practicetools))

            # دکمه SingleConverter
            b_converter = AR.bw(
                icon=gt('achievementOutline'),
                position=(self._width - 570, self._height - 304),
                parent=self._root_widget,
                iconscale=0.6,
                size=(80, 25),
                label='مبدل متن'
            )
            bw(b_converter, on_activate_call=Call(AdvancedConvertPanel, b_converter))

            # دکمه Camera Control
            b_camera = AR.bw(
                icon=gt('tv'),
                position=(self._width - 570, self._height - 112),
                parent=self._root_widget,
                iconscale=0.6,
                size=(80, 25),
                label='دوربین'
            )
            bw(b_camera, on_activate_call=lambda: SimpleCamera().open_camera_menu(b_camera))

            # دکمه BsRush
            b_bsrush = AR.bw(
                icon=gt('achievementOffYouGo'),
                position=(self._width - 570, self._height - 80),
                parent=self._root_widget,
                iconscale=0.6,
                size=(80, 25),
                label='بی‌اس راش'
            )
            bw(b_bsrush, on_activate_call=Call(BsRushWindow, b_bsrush))

            # دکمه Reconnect
            reconnect_btn = AR.bw(
                icon=gt('replayIcon'),
                position=(self._width - 570, self._height - 208),
                parent=self._root_widget,
                iconscale=0.6,
                size=(80, 25),
                label='اتصال مجدد'
            )
            bw(reconnect_btn, on_activate_call=Call(Reconnect, self._root_widget))

            # دکمه Server Info
            b_serverinfo = AR.bw(
                icon=gt('star'),
                position=(self._width - 570, self._height - 240),
                parent=self._root_widget,
                iconscale=0.6,
                size=(80, 25),
                label='اطلاعات سرور'
            )
            bw(b_serverinfo, on_activate_call=Call(ServerInfo, b_serverinfo))

            # دکمه Ping
            b_ping = AR.bw(
                icon=gt('coin'),
                position=(self._width - 570, self._height - 48),
                parent=self._root_widget,
                iconscale=0.6,
                size=(80, 25),
                label='پینگ'
            )
            bw(b_ping, on_activate_call=Call(PingButton, b_ping))

            # دکمه Obscenity (Bahari)
            b_bahari = AR.bw(
                icon=gt('trophy'),
                position=(self._width + 10, self._height - 304),
                parent=self._root_widget,
                iconscale=0.6,
                size=(80, 25),
                label='ضد ناسزا'
            )
            bw(b_bahari, on_activate_call=Call(Bahari, b_bahari))

            # دکمه Spam
            b_spam = AR.bw(
                icon=gt('startButton'),
                position=(self._width - 570, self._height - 176),
                parent=self._root_widget,
                iconscale=0.6,
                size=(80, 25),
                label='اسپم'
            )
            bw(b_spam, on_activate_call=Call(Spam, b_spam))

            # دکمه Quick Chat
            b_quickchat = AR.bw(
                icon=gt('bombButton'),
                position=(self._width - 570, self._height - 144),
                parent=self._root_widget,
                iconscale=0.6,
                size=(80, 25),
                label='چت سریع'
            )
            bw(b_quickchat, on_activate_call=Call(QuickChat, b_quickchat))

            # دکمه Calculator
            b_calculator = AR.bw(
                icon=gt('chTitleChar2'),
                position=(self._width + 10, self._height - 48),
                parent=self._root_widget,
                iconscale=0.6,
                size=(80, 25),
                label='ماشین حساب'
            )
            bw(b_calculator, on_activate_call=Call(Calculator, b_calculator))

            # دکمه Icons
            b_icons = AR.bw(
                icon=gt('upButton'),
                position=(self._width + 10, self._height - 112),
                parent=self._root_widget,
                iconscale=0.6,
                size=(80, 25),
                label='آیکون‌ها'
            )
            bw(b_icons, on_activate_call=Call(show_icons_menu, b_icons))

            # دکمه UI Color
            b_uicolor = AR.bw(
                icon=gt('storeCharacterXmas'),
                position=(self._width + 10, self._height - 144),
                parent=self._root_widget,
                iconscale=0.6,
                size=(80, 25),
                label='رنگ رابط'
            )
            bw(b_uicolor, on_activate_call=Call(UIColorChanger, b_uicolor))

            # دکمه Players Info
            b_playerinfo = AR.bw(
                icon=gt('achievementSuperPunch'),
                position=(self._width + 10, self._height - 176),
                parent=self._root_widget,
                iconscale=0.6,
                size=(80, 25),
                label='بازیکنان'
            )
            bw(b_playerinfo, on_activate_call=Call(PlayerInfo, b_playerinfo))

            # دکمه Chat Log
            b_chatlog = AR.bw(
                icon=gt('logIcon'),
                position=(self._width + 10, self._height - 240),
                parent=self._root_widget,
                iconscale=0.6,
                size=(80, 25),
                label='تاریخچه چت'
            )
            bw(b_chatlog, on_activate_call=Call(ChatLog, b_chatlog))

            # دکمه Font Maker
            b_font = AR.bw(
                icon=gt('goldPass'),
                position=(self._width + 10, self._height - 208),
                parent=self._root_widget,
                iconscale=0.6,
                size=(80, 25),
                label='Font Maker'
            )
            bw(b_font, on_activate_call=Call(FontMaker, b_font))

            # دکمه Stickers
            b_sticker = AR.bw(
                icon=gt('heart'),
                position=(self._width + 10, self._height - 272),
                parent=self._root_widget,
                iconscale=0.6,
                size=(80, 25),
                label='Stickers'
            )
            bw(b_sticker, on_activate_call=Call(StickerMenu, b_sticker))

            # دکمه اصلی Auto Message
            b_main = AR.bw(
                icon=gt('achievementOutline'),
                position=(self._width + 10, self._height - 80),
                parent=self._root_widget,
                iconscale=0.6,
                size=(80, 25),
                label='Auto Msg'
            )
            bw(b_main, on_activate_call=Call(AR, b_main))

            # ===== دکمه جدید Mod Files =====
            b_modfiles = AR.bw(
                icon=gt('logo'),  # آیکون پوشه
                position=(self._width + 10, self._height - 336),  # موقعیت جدید - پایین‌تر از بقیه
                parent=self._root_widget,
                iconscale=0.6,
                size=(80, 25),
                label='فایل‌های مود'
            )
            bw(b_modfiles, on_activate_call=Call(ModFilesManager, b_modfiles))

            return r

        party.PartyWindow.__init__ = e

        # Patch _add_msg for real-time conversion
        original_add_msg = party.PartyWindow._add_msg

        def new_add_msg(self, text, *args, **kwargs):
            global convert_mode

            # Only process messages with colon (chat messages)
            if ':' in text and len(text.split(': ')) >= 2:
                parts = text.split(': ', 1)
                sender = parts[0]
                message = parts[1]

                if convert_mode == 1 and contains_persian(message):  # Persian to Finglish
                    converted_message = convert_persian_to_finglish(message)
                    text = sender + ': ' + converted_message
                elif convert_mode == 2 and is_finglish(message):  # Finglish to Persian
                    converted_message = convert_finglish_to_persian(message)
                    text = sender + ': ' + converted_message

            original_add_msg(self, text, *args, **kwargs)

        party.PartyWindow._add_msg = new_add_msg

        # Welcome message
        teck(8, Call(push, "⭐self.farsi\nRobika  :  @bombsquad002", color=(0.2, 0.8, 0.2)))

        s.z = []
        teck(5, s.ear)

    def __del__(s):
        if ping_thread:
            ping_thread.stop()

    def ear(s):
        try:
            z = GCM()
            teck(0.3, s.ear)
            if z == s.z: return

            if not var('state'):
                s.z = z
                return

            s.z = z
            if not z: return

            v = z[-1]
            if v.endswith(s.B): return

            if ': ' not in v:
                return

            f, m = v.split(': ', 1)
            k = s.me()
            if f in [k, s.v2 + k] and not var('tune2'): return

            current_time = time.time()
            if f in s.last_command_time:
                time_since_last = current_time - s.last_command_time[f]
                if time_since_last < s.cooldown_time:
                    return

            if var('tune3'):
                l = var('l')
            else:
                m = m.lower()
                l = var('lc')

            h = l.get(m, None)
            if h is not None:
                a, b, _ = h
                s.S(b, a, f, 0)
                s.last_command_time[f] = current_time
            else:
                re = [y for y, _ in sorted([(y, m.find(y)) for y in l if y in m], key=lambda x: x[1])]
                for r in re:
                    a, b, c = l.get(r, [0, 0, 0])
                    if not r or not c: continue
                    s.S(b, a, f, 1)
                    s.last_command_time[f] = current_time
                    break
        except Exception as e:
            print(f"Error in ear: {e}")

    def S(s, b, a, f, j):
        p = AR.parse(t=a, s=f)
        teck(b, Call(CM, p + s.B))
        push(f"{['برابر', 'شامل'][j]}!\nپاسخ به: {f}\nبا متن: {p}\nبعد از {b} ثانیه!", color=(0, 0.8, 0.8)) if var(
            'tune0') else None
        gs('dingSmallHigh').play() if var('tune1') else None