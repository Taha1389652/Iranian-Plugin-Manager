# ba_meta require api 9
from __future__ import annotations

import os
import shutil
import hashlib
import importlib
import logging

import babase
import bauiv1 as bui
import _babase
from bauiv1lib import popup

logger = logging.getLogger('Tex_fu')

pack_dir = 'Tex_fu'
pack_name = '@Bombsquad_mod1'
creator = 'bombsquad_mod1'

_STRINGS = {
    'Spanish': {
        'success': '¡Instalación Exitosa!',
        'fail': '¡Instalación Fallida! (archivos no encontrados)',
        'created': 'Creado por: ' + creator,
    },
    'Chinese': {
        'success': '安装成功！',
        'fail': '安装失败！（未找到文件）',
        'created': '由...制作： ' + creator,
    },
    'default': {
        'success': 'نصب با موفقیت انجام شد',
        'fail': 'نصب ناموفق بود (فایل تکسچرر یافت نشد)',
        'created': 'Created by: ' + creator,
    },
}


def _get_strings() -> dict:
    try:
        lang = babase.app.lang.language
    except Exception:
        lang = None
    return _STRINGS.get(lang, _STRINGS['default'])


class NewModPopup(popup.PopupWindow):

    def __init__(self, success: bool = True):
        app = babase.app
        uiscale = app.ui_v1.uiscale
        strings = _get_strings()

        self._width = 400
        self._height = 310
        bg_color = (0.5, 0.4, 0.6)

        scale = (1.8 if uiscale is bui.UIScale.SMALL else
                 1.4 if uiscale is bui.UIScale.MEDIUM else 1.0)

        popup.PopupWindow.__init__(self,
                                    position=(0.0, 0.0),
                                    size=(self._width, self._height),
                                    scale=scale,
                                    bg_color=bg_color)

        if success:
            install_text = strings['success']
            sound = 'achievement'
            image = 'chestOpenIcon'
            color = (0.0, 1.0, 0.0)
            modcolor = (1.0, 1.0, 1.0)
            extray = 0
        else:
            install_text = strings['fail']
            sound = 'kronk2'
            image = 'chestIcon'
            color = (1.0, 0.1, 0.1)
            modcolor = (0.7, 0.7, 0.7)
            extray = -2

        bui.buttonwidget(
            parent=self.root_widget,
            position=(self._width * 0.5 - 75, self._height * 0.07),
            size=(150, 52),
            scale=1.0,
            autoselect=True,
            color=(0.3, 0.8, 0.5),
            label=bui.Lstr(resource='okText'),
            on_activate_call=self.close,
        )

        bui.textwidget(
            parent=self.root_widget,
            position=(self._width * 0.5, self._height * 0.9),
            size=(0, 0),
            h_align='center',
            v_align='center',
            scale=1.1,
            text=install_text,
            maxwidth=self._width * 0.7,
            color=color,
        )
        bui.imagewidget(
            parent=self.root_widget,
            position=(self._width * 0.5 - 55, self._height * 0.494 + extray),
            size=(110, 110),
            texture=bui.gettexture(image),
        )
        bui.textwidget(
            parent=self.root_widget,
            position=(self._width * 0.5, self._height * 0.426),
            size=(0, 0),
            h_align='center',
            v_align='center',
            scale=1.3,
            text=pack_name,
            maxwidth=self._width * 0.7,
            color=modcolor,
        )
        bui.textwidget(
            parent=self.root_widget,
            position=(self._width * 0.5, self._height * 0.314),
            size=(0, 0),
            h_align='center',
            v_align='center',
            scale=0.8,
            text=strings['created'],
            maxwidth=self._width * 0.7,
            color=(1.0, 1.0, 0.0),
        )

        try:
            if not success:
                bui.playsound(bui.getsound('error'))
            bui.playsound(bui.getsound(sound))
        except Exception:
            logger.exception('Tex_fu: could not play install sound')

    def close(self) -> None:
        bui.containerwidget(
            edit=self.root_widget,
            transition='out_scale',
        )


