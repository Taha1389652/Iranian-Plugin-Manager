# ba_meta require api 6


max_price = 20000


_cbb = 100
_e = 20
_fish = 100
_g = 150
_k = 500
_orb = 50
_plasma = 50
_re = 200
_rich = 50
_sp = 90
_spin = 1000
_vip = 500
_z = 150

_b3 = 0
_bi = 0
_bm = 0
_bo = 0
_bot = 0
_bs = 0
_bt = 0
_cba = 0
_cel = 0
_cm = 0
_cu = 0
_d = 0
_efs = 0
_fire = 0
_fl = 0
_fly = 0
_fr = 0
_h = 0
_hed = 0
_hug = 0
_li = 0
_m = 0
_n = 0
_pun = 3.5
_r = 0
_sh = 0
_sl = 0
_sm = 0
_spike = 0
_t = 0
_tag = 0
_tex = 0
_u = 0
_v = 0
######################







#به این پایینی ها دست نزنید
#این هشدار نیست ، نصیحته

sod = False;_name=-1;lasch=''
import ba,_ba
exec("""def buysel():\n global lasch,max_price\n m = _ba.get_chat_messages()[-2:]\n for i in m:\n  if "💳Buy < " in i:\n   try:\n    cod = i.split(": ")[1];i = i.split(": ")[2].replace(",",'')\n    if lasch == cod:\n     i = i.split(" ")\n     price = int(i[7]) / int(i[2])\n     if int(i[7]) <= max_price:\n      if price <= eval(f"_{i[3]}"):\n       lasch="1 "\n       _ba.chatmessage("1 ")\n      else:\n       lasch="0 "\n       _ba.chatmessage("0 ")\n     else:\n      lasch="0 "\n      _ba.chatmessage("0 ")\n   except:pass\ndef dls():\n global lasch\n if lasch[:1] == 's':\n  buysel()\ndef sellcek():\n global sod,max_price,lasch\n m = _ba.get_chat_messages()[-1]\n if "Server" in m:\n  if "💰Sell <" in m:\n   m = m.split("💰Sell <")[1].replace(",",'')\n   m = m.split(" ")\n   price = int(m[4][:-1]) / int(m[0])\n   if int(m[4][:-1]) <= max_price:\n    if price <= eval(f"_{m[1]}"):sod = True\n    else:sod = False\n  elif "💰Sell ID: " in m and sod:\n   lasch = (m.split("💰Sell ID: ")[1])\n   _ba.chatmessage("b " + m.split("💰Sell ID: ")[1])\n   ba.timer(0.2,buysel)\n   ba.timer(0.4,dls)\n   ba.timer(0.6,dls)\n   ba.timer(0.8,dls)\n   ba.timer(1,dls)\nba.timer(0.2,sellcek,True)""")
# ba_meta export plugin
class fast_buy2(ba.Plugin):pass