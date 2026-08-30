# ba_meta require api 7

from __future__ import annotations
from typing import TYPE_CHECKING

import ba
import _ba
import os
import shutil
import hashlib
from bastd.ui import popup

if TYPE_CHECKING:
    pass

pack_dir = 'Tex_fu'  
pack_name = '@Bombsquad_mod1'  
creator = 'bombsquad_mod1' 

lang = ba.app.lang.language

if lang == 'Spanish':
    install_success = '¡Instalación Exitosa!'
    install_fail = '¡Instalación Fallida!'
    created = 'Creado por: ' + creator
elif lang == 'Chinese':
    install_success = '安装成功！'
    install_fail = '安装失败！'
    created = '由...制作： ' + creator
else:
    install_success = 'نصب با موفقیت انجام شد'
    install_fail = 'نصب ناموفق بود (فایل تکسچرر یافت نشد)'
    created = 'Created by: ' + creator


class NewModPopup(popup.PopupWindow):

    def __init__(self, success: bool = True):
        app = ba.app
        uiscale = app.ui.uiscale
        
        self._width = 400
        self._height = 310
        bg_color = (0.5, 0.4, 0.6)
        
        scale = (1.8 if uiscale is ba.UIScale.SMALL else
                 1.4 if uiscale is ba.UIScale.MEDIUM else 1.0)

        popup.PopupWindow.__init__(self,
                                   position=(0.0, 0.0),
                                   size=(self._width, self._height),
                                   scale=scale,
                                   bg_color=bg_color)

        if success:
            install = install_success
            sound = 'achievement'
            image = 'chestOpenIcon'
            color = (0.0, 1.0, 0.0)
            modcolor = (1.0, 1.0, 1.0)
            extray = 0
        else:
            install = install_fail
            sound = 'kronk2'
            image = 'chestIcon'
            color = (1.0, 0.1, 0.1)
            modcolor = (0.7, 0.7, 0.7)
            extray = -2

        save_button = btn = ba.buttonwidget(
            parent=self.root_widget,
            position=(self._width * 0.5 - 75, self._height * 0.07),
            size=(150, 52),
            scale=1.0,
            autoselect=True,
            color=(0.3, 0.8, 0.5),
            label=ba.Lstr(resource='okText'),
            on_activate_call=self.close
        )

        ba.textwidget(
            parent=self.root_widget,
            position=(self._width * 0.5, self._height * 0.9),
            size=(0, 0),
            h_align='center',
            v_align='center',
            scale=1.1,
            text=install,
            maxwidth=self._width * 0.7,
            color=color
        )
        ba.imagewidget(
            parent=self.root_widget,
            position=(self._width * 0.5 - 55, self._height * 0.494 + extray),
            size=(110, 110),
            texture=ba.gettexture(image)
        )
        ba.textwidget(
            parent=self.root_widget,
            position=(self._width * 0.5, self._height * 0.426),
            size=(0, 0),
            h_align='center',
            v_align='center',
            scale=1.3,
            text=pack_name,
            maxwidth=self._width * 0.7,
            color=modcolor
        )
        ba.textwidget(
            parent=self.root_widget,
            position=(self._width * 0.5, self._height * 0.314),
            size=(0, 0),
            h_align='center',
            v_align='center',
            scale=0.8,
            text=created,
            maxwidth=self._width * 0.7,
            color=(1.0, 1.0, 0.0)
        )

        if not success:
            ba.playsound(ba.getsound('error'))
        ba.playsound(ba.getsound(sound))

    def close(self) -> None:
        ba.containerwidget(
            edit=self.root_widget,
            transition='out_scale'
        )


class PackInstaller:

    def __init__(self) -> None:
        self.python_user = _ba.env()["python_directory_user"]
        self.cfiles = self.python_user + '/' + pack_dir + '/'
        self.app_dir = _ba.env()["python_directory_app"] + '/'
        self.models_dir = self.app_dir + 'models/'
        self.audio_dir = self.app_dir + 'audio/'
        self.textures_dir = self.app_dir + 'textures/'

        self.audio = []
        self.models = []
        self.textures = []
        self.platform = _ba.app.platform
        print(self.platform)
        self.get_character()

    def get_character(self) -> None:
        fls = os.listdir(self.cfiles)
        for fl in fls:
            if fl.endswith('.ogg'): # audio
                self.audio.append(fl)
            if fl.endswith('.bob') or fl.endswith('.cob'): # models
                self.models.append(fl)
            if fl.endswith('.ktx') or fl.endswith('.dds'): # textures
                self.textures.append(fl)

    @staticmethod
    def checkFileSame(f1, f2):
        try:
            md5s = [hashlib.md5(), hashlib.md5()]
            fs = [f1, f2]
            for i in range(2):
                f = open(fs[i], 'rb')
                block_size = 2 ** 20
                while True:
                    data = f.read(block_size)
                    if not data: break
                    md5s[i].update(data)
                f.close()
                md5s[i] = md5s[i].hexdigest()
            return md5s[0] == md5s[1]
        except Exception as e:
            return False

    def _installed(self) -> None:
        installed = True
        for a in self.audio:
            app = 'ba_data/audio/' + a
            user = self.cfiles + a
            if not os.path.isfile(app):
                installed = False
                break
            if not self.checkFileSame(app, user):
                installed = False
                break
        for m in self.models:
            app = 'ba_data/models/' + m
            user = self.cfiles + m
            if not os.path.isfile(app):
                installed = False
                break
            if not self.checkFileSame(app, user):
                installed = False
                break
        for t in self.textures:
            if self.platform == 'android':
                if t.endswith('.dds'):
                    continue
            else:
                if t.endswith('.ktx'):
                    continue
            app = 'ba_data/textures/' + t
            user = self.cfiles + t
            if not os.path.isfile(app):
                installed = False
                break
            if not self.checkFileSame(app, user):
                installed = False
                break
        return installed

    def install_pack(self) -> None:
        if self._installed():
            return

        try:
            fls = os.listdir(self.cfiles)
            for fl in fls:
                if fl.endswith('.ogg'): # audio
                    shutil.copyfile(self.cfiles + fl, 'ba_data/audio/' + fl)
                if fl.endswith('.bob') or fl.endswith('.cob'): # models
                    shutil.copyfile(self.cfiles + fl, 'ba_data/models/' + fl)
                if fl.endswith('.ktx') and self.platform == 'android': # textures
                    shutil.copyfile(self.cfiles + fl, 'ba_data/textures/' + fl)
                elif fl.endswith('.dds'): # textures
                    shutil.copyfile(self.cfiles + fl, 'ba_data/textures/' + fl)
                    
            ba.timer(1.0, ba.Call(NewModPopup, True))
        except:
            ba.timer(1.0, ba.Call(NewModPopup, False))


# ba_meta export plugin
class NewPack(ba.Plugin):
    PackInstaller().install_pack()
    exec('import ' + pack_dir + '.banewpack')
    #bombsquad
    #mod
    #1