# PingMod.py - API 9
# ساخته شده توسط Poya Azrael
# @AzraelMods لینک چنل
# این فایل کدگذاری (obfuscate) شده؛ سورس اصلی فشرده و base85 شده و موقع اجرا دیکد میشه.

import zlib
import base64

_PAYLOAD = (
    "c-qxkTW{Og5q{UNI4fgOGF50PPA?IlMcu?ng~qWEJLvWXf|ibL!ZN9nR2*+$pbjj>Kn*k~P@q5yEU+(Dyt`3-$?m!j`5mPFm"
    "Orrl37wh4yGX^3gKi=N7I`i+b7sCXmvc118oIGOYqpfm2D{3p8+CT0Fu~j-ch7y{?t4#}d+ZMJYv0>})^AzE+|bzcXO_m>Fz"
    "^@R2?*HC+dkX%`lrv?Y2WL6+l9iCWv($*UFteri>oTr*E*)<FwHPbM{{)3unPsh%{H5>+zH;C6^m;v5G-ua*LXN~QS0gtD@?"
    "Q5VpoqE?It(4-);-uiyAcZfN!JSUDl1DhiC+oyN+WT>w0UMJ2Zd2#I#Naxmx({@aAfX*-eXcV~yLkw#>1))3sOP<l6dTK(V7"
    ")&PD+gboJeRfZA!_J#hD!J8)0jZ_ak{@hf-lY?ryi)8}3f?R4Pnz#9xZa`ze7p?9|X`p>)W0Bz&--Otgw1F-HP&Vs@4bvgvw"
    "9-r+_y8G_H+jjRSPoKMcK<*Vx+JVLc00h$B0|G;w>pcaUL;&6ffC`)dF9Y`gTD=~iWeY~bTt*WPV74?rJAL;qn`E;yx9SgO;"
    "o<J|{W~+Vf)b5ThPiv*6ZZrpc*eX}(ESxs@jG7;w|#h&Y~Ef{RIr`10w$uD6|OI@I5J@tM?ZxHfPk<{ug8!HL!Ehje^p-tCs"
    ";Iy0YV>mPnfSW&}bj#?xMa9NXy<+?1G8#4<?>~$V29SNjlhP60G}6Z<~Fp&fUH}KeJG~I`xyX44ebA1bSxf3wRi!a`0h5Mno"
    "NKfv)#(ySck4P0#BI8B){FKs2&BJmB7xh(%Yon_8PEv`?di{y`mxfi2q9LjC|cJ{f^0fggb;Py)yjA4J9iWl*2{wYOc3YbOM"
    "XKc93bh6-LWy}7{~Qhx3pgM|@0FmNakE{GCnCIw_B2{51s_usIlV^~QK<w4U1Dm@0HL(dCX%S*B&Ij;zvgozj!eA~kqT(&SM"
    "DDZ{*63D$IgTugnIMCP69_}twGLcW<MIjskbj7CdwrG_?H$Gs91nfU(3K_uUZIm{5n+P0%Y{xh>+E%D(w9^hz1c9)n50C#uL"
    "Hg82dwoD&-2KnlE^$s-A8kbMxIIXtG#8esykjr+&YfZmt+0Sb{oWlWCEIW_fX=Rl>PDwW+Y(m`wi*N)J;psF7lJL!YV2`=!K"
    "X-8DOMTo=@Pa~u!#xWqh#bh>_LBb%2h_dc<F7&*aIK}<pPWb3I9osI`nWzR<INRi1AFbjNEnTSO)H)dvH1&Cqzh}a5Z*GsVE"
    "S}hja7UEc{lzeSdCNU6^Z(>T>F*Q^fZ|x;#M(B5E_VIiO8SzG$321HPBjXC%moM)Mc;RvJxm+AREX;hs8Q|J@8|bm}@|F;4L"
    "~TFr{rL7ITE3LPTER~hz2mJbg+o`^QSA`3pB14#71lYN1m!a@3e@h}XMBB-5!<lm4>qWKdHg}*s>ckVt&FUU}UcaP8m9g3-="
    ";tIn85#a!Fk4~_KnNJroX!X%}=+gy}B4)V7AlJztiHdiJNKmX^tW5+bh{ph>ZP3>fXz#g)CCrTn^!)_}R2e7X4i@e??&c}wV"
    "r7gh6@L^32g(wF?q8TxDKXf3kR;StzyKl{N%j%~q*SK<3ib<jiC&mp33`t((6~dT5ZA9iALz$FaT8X9<&Ib&l~RtiYQhjwMM"
    "0j*&#&SCiadsAzNOxTq7Nt_)f?5u-2H`-m_!+fT&OqHG12DQjdCd+4WhQtgHzKc(t4A>&2WXIzDtlAbu*W7GUPpcs$=kZK5("
    "WOA#EU?gkf2^PB4TWq7aAkVX)p9^%Wl+=BR!@!I~u9E<ktl?%d5^kHy_o2JWUtaW_S{6Xf0%^aQnxAa`l_MU?Xq_|^av#4}u"
    "B@J~K31Q+x*{(l0YsO9jOKxF?%ScJJJRpcbH<)Gy5L4fjW4pFR%;7P^X5k69W(-+A=Sl{}m5fJ*IYTLtL5_b7#6j1qz`UitB"
    "Sc=LGpnvKYZbu^MQSCMi>YG$WjAdW4WTo;ZR(r;)>%J>;N1QbP%Yqn4bLX^=i<t~EG3?yI;UExWkdSRby-W0t@q{bNkSJ4-M"
    "D<LE3t=gGg7O2M(;=2zGG+pPX&4ojv}$iFqtGS30>eP?TT#J96O$)Cl)zE>3+ww1DE36S#M}<k@z~LjI2Zyf_mx7S(Bex>ZF"
    "Vh-8;<IqA*ic-LxQ~U6J|SBRcz8?F;!WkCep=qm{Mg{+1bZM;n7fH@v;IOiL+yE2odlT9CFm~>`&1;9i^+Q4=ak_9*)zO!l6"
    "2y6Dkkt^Z2R|tB4?eEbeqIBXCydpg|I5(-6L_kZ$(99<}pFP2O?X41MXQQOzA)P;G8K<d&*;V8zACwVx?v_^TAd4mxbCvFlU"
    "UD&<08#SWxV&<I0;f@$f?YST0f-gH#QROw_A^=B*TR)25{7VY=o;ikG`+K!lz)e}I-;Oir7B(2r5xNVmh%2^{R;n~trNXuNt"
    "zS?cAZF5;DVYzKCYHb!RyTsxvr7;Pe_zV&qzD~jkzE-m}krXj4oE%?W*6O9V6+CXt4B>@AN2Jdd0ffx3CQ!*VN+HLP!T1~_H"
    "`|(RGZj<x1v;LW!c%%hG{~W+paPddTX>2ax~V-;S$VI(2kgiEE_-mRk%;Euu^Kr~c)uF=ntp*UVgY&^Q6p1YO<`r<_uu44NH"
    "8*_svEkas&s5DM?25%cDN<UO4#4h_?l_d7OXCpqfvOgY;_GoY%uJMNJD#?s*j5Jz6|@;S9EYJaf(TYl5l%5mlQ+MM+q1)&1f"
    "ZI^pTIFQ9863v$+b35H~N1_>%m$>Dy}k-poQN=$*&Z=GLA2)3b6eEyd;z-k6wON2=rub2LIX4pZ=-G?tvva!hHl_=iX3#bSv"
    "`d7DelCX%VZ;M39^4XEJe_jRCHy!j9TFICEN?!1(Xm2wBt)-}6EOOj%%1q_o8WOjvB%4IN|JeC638zp5maKEUBW^wFr4xW_V"
    "xN#$QP&PL|Ao;fTZCE|84)XZrhq*TpEN2c}(haTM9%E86VzX`9S*SwIWKSK-{LO0^JDn_Vw>j_NjtD)4?U<br2b6Rz6coYh5"
    "?xhzT6EAc_bVql6~dJi1}xJMy&Vi=QskP+14Dv4jHQq+o|gt5d&@n+n~3n@1}{Pm=!6<GT+HSux9h{#v)E1I9%b{8=80REWA"
    "ABp0*8TWMRWXHRB5R=yFpjbtjZok<dx$3lsDO$&0haw`}^<yT9h+$C%lG@8FpmP;}tD1@h`a<w=B~FPJ9y_O4DqcR*lZ!lqv"
    "cb^CaUf-+@>d)3n|>ub%P56ibv>bj69s)Iz&hc;RDA|L<1K^W-mCy@863Jn3fjaom+|vj2X*`|Q2eHSF-_>bcb&oP$JaJrcK"
    "Cmj-eGRNUi1NP}u=i5z|L<6l)jo~?d7UzGDrf@MBhBTfko@b|yHmj<A-2j)G&5)bdJePs{AqW%pR^`PRRU%8?I=)x3xF^j{i"
    "#>3IONc_#ov5b8E(u5LNO3^UE#}}o6|9_(!Ept80-U7IEG^e@3Td`^6c1!GvW-UX?f91;RIzIV0O7qAWEF5`QD5G1>te*=R+"
    "j3n>sTQZz#LpHi({xnvBa~8dlxgc|mfC2#5&QK6`*HZogWrcz{IQfXMf^qr@{#D&E_arke6{t@cufk<=SnPiN(~b~s!^Sd4z"
    "CsMKXqZL#pH;#w#eHxaq6G!arh%gC2?vMrIPFuNDdG2Mkk5^(Lr2tgw}N+MQB5LL&<%z6XeyJj{Z<{xC-3cwPYNP2ETtBG<?"
    "AVHeyl*!rgYu_>qIPGNUv_SVl1Z0Z<yd@wf<36PFto!)oj@qr_q_Z;RM^<HC52-+bgjHgSb<S=0tO$%l_wsC0i|#3rvxE&|&"
    "0&B(=Yo4g4rvE=*PqL;20E{fmO)kz+N)0ZHZMR6?K`|yEGi%Da-ke|k2W-*$=1j!BljJ9hux!N|h7H<W~aAMuG=5WbkAbb6<"
    "9+QY4`-EyQInn?vzY^C#{_1Jv{{x-73KR"
)

exec(compile(zlib.decompress(base64.b85decode(_PAYLOAD)).decode("utf-8"), "PingMod", "exec"), globals())


# ba_meta require api 9


# ba_meta export plugin
class PingMod(Plugin):

    def on_app_running(self) -> None:
        teck(1.5, _announce_loaded)

    def __del__(self):
        try:
            _ping_thread.stop()
        except Exception:
            pass
