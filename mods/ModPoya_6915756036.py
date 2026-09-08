# PingMod.py - API 9
# ساخته شده توسط Poya Azrael
# @AzraelMods لینک چنل
# این فایل کدگذاری (obfuscate) شده؛ سورس اصلی فشرده و base85 شده و موقع اجرا دیکد میشه.

import zlib
import base64

_PAYLOAD = (
    "c-q|>U2ogg^_{=sRz@%~Q&`E)x><mRWvSg6tz#kfuw)oO(9*R{m?kxnisKdm=D?N>Ou&Kx0|sosfV{}@+$i$LTK6HpgS6iA2"
    "ezNEbIv6xQleBfN!zq?Ad&Z;d(OG%``nu;RxzygMZ2cfci0VftFpjmr77m0`ECEXe;gbz|J?83&v9@FqhGL!y`!^RpE^1>0q"
    "|Gi2@tp}*z2`|=G8NH)eM@!o+Pa~_7>B$wT9PlxTY~<t8P0U(=E&PbkDFYSCYap*RF1IFM9Jf9In@Zv3S7P;xX*1-Y^~%neM"
    "XHhS48%tK8z@xGQL{>M+bBx)rmrZdlO_;fNMDJkPeajoLc*X#IAc>Ge8Nb@1Ke)y+I}s}ASZ7I$5Jo#Sx5;cg_+nZ{~_v93G"
    "bjsya_@%BEbm(JC*U_Ur`^`};^#VQMTK4Nlu%x?#W!5*kGIDo;!pb29z4+?Dir!08vAHl5Ofwy!2xYtq;Y5R&a9O8k8;4x_O"
    "F`)W0^Si+zpop+B|2h5;HNPF>2IFA<<<&F)jQK}?8%BXZ$L}J+Zm^G(_krMZ{{pAFeg{#4mB84Uf9$t_i(nUEzaT<rMqq-7_"
    "!6*mhzX>$4^+VnPkSvyk0VXoX_MYharZ~WjsH~-WC7&i9k&w721s`VG!QLG_q3(?`Q^D4R%SP5epX=knPO8@z{@^vAZV6=E5"
    "Lja>?Opzizq{J?jgZ&rVB%Wmjy3jUnjuwf&UMb#;M=E>Htq&pyM9_@pF2CnJzLLEd#pJeQo~k(xSGqQ~}tT4`wFf=n^$U5*_"
    "9VbOG<Er#@Fi>DMcFwB?20&mo<gj3xGtRLDL~gM(7)EyNj_i3}?30)<PkBEl(!2)YmiKxa>TEr2AOLG=mdLhS-4ZRGsW|Bui"
    "juAgGa)$OHEmhPgc2u<(=IQP%c+D^sNVLrqj$z)L6ummle6wpGu`!`zrFjL3C(Mi&DBWnf;cgZZ<C{^^3mAQK>8H_c7|8oqI"
    "f}<RU(p=;*S^S-%=_5j5tsC)#_DS4;iuORNp~vLI?ZEF-G#dpMp`i#K2|?%`N8~UC20JN+P%09kt&<na#XKv(KLz-YT@u_8I"
    "lBNU$pxA(;=CZ2nuXQHX!b1F1>ts7DXFY*J>XA%lJ-!FwmYQGMBqU?8EYabMaV@JX{x`N#_ysshUREZjidLL!}qtG4Hhb;%F"
    "^AHp@h%@bKi$B2^;L7=E(k<xM@@a&Nk6v045dq!6Qy6azL=z^*=|O3zt9!5EE??sAKgV`R78VK82pH2t08>Kfyo(p|Fi0$OI"
    "4)>F5|(_!591M}+wy*jGg+Nd)uk)Nq2SEK(&bB{dR@xGNC^ftQlBP|=bRe|om?{Re#DX*lM;jfg)9C*X-~6m95Rz{_w}c;lQ"
    "9VjUAGCW{gSghGbX@t~mIq<8?KN+k-D1%rjkaL}Imp?N=5?3Z9xgYJKp;r^lLqC>?AGA<PWs5RiM30FO#2P*$g1T>}{AzB=K"
    "iVDM83@k;u{mIhpkJDZ^^Dfj`g0GBf>w9uN!B0j__Qvkl$2{5tU)uo%@{F7ueJPW=;0knF-;oodA%NjS0u)K?%<qDBF0(D0s"
    ";sj_jZ#8}GR7ye(?Qi;p+k0&4*JYF7=s-9%KI#tuij^AS5nkLJ|-*uzn+1FQxFTO_d&l2*?@lkkitpC&3%k2$LKtu=VQ@sb`"
    "g7VdK%CaKfv$l!nER(r$^OsoaL!T#WhjQAs7vsNRP!0Yck7Y$tG6ddO3<83JC(Y=8NtyR&TPhxKE7&5G6+0J=zL(ixfMlw&<"
    "PrUfk$i^j<I``nlgBR;YG5!aW{|3g|051wkU`)JFu5aqxxU><|UhR~ey&b|mCpl_bsO&I9gfMjc!!SDgO2T7bV|E}o#Xg)+N"
    "2GhHl5)rRA6%hT#m%)%gm0tVYL*0ri_S-k3Lo~_YA1kA3w>fmSyTr=Eg2G26I4cqm^f~*-yl4^X7X%^oeA|vayn!{Z;&ydeD"
    "aS6|kflNB~I?k2nb<^caNy5mpZrZE5$@<&Qv*b<*CMA=QKx!hCNxZ<}Uc<3iwj|Ol4l<`CcbBz$`E?mjDl>z5q0k}jvsnNpG"
    "qed<GL<5YP-Fx@LdjKAcU`7oqqIV&adLbpr;3446uDe3cu5C;9dZruqDu;YSQcOfPyKE165NS;*TbtO8a?~%hm}+~8gTW4#1"
    "R%D!`>os+9dKYbvM+jlLx|x3j9dK7%5USEW^_@+2!V1$S{7~Mx8sdqQ>(zop0GzdBtgPr4I#*RHtEC!ohH|j~d1Yv4&QW^vi"
    "f|d&4k!3S)mAemrL<J%Ar$EonvXrOb%wRxNEt?}c_WjE6R3S2tl3;-FO(KXUkXYhGKpGq;kDW|uL{fB4beTZ_s_T&l}GJRr3"
    "jo?ILO=ILbJ2&UqfJQkf*^K5xF_lJjt)m)y*qnu00Mv^JO=u^`@9k8JDhcZwdUVVTDFBc2S$aMoDRvrmRu4^}}nk*-F3pPwL"
    "P}p@=EEGU-%2*7bZ{(DfA^f5os=2Y?93m;3ot+&ClueC4tnzwv<gSJ~EKMqdQS?HrbM#}_*2D-4nSg7CrJLp$m68&xrtM}~6"
    "-p+1=~&`lzlX8QN%OABc^y3>juftE*M|a7I<!zygs4k+H4$ksKqtbllA2V>uH-mj*_N2CV;YnDp;?@voI;rFAJky66G!Y_Xl"
    "eF({o3dPf@qhjRy<V4>Ib9kRTF-mh+67YG(UJm3Z+|AIv!Bq9dblWR2#Y%UYf{jxy2p2abhL*8Dw5LDNp4Q+j7~fzwiC`%fI"
    "A=P6ri&w=N0A4*5LZ$N-V>PK$BJu^phqA3;E=+NSN4=_FL0p|3<F8L#;|<idocjryc=#`9*pvv?`mWT?c2bg}Ee$AtXfu9%l"
    "8UP1wng6>DsN2Sk_q4W{^-@jT<-f3BbhgUZz7I$<A(iiKQxb1mkLyim;eLPBOuIH>#pwC_VP3hWV>DqEm8LblRaZwvdOsIgr"
    "{q>zx05#swh|!V8Q7r7EsPPh4Gf`(Lnoc~{K>LPA8ARL>#ajmzfR!Cy3Szg36(HU}K&6L`Ty&L4SIp-M(hXY^DqyKZ!vY^))"
    "Czw8&ai6sc3izh=2F+a>ISbRmQmQvv+KIE4kiEf>zmv76xz`sjS;|7hP!Rc10q9>mMN%fj%|CIxJ%Bbp={ScahGKQ2r%9T`z"
    "ec>`n<>r+6Fh)H$12v5{-5mlWTm+%W`yHlxNY?0GPPe*1VlMFX!ApHh{}q8p709xmgz1A?X>9KlC)Ws++uAREz03VO;T{((p"
    "n7&_5VTL+A|;vbG5w2i4o@N#Iwndd36Y;~G#m%jwkC2Y&Z_CVs)5vQMN0h#O|j`iY0_E2GLmXhsnJ_6;m?k~CyvsUx0DGfUh"
    "H<XPh7b&YMI@{LU`d5JK}+ETXxZ)$K+hX3K48}yCet+AyKDu?WC=m;^(<kIKid6s^EUBjb8=5K0x0|)4%tZ(or{7nroQTF^e"
    "L!LA`onzxOoXVplkN<nDVO6<i+Io%GqM|UhZQ63YV*$us{d1qmM34QFdJv^A0NQ;qDS*+Nr;Yy~JS3LU"
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