class PackInstaller:

    def __init__(self) -> None:
        env = _babase.env()
        self.python_user = env['python_directory_user']
        self.app_dir = env['python_directory_app']

        self.cfiles = os.path.join(self.python_user, pack_dir) + os.sep
        self.models_dir = os.path.join(self.app_dir, 'models') + os.sep
        self.audio_dir = os.path.join(self.app_dir, 'audio') + os.sep
        self.textures_dir = os.path.join(self.app_dir, 'textures') + os.sep

        self.audio: list[str] = []
        self.models: list[str] = []
        self.textures: list[str] = []

        try:
            self.platform = 'android' if babase.app.env.android else 'other'
        except Exception:
            self.platform = 'other'

        self._pack_dir_ok = self.get_character()

    def get_character(self) -> bool:
        if not os.path.isdir(self.cfiles):
            logger.error('Tex_fu: pack folder not found: %s', self.cfiles)
            return False

        try:
            fls = os.listdir(self.cfiles)
        except OSError:
            logger.exception('Tex_fu: could not list pack folder %s', self.cfiles)
            return False

        for fl in fls:
            lower = fl.lower()
            if lower.endswith('.ogg'):
                self.audio.append(fl)
            elif lower.endswith('.bob') or lower.endswith('.cob'):
                self.models.append(fl)
            elif lower.endswith('.ktx') or lower.endswith('.dds'):
                self.textures.append(fl)
        return True

    @staticmethod
    def checkFileSame(f1: str, f2: str) -> bool:
        try:
            md5s = [hashlib.md5(), hashlib.md5()]
            fs = [f1, f2]
            for i in range(2):
                with open(fs[i], 'rb') as f:
                    block_size = 2 ** 20
                    while True:
                        data = f.read(block_size)
                        if not data:
                            break
                        md5s[i].update(data)
                md5s[i] = md5s[i].hexdigest()
            return md5s[0] == md5s[1]
        except Exception:
            return False

    def _dest_for_texture(self, t: str) -> str | None:
        lower = t.lower()
        if self.platform == 'android':
            if lower.endswith('.dds'):
                return None
        else:
            if lower.endswith('.ktx'):
                return None
        return os.path.join(self.textures_dir, t)

    def _installed(self) -> bool:
        if not self._pack_dir_ok:
            return False

        for a in self.audio:
            app_path = os.path.join(self.audio_dir, a)
            user_path = os.path.join(self.cfiles, a)
            if not os.path.isfile(app_path) or not self.checkFileSame(app_path, user_path):
                return False

        for m in self.models:
            app_path = os.path.join(self.models_dir, m)
            user_path = os.path.join(self.cfiles, m)
            if not os.path.isfile(app_path) or not self.checkFileSame(app_path, user_path):
                return False

        for t in self.textures:
            app_path = self._dest_for_texture(t)
            if app_path is None:
                continue
            user_path = os.path.join(self.cfiles, t)
            if not os.path.isfile(app_path) or not self.checkFileSame(app_path, user_path):
                return False

        return True

    def install_pack(self) -> bool:
        if not self._pack_dir_ok:
            return True

        if not (self.audio or self.models or self.textures):
            return True

        if self._installed():
            return True

        try:
            os.makedirs(self.audio_dir, exist_ok=True)
            os.makedirs(self.models_dir, exist_ok=True)
            os.makedirs(self.textures_dir, exist_ok=True)

            for fl in self.audio:
                shutil.copyfile(os.path.join(self.cfiles, fl), os.path.join(self.audio_dir, fl))

            for fl in self.models:
                shutil.copyfile(os.path.join(self.cfiles, fl), os.path.join(self.models_dir, fl))

            for fl in self.textures:
                dest = self._dest_for_texture(fl)
                if dest is None:
                    continue
                shutil.copyfile(os.path.join(self.cfiles, fl), dest)

            return True
        except Exception:
            logger.exception('Tex_fu: install_pack failed')
            return False


def _load_subpackage() -> bool:
    try:
        importlib.import_module(pack_dir + '.banewpack')
        return True
    except Exception:
        logger.exception('Tex_fu: failed to import %s.banewpack', pack_dir)
        return False


# ba_meta export babase.Plugin
class NewPack(babase.Plugin):

    def __init__(self) -> None:
        super().__init__()

    def on_app_running(self) -> None:
        copy_ok = True
        try:
            copy_ok = PackInstaller().install_pack()
        except Exception:
            logger.exception('Tex_fu: PackInstaller failed')
            copy_ok = False

        load_ok = _load_subpackage()

        babase.apptimer(1.0, babase.Call(NewModPopup, copy_ok and load_ok))

    # bombsquad
    # mod
    # 1
