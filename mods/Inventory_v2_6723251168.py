# ba_meta require api 9

# •━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━•
#
#     Version v2.0.1
#     Create by Unknown_#7004 - ( @uwu.user )
#         - Github https://github.com/uwu-user
#         - https://gamebanana.com/members/2496091
#
# •━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━•

from __future__ import annotations
from typing import TYPE_CHECKING, cast, override

import bauiv1 as bs
import babase as bb
import _babase as _ba
import bascenev1 as ba
from enum import Enum
import bauiv1lib.inventory
import time, random, math
from bauiv1lib.tabs import TabRow
from bascenev1lib import mainmenu
from bascenev1lib.actor.spaz import Spaz
from bauiv1lib.iconpicker import IconPicker
from bauiv1lib.colorpicker import ColorPicker
from bauiv1lib.confirm import ConfirmWindow
from bascenev1lib.actor import spazappearance
from bauiv1lib.profile import upgrade as pupgrade
from bascenev1lib.gameutils import SharedObjects
from bauiv1lib.characterpicker import CharacterPicker
from bascenev1lib.mainmenu import MainMenuActivity
from bauiv1lib.account.signin import show_sign_in_prompt
from bascenev1lib.mainmenu import MainMenuActivity, MainMenuSession

if TYPE_CHECKING:
    from typing import Any, Sequence, Callable, List, Dict, Tuple, Optional, Union

# •━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━•

temporary_account_name = "__temporary_account__" # warn: do not edit it - not safe
enable_ui_animation = True

# •━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━•

class ProfileSpaz(Spaz):
    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, ba.OutOfBoundsMessage):
            activity = ba.get_foreground_host_activity()
            if activity:
                with activity.context: activity.set_character(activity.character); activity.set_color(activity.color); activity.set_highlight(activity.highlight)
        if isinstance(msg, ba.DieMessage):
            try:
                if hasattr(self, 'node') and self.node: self.node.delete()
            except: pass
        try: return super().handlemessage(msg)
        except AttributeError: return None

# •━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━•

class SoundManager:
    @staticmethod
    def play_sound(sound_name: str) -> None:
        try:  sound = ba.getsound(sound_name).play()
        except: pass

    @staticmethod
    def play_character_sound(character: str) -> None:
        try:
            classic = bs.app.classic
            if classic is not None:
                spaz_appearances = classic.spaz_appearances; appearance = spaz_appearances.get(character)
                if appearance:
                    sounds = ( appearance.jump_sounds + appearance.attack_sounds + appearance.pickup_sounds )
                    if sounds:
                        try: bs.getsound(random.choice(sounds)).play()
                        except: pass
        except: pass

# •━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━•

class inventoryActivity(ba.Activity[ba.Player, ba.Team]):
    def __init__(self, settings: dict):
        super().__init__(settings)
        self.character, self.color, self.highlight = 'Spaz', (0.5, 0.5, 0.5), (1.0, 1.0, 1.0)
        self.spaz = self._base_target = self._base_position = self._rotation_timer = self._return_animation_timer = self._selected_profile = self._light_enabled = self._light_node = None
        self._camera_animation_started = self._rotate_camera_enabled = self._is_rotating = self._spawning = self._editor_update_needed = False
        self._rotation_direction, self._rotation_angle = 1, 0.0
        profiles = bs.app.config.get('Player Profiles', {})
        plus, order = bs.app.plus, []; signed_in = plus is not None and plus.get_v1_account_state() == 'signed_in'

        if 'profile_order' in bs.app.config:
            order = bs.app.config.get('profile_order', [])
            if not signed_in and '__account__' in order: order.remove('__account__')
            order = [name for name in order if name in profiles]
        else:
            order = list(profiles.keys())
            if not signed_in and '__account__' in order: order.remove('__account__')
            order.sort(key=lambda x: (0 if x == '__account__' else 1, x.lower()))
            bs.app.config['profile_order'] = order; bs.app.config.commit()

        if order:
            last_profile = order[-1]; self._selected_profile, info = last_profile, profiles.get(last_profile, {})
            if 'character' in info: self.character = info['character']
            classic = bs.app.classic
            if classic:
                try: self.color, self.highlight = classic.get_player_profile_colors(last_profile)
                except: pass

    @override
    def on_transition_in(self) -> None:
        super().on_transition_in()
        self.shared = SharedObjects.get(); ba.set_map_bounds((-99, -99, -99, 99, 99, 99))
        self.globalsnode.tint, self.stand_message_position= (0.5, 0.5, 0.5), (0.5, 6.5, -1.85)        
        self._initialize_materials(); self._create_background(); self._create_water(); self._create_region(); self._create_floors(); self._create_boxes(); self._create_landMine(); self._create_bombs(); self._create_ice(); self._create_impactbombs()
        ba.apptimer(0.15, self.spawn_character); ba.apptimer(0.3, self._animate_camera_to_character)
        ba.setmusic(ba.MusicType.GRAND_ROMP)

    def _initialize_materials(self):
        self.floor = ba.Material(); self._player_floor = ba.Material()
        self.floor.add_actions(conditions=("they_are_different_node_than_us",), actions=("modify_part_collision", "collide", False))
        self._player_floor.add_actions(conditions=("we_are_older_than", 1), actions=("modify_part_collision", "collide", True))

    def _create_background(self):
        ba.newnode("terrain", attrs={"mesh": ba.getmesh("thePadBG"), "lighting": False, "background": True, "color_texture": ba.gettexture("tipTopBGColor")})

    def _create_water(self):
        ba.newnode("locator", attrs={"shape": "circle", "position": (0, 6, 0), "color": (0.3, 0.35, 1.0), "opacity": 0.57, "draw_beauty": True, "additive": False, "size": [500]})

    def _create_region(self):
        ba.newnode("region", attrs={"position": (0, 7, -1), "scale": (10, 0.1, 10), "type": "box", "materials": [self._player_floor, self.shared.footing_material]})

    def _create_floors(self):
        positions = [(x, 7, z) for x in [-5.0, -3.0, -1.0, 1.0, 3.0, 5.0] for z in range(2, -10, -2)]
        new = [(-3.0, 7.0, -10), (-3.0, 7.0, -12), (-5.0, 7.0, -12), (-7.0, 7.0, -12), (-9.0, 7.0, -12), (-9, 7.0, -10), (-7.0, 7.0, -6.0), (7.0, 7.0, -8.0), (7.0, 7.0, -10), (7.0, 7.0, -12), (7.0, 7.0, -14), (9.0, 7.0, -14), (1.0, 7.0, 4), (1.0, 7.0, 6), (3.0, 7.0, 6)]
        for pos in positions: self._create_floor(position=pos)
        for pos in new: self._create_floor(position=pos)

    def _create_floor(self, position):
        ba.newnode("prop", attrs={"position": position, "mesh": ba.getmesh("image1x1"), "color_texture": ba.gettexture("flagColor"), "mesh_scale": 2, "body": "puck", "density": float("inf"), "damping": float("inf"), "materials": [self.floor]})

    def _create_boxes(self):
        boxes = [
            {"position": (5, 8, -7.5), "velocity": (0, 1, 0), "mesh": "tnt", "texture": "tnt", "size": 2.5, "light_radius": 0.45, "light_color": (0.74, 0.56, 0.56), "intensity": 7, "light_animate": False, "light_animate_speed": 0, "gravity": False},
            {"position": (4.75, 7.5, -5.85), "velocity": (-5, 0, 0), "mesh": "tnt", "texture": "powerupImpactBombs", "size": 1.5, "light_radius": 0.35, "light_color": (0, 0, 2.55), "intensity": 20, "light_animate": True, "light_animate_speed": 2.0, "gravity": True},
            {"position": (4.95, 8.3, -5.65), "velocity": (5, 0, 0), "mesh": "powerup", "texture": "powerupShield", "size": 1, "light_radius": 0.05, "light_color": (0, 2.55, 2.55), "intensity": 1.0, "light_animate": False, "light_animate_speed": 0, "gravity": False},
            {"position": (5.1, 7.5, 2), "velocity": (0, 5, 0), "mesh": "powerup", "texture": "powerupSpeed", "size": 1.5, "light_radius": 0.15, "light_color": (0, 2.55, 0), "intensity": 0.5, "light_animate": True, "light_animate_speed": 0.75, "gravity": False},
            {"position": (9.0, 7.5, -14), "velocity": (0, 5, 0), "mesh": "powerup", "texture": "powerupCurse", "size": 1.5, "light_radius": 0.15, "light_color": (2.55, 0, 0), "intensity": 0.35, "light_animate": True, "light_animate_speed": 3.25, "gravity": True},
            {"position": (-9, 7.5, -12), "velocity": (0, -5, 0), "mesh": "powerup", "texture": "powerupLandMines", "size": 1.5, "light_radius": 0.15, "light_color": (0, 9, 0), "intensity": 0.45, "light_animate": False, "light_animate_speed": 0, "gravity": True},
            {"position": (-7.0, 7.5, -6.0), "velocity": (0, 0, -1), "mesh": "powerup", "texture": "powerupIceBombs", "size": 1.35, "light_radius": 0.15, "light_color": (0, 0, 2.55), "intensity": 0.5, "light_animate": True, "light_animate_speed": 5, "gravity": True},
            {"position": (-5.0, 7.75, 2.15), "velocity": (0, 1, 0), "mesh": "tnt", "texture": "tnt", "size": 1.5, "light_radius": 0.15, "light_color": (0.74, 0.56, 0.56), "intensity": 7, "light_animate": False, "light_animate_speed": 0, "gravity": False},
            {"position": (-4.2, 7.5, 1.0), "velocity": (0, 1, 0), "mesh": "powerup", "texture": "powerupHealth", "size": 1.05, "light_radius": 0.05, "light_color": (2.55, 2.55, 2.55), "intensity": 0.45, "light_animate": True, "light_animate_speed": 20, "gravity": True},
            {"position": (1, 7.85, -3.5), "velocity": (0, -1, 0), "mesh": "tnt", "texture": "tnt", "size": 2.0, "light_radius": 0.15, "light_color": (0.74, 0.56, 0.56), "intensity": 7, "light_animate": False, "light_animate_speed": 0, "gravity": False},
            {"position": (1.75, 7.5, -1.95), "velocity": (0, -1, 0), "mesh": "powerup", "texture": "powerupStickyBombs", "size": 1.15, "light_radius": 0.15, "light_color": (0, 2.55, 0), "intensity": 0.45, "light_animate": False, "light_animate_speed": 0, "gravity": True},]
        for box in boxes: self._create_box(**box)

    def _create_box(self, position, velocity, mesh, texture, size, light_radius, light_color, intensity, light_animate, light_animate_speed, gravity):
        ba.newnode("prop", delegate=self, attrs={"position": position, "velocity": velocity, "mesh": ba.getmesh(mesh), "mesh_scale": size, "density": float("inf"), "damping": float("inf"), "gravity_scale": 10 if gravity else 0, "body": "crate", "reflection": "powerup", "is_area_of_interest": False, "reflection_scale": [0.05], "color_texture": ba.gettexture(texture), "materials": [self.shared.footing_material, self.floor]})
        self._create_light(position, light_radius, light_color, intensity, light_animate, light_animate_speed)

    def _create_light(self, position, light_radius, light_color, intensity, animate, speed):
        self.light_node = ba.newnode("light", attrs={"position": position, "intensity": intensity, "radius": light_radius, "color": light_color})
        if animate: ba.timer(0.01, ba.CallPartial(self.animate_light, self.light_node, speed))

    def animate_light(self, node, speed):
        ba.animate(node, "intensity", {0: 0.05, speed: 5, speed*2: 0.05}, loop=True)

    def _create_landMine(self):
        landmine_data = [((3.95, 7.2, 2.25), 1.5), ((3.15, 7.2, 6.15), 1.5)]
        for (position, size) in landmine_data: self._create_landmine(position, size)

    def _create_landmine(self, position, size):
        node = self._initialize_landmine_node(position, size)
        self._initialize_landmine_texture_sequence(node)

    def _initialize_landmine_node(self, position, size):
        return ba.newnode("prop", delegate=self, attrs={"position": position, "velocity": (0, 0, 0), "mesh": ba.getmesh("landMine"), "mesh_scale": size, "body_scale": size, "density": float("inf"), "damping": float("inf"), "gravity_scale": 0, "body": "crate", "reflection": "powerup", "is_area_of_interest": False, "reflection_scale": [0], "extra_acceleration": (0, 20, 0), "color_texture": ba.gettexture("landMine"), "materials": [self.shared.footing_material]})

    def _initialize_landmine_texture_sequence(self, node):
        texture_sequence = ba.newnode("texture_sequence", owner=node, attrs={"rate": 20 * 60, "input_textures": (ba.gettexture("landMineLit"), ba.gettexture("landMine"))})
        texture_sequence.connectattr("output_texture", node, "color_texture")

    def _create_bombs(self):
        bombs_data = [((3.5, 7.5, -6), 2), ((-0.5, 7.5, -4.0), 1.75)]
        for (position, size) in bombs_data: self._bomb(position, size)

    def _bomb(self, position, size): 
        self.node = ba.newnode("bomb", attrs={"position": position, "mesh": ba.getmesh("bomb"), "mesh_scale": size, "body_scale": size, "shadow_size": 0.3, "gravity_scale": 0, "density": float("inf"), "damping": float("inf"), "color_texture": ba.gettexture("bombColor"), "reflection": "sharper", "sticky": False})
        self.sound = ba.newnode("sound", owner=self.node, attrs={"sound": ba.getsound("fuse01"), "volume": 0.05})
        self.node.connectattr("position", self.sound, "position")

    def _create_ice(self) -> None:
        positions = [((-8.5, 4.35, 1), 1.5), ((-10.5, 4.75, -7.5), 1), ((-4, 4.5, -20), 1.7), ((-30, 4.25, -60), 1.8), ((5, 4.25, -80), 1.8), ((-8, 4.05, -47), 1.5), ((2, 5, -15), 1.2), ((12, 4.65, -3), 1.5), ((6, 4.5, 5), 0.8)]
        for position, size in positions: self._create_ice_node(position=position, size=size)

    def _create_ice_node(self, position, size):
        node, node_light = ba.newnode("prop", delegate=self, attrs=self._ice_node_attrs(position, size)), ba.newnode("light", attrs=self._ice_node_light_attrs(position, size))
        ba.timer(0.01, ba.CallPartial(self.ice_move, node, size))

    def _ice_node_attrs(self, position, scale):
        return {"position": position, "velocity": (0, 1, 0), "mesh": ba.getmesh("shrapnel1"), "mesh_scale": scale, "body_scale": scale - 0.5, "density": float("inf"), "damping": float("inf"), "gravity_scale": 0, "body": "crate", "reflection": "powerup", "is_area_of_interest": False, "reflection_scale": [0], "extra_acceleration": (0, 20, 0), "color_texture": ba.gettexture("bar"), "materials": [self.shared.footing_material]}

    def _ice_node_light_attrs(self, position, radius):
        return {"position": position, "radius": radius, "intensity": 0.055, "color": (2, 2, 2)}

    def ice_move(self, node, size):
        x, y, z = node.position; (a, b), t, m, f = (random.uniform(size/2 + 0.1, size/2 + 0.7) for _ in range(2)), random.uniform(1.0, 5.0), 2, 0.15
        ba.animate_array(node, "position", 3, {0.0: (x, (y+a)+f, z), t: (x, (y+b)+f, z), t*m: (x, (y+a)+f, z)}, loop=True)

    def _create_impactbombs(self):
        impactbombs_data = [((4.95, 7.2, 0.2), 1.75)]
        for (position, size) in impactbombs_data: self._impactbomb(position, size)

    def _impactbomb(self, position, size):
        self.node = ba.newnode("prop", attrs={"position": position, "mesh": ba.getmesh("impactBomb"), "mesh_scale": size, "body_scale": size, "shadow_size": 0.3, "gravity_scale": 0, "density": float("inf"), "damping": float("inf"), "color_texture": ba.gettexture("impactBombColor"), "body": "sphere", "reflection": "powerup"})
        self._initialize_impactbomb_texture_sequence(self.node)

    def _initialize_impactbomb_texture_sequence(self, node):
        texture_sequence = ba.newnode("texture_sequence", owner=node, attrs={"rate": 15 * 60, "input_textures": (ba.gettexture("impactBombColorLit"), ba.gettexture("impactBombColor"))})
        texture_sequence.connectattr("output_texture", node, "color_texture")

    def delete_spaz(self):
        if self.spaz is not None:
            try:
                if hasattr(self.spaz, 'handlemessage'): self.spaz.handlemessage(ba.DieMessage(immediate=True))
                if hasattr(self.spaz, 'node') and self.spaz.node: self.spaz.node.delete()
            except: pass
            self.spaz, self._spawning = None, False

    def spawn_character(self):
        if self._spawning: return
        self._spawning = True
        try:
            self.delete_spaz()
            def create_character():
                try:
                    current_session = ba.get_foreground_host_session()
                    if not current_session: self._spawning = False; return
                    current_activity = current_session.getactivity()
                    if current_activity is not self: self._spawning = False; return
                    with self.context:
                        self.spaz = ProfileSpaz(character=self.character, start_invincible=False).autoretain()
                        if hasattr(self.spaz, 'node') and self.spaz.node:
                            self.spaz.node.is_area_of_interest = False
                            self.spaz.node.color, self.spaz.node.highlight = self.color, self.highlight
                            self.spaz.handlemessage(ba.StandMessage(position=self.stand_message_position, angle=0))
                            if self._light_enabled: self._create_character_light()
                    self._spawning = False
                except Exception as e:
                    print(f"[ ! ] Error unknown character assets: {e} - [ auto-fix: repaced with spaz ]")
                    self._spawning = False; self._create_fallback_character()
            bs.pushcall(create_character)
        except Exception as e:
            print(f"[ ! ] Error in spawn_character: {e}")
            self._spawning = False; self._create_fallback_character()

    def _create_fallback_character(self):
        try:
            self.character, current_session = 'Spaz', ba.get_foreground_host_session()
            if not current_session: self._spawning = False; return
            current_activity = current_session.getactivity()
            if current_activity is not self: self._spawning = False; return
            with self.context:
                self.spaz = ProfileSpaz(character='Spaz', start_invincible=False).autoretain()
                if hasattr(self.spaz, 'node') and self.spaz.node:
                    self.spaz.node.is_area_of_interest = False
                    self.spaz.node.color, self.spaz.node.highlight = self.color, self.highlight
                    self.spaz.handlemessage(ba.StandMessage(position=self.stand_message_position, angle=0))
                    if self._light_enabled: self._create_character_light()
        except Exception as e: print(f"[ ! ] Error creating fallback character: {e}")
        self._spawning = False

    def _create_character_light(self):
        self._remove_character_light()
        if not self._light_enabled: return
        if self.spaz is None: return
        try:
            if not hasattr(self.spaz, 'node') or self.spaz.node is None: return
            char_color = self.spaz.node.color if self.spaz.node.color else self.color
            with self.context:
                self._light_node = ba.newnode("light", attrs={"color": char_color, "radius": 3.0, "intensity": 0.5, "position": (0.5, 7, -1.85)})
            self.spaz.node.connectattr("position", self._light_node, "position")
            ba.animate(self._light_node, "intensity", {0: 0.0, 1.0: 0.5})
        except: pass

    def _remove_character_light(self):
        if self._light_node:
            try: self._light_node.delete(); self._light_node = None
            except: pass

    def toggle_character_light(self, enabled: bool):
        self._light_enabled = enabled
        if enabled: self._create_character_light()
        else: self._remove_character_light()

    def _save_profile(self, profile_name=None):
        name = profile_name if profile_name else self._selected_profile
        if not name: return
        profiles = bs.app.config.get('Player Profiles', {})
        if name in profiles:
            profiles[name]['character'] = self.character; profiles[name]['color'] = list(self.color); profiles[name]['highlight'] = list(self.highlight)
            bs.app.config['Player Profiles'] = profiles; bs.app.config.commit()

    def set_character(self, name: str) -> None:
        if self.character == name: return
        self.character = name
        def apply_character():
            current_session = ba.get_foreground_host_session()
            if current_session:
                activity = current_session.getactivity()
                if activity is self:
                    self._save_profile(); self.spawn_character()
                    SoundManager.play_character_sound(name)
        bs.pushcall(apply_character)

    def set_color(self, color: tuple[float, float, float]) -> None:
        if len(color) > 3: color = color[:3]
        self.color = color
        if self.spaz and hasattr(self.spaz, 'node') and self.spaz.node:
            try:
                self.spaz.node.color = color
                if self._light_enabled and self._light_node:
                    try: self._light_node.color = color
                    except: pass
            except: pass
        self._save_profile()

    def set_highlight(self, color: tuple[float, float, float]) -> None:
        if len(color) > 3: color = color[:3]
        self.highlight = color
        if self.spaz and hasattr(self.spaz, 'node') and self.spaz.node:
            try: self.spaz.node.highlight = color
            except: pass
        self._save_profile()

    def set_icon(self, icon: str) -> None:
        if not self._selected_profile: return
        profiles = bs.app.config.get('Player Profiles', {})
        if self._selected_profile in profiles: profiles[self._selected_profile]['icon'] = icon; bs.app.config['Player Profiles'] = profiles; bs.app.config.commit()

    def set_profile(self, profile_name: str) -> None:
        profiles = bs.app.config.get('Player Profiles', {})
        if profile_name in profiles:
            info = profiles[profile_name]
            with self.context:
                try:
                    if 'character' in info: self.character = info['character']
                    classic = bs.app.classic
                    if classic: self.color, self.highlight = classic.get_player_profile_colors(profile_name)
                    self._selected_profile = profile_name
                    SoundManager.play_character_sound(self.character)
                    self.spawn_character()
                except:
                    try: self.set_character('Spaz')
                    except: pass

    def get_selected_profile(self):
        return self._selected_profile

    def get_character_name(self):
        return self.character

    def _animate_camera_to_character(self):
        if self._camera_animation_started or self.spaz is None: return
        self._camera_animation_started = True
        if not hasattr(self.spaz, 'node') or self.spaz.node is None: return
        try: char_pos = (self.spaz.node.position[0] + 0.4, self.spaz.node.position[1], self.spaz.node.position[2])
        except: return

        (char_x, char_y, char_z), camera_distance, camera_height, target_offset_x, duration = char_pos, 7.25, 1.85, -1.65, 2.0
        start_pos, start_target = _ba.get_camera_position(), _ba.get_camera_target()
        target_pos, target_target = (char_x, char_y + camera_height, char_z + camera_distance), (char_x + target_offset_x, char_y, char_z)
        start_time = time.time()

        _ba.set_camera_manual(True)
        self._base_position, self._base_target = target_pos, target_target

        def update_camera():
            elapsed = time.time() - start_time
            if elapsed >= duration: _ba.set_camera_position(*target_pos); _ba.set_camera_target(*target_target); return
            progress = elapsed / duration; progress = progress * progress * (3.0 - 2.0 * progress)
            current_x = start_pos[0] + (target_pos[0] - start_pos[0]) * progress
            current_y = start_pos[1] + (target_pos[1] - start_pos[1]) * progress
            current_z = start_pos[2] + (target_pos[2] - start_pos[2]) * progress
            target_x = start_target[0] + (target_target[0] - start_target[0]) * progress
            target_y = start_target[1] + (target_target[1] - start_target[1]) * progress
            target_z = start_target[2] + (target_target[2] - start_target[2]) * progress
            _ba.set_camera_position(current_x, current_y, current_z)
            _ba.set_camera_target(target_x, target_y, target_z)
            ba.apptimer(0.016, update_camera)
        update_camera()

    def reset_camera(self):
        self._rotate_camera_enabled = self._is_rotating = False
        _ba.set_camera_manual(False)

    def toggle_camera_rotation(self, value: bool):
        self._rotate_camera_enabled = value
        if value: self._start_camera_rotation()
        else: self._stop_camera_rotation()

    def _start_camera_rotation(self):
        if self._is_rotating or self.spaz is None: return
        self._is_rotating = True
        self._rotation_angle, self._rotation_direction = 0.0, 1
        if self._base_position is None or self._base_target is None:
            if not hasattr(self.spaz, 'node') or self.spaz.node is None: return
            try: char_pos = self.spaz.node.position
            except: return
            if char_pos is None: return
            char_x, char_y, char_z = char_pos
            camera_distance, camera_height, target_offset_x = 7.0, 1.85, -1.35
            self._base_position, self._base_target = (char_x, char_y + camera_height, char_z + camera_distance), (char_x + target_offset_x, char_y, char_z)
        self._update_rotation()

    def _update_rotation(self):
        if not self._is_rotating or not self._rotate_camera_enabled or self.spaz is None:  return
        try:
            max_angle, speed = 0.3, 0.01
            self._rotation_angle += speed * self._rotation_direction
            if self._rotation_angle >= max_angle: self._rotation_angle = max_angle; self._rotation_direction = -1
            elif self._rotation_angle <= -max_angle: self._rotation_angle = -max_angle; self._rotation_direction = 1
            if not hasattr(self.spaz, 'node') or self.spaz.node is None: return
            try:  char_pos = self.spaz.node.position
            except: return

            if char_pos is None: return
            char_x, char_y, char_z = char_pos
            base_pos, base_target = self._base_position, self._base_target
            if base_pos is None or base_target is None: return
            offset_x, offset_y, offset_z = base_pos[0] - char_x, base_pos[1] - char_y, base_pos[2] - char_z
            angle = self._rotation_angle; cos_a, sin_a = math.cos(angle), math.sin(angle)
            rotated_x, rotated_z = offset_x * cos_a - offset_z * sin_a, offset_x * sin_a + offset_z * cos_a
            new_pos, new_target = (char_x + rotated_x, char_y + offset_y, char_z + rotated_z), (base_target[0], base_target[1], base_target[2])
            _ba.set_camera_position(*new_pos); _ba.set_camera_target(*new_target)
            self._rotation_timer = ba.apptimer(0.05, self._update_rotation)
        except: pass

    def _stop_camera_rotation(self):
        self._is_rotating = False
        if self._rotation_timer:
            try: self._rotation_timer = None
            except: pass

        if self._base_position and self._base_target:
            start_pos, start_target = _ba.get_camera_position(), _ba.get_camera_target()
            target_pos, target_target, duration = self._base_position, self._base_target, 0.8
            start_time = time.time()

            def animate_back():
                elapsed = time.time() - start_time
                if elapsed >= duration: _ba.set_camera_position(*target_pos); _ba.set_camera_target(*target_target); return
                progress = elapsed / duration; progress = progress * progress * (3.0 - 2.0 * progress)
                current_x = start_pos[0] + (target_pos[0] - start_pos[0]) * progress
                current_y = start_pos[1] + (target_pos[1] - start_pos[1]) * progress
                current_z = start_pos[2] + (target_pos[2] - start_pos[2]) * progress
                target_x = start_target[0] + (target_target[0] - start_target[0]) * progress
                target_y = start_target[1] + (target_target[1] - start_target[1]) * progress
                target_z = start_target[2] + (target_target[2] - start_target[2]) * progress
                _ba.set_camera_position(current_x, current_y, current_z); _ba.set_camera_target(target_x, target_y, target_z)
                ba.apptimer(0.016, animate_back)
            animate_back()

    def on_transition_out(self):
        self._remove_character_light(); self.delete_spaz()
        super().on_transition_out()

# •━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━•

class CustomSwitch:
    def __init__(self, parent: bs.Widget, position: tuple[float, float], size: tuple[float, float], config_key: str, display_text: str, on_value_change: callable = None):
        self._config_key, self._parent_widget, self._is_animating, self._display_text, self._on_value_change, self._widgets = config_key, parent, False, display_text, on_value_change, []
        self._animation_progress = self._animation_start_time = 0.0
        checkbox_height = size[1] * 0.7; checkbox_width = checkbox_height * 1.4
        checkbox_x, checkbox_y, circle_size = position[0] + 14, position[1] + (size[1] * 0.5) - (checkbox_height * 0.5) - 0.5, checkbox_height * 0.85
        self._start_x,  self._end_x, self._circle_y = checkbox_x + 1, checkbox_x + (checkbox_width * 0.38), checkbox_y + (checkbox_height * 0.5) - (circle_size * 0.5) - 0.5
        self._is_checked = bs.app.config.get(self._config_key, False)
        initial_x, initial_color = (self._end_x, (0.0, 1.0, 0.0)) if self._is_checked else (self._start_x, (1.0, 0.0, 0.0))
        text_x, text_y = checkbox_x + checkbox_width + 10, position[1] + (size[1] * 0.5)
        self._button = bs.buttonwidget(parent=parent, position=position, size=size, button_type='regular', label='', texture=bs.gettexture('empty'), on_activate_call=self._toggle_state)
        self.background = bs.imagewidget(parent=parent, position=(position[0] * 1.005, position[1] * 0.99), size=(size[0] * 0.825, size[1] * 1.3), draw_controller=self._button, opacity=0.7, texture=bs.gettexture('scrollWidget'))
        self.check_background = bs.imagewidget(parent=parent, position=(checkbox_x, checkbox_y), size=(checkbox_width, checkbox_height), draw_controller=self._button, color=(0.0, 0.0, 0.0), texture=bs.gettexture('chestIconEmpty'))
        self._dot = bs.imagewidget(parent=parent, position=(initial_x, self._circle_y), size=(circle_size, circle_size), draw_controller=self._button, color=initial_color, texture=bs.gettexture('nub'))
        self._text = bs.textwidget(parent=parent, position=(text_x, text_y), size=(0, 0), draw_controller=self._button, h_align='left', v_align='center', scale=0.85, text=display_text, maxwidth=size[0] * 0.7, color=(0.9, 0.9, 0.9))
        self._widgets.extend([self._button, self.background, self.check_background, self._dot, self._text])

    def _start_animation(self, target_checked: bool) -> None:
        self._is_animating = True
        self._animation_start_time = time.time()
        self._target_checked = target_checked
        self._start_color = self._get_current_color()
        self._animate()

    def _get_current_color(self) -> tuple[float, float, float]:
        if self._is_checked: return (0.0, 1.0, 0.0)
        else: return (1.0, 0.0, 0.0)

    def _get_target_color(self) -> tuple[float, float, float]:
        if self._target_checked: return (0.0, 1.0, 0.0)
        else: return (1.0, 0.0, 0.0)

    def _animate(self) -> None:
        if not self._is_animating: return
        elapsed, duration = time.time() - self._animation_start_time, 0.25
        if elapsed >= duration: self._is_animating = False; progress = 1.0
        else: progress = elapsed / duration; progress = progress * progress * (3.0 - 2.0 * progress); bs.apptimer(0.01, self._animate)
        if self._target_checked: current_x = self._start_x + (self._end_x - self._start_x) * progress
        else: current_x = self._end_x - (self._end_x - self._start_x) * progress
        start_r, start_g, start_b = self._start_color
        target_r, target_g, target_b = self._get_target_color()
        current_r = start_r + (target_r - start_r) * progress
        current_g = start_g + (target_g - start_g) * progress
        current_b = start_b + (target_b - start_b) * progress
        current_color = (current_r, current_g, current_b)
        bs.imagewidget(edit=self._dot, position=(current_x, self._circle_y), color=current_color)

        if not self._is_animating:
            self._is_checked = self._target_checked
            final_x = self._end_x if self._is_checked else self._start_x
            final_color = (0.0, 1.0, 0.0) if self._is_checked else (1.0, 0.0, 0.0)
            bs.imagewidget(edit=self._dot, position=(final_x, self._circle_y), color=final_color)
            if self._on_value_change: self._on_value_change(self._is_checked)

    def sync_from_config(self) -> None:
        current = bs.app.config.get(self._config_key, False)
        if current == self._is_checked: return
        self._is_checked, self._is_animating, final_x, final_color = current, False, self._end_x if current else self._start_x, (0.0, 1.0, 0.0) if current else (1.0, 0.0, 0.0)
        try: bs.imagewidget(edit=self._dot, position=(final_x, self._circle_y), color=final_color)
        except: pass

    def delete(self) -> None:
        for widget in self._widgets:
            try: widget.delete()
            except Exception: pass
        self._widgets.clear()

    def _toggle_state(self) -> None:
        current_value = bs.app.config.get(self._config_key, False)
        new_value = not current_value
        bs.app.config[self._config_key] = new_value; bs.app.config.commit()
        self._start_animation(new_value)

# •━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━•

class InventoryWindow:
    class TabID(Enum):
        PROFILES = 'profiles'
        CHARACTERS = 'characters'
        ICONS = 'icons'
        MAPS = 'maps'
        MINIGAMES = 'mini-games'
        ITEMS = 'items'

    DEFAULT_CHARS = ['Spaz', 'Zoe', 'Snake Shadow', 'Kronk', 'Mel', 'Jack Morgan', 'Santa Claus', 'Frosty', 'Bones', 'Bernard', 'Pascal', 'Taobao Mascot', 'B-9000', 'Agent Johnson', 'Grumbledorf', 'Pixel', 'Easter Bunny', 'Zola', 'OldLady']
    CHARACTER_INFO = {
        'Spaz':                          ('Spaz', 'The one and only, always ready.'),
        'Zoe':                            ('Zoe', 'Quick as a whip, and twice as clever.\nNever left Sal behind her.'),
        'Kronk':                        ('Kronk', 'Big Gloves, bigger heart.'),
        'Mel':                            ('Mel', 'Sweet on the outside, deadly on the inside.'),
        'Snake Shadow':       ('Snake Shadow', 'Silent as the night. You never see him coming.'),
        'Jack Morgan':          ('Jack Morgan', 'A classic man. Fights like the old days.'),
        'Santa Claus':            ('Santa Claus', 'Ho ho ho.\nHe knows when you have been bad.'),
        'Frosty':                       ('Frosty', 'Cold hands. Colder heart.'),
        'Bones':                       ('Bones', 'Not much left of him, but he still fights.'),
        'Bernard':                    ('Bernard', 'Warm, fuzzy, slow to anger, impossible to dodge, and\n built like a wall. Do not let the softness fool you!'),
        'Pascal':                      ('Pascal', 'Quiet little penguin. Hides in the terminal. \n strikes without warning!.'),
        'Taobao Mascot':    ('Taobao Mascot', 'Straight from the shopping aisles.'),
        'B-9000':                     ('B-9000', 'Beep boop. an old robot before ai gen. \n Resistance is futile.'),
        'Agent Johnson':      ('Agent Johnson', 'Top secret. You did not see him here.'),
        'Grumbledorf':          ('Grumbledorf', 'An old wizard with a short temper and a long beard.\n Best not to disturb him.'),
        'Pixel':                          ('Pixel', 'A little fly of pure fury.'),
        'Easter Bunny':          ('Easter Bunny', 'Fluffy, fast, and jump higher then anyone and full\n of surprises. Nobody expects the rabbit.'),
        'OldLady':                   ('OldLady', 'Waiting for death to finally show up.\n Until then, she fights.'),
        'Zola':                          ('Zola', 'A man with quick hands. Check your pockets! \nYour 300 token may or may not still be there.')}

    ICON_INFO = {
        'LOGO_FLAT':                                                         ('Flat Logo', 'The old logo, laid flat.'),
        'TOKEN':                                                                  ('Token', 'A coin, they said.'),
        'LOGO':                                                                     ('Logo', 'The default logo of the game. Old as the hills.'),
        'TICKET':                                                                  ('Ticket', 'tickets? for something.'),
        'GOOGLE_PLAY_GAMES_LOGO':                     ('Google Play Games', 'Google Play Games.'),
        'V2_LOGO':                                                             ('V2 Logo', 'The new style of login. Default logo for V2 accounts.'),
        'GAME_CENTER_LOGO':                                    ('Game Center', "Apple's way of login?\n already deleted how did your get it?"),
        'GAME_CIRCLE_LOGO':                                      ('GameCircle', "Amazon's way of login?\n already deleted how did your get it?"),
        'OCULUS_LOGO':                                                  ('Oculus', 'VR headsets way of login?'),
        'STEAM_LOGO':                                                    ('Steam', 'Valve store way of login.'),
        'NVIDIA_LOGO':                                                    ('NVIDIA', 'fake and expensive.'),
        'TEST_ACCOUNT':                                               ('Test Account', 'For the testers.\n hello there the world is over.'),
        'TICKET_BACKING':                                             ('Ticket Backing', "weird that shouldn't exist here."),
        'LOCAL_ACCOUNT':                                            ('Local Account', 'localy way of auto login, not stable.'),
        'EXPLODINARY_LOGO':                                      ('Explodinary', 'wierd smile logo.'),
        'FEDORA':                                                                ('Fedora', 'Proper hat, brown hat?'),
        'HAL':                                                                       ('HAL', 'That red eye. Watching you!'),
        'CROWN':                                                                ('Crown', 'Crown for those who deserve.'),
        'YIN_YANG':                                                           ('Yin Yang', 'Two halves, forever turning, one mean.'),
        'EYE_BALL':                                                            ('Eye Ball', 'Just an eye.'),
        'SKULL':                                                                   ('Skull', 'of someone your lose...'),
        'HEART':                                                                  ('Heart', 'For those you care about.'),
        'DRAGON':                                                              ('Dragon', 'A dragon icon. Given to those who deserve it.'),
        'HELMET':                                                              ('Helmet', "A knight's helm."),
        'MUSHROOM':                                                      ('Mushroom', 'A red mushroom.'),
        'NINJA_STAR':                                                      ('Ninja Star', 'A shuriken. Quiet and sharp.'),
        'VIKING_HELMET':                                              ('Viking Helmet', 'Horned and ready.'),
        'MOON':                                                                  ('Moon', 'A crescent, glowing soft.'),
        'SPIDER':                                                                 ('Spider', 'Eight legs, one web.'),
        'FIREBALL':                                                             ('Fireball', 'A ball of fire. Do not touch.'),
        'MIKIROG':                                                              ('Mikirog', 'A name that means something to someone.'),
        'SANTA_HAT':                                                       ('Santa Hat', 'A festive red cap.'),
        'POTATO':                                                               ('Potato', 'A potato. Yes, a potato but expansive.'),
        'PALM_TREE':                                                        ('Palm Tree', 'A Tree.'),
        'BOXING_GLOVE':                                                ('Boxing Glove', 'For a fight, fair or not.'),
        'OUYA_BUTTON_O':                                            ('Ouya O', 'The O button of the Ouya.'),
        'OUYA_BUTTON_U':                                            ('Ouya U', 'The U button of the Ouya.'),
        'OUYA_BUTTON_Y':                                            ('Ouya Y', 'The Y button of the Ouya.'),
        'OUYA_BUTTON_A':                                            ('Ouya A', 'The A button of the Ouya.'),

        'FLAG_POLAND':                                                 ('Poland', 'A flag of Poland.'),
        'FLAG_ARGENTINA':                                          ('Argentina', 'A flag of Argentina.'),
        'FLAG_IRAN':                                                        ('Iran', 'A flag of Iran.'),
        'FLAG_PHILIPPINES':                                         ('Philippines', 'A flag of the Philippines.'),
        'FLAG_CHILE':                                                      ('Chile', 'A flag of Chile.'),
        'FLAG_UNITED_STATES':                                  ('United States', 'A flag of the United States.'),
        'FLAG_UNITED_KINGDOM':                             ('United Kingdom', 'A flag of the United Kingdom.'),
        'FLAG_RUSSIA':                                                    ('Russia', 'A flag of Russia.'),
        'FLAG_MEXICO':                                                  ('Mexico', 'A flag of Mexico.'),
        'FLAG_ITALY':                                                       ('Italy', 'A flag of Italy.'),
        'FLAG_GERMANY':                                             ('Germany', 'A flag of Germany.'),
        'FLAG_JAPAN':                                                    ('Japan', 'A flag of Japan.'),
        'FLAG_CHINA':                                                     ('China', 'A flag of China.'),
        'FLAG_BRAZIL':                                                    ('Brazil', 'A flag of Brazil.'),
        'FLAG_CANADA':                                                 ('Canada', 'A flag of Canada.'),
        'FLAG_INDIA':                                                       ('India', 'A flag of India.'),
        'FLAG_FRANCE':                                                  ('France', 'A flag of France.'),
        'FLAG_INDONESIA':                                            ('Indonesia', 'A flag of Indonesia.'),
        'FLAG_SOUTH_KOREA':                                     ('South Korea', 'A flag of South Korea.'),
        'FLAG_NETHERLANDS':                                    ('Netherlands', 'A flag of the Netherlands.'),
        'FLAG_UNITED_ARAB_EMIRATES':                ('United Arab Emirates', 'A flag of the UAE.'),
        'FLAG_QATAR':                                                     ('Qatar', 'A flag of Qatar.'),
        'FLAG_EGYPT':                                                     ('Egypt', 'A flag of Egypt.'),
        'FLAG_KUWAIT':                                                   ('Kuwait', 'A flag of Kuwait.'),
        'FLAG_ALGERIA':                                                  ('Algeria', 'A flag of Algeria.'),
        'FLAG_SAUDI_ARABIA':                                      ('Saudi Arabia', 'A flag of Saudi Arabia.'),
        'FLAG_MALAYSIA':                                              ('Malaysia', 'A flag of Malaysia.'),
        'FLAG_CZECH_REPUBLIC':                               ('Czech Republic', 'A flag of the Czech Republic.'),
        'FLAG_AUSTRALIA':                                            ('Australia', 'A flag of Australia.'),
        'FLAG_SINGAPORE':                                           ('Singapore', 'A flag of Singapore.')}

    MINIGAME_INFO = {
        'Easter Egg Hunt':      ('Easter Egg Hunt',    'Gather eggs!',                                                     'towerDPreview'),
        'Meteor Shower':        ('Meteor Shower',     'Dodge the falling bombs.',                              'thePadPreview'),
        'Ninja Fight':                 ('Ninja Fight',              'How fast can you defeat the ninjas?',          'courtyardPreview'),
        'Onslaught':                  ('Onslaught',               'Defeat all enemies.',                                          'doomShroomPreview'),
        'Race':                            ('Race',                         'Run real fast!',                                                     'bigGPreview'),
        'Runaround':                 ('Runaround',              'Prevent enemies from reaching the exit.',  'towerDPreview'),
        'Target Practice':        ('Target Practice',      'Bomb as many targets as you can.',            'doomShroomPreview'),
    }

    TARGET_MAP = 'Lake Frigid'
    TARGET_MAP_PLAYTYPE = 'melee'
    TARGET_MAP_DESCRIPTION = 'frozen Lake behind trees'

    def __init__(self):
        for name in ('_root_widget', '_close_button', '_scroll_widget', '_profile_container', '_activity', '_selected_profile_name', '_refresh_timer', '_no_profiles_text', '_rotate_checkbox', '_light_checkbox', '_rotate_switch', '_light_switch',
                  '_editor_container', '_character_button', '_color_button', '_highlight_button', '_upgrade_button', '_delete_button', '_profile_name_text', '_icon_button', '_icon_button_label', '_icon_text_label', '_create_button', '_up_button', '_down_button',
                  '_tab_row', '_tab_scroll', '_tab_container', '_selected_char_name', '_selected_icon_glyph', '_selected_minigame_name', '_selected_map_name', '_selected_item_name'): setattr(self, name, None)
        for name in ('_profile_widgets', '_profile_only_widgets', '_char_widgets', '_icon_widgets', '_map_widgets', '_minigame_widgets', '_item_widgets', '_big_icon_preview_widgets'): setattr(self, name, [])
        for name in ('_char_row_widgets', '_map_row_widgets', '_minigame_row_widgets', '_item_row_widgets', '_item_widgets_map'): setattr(self, name, {})
        for name in ('_is_closing', '_editor_visible', '_pending_new_profile', '_profile_ui_built'): setattr(self, name, False)
        for name in ('_last_name', '_new_profile_name', '_tmp_name'): setattr(self, name, "")
        self._current_tab = InventoryWindow.TabID.PROFILES
        self._r = "inventory"
        self._item_refresh_timer = None

    def getname(self) -> str:
        if self._pending_new_profile: return temporary_account_name
        session = ba.get_foreground_host_session()
        if session:
            activity = session.getactivity()
            if activity and hasattr(activity, 'get_selected_profile'): return activity.get_selected_profile()
        return ""

    def reload_window(self) -> None:
        profiles, session = bs.app.config.get('Player Profiles', {}), ba.get_foreground_host_session()
        if session:
            activity = session.getactivity()
            if activity and hasattr(activity, 'get_selected_profile'):
                profile_name = activity.get_selected_profile()
                if profile_name:
                    if profile_name in profiles:
                        is_global = profiles[profile_name].get('global', False)
                        if is_global:
                            if hasattr(activity, '_selected_profile'):
                                activity._selected_profile = profile_name

        self._show_profiles(); self._update_editor_ui()
        bs.getsound('gunCocking').play()

    def save(self, transition_out: bool = True) -> bool:
        try:
            self._save_current_profile(True)
            if self._profile_name_text: self._save_name(True)
            if transition_out: bs.getsound('gunCocking').play()
            return True
        except Exception as e: print(f"Error saving profile: {e}"); return False

    def create_styled_button(self, position: tuple, size: tuple, label: str, callback: callable = None, color: tuple = (0.3, 0.8, 0.5), button_text: str = None) -> None:
        parent, (x, y) = self._sub_container, position; w, h = size 
        button = bs.buttonwidget(parent=parent, position=position, size=size, label='', on_activate_call=callback if callback else None, autoselect=True, button_type='square', texture=bs.gettexture('empty'))
        background = bs.imagewidget(parent=parent, size=(w, h), color=color, position=(x, y), opacity=1.5, texture=bs.gettexture('scrollWidgetGlow'))
        lbl = bs.textwidget(parent=parent, position=(x + (w/2.5) * 0.25, y + h/2.5), text=label, scale=1.05, h_align='center', v_align='center')
        if button_text: bt = bs.textwidget(parent=parent, position=(x + (w/2.5) * 0.25, y), text=button_text, scale=0.6, h_align='center', v_align='center'); self._profile_only_widgets.append(bt)
        self._profile_only_widgets.extend([button, background, lbl])
        return button

    def create_window(self, transition: str | None = 'in_right', origin_widget: bs.Widget | None = None):
        screen_width, screen_height = bs.get_virtual_screen_size()
        self._screen_width, self._screen_height = screen_width, screen_height
        self._root_widget = bs.containerwidget(size=(screen_width, screen_height), background=False)
        self.set_session()
        ba.apptimer(2.3 if enable_ui_animation else 0.1, ba.CallPartial(self._build_ui))
        return MainWindow(self._root_widget, transition=transition, origin_widget=origin_widget)

    def _build_ui(self):
        if self._is_closing: return
        screen_width, screen_height = self._screen_width, self._screen_height
        ui_width, ui_height, close_size = screen_width * 0.35, screen_height * 0.85, 50; inset = ui_width * 0.02
        self._sub_container = sub_container = bs.containerwidget(parent=self._root_widget, size=(screen_width, screen_height), background=False)
        close_x, close_y = ui_width - close_size - 10, ui_height - close_size + screen_height * 0.1; self._close_y = close_y
        self._close_button = bs.buttonwidget(parent=sub_container, position=(10, close_y * 1.04), size=(close_size, close_size), label='✕', color=(0.6, 0.5, 0.6), textcolor=(1, 1, 1), on_activate_call=self._close_window, autoselect=True, button_type='square')
        self._build_profile_only_widgets(); TabID = InventoryWindow.TabID
        tab_scroll_width, tab_scroll_height, tab_scroll_x, tab_scroll_y = ui_width - inset * 2, ui_height * 0.08, inset * 2, ui_height - inset * 2
        scroll_x, scroll_y, scroll_width, scroll_height = inset * 2, ui_height * 0.08, ui_width - inset * 2, ui_height - inset * 2 - ui_height * 0.08
        self._tab_scroll = bs.hscrollwidget(parent=sub_container, size=(tab_scroll_width, tab_scroll_height), position=(tab_scroll_x, tab_scroll_y), highlight=False, background=False, capture_arrows=False, border_opacity=0.85)
        tab_container_width = tab_scroll_width * 1.2
        self._tab_container = bs.containerwidget(parent=self._tab_scroll, size=(tab_scroll_width * 1.65, tab_scroll_height), background=False)
        self._tab_row = TabRow(self._tab_container, [(TabID.PROFILES, 'Profiles'), (TabID.CHARACTERS, 'Characters'), (TabID.ICONS, 'Icons'), (TabID.MAPS, 'Maps'), (TabID.MINIGAMES, 'Mini-games'), (TabID.ITEMS, 'Items')], idprefix='inventory_tabs', size=(tab_scroll_width * 1.65, tab_scroll_height), pos=(0, 0), on_select_call=ba.WeakCallPartial(self._on_tab_select))
        try: self._tab_row.update_appearance(TabID.PROFILES)
        except: pass

        self._scroll_widget = bs.scrollwidget(parent=sub_container, size=(scroll_width, scroll_height), position=(scroll_x, scroll_y), simple_culling_v=10.0, selection_loops_to_parent=True, highlight=False, background=False, border_opacity=0.85)
        self._container_width, self._container_height = scroll_width - inset, scroll_height - inset
        self._profile_container = bs.containerwidget(parent=self._scroll_widget, size=(scroll_width - inset, scroll_height - inset), background=False)
        self._show_profiles()
        self._start_refresh_timer()

    def _build_profile_only_widgets(self):
        if self._profile_ui_built: self._destroy_profile_widgets()
        screen_width, screen_height = bs.get_virtual_screen_size()
        sub_container, close_y, self._profile_ui_built, x_fix = self._sub_container, self._close_y, True, 0.45
        button_size, button_x, button_y, create_y_offset = (60, 60), screen_width * x_fix * 0.8, screen_height * 0.2, screen_height * 0.52
        self._rotate_switch = self._create_switch(parent=sub_container, position=(screen_width * x_fix * 0.8, close_y - screen_height * 0.25), size=(150, 30), config_key='rotate_enabled', display_text='Rotate', on_value_change=self._on_rotation_toggle)
        for widget in self._rotate_switch._widgets: self._profile_only_widgets.append(widget)
        self._light_switch = self._create_switch(parent=sub_container, position=(screen_width * x_fix * 0.8, close_y - screen_height * 0.32), size=(150, 30), config_key='light_enabled', display_text='Light', on_value_change=self._on_light_toggle)
        for widget in self._light_switch._widgets: self._profile_only_widgets.append(widget); self._fix_auto_off()
        self._create_button = self.create_styled_button(position=(button_x, button_y + create_y_offset), size=button_size, label='+', callback=self._create_profile, color=(0.3, 0.8, 0.5), button_text='create')
        self._up_button = self.create_styled_button(position=(button_x, button_y), size=button_size, label='↑', callback=self._move_selected_up, color=(0.3, 0.8, 0.5), button_text='up')
        self._down_button = self.create_styled_button(position=(button_x, button_y - screen_height * 0.1), size=button_size, label='↓', callback=self._move_selected_down, color=(0.3, 0.8, 0.5), button_text='down')
        self._create_editor_ui(sub_container)

    def _fix_auto_off(self):
        try: bs.app.config['rotate_enabled'] = False; bs.app.config['light_enabled'] = False; bs.app.config.commit()
        except: pass
        for switch in (self._rotate_switch, self._light_switch):
            if switch is None: continue
            try: switch._is_checked, switch._is_animating = False, False; final_x = switch._start_x; final_color = (1.0, 0.0, 0.0); bs.imagewidget(edit=switch._dot, position=(final_x, switch._circle_y), color=final_color)
            except: pass
        session = ba.get_foreground_host_session()
        if session:
            activity = session.getactivity()
            if activity:
                try:
                    if hasattr(activity, 'toggle_camera_rotation'): bs.pushcall(ba.CallPartial(activity.toggle_camera_rotation, False))
                    if hasattr(activity, 'toggle_character_light'): bs.pushcall(ba.CallPartial(activity.toggle_character_light, False))
                except: pass

    def _destroy_profile_widgets(self):
        self._profile_ui_built = False; self._delete_icon_button()
        if self._upgrade_button:
            try: self._upgrade_button.delete()
            except: pass
            self._upgrade_button = None
        if self._delete_button:
            try: self._delete_button.delete()
            except: pass
            self._delete_button = None
        if self._editor_container:
            try: self._editor_container.delete()
            except: pass
            self._editor_container = None
        for name in ('_character_button', '_color_button', '_highlight_button', '_profile_name_text'): setattr(self, name, None)
        if self._rotate_switch:
            try: self._rotate_switch.delete()
            except: pass
            self._rotate_switch = None
        if self._light_switch:
            try: self._light_switch.delete()
            except: pass
            self._light_switch = None

        for widget in self._profile_only_widgets:
            try: widget.delete()
            except: pass
        self._profile_only_widgets = []
        for name in ('_create_button', '_up_button', '_down_button'): setattr(self, name, None)

    def _on_tab_select(self, tab_id):
        self._switch_tab(tab_id)

    def _switch_tab(self, tab_id):
        if self._is_closing: return
        self._current_tab = tab_id
        try: self._tab_row.update_appearance(tab_id)
        except Exception: pass
        self._save_name(True); self._save_current_profile(True)
        TabID = InventoryWindow.TabID; show_profiles = (tab_id == TabID.PROFILES)
        for widgets_list in (self._profile_widgets, self._char_widgets, self._icon_widgets, self._map_widgets, self._minigame_widgets, self._item_widgets):
            for widget in widgets_list:
                try: widget.delete()
                except: pass
            widgets_list.clear()

        self._char_row_widgets = self._map_row_widgets = {}
        self._minigame_row_widgets = self._item_row_widgets = {}
        self._item_widgets_map = {}
        self._item_refresh_timer = None
        if self._no_profiles_text:
            try: self._no_profiles_text.delete()
            except: pass
            self._no_profiles_text = None

        self._clear_big_icon_preview()
        if show_profiles: self._restore_spaz(); self._build_profile_only_widgets(); self._show_profiles(); self._update_editor_ui()
        else:
            self._destroy_profile_widgets(); self._disable_rotate_and_light(); self._hide_spaz()
            if tab_id == TabID.CHARACTERS: self._show_characters()
            elif tab_id == TabID.ICONS: self._show_icons()
            elif tab_id == TabID.MAPS: self._show_maps()
            elif tab_id == TabID.MINIGAMES: self._show_minigames()
            elif tab_id == TabID.ITEMS: self._show_items()

    def _hide_spaz(self):
        session = ba.get_foreground_host_session()
        if not session: return
        activity = session.getactivity()
        if not activity: return
        try:
            if hasattr(activity, 'spaz') and activity.spaz is not None:
                try:
                    if hasattr(activity.spaz, 'node') and activity.spaz.node: activity.spaz.node.delete()
                except: pass
                try: activity.spaz = None
                except: pass
        except Exception as e:
            print(f"[ ! ] Error on-remove spaz: {e}")

    def _restore_spaz(self):
        session = ba.get_foreground_host_session()
        if not session: return
        activity = session.getactivity()
        if not activity: return
        try:
            profile_name = None
            if hasattr(activity, 'get_selected_profile'): profile_name = activity.get_selected_profile()
            if profile_name:
                profiles = bs.app.config.get('Player Profiles', {})
                if profile_name in profiles:
                    info = profiles[profile_name]
                    if 'character' in info: activity.character = info['character']
                    classic = bs.app.classic
                    if classic:
                        try: activity.color, activity.highlight = classic.get_player_profile_colors(profile_name)
                        except: pass
        except Exception as e:
            print(f"[ ! ] Error reloading profile character: {e}")

        try:
            if hasattr(activity, 'spawn_character'): bs.pushcall(ba.CallPartial(activity.spawn_character))
        except Exception as e: print(f"Error restoring spaz: {e}")

    def _disable_rotate_and_light(self):
        try: bs.app.config['rotate_enabled'] = False; bs.app.config['light_enabled'] = False; bs.app.config.commit()
        except: pass
        session = ba.get_foreground_host_session()
        if session:
            activity = session.getactivity()
            if activity:
                try:
                    if hasattr(activity, 'toggle_camera_rotation'): bs.pushcall(ba.CallPartial(activity.toggle_camera_rotation, False))
                    if hasattr(activity, 'toggle_character_light'): bs.pushcall(ba.CallPartial(activity.toggle_character_light, False))
                except: pass

    def _show_characters(self):
        if self._is_closing: return
        if not self._profile_container: return
        classic = bs.app.classic
        if classic is None: return
        screen_width, screen_height = bs.get_virtual_screen_size()
        all_chars = spazappearance.get_appearances()
        chars_to_show = [c for c in all_chars if c in InventoryWindow.DEFAULT_CHARS]
        chars_to_show.sort()

        if not chars_to_show:
            no_characters = bs.textwidget(parent=self._profile_container, position=(self._container_width // 2 * 0.85, self._container_height // 2), text="No Characters", h_align='center', v_align='center', scale=0.95, color=(0.7, 0.7, 0.7), selectable=False); self._char_widgets.append(no_characters)
            try: bs.containerwidget(edit=self._profile_container, size=(self._container_width, self._container_height))
            except: pass
            return
        if self._selected_char_name not in chars_to_show: self._selected_char_name = chars_to_show[-1]

        try: SoundManager.play_character_sound(self._selected_char_name)
        except Exception: pass
        try:
            session = ba.get_foreground_host_session()
            activity = session.getactivity() if session else None
            if activity and hasattr(activity, 'spawn_character'):
                activity.character = self._selected_char_name
                bs.pushcall(ba.CallPartial(activity.spawn_character))
        except: pass

        y_pos, spacing, sub_scroll_width = 5, 70, self._container_width
        card_w, card_h = sub_scroll_width * 0.95, 60
        self._char_row_widgets = {}
        for char_name in chars_to_show:
            appearance, crosshair = classic.spaz_appearances.get(char_name), None
            if appearance is None: continue
            is_selected = (char_name == self._selected_char_name)
            row = bs.containerwidget(parent=self._profile_container, size=(card_w, card_h), position=(sub_scroll_width * 0.025, y_pos), background=False)
            self._char_widgets.append(row)
            background_color, background_opacity = ((0.2, 0.63, 0.5), 0.45) if is_selected else ((0, 0, 0), 0.25)
            background = bs.imagewidget(parent=row, texture=bs.gettexture('white'), opacity=background_opacity, position=(-5, 10), size=(card_w, card_h * 1.08), color=background_color); self._char_widgets.append(background)
            icon = bs.imagewidget(parent=row, position=(5, 25), size=(35, 35), texture=bs.gettexture(appearance.icon_texture), tint_color=(1, 1, 1), tint2_color=(1, 1, 1)); self._char_widgets.append(icon)
            name_w = bs.textwidget(parent=row, position=(50, 38), size=(200, 25), text=char_name, h_align='left', v_align='center', scale=0.85, color=(0.9, 0.9, 0.9), selectable=False); self._char_widgets.append(name_w)
            if is_selected: crosshair = bs.imagewidget(parent=row, texture=bs.gettexture('achievementCrossHair'), position=(card_w * 0.85, card_h * 0.39), size=(40, 40), color=(0.3, 0.8, 1.0)); self._char_widgets.append(crosshair)
            button = bs.buttonwidget(parent=row, position=(0, 0), size=(card_w, card_h), label='', color=(0, 0, 0), texture=bs.gettexture('empty'), button_type='square', on_activate_call=ba.CallPartial(self._on_character_row_press, char_name)); self._char_widgets.append(button)
            self._char_row_widgets[char_name] = (row, background, crosshair)
            y_pos += spacing
        try: bs.containerwidget(edit=self._profile_container, size=(sub_scroll_width + 20, y_pos + 10))
        except: pass

        try:
            if self._selected_char_name: self._show_character_preview(self._selected_char_name)
        except: pass

    def _on_character_row_press(self, char_name: str):
        if self._is_closing: return
        prev = self._selected_char_name
        if prev != char_name:
            if prev in self._char_row_widgets:
                _, old_bg, old_cross = self._char_row_widgets[prev]
                try: bs.imagewidget(edit=old_bg, color=(0, 0, 0), opacity=0.25)
                except: pass
                if old_cross is not None:
                    try: old_cross.delete()
                    except: pass
                    self._char_row_widgets[prev] = (self._char_row_widgets[prev][0], self._char_row_widgets[prev][1], None)
            self._selected_char_name = char_name
            if char_name in self._char_row_widgets:
                row, bg, cross = self._char_row_widgets[char_name]
                try: bs.imagewidget(edit=bg, color=(0.2, 0.63, 0.5), opacity=0.45)
                except: pass
                if cross is None:
                    try:
                        card_w, card_h = self._container_width * 0.95, 60
                        cross = bs.imagewidget(parent=row, texture=bs.gettexture('achievementCrossHair'), position=(card_w * 0.85, card_h * 0.39), size=(40, 40), color=(0.3, 0.8, 1.0))
                        self._char_widgets.append(cross)
                        self._char_row_widgets[char_name] = (row, bg, cross)
                    except: pass
        try: SoundManager.play_character_sound(char_name)
        except Exception: pass
        session = ba.get_foreground_host_session()
        if not session: return
        activity = session.getactivity()
        if not activity or not hasattr(activity, 'spawn_character'): return
        try: activity.character = char_name; activity.spawn_character()
        except Exception: pass
        self._show_character_preview(char_name)

    def _show_character_preview(self, char_name: str):
        self._clear_big_icon_preview()
        try:
            info = InventoryWindow.CHARACTER_INFO.get(char_name)
            if info: name, desc = info
            else: name, desc = char_name, 'weird character that no one know yet...' 
            text_bg_w, text_bg_h, cx = 320 * 1.3, 100 * 1.3, self._screen_width * 0.72
            text_bg = bs.imagewidget(parent=self._sub_container, position=(cx - text_bg_w / 2, self._screen_height * 0.20 - (text_bg_h - 100) / 2), size=(text_bg_w, text_bg_h), color=(0.2, 0.63, 0.5), opacity=0.75, texture=bs.gettexture('scrollWidgetGlow')); self._big_icon_preview_widgets.append(text_bg)
            name_w = bs.textwidget(parent=self._sub_container, position=(cx, self._screen_height * 0.285), size=(0, 0), text=name, h_align='center', v_align='center', scale=1.1, color=(0.9, 0.9, 0.9), maxwidth=400); self._big_icon_preview_widgets.append(name_w)
            if desc: desc_w = bs.textwidget(parent=self._sub_container, position=(cx, self._screen_height * 0.245), size=(0, 0), text=desc, h_align='center', v_align='top', scale=0.65, color=(0.75, 0.75, 0.75), maxwidth=400); self._big_icon_preview_widgets.append(desc_w)
        except Exception as e:
            print(f"[ ! ] Error showing character preview: {e}")

    def _show_icons(self):
        if self._is_closing: return
        if not self._profile_container: return
        icon_entries = self._collect_icons()
        if not icon_entries:
            no_icon = bs.textwidget(parent=self._profile_container, position=(self._container_width // 2 * 0.85, self._container_height // 2), text="No Icons", h_align='center', v_align='center', scale=0.95, color=(0.7, 0.7, 0.7), selectable=False)
            self._icon_widgets.append(no_icon)
            try: bs.containerwidget(edit=self._profile_container, size=(self._container_width, self._container_height))
            except Exception: pass
            return
 
        sub_scroll_width, cols, gap = self._container_width, 4, 8
        cell = (sub_scroll_width - 20 - (cols - 1) * gap) / cols
        cell_height = cell
        total_rows = (len(icon_entries) + cols - 1) // cols
        top = max(self._container_height, total_rows * (cell_height + gap) + 20)
        for i, entry in enumerate(icon_entries):
            glyph, name, desc = entry
            row = i // cols; col = i % cols
            x, y = 2.5 + col * (cell + gap), top - (row + 1) * (cell_height + gap)
            button = bs.buttonwidget(parent=self._profile_container, position=(x, y), size=(cell, cell_height), label=glyph, color=(0.6, 0.5, 0.6), button_type='square', text_scale=1.8, on_activate_call=ba.CallPartial(self._on_icon_cell_press, glyph, name, desc))
            self._icon_widgets.append(button)

        try: bs.containerwidget(edit=self._profile_container, size=(sub_scroll_width, top))
        except: pass
        if icon_entries:
            target_glyph, entry = self._selected_icon_glyph, None
            for e in icon_entries:
                if e[0] == target_glyph: entry = e; break
            if entry is None: entry = icon_entries[0]
            self._selected_icon_glyph = entry[0]
            self._on_icon_cell_press(entry[0], entry[1], entry[2])

    def _collect_icons(self):
        result = []
        try:
            classic = bs.app.classic
            if classic is not None:
                icons = [bs.charstr(bs.SpecialChar.LOGO)]
                try: icons.extend(list(classic.accounts.get_purchased_icons()))
                except Exception as e: print(f"[ ! ] get_purchased_icons error: {e}")

                seen = set()
                for glyph in icons:
                    if glyph in seen: continue
                    seen.add(glyph)
                    name, desc = self._lookup_icon_info(glyph)
                    result.append((glyph, name, desc))
        except Exception as e:print(f"[ ! ] collect icons error: {e}")
        return result

    def _lookup_icon_info(self, glyph: str):
        try:
            from babase._mgen.enums import SpecialChar
            for member in SpecialChar:
                try:
                    if bs.charstr(member) == glyph:
                        key = member.name
                        if key in InventoryWindow.ICON_INFO: return InventoryWindow.ICON_INFO[key]
                        return (key.replace('_', ' ').title(), '')
                except: continue
        except: pass
        return ('', '')

    def _on_icon_cell_press(self, glyph: str, name: str, desc: str):
        self._clear_big_icon_preview()
        self._selected_icon_glyph = glyph
        try:
            cx, text_bg_w, text_bg_h = self._screen_width * 0.72, 320 * 1.3, 100 * 1.3
            big = bs.textwidget(parent=self._sub_container, position=(cx, self._screen_height * 0.45), size=(0, 0), text=glyph, h_align='center', v_align='center', scale=8.0, color=(1, 1, 1), maxwidth=400); self._big_icon_preview_widgets.append(big) 
            text_bg = bs.imagewidget(parent=self._sub_container, position=(cx - text_bg_w / 2, self._screen_height * 0.20 - (text_bg_h - 100) / 2), size=(text_bg_w, text_bg_h), color=(0.2, 0.63, 0.5), opacity=0.75, texture=bs.gettexture('scrollWidgetGlow'))
            self._big_icon_preview_widgets.append(text_bg)
            name_w = bs.textwidget(parent=self._sub_container, position=(cx, self._screen_height * 0.285), size=(0, 0), text=name, h_align='center', v_align='center', scale=1.1, color=(0.9, 0.9, 0.9), maxwidth=400); self._big_icon_preview_widgets.append(name_w)
            if desc: desc_w = bs.textwidget(parent=self._sub_container, position=(cx, self._screen_height * 0.245), size=(0, 0), text=desc, h_align='center', v_align='top', scale=0.65, color=(0.75, 0.75, 0.75), maxwidth=400); self._big_icon_preview_widgets.append(desc_w)
        except Exception as e:
            print(f"[ ! ] Error showing big icon: {e}")

    def _clear_big_icon_preview(self):
        for widget in self._big_icon_preview_widgets:
            try: widget.delete()
            except: pass
        self._big_icon_preview_widgets = []

    def _show_maps(self):
        if self._is_closing: return
        if not self._profile_container: return
        entries = []
        try:
            classic = bs.app.classic
            if classic is not None:
                maps = classic.getmaps(InventoryWindow.TARGET_MAP_PLAYTYPE)
                if InventoryWindow.TARGET_MAP in maps: entries.append((InventoryWindow.TARGET_MAP, InventoryWindow.TARGET_MAP_DESCRIPTION))
        except Exception as e:
            print(f"[ ! ] map lookup error: {e}")

        if not entries:
            no_maps = bs.textwidget(parent=self._profile_container, position=(self._container_width // 2 * 0.85, self._container_height // 2), text="No Maps", h_align='center', v_align='center', scale=0.95, color=(0.7, 0.7, 0.7), selectable=False); self._map_widgets.append(no_maps)
            try: bs.containerwidget(edit=self._profile_container, size=(self._container_width, self._container_height))
            except: pass
            return

        self._selected_map_name = entries[0][0]
        count, button_width, button_height, button_buffer_v = len(entries), 410, 155, 0; rows = count; grid_width = button_width; sub_width = max(grid_width, self._container_width)
        x_offset, sub_height = (sub_width - grid_width) * 0.5, (rows * (button_height + 2 * button_buffer_v) + 20)
        mesh_opaque, mesh_transparent, mask_tex = bs.getmesh('level_select_button_opaque'), bs.getmesh('level_select_button_transparent'), bs.gettexture('mapPreviewMask')

        index = 0
        for y in range(rows):
            if index >= count: break
            name, desc = entries[index]
            pos = (x_offset - 4, sub_height - 20 - (y + 1) * (button_height + 2 * button_buffer_v))
            button = bs.buttonwidget(parent=self._profile_container, button_type='square', size=(button_width, button_height), autoselect=True, label='', color=(0, 0, 0), texture=bs.gettexture('empty'), position=pos, on_activate_call=ba.CallPartial(self._on_map_card_press, name, desc)); self._map_widgets.append(button)

            try:
                maptype = ba.get_map_class(name); tex_name = maptype.get_preview_texture_name()
                if tex_name is None: raise RuntimeError('no preview texture')
                preview_img = bs.imagewidget(parent=self._profile_container, size=(button_width, button_height), position=pos, texture=bs.gettexture(tex_name), draw_controller=button, mesh_opaque=mesh_opaque, mesh_transparent=mesh_transparent, mask_texture=mask_tex); self._map_widgets.append(preview_img)
            except Exception as e:
                print(f"[ ! ] {name} Map preview error: {e}")
                try: fallback = bs.imagewidget(parent=self._profile_container, size=(button_width, button_height), position=pos, color=(0.55, 0.5, 0.6), draw_controller=btn, mesh_opaque=mesh_opaque, mesh_transparent=mesh_transparent, mask_texture=mask_tex); self._map_widgets.append(fallback)
                except: pass

            name_w = bs.textwidget(parent=self._profile_container, text=name, position=(pos[0] + button_width * 0.5, pos[1] + button_height * 0.5), size=(0, 0), scale=button_width * 0.0025, maxwidth=button_width * 0.7, draw_controller=button, h_align='center', v_align='center', color=(1, 1, 1)); self._map_widgets.append(name_w); index += 1
        try: bs.containerwidget(edit=self._profile_container, size=(sub_width, sub_height))
        except: pass
        last_name, last_desc = entries[-1];  self._selected_map_name = last_name; self._show_card_preview(last_name, last_desc, kind='map')

    def _on_map_card_press(self, name: str, desc: str):
        if self._is_closing: return
        self._selected_map_name = name
        bs.getsound('click01').play()
        self._show_card_preview(name, desc, kind='map')

    def _show_minigames(self):
        if self._is_closing: return
        if not self._profile_container: return
        entries = list(InventoryWindow.MINIGAME_INFO.values())
        if not entries:
            no_minigames = bs.textwidget(parent=self._profile_container, position=(self._container_width // 2 * 0.85, self._container_height // 2), text="No MiniGames", h_align='center', v_align='center', scale=0.95, color=(0.7, 0.7, 0.7), selectable=False)
            self._minigame_widgets.append(no_minigames)
            try: bs.containerwidget(edit=self._profile_container, size=(self._container_width, self._container_height))
            except: pass
            return

        if self._selected_minigame_name not in [e[0] for e in entries]:
            self._selected_minigame_name = entries[-1][0]

        count = len(entries)
        button_width, button_height, button_buffer_v = 410, 155, 5
        rows = count; grid_width = button_width
        sub_width = max(grid_width, self._container_width)
        x_offset = (sub_width - grid_width) * 0.5
        sub_height = rows * (button_height + 2 * button_buffer_v) + 20
        mesh_opaque = bs.getmesh('level_select_button_opaque')
        mesh_transparent = bs.getmesh('level_select_button_transparent')
        mask_tex = bs.gettexture('mapPreviewMask')

        self._minigame_row_widgets = {}
        self._minigame_widgets = []

        index = 0
        for y in range(rows):
            if index >= count: break
            name, desc, tex_name = entries[index]
            pos = (x_offset - 4, sub_height - 15 - (y + 1) * (button_height + 2 * button_buffer_v))

            button = bs.buttonwidget(parent=self._profile_container, button_type='square', size=(button_width, button_height), autoselect=True, label='', color=(0, 0, 0), texture=bs.gettexture('empty'), position=pos, on_activate_call=ba.CallPartial(self._on_card_press, name, desc, 'minigame'))
            self._minigame_widgets.append(button)

            try:
                preview_img = bs.imagewidget(parent=self._profile_container, size=(button_width, button_height), position=pos, texture=bs.gettexture(tex_name), draw_controller=button, mesh_opaque=mesh_opaque, mesh_transparent=mesh_transparent, mask_texture=mask_tex)
                self._minigame_widgets.append(preview_img)
            except Exception as e:
                print(f"[ ! ] {name} MiniGame preview error: {e}")
                try:
                    fallback = bs.imagewidget(parent=self._profile_container, size=(button_width, button_height), position=pos, color=(0.55, 0.5, 0.6), draw_controller=button, mesh_opaque=mesh_opaque, mesh_transparent=mesh_transparent, mask_texture=mask_tex)
                    self._minigame_widgets.append(fallback)
                except: pass

            name_w = bs.textwidget(parent=self._profile_container, text=name, position=(pos[0] + button_width * 0.5, pos[1] + button_height * 0.5), size=(0, 0), scale=button_width * 0.0025, maxwidth=button_width * 0.7, draw_controller=button, h_align='center', v_align='center', color=(1, 1, 1))
            self._minigame_widgets.append(name_w)

            self._minigame_row_widgets[name] = (button, name_w, None)
            index += 1

        try: bs.containerwidget(edit=self._profile_container, size=(sub_width, sub_height))
        except: pass

        target, entry = self._selected_minigame_name, None
        for e in entries:
            if e[0] == target: entry = e; break
        if entry is None: entry = entries[-1]
        self._selected_minigame_name = entry[0]
        self._show_card_preview(entry[0], entry[1], kind='minigame')

    def _show_items(self):
        if self._is_closing: return
        if not self._profile_container: return
        items = [
            ('Tickets',                'tickets',                'tickets'),
            ('Purple Tickets',   'ticketsPurple',   'tickets_purple'),
            ('Tokens',                 'coin',                    'tokens')]

        if self._selected_item_name not in [e[0] for e in items]: self._selected_item_name = items[0][0]
        sub_scroll_width, cols, gap = self._container_width, 4, 8 
        cell = (sub_scroll_width - 20 - (cols - 1) * gap) / cols; cell_height = cell
        total_rows = (len(items) + cols - 1) // cols
        top = max(self._container_height, total_rows * (cell_height + gap) + 20)
        self._item_widgets, self._item_row_widgets  = [], {}
        for i, (display_name, texture_name, attr_name) in enumerate(items):
            row = i // cols; col = i % cols
            x, y = 9 + col * (cell + gap), top - (row + 1) * (cell_height + gap)
            button = bs.buttonwidget(parent=self._profile_container, position=(x, y), size=(cell, cell_height), label='', color=(0.55, 0.5, 0.6), button_type='square', texture=bs.gettexture('buttonSquare'), on_activate_call=ba.CallPartial(self._on_item_cell_press, display_name, texture_name, attr_name)); self._item_widgets.append(button)
            try: icon = bs.imagewidget(parent=self._profile_container, position=(x + cell * 0.15, y + cell_height * 0.15), size=(cell * 0.7, cell_height * 0.7), texture=bs.gettexture(texture_name), draw_controller=button)
            except: icon = bs.imagewidget(parent=self._profile_container, position=(x + cell * 0.15, y + cell_height * 0.15), size=(cell * 0.7, cell_height * 0.7), texture=bs.gettexture('nub'), draw_controller=button)
            self._item_widgets.append(icon)
            self._item_row_widgets[display_name] = (button, icon)
        try: bs.containerwidget(edit=self._profile_container, size=(sub_scroll_width, top))
        except: pass
        self._item_widgets_map = {}

        def _retry_items():
            self._item_refresh_timer = None
            if self._is_closing or self._current_tab != InventoryWindow.TabID.ITEMS: return
            self._refresh_item_values()
            classic = bs.app.classic
            need_retry = False
            if classic is not None:
                for key in ('tickets', 'tickets_purple', 'tokens'):
                    val = getattr(classic, key, -1)
                    if val in (-1, 0): need_retry = True; break
            if need_retry: self._item_refresh_timer = ba.apptimer(0.5, _retry_items)

        target = self._selected_item_name
        entry = None
        for e in items:
            if e[0] == target: entry = e; break
        if entry is None: entry = items[0]
        self._selected_item_name = entry[0]
        self._on_item_cell_press(entry[0], entry[1], entry[2])
        self._item_refresh_timer = ba.apptimer(0.5, _retry_items)

    def _on_item_cell_press(self, display_name: str, texture_name: str, attr_name: str):
        if self._is_closing: return
        self._selected_item_name = display_name
        bs.getsound('click01').play()
        self._clear_big_icon_preview()

        try:
            cx, text_bg_w, text_bg_h = self._screen_width * 0.72, 320 * 1.3, 100 * 1.3
            text_bg = bs.imagewidget(parent=self._sub_container, position=(cx - text_bg_w / 2, self._screen_height * 0.20 - (text_bg_h - 100) / 2), size=(text_bg_w, text_bg_h), color=(0.2, 0.63, 0.5), opacity=0.75, texture=bs.gettexture('scrollWidgetGlow')); self._big_icon_preview_widgets.append(text_bg)
            name_w = bs.textwidget(parent=self._sub_container, position=(cx, self._screen_height * 0.285), size=(0, 0), text=display_name, h_align='center', v_align='center', scale=1.1, color=(0.9, 0.9, 0.9), maxwidth=400); self._big_icon_preview_widgets.append(name_w)
            count_w = bs.textwidget(parent=self._sub_container, position=(cx, self._screen_height * 0.245), size=(0, 0), text='0', h_align='center', v_align='top', scale=0.85, color=(0.85, 0.85, 0.85), maxwidth=400); self._big_icon_preview_widgets.append(count_w)
            self._item_widgets_map[attr_name] = count_w
            self._refresh_item_values()
        except Exception as e: print(f"[ ! ] Error showing item preview: {e}")

    def _refresh_item_values(self):
        if self._is_closing or not self._item_widgets_map: return
        try:
            classic = bs.app.classic
            if classic is None: return
            for attr_name, widget in list(self._item_widgets_map.items()):
                try: val = getattr(classic, attr_name, -1)
                except: val = -1
                try: bs.textwidget(edit=widget, text=str(val))
                except: pass
        except Exception as e: print(f"[ ! ] Error refreshing item values: {e}")

    def _on_card_press(self, name: str, desc: str, kind: str = 'minigame'):
        if self._is_closing: return
        prev = self._selected_map_name if kind == 'map' else self._selected_minigame_name
        if prev != name:
            row_map = self._map_row_widgets if kind == 'map' else self._minigame_row_widgets
            if prev in row_map:
                _, old_bg, old_cross = row_map[prev]
                try: bs.imagewidget(edit=old_bg, color=(0, 0, 0), opacity=0.25)
                except: pass
                if old_cross is not None:
                    try: old_cross.delete()
                    except: pass
                    row_map[prev] = (row_map[prev][0], row_map[prev][1], None)

            if kind == 'map': self._selected_map_name = name
            else: self._selected_minigame_name = name
            if name in row_map:
                row, bg, cross = row_map[name]
                try: bs.imagewidget(edit=bg, color=(0.2, 0.63, 0.5), opacity=0.45)
                except: pass
                if cross is None:
                    try:
                        cross = bs.imagewidget(parent=row, texture=bs.gettexture('achievementCrossHair'), position=(355, 23.5), size=(40, 40), color=(0.3, 0.8, 1.0))
                        widget_list = self._map_widgets if kind == 'map' else self._minigame_widgets; widget_list.append(cross)
                        row_map[name] = (row, bg, cross)
                    except: pass
        try:
            if kind == 'minigame': bs.getsound('swish').play()
            else: bs.getsound('click01').play()
        except: bs.getsound('swish').play()
        self._show_card_preview(name, desc, kind)

    def _show_card_preview(self, name: str, desc: str, kind: str = 'minigame'):
        self._clear_big_icon_preview()
        try:
            cx, text_bg_w, text_bg_h = self._screen_width * 0.72, 320 * 1.3, 100 * 1.3
            text_bg = bs.imagewidget(parent=self._sub_container, position=(cx - text_bg_w / 2, self._screen_height * 0.20 - (text_bg_h - 100) / 2), size=(text_bg_w, text_bg_h), color=(0.2, 0.63, 0.5), opacity=0.75, texture=bs.gettexture('scrollWidgetGlow')); self._big_icon_preview_widgets.append(text_bg)
            name_w = bs.textwidget(parent=self._sub_container, position=(cx, self._screen_height * 0.285), size=(0, 0), text=name, h_align='center', v_align='center', scale=1.1, color=(0.9, 0.9, 0.9), maxwidth=400); self._big_icon_preview_widgets.append(name_w)
            if desc: desc_w = bs.textwidget(parent=self._sub_container, position=(cx, self._screen_height * 0.245), size=(0, 0), text=desc, h_align='center', v_align='top', scale=0.65, color=(0.75, 0.75, 0.75), maxwidth=400); self._big_icon_preview_widgets.append(desc_w)
        except Exception as e: print(f"[ ! ] Error on-card preview: {e}")

    def _create_switch(self, parent, position, size, config_key, display_text, on_value_change):
        return CustomSwitch(parent=parent, position=position, size=size, config_key=config_key, display_text=display_text, on_value_change=on_value_change)

    def _create_icon_button(self):
        if self._icon_button:
            try: self._icon_button.delete()
            except: pass
            self._icon_button = None
        if self._icon_button_label:
            try: self._icon_button_label.delete()
            except: pass
            self._icon_button_label = None
        if self._icon_text_label:
            try: self._icon_text_label.delete()
            except: pass
            self._icon_text_label = None

        if not self._editor_container: return
        editor_width, editor_height = self._editor_width, self._editor_height
        icon_size, text_scale = min(editor_width * 0.5, editor_height * 0.45), min(editor_width * 0.004, 0.45)
        pos_x, pos_y = (editor_width/2 - icon_size/4) - (editor_width * 0.37), editor_height * 0.6
        self._icon_button = bs.buttonwidget(parent=self._editor_container, position=(pos_x, pos_y), size=(icon_size/2, icon_size/2), label='', color=(0.6, 0.5, 0.6), button_type='square', text_scale=0.95, on_activate_call=self._on_icon_press)
        self._icon_text_label = bs.textwidget(parent=self._editor_container, position=(pos_x * 0.5 + (icon_size/4), pos_y - (editor_height * 0.15)), text='Icon', h_align='center', v_align='center', scale=text_scale)
        self._update_icon()

    def _update_icon(self):
        if not self._icon_button: return
        session, activity = ba.get_foreground_host_session(), None
        if session: activity = session.getactivity()
        if not activity or not hasattr(activity, 'get_selected_profile'): return
        selected_profile = activity.get_selected_profile()
        if not selected_profile: return
        profiles = bs.app.config.get('Player Profiles', {})
        info = profiles.get(selected_profile, {})
        icon = info.get('icon', '')
        if not icon: icon = ''
        try: bs.buttonwidget(edit=self._icon_button, label=icon)
        except: pass

    def _delete_icon_button(self):
        if self._icon_button:
            try: self._icon_button.delete()
            except: pass
            self._icon_button = None
        if self._icon_button_label:
            try: self._icon_button_label.delete()
            except: pass
            self._icon_button_label = None
        if self._icon_text_label:
            try: self._icon_text_label.delete()
            except: pass
            self._icon_text_label = None

    def _delete_new_profile(self):
        profiles = bs.app.config.get('Player Profiles', {})
        if temporary_account_name in profiles:
            plus = bs.app.plus
            if plus is not None:
                plus.add_v1_account_transaction({'type': 'REMOVE_PLAYER_PROFILE', 'name': temporary_account_name})
                plus.run_v1_account_transactions()

            del profiles[temporary_account_name]
            bs.app.config['Player Profiles'] = profiles; order = bs.app.config.get('profile_order', [])
            if temporary_account_name in order: order.remove(temporary_account_name); bs.app.config['profile_order'] = order
            bs.app.config.commit()
        self._pending_new_profile, self._new_profile_name, self._tmp_name = False, None, ""

    def _cancel_new_profile(self):
        if not self._pending_new_profile: return
        self._delete_new_profile()
        session = ba.get_foreground_host_session()
        if session:
            activity = session.getactivity()
            if activity and hasattr(activity, 'set_profile'):
                profiles = bs.app.config.get('Player Profiles', {})
                if profiles:
                    first_profile = None
                    for name in profiles:
                        if name != temporary_account_name: first_profile = name; break
                    if first_profile:
                        activity.set_profile(first_profile)
                        self._selected_profile_name = first_profile
        self._show_profiles(); self._update_editor_ui()

    def _save_profile_to_cloud(self, profile_name: str, profile_data: dict, is_delete: bool = False):
        plus = bs.app.plus
        if plus is None: return
        if is_delete: plus.add_v1_account_transaction({'type': 'REMOVE_PLAYER_PROFILE', 'name': profile_name})
        else: plus.add_v1_account_transaction({'type': 'ADD_PLAYER_PROFILE', 'name': profile_name, 'profile': profile_data})
        plus.run_v1_account_transactions()

    def _save_current_profile(self, force_save=False):
        if not self._profile_name_text: return
        session, activity = ba.get_foreground_host_session(), None
        if session: activity = session.getactivity()
        if not activity or not hasattr(activity, 'get_selected_profile'): return
        profile_name = activity.get_selected_profile()
        if not profile_name or profile_name == temporary_account_name: return
        profiles = bs.app.config.get('Player Profiles', {})
        current_character = activity.character if hasattr(activity, 'character') else 'Spaz'
        current_color = activity.color if hasattr(activity, 'color') else (0.5, 0.5, 0.5)
        current_highlight = activity.highlight if hasattr(activity, 'highlight') else (1.0, 1.0, 1.0)
        current_icon = profiles.get(profile_name, {}).get('icon', '')
        is_global = profiles.get(profile_name, {}).get('global', False)
        profile_data = {'character': current_character, 'color': list(current_color), 'highlight': list(current_highlight), 'global': is_global}
        if current_icon: profile_data['icon'] = current_icon

        if profile_name in profiles:
            profiles[profile_name] = profile_data
            bs.app.config['Player Profiles'] = profiles; bs.app.config.commit()
            self._save_profile_to_cloud(profile_name, profile_data)

    def _save_name(self, force_save=False):
        if not self._profile_name_text: return
        if not force_save: return
        if self._pending_new_profile:
            if self._tmp_name and self._tmp_name != temporary_account_name: self._save_temporary_profile(); return
            new_name = bs.textwidget(query=self._profile_name_text)
            if new_name and new_name.strip() and new_name.strip() != temporary_account_name:
                self._tmp_name = new_name.strip(); self._save_temporary_profile(); return
            return

        session, activity = ba.get_foreground_host_session(), None
        if session: activity = session.getactivity()
        if not activity or not hasattr(activity, 'get_selected_profile'): return
        old_name = activity.get_selected_profile()
        if not old_name: return
        if old_name == '__account__':
            plus = bs.app.plus
            if plus and plus.get_v1_account_state() == 'signed_in': display_name = plus.get_v1_account_display_string()
            else: display_name = 'Account'
            bs.textwidget(edit=self._profile_name_text, text=display_name)
            return

        new_name = bs.textwidget(query=self._profile_name_text)
        if not new_name or len(new_name.strip()) < 1: return
        new_name = new_name.strip()
        if new_name == '__account__': bs.textwidget(edit=self._profile_name_text, text=old_name); return
        profiles = bs.app.config.get('Player Profiles', {})
        if new_name in profiles and new_name != old_name: bs.textwidget(edit=self._profile_name_text, text=old_name); return
        current_character = activity.character if hasattr(activity, 'character') else 'Spaz'
        current_color = activity.color if hasattr(activity, 'color') else (0.5, 0.5, 0.5)
        current_highlight = activity.highlight if hasattr(activity, 'highlight') else (1.0, 1.0, 1.0)
        current_icon = profiles.get(old_name, {}).get('icon', '') if old_name in profiles else ''
        is_global = profiles.get(old_name, {}).get('global', False)
        profile_data = {'character': current_character, 'color': list(current_color), 'highlight': list(current_highlight), 'global': is_global}
        if current_icon: profile_data['icon'] = current_icon
        profiles[new_name] = profiles.pop(old_name)
        bs.app.config['Player Profiles'] = profiles

        order = bs.app.config.get('profile_order', [])
        if old_name in order:
            idx = order.index(old_name); order[idx] = new_name
            bs.app.config['profile_order'] = order

        if new_name in profiles:
            profiles[new_name] = profile_data
            bs.app.config['Player Profiles'] = profiles
            bs.app.config.commit()

            plus = bs.app.plus
            if plus is not None:
                plus.add_v1_account_transaction({'type': 'REMOVE_PLAYER_PROFILE', 'name': old_name})
                plus.add_v1_account_transaction({'type': 'ADD_PLAYER_PROFILE', 'name': new_name, 'profile': profile_data})
                plus.run_v1_account_transactions()

        if hasattr(activity, '_selected_profile'): activity._selected_profile = new_name
        self._selected_profile_name, self._pending_new_profile, self._tmp_name = new_name, False, ""
        self._show_profiles(); self._update_editor_ui()

    def _save_new_profile(self, name: str):
        profiles = bs.app.config.get('Player Profiles', {})
        if name in profiles: bs.textwidget(edit=self._profile_name_text, text=temporary_account_name); return
        temp_data = profiles.pop(temporary_account_name, {})
        profile_data = {'character': temp_data.get('character', 'Spaz'), 'color': temp_data.get('color', [0.5, 0.5, 0.5]), 'highlight': temp_data.get('highlight', [1.0, 1.0, 1.0]), 'global': False}
        if 'icon' in temp_data: profile_data['icon'] = temp_data['icon']
        profiles[name] = profile_data
        bs.app.config['Player Profiles'] = profiles
        order = bs.app.config.get('profile_order', [])
        if temporary_account_name in order: idx = order.index(temporary_account_name); order[idx] = name
        elif name not in order: order.append(name)
        bs.app.config['profile_order'] = order; bs.app.config.commit()
        self._save_profile_to_cloud(name, profile_data)

        session = ba.get_foreground_host_session()
        if session:
            activity = session.getactivity()
            if activity and hasattr(activity, 'set_profile'):
                activity.set_profile(name)
                self._selected_profile_name, self._pending_new_profile, self._new_profile_name, self._tmp_name = name, False, None, ""

        self._show_profiles(); self._update_editor_ui()
        bs.screenmessage(f'[ ? ] Profile "{name}" created!', color=(0.3, 0.8, 0.5))
        bs.getsound('gunCocking').play()

    def _create_profile(self):
        if self._pending_new_profile: bs.getsound('error').play(); return
        profiles = bs.app.config.get('Player Profiles', {})
        if temporary_account_name in profiles: bs.getsound('error').play(); return
        profiles[temporary_account_name] = {'character': 'Spaz', 'color': [0.5, 0.5, 0.5], 'highlight': [1.0, 1.0, 1.0], 'global': False, 'temporary': True}
        bs.app.config['Player Profiles'] = profiles
        order = bs.app.config.get('profile_order', [])
        if temporary_account_name not in order: order.append(temporary_account_name); bs.app.config['profile_order'] = order
        bs.app.config.commit()
        self._pending_new_profile, self._new_profile_name, self._tmp_name = True, temporary_account_name, ""
        session = ba.get_foreground_host_session()
        if session:
            activity = session.getactivity()
            if activity and hasattr(activity, 'set_profile'):
                activity.set_profile(temporary_account_name)
                self._selected_profile_name = temporary_account_name
        self._show_profiles(); self._update_editor_ui()

    def _create_editor_ui(self, parent_widget):
        screen_width, screen_height = bs.get_virtual_screen_size()
        self._editor_width, self._editor_height, ui_width = screen_width * 0.4, screen_height * 0.2, screen_width * 0.35
        x_pos, y_pos = ui_width + (screen_width * 0.125), (screen_height - self._editor_height) / 5
        icon_size, text_scale = min(self._editor_width * 0.5, self._editor_height * 0.45), min(self._editor_width * 0.004, 0.45)
        color_size, color_y_pos, color_spacing = min(self._editor_width * 0.35, self._editor_height * 0.28), self._editor_height * 0.55, self._editor_width * 0.25
        self._editor_container = bs.containerwidget(parent=parent_widget, size=(self._editor_width, self._editor_height), position=(x_pos, y_pos), background=False, scale=1.0)
        bs.imagewidget(parent=self._editor_container, size=(self._editor_width, self._editor_height + 10), texture=bs.gettexture('scrollWidgetGlow'))
        session, activity = ba.get_foreground_host_session(), None
        if session: activity = session.getactivity()
        profiles, selected_profile = bs.app.config.get('Player Profiles', {}), None
        if activity and hasattr(activity, 'get_selected_profile'): selected_profile = activity.get_selected_profile()
        is_global, is_temporary, is_account = False, False, False; editable = is_temporary
        if selected_profile: info = profiles.get(selected_profile, {}); is_global, is_temporary, is_account = info.get('global', False), info.get('temporary', False), selected_profile == '__account__'        
        self._profile_name_text = bs.textwidget(parent=self._editor_container, position=(self._editor_width / 2 - 100, self._editor_height * 0.2), size=(200, 30), text='', h_align='center', v_align='center', scale=0.95, color=(1, 1, 1), maxwidth=190, padding=4, editable=editable, on_return_press_call=self._on_name_entered)
        self._character_button = bs.buttonwidget(parent=self._editor_container, position=(self._editor_width/2 - icon_size/2, self._editor_height - icon_size - (self._editor_height * 0.1)), size=(icon_size, icon_size), label='', color=(1, 1, 1), mask_texture=bs.gettexture('characterIconMask'), on_activate_call=self._on_character_press, button_type='square')
        self._color_button = bs.buttonwidget(parent=self._editor_container, position=(color_spacing, color_y_pos), size=(color_size, color_size), label='', color=(0.5, 0.5, 0.5), on_activate_call=self._on_color_press, button_type='square')
        bs.textwidget(parent=self._editor_container, position=(color_spacing + color_size/15, color_y_pos - (self._editor_height * 0.15)), text='Color', h_align='center', v_align='center', scale=text_scale)
        self._highlight_button = bs.buttonwidget(parent=self._editor_container, position=(self._editor_width - color_spacing * 1.4, color_y_pos), size=(color_size, color_size), label='', color=(1.0, 1.0, 1.0), on_activate_call=self._on_highlight_press, button_type='square')
        bs.textwidget(parent=self._editor_container, position=(self._editor_width - color_spacing * 1.6 + color_size/2, color_y_pos - (self._editor_height * 0.15)), text='Highlight', h_align='center', v_align='center', scale=text_scale)
        if is_global and not is_account: self._create_icon_button()
        else: self._delete_icon_button()
        self._upgrade_button, self._delete_button = None, None
        bs.apptimer(0.3, self._update_editor_ui)

    def _on_name_entered(self):
        new_name = bs.textwidget(query=self._profile_name_text)
        if new_name:
            self._tmp_name = new_name.strip()
            if self._pending_new_profile and self._tmp_name and self._tmp_name != temporary_account_name: self._save_temporary_profile()

    def _create_upgrade_delete_buttons(self):
        if self._upgrade_button:
            try: self._upgrade_button.delete()
            except: pass
            self._upgrade_button = None

        if self._delete_button:
            try: self._delete_button.delete()
            except: pass
            self._delete_button = None

        session, activity = ba.get_foreground_host_session(), None
        if session: activity = session.getactivity()
        if not activity or not hasattr(activity, 'get_selected_profile'): return
        selected_profile = activity.get_selected_profile()
        if not selected_profile: return
        profiles = bs.app.config.get('Player Profiles', {})
        info = profiles.get(selected_profile, {})
        is_account = selected_profile == '__account__'
        is_global, is_temporary = info.get('global', False), info.get('temporary', False)
        editor_width, editor_height = self._editor_width, self._editor_height
        y_pos, save_x, del_x = editor_height * 0.85, editor_width * 0.75, editor_width * 0.8

        if is_temporary:
            self._upgrade_button = bs.buttonwidget(parent=self._editor_container, position=(save_x + editor_width * 0.015, y_pos), size=(50, 25), label='Save', text_scale=0.8, color=(0.1, 0.8, 0.1), on_activate_call=self._save_temporary_profile, button_type='square')
            self._delete_button = bs.buttonwidget(parent=self._editor_container, position=(save_x + editor_width * 0.15, y_pos), size=(25, 25), label='✕', text_scale=0.5, color=(0.8, 0.1, 0.1), on_activate_call=self._cancel_new_profile, button_type='square')
            return

        if is_account: return
        if not is_global: self._upgrade_button = bs.buttonwidget(parent=self._editor_container, position=(del_x + editor_width * 0.015, y_pos), size=(25, 25), label=' ↑ ', text_scale=0.95, color=(0.1, 0.8, 0.1), on_activate_call=self._on_upgrade_press, button_type='square')
        if not is_account: self._delete_button = bs.buttonwidget(parent=self._editor_container, position=(del_x + editor_width * 0.1, y_pos), size=(25, 25), label='✕', text_scale=0.5, color=(0.8, 0.1, 0.1), on_activate_call=self._on_delete_press, button_type='square')

    def _save_temporary_profile(self):
        if not self._profile_name_text: bs.getsound('error').play(); return
        new_name = self._tmp_name
        if not new_name or new_name == temporary_account_name:
            text_name = bs.textwidget(query=self._profile_name_text)
            if text_name and text_name.strip() and text_name.strip() != temporary_account_name:
                new_name = text_name.strip(); self._tmp_name = new_name
            else: bs.getsound('error').play(); return

        if len(new_name) < 1 or new_name == temporary_account_name or new_name == "__account__": bs.getsound('error').play(); return
        profiles = bs.app.config.get('Player Profiles', {})
        if temporary_account_name not in profiles:
            bs.getsound('error').play()
            self._pending_new_profile, self._new_profile_name, self._tmp_name = False, None, ""
            session = ba.get_foreground_host_session()
            if session:
                activity = session.getactivity()
                if activity and hasattr(activity, 'set_profile'):
                    if profiles:
                        first_profile = next(iter(profiles))
                        activity.set_profile(first_profile)
                        self._selected_profile_name = first_profile
            self._show_profiles(); self._update_editor_ui()
            return

        temp_data = profiles.pop(temporary_account_name)
        temp_data.pop('temporary', None)
        profiles[new_name] = temp_data
        bs.app.config['Player Profiles'] = profiles   
        order = bs.app.config.get('profile_order', [])
        if temporary_account_name in order: idx = order.index(temporary_account_name); order[idx] = new_name
        elif new_name not in order: order.append(new_name)
        bs.app.config['profile_order'] = order; bs.app.config.commit()
        self._save_profile_to_cloud(new_name, temp_data)

        self._pending_new_profile, self._new_profile_name, self._tmp_name = False, None, ""
        session = ba.get_foreground_host_session()
        if session:
            activity = session.getactivity()
            if activity and hasattr(activity, 'set_profile'):
                activity.set_profile(new_name)
                self._selected_profile_name = new_name

        self._show_profiles(); self._update_editor_ui()
        bs.screenmessage(f'Profile "{new_name}" saved!', color=(0.3, 0.8, 0.5))
        bs.getsound('gunCocking').play()

    def _update_editor_ui(self):
        if not self._editor_container: return
        session, activity = ba.get_foreground_host_session(), None
        if session: activity = session.getactivity()
        if not activity or not hasattr(activity, 'get_selected_profile'): return
        selected_profile = activity.get_selected_profile()
        if not selected_profile:
            bs.textwidget(edit=self._profile_name_text, text='No Profile', editable=False)
            bs.buttonwidget(edit=self._character_button, texture=None, tint_texture=None)
            self._delete_icon_button()
            return

        profiles = bs.app.config.get('Player Profiles', {})
        info = profiles.get(selected_profile, {})
        is_account = selected_profile == '__account__'
        is_global, is_temporary = info.get('global', False), info.get('temporary', False)
        if is_account: is_global = True
        current_name = selected_profile
        self._last_name = current_name
        editable = is_temporary

        if is_account:
            plus = bs.app.plus
            if plus and plus.get_v1_account_state() == 'signed_in': display_name = plus.get_v1_account_display_string()
            else: display_name = 'Account'
            bs.textwidget(edit=self._profile_name_text, text=display_name, editable=False, size=(200, 30), maxwidth=190)
        elif is_temporary:
            display_text = self._tmp_name if self._tmp_name and self._tmp_name != temporary_account_name else temporary_account_name
            bs.textwidget(edit=self._profile_name_text, text=display_text, editable=True, size=(200, 30), maxwidth=190, max_chars=16, description='Enter profile name')
        elif is_global: bs.textwidget(edit=self._profile_name_text, text=current_name, editable=False, size=(200, 30), maxwidth=190)
        else: bs.textwidget(edit=self._profile_name_text, text=current_name, editable=True, size=(200, 30), maxwidth=190, max_chars=16, description='Profile Name')

        if hasattr(activity, 'color'):
            color = activity.color
            if len(color) > 3: color = color[:3]
            bs.buttonwidget(edit=self._color_button, color=color)
        if hasattr(activity, 'highlight'):
            highlight = activity.highlight
            if len(highlight) > 3: highlight = highlight[:3]
            bs.buttonwidget(edit=self._highlight_button, color=highlight)

        if is_global and not is_account:
            if not self._icon_button: self._create_icon_button()
            else: self._update_icon()
        else: self._delete_icon_button()

        classic = bs.app.classic
        if classic:
            char_name = info.get('character', 'Spaz')
            appearance = classic.spaz_appearances.get(char_name)
            if appearance:
                icon_texture, mask_texture = bs.gettexture(appearance.icon_texture), bs.gettexture(appearance.icon_mask_texture) if hasattr(appearance, 'icon_mask_texture') else None
                color, highlight = activity.color if hasattr(activity, 'color') else (0.5, 0.5, 0.5), activity.highlight if hasattr(activity, 'highlight') else (1.0, 1.0, 1.0)
                if len(color) > 3: color = color[:3]
                if len(highlight) > 3: highlight = highlight[:3]
                bs.buttonwidget(edit=self._character_button, texture=icon_texture, tint_texture=mask_texture, tint_color=color, tint2_color=highlight)
            else:
                appearance = classic.spaz_appearances.get('Spaz')
                if appearance: bs.buttonwidget(edit=self._character_button, texture=bs.gettexture(appearance.icon_texture), tint_texture=None)
        self._create_upgrade_delete_buttons()

    def _on_character_press(self):
        if self._pending_new_profile:
            new_name = bs.textwidget(query=self._profile_name_text)
            if new_name and new_name.strip() and new_name.strip() != temporary_account_name: self._tmp_name = new_name.strip()
            bs.getsound('error').play()
            return

        self._save_name(True)
        session, activity = ba.get_foreground_host_session(), None
        if session: activity = session.getactivity()
        if not activity or not hasattr(activity, 'get_selected_profile'): return
        selected_profile = activity.get_selected_profile()
        if not selected_profile: return

        if selected_profile == temporary_account_name: bs.getsound('error').play(); return
        profiles = bs.app.config.get('Player Profiles', {})
        info = profiles.get(selected_profile, {})
        current_char = info.get('character', 'Spaz')
        if self._character_button:
            pos, color, highlight = self._character_button.get_screen_space_center(), activity.color if hasattr(activity, 'color') else (0.5, 0.5, 0.5), activity.highlight if hasattr(activity, 'highlight') else (1.0, 1.0, 1.0)
            if len(color) > 3: color = color[:3]
            if len(highlight) > 3: highlight = highlight[:3]
            CharacterPicker(parent=self._editor_container, position=pos, selected_character=current_char, delegate=self, tint_color=color, tint2_color=highlight)

    def _on_color_press(self):
        if self._pending_new_profile:
            new_name = bs.textwidget(query=self._profile_name_text)
            if new_name and new_name.strip() and new_name.strip() != temporary_account_name: self._tmp_name = new_name.strip()
            bs.getsound('error').play()
            return

        self._save_name(True)
        session, activity = ba.get_foreground_host_session(), None
        if session: activity = session.getactivity()
        if not activity or not hasattr(activity, 'color'): return
        if self._color_button: ColorPicker(parent=self._editor_container, position=self._color_button.get_screen_space_center(), offset=(0, 0), initial_color=activity.color, delegate=self, tag='color')

    def _on_highlight_press(self):
        if self._pending_new_profile:
            new_name = bs.textwidget(query=self._profile_name_text)
            if new_name and new_name.strip() and new_name.strip() != temporary_account_name: self._tmp_name = new_name.strip()
            bs.getsound('error').play()
            return

        self._save_name(True)
        session, activity = ba.get_foreground_host_session(), None
        if session: activity = session.getactivity()
        if not activity or not hasattr(activity, 'highlight'): return
        if self._highlight_button: ColorPicker(parent=self._editor_container, position=self._highlight_button.get_screen_space_center(), offset=(0, 0), initial_color=activity.highlight, delegate=self, tag='highlight')

    def _on_icon_press(self):
        if self._pending_new_profile:
            new_name = bs.textwidget(query=self._profile_name_text)
            if new_name and new_name.strip() and new_name.strip() != temporary_account_name: self._tmp_name = new_name.strip()
            bs.getsound('error').play()
            return

        self._save_name(True)
        session, activity = ba.get_foreground_host_session(), None
        if session: activity = session.getactivity()
        if not activity or not hasattr(activity, 'get_selected_profile'): return
        selected_profile = activity.get_selected_profile()
        if not selected_profile: return

        if selected_profile == temporary_account_name or selected_profile == "__account__":
            if selected_profile == temporary_account_name: bs.getsound('error').play()
            return

        profiles = bs.app.config.get('Player Profiles', {})
        info = profiles.get(selected_profile, {}); current_icon = info.get('icon', '')
        if self._icon_button:
            pos, color, highlight = self._icon_button.get_screen_space_center(), activity.color if hasattr(activity, 'color') else (0.5, 0.5, 0.5), activity.highlight if hasattr(activity, 'highlight') else (1.0, 1.0, 1.0)
            if len(color) > 3: color = color[:3]
            if len(highlight) > 3: highlight = highlight[:3]
            IconPicker(parent=self._editor_container, position=pos, selected_icon=current_icon, delegate=self, tint_color=color, tint2_color=highlight)

    def _on_upgrade_press(self):
        if self._pending_new_profile: bs.getsound('error').play(); return
        session, activity = ba.get_foreground_host_session(), None
        if session: activity = session.getactivity()
        if not activity or not hasattr(activity, 'get_selected_profile'): return
        profile_name = activity.get_selected_profile()
        if profile_name == '__account__': bs.screenmessage('[ ? ] Account profile is already global!', color=(0.8, 0.4, 0.4)); bs.getsound('error').play(); return
        if not profile_name or profile_name == temporary_account_name: bs.screenmessage('[ ! ] Cannot upgrade this profile', color=(0.8, 0.4, 0.4)); bs.getsound('error').play(); return
        self._save_name(True)
        plus = bs.app.plus
        if plus is None or plus.accounts.primary is None: show_sign_in_prompt(); return
        pupgrade.ProfileUpgradeWindow(self)

    def _confirm_action(self, title: str, message: str, action: Callable) -> None:
        ConfirmWindow(text=message, action=action, width=360, height=105, ok_text=title, origin_widget=self._root_widget)

    def _do_delete_profile(self, profile: str):
        session, activity = ba.get_foreground_host_session(), None
        if session: activity = session.getactivity()
        profiles = bs.app.config.get('Player Profiles', {})
        if profile in profiles:
            self._save_profile_to_cloud(profile, {}, is_delete=True)

            del profiles[profile]
            bs.app.config['Player Profiles'] = profiles

            order = bs.app.config.get('profile_order', [])
            if profile in order:
                order.remove(profile); bs.app.config['profile_order'] = order
            bs.app.config.commit()

            if profiles:
                first_profile = next(iter(profiles))
                if activity and hasattr(activity, 'set_profile'):
                    activity.set_profile(first_profile)
                    self._selected_profile_name = first_profile

            self._show_profiles(); self._update_editor_ui()
            bs.screenmessage(f'[ ! ] {profile} profile has been deleted!', color=(1, 0.0, 0.0))
            bs.getsound('shieldDown').play()

    def _on_delete_press(self):
        session, activity = ba.get_foreground_host_session(), None
        if session: activity = session.getactivity()
        if activity and hasattr(activity, 'get_selected_profile'):
            profile = activity.get_selected_profile()
            if profile and profile != '__account__' and profile != temporary_account_name:
                self._save_name(True); self._confirm_action(title="Delete", message=f"Are you sure your want to delete \n profile '{profile}'? This cannot be undone!", action=lambda: self._do_delete_profile(profile))
            elif profile == temporary_account_name: self._cancel_new_profile()
            elif profile == '__account__': bs.screenmessage("[ ! ] Cannot delete the account profile!", color=(0.8, 0.4, 0.4)); bs.getsound("error").play()

    def color_picker_closing(self, picker):
        pass
    
    def color_picker_selected_color(self, picker, color):
        if len(color) > 3: color = color[:3]
        tag = picker.get_tag(); session, activity = ba.get_foreground_host_session(), None
        if session: activity = session.getactivity()
        if not activity: return

        if tag == 'color' and hasattr(activity, 'set_color'):
            activity.set_color(color)
            self._save_current_profile(True)
            bs.getsound('gunCocking').play()
        elif tag == 'highlight' and hasattr(activity, 'set_highlight'):
            activity.set_highlight(color)
            self._save_current_profile(True)
            bs.getsound('gunCocking').play()

        bs.apptimer(0.1, self._update_editor_ui)
        bs.apptimer(0.2, self._show_profiles)

    def on_character_picker_pick(self, character):
        session = ba.get_foreground_host_session()
        if not session: return
        activity = session.getactivity()
        if not activity or not hasattr(activity, 'set_character'): return

        def apply_character():
            try:
                current_session = ba.get_foreground_host_session()
                if not current_session: return
                current_activity = current_session.getactivity()
                if current_activity and hasattr(current_activity, 'set_character'):
                    current_activity.set_character(character)
                    self._save_current_profile(True)
                    bs.apptimer(0.1, self._update_editor_ui)
                    bs.apptimer(0.2, self._show_profiles)
            except Exception as e: print(f"[ ! ] Error applying character: {e}")
        bs.pushcall(apply_character)

    def on_character_picker_get_more_press(self):
        pass

    def on_icon_picker_pick(self, icon: str) -> None:
        session = ba.get_foreground_host_session()
        if not session: return
        activity = session.getactivity()
        if not activity or not hasattr(activity, 'set_icon'): return

        def apply_icon():
            try:
                current_session = ba.get_foreground_host_session()
                if not current_session: return
                current_activity = current_session.getactivity()
                if current_activity and hasattr(current_activity, 'set_icon'):
                    current_activity.set_icon(icon)
                    self._save_current_profile(True)
                    bs.getsound('gunCocking').play()
                    bs.apptimer(0.1, self._update_editor_ui)
                    bs.apptimer(0.2, self._show_profiles)
            except Exception as e: print(f"[ ! ] Error applying icon: {e}")
        bs.pushcall(apply_icon)

    def on_icon_picker_get_more_press(self) -> None:
        pass

    def _start_refresh_timer(self):
        if self._refresh_timer:
            try: self._refresh_timer = None
            except: pass

        def refresh():
            if self._refresh_timer is not None and not self._is_closing:
                if self._current_tab == InventoryWindow.TabID.PROFILES: self._show_profiles(); self._update_editor_ui()
                self._refresh_timer = ba.apptimer(0.5, refresh)
        self._refresh_timer = ba.apptimer(0.5, refresh)

    def _get_profile_order(self) -> list[str]:
        config = bs.app.config
        profiles = config.get('Player Profiles', {})
        profile_names = list(profiles.keys())
        plus = bs.app.plus
        signed_in = plus is not None and plus.get_v1_account_state() == 'signed_in'
        if not signed_in and '__account__' in profile_names: profile_names.remove('__account__')
        if not profile_names: return []
        if 'profile_order' not in config:
            items = sorted(profile_names, key=lambda x: (0 if x == '__account__' else 1, x.lower()))
            config['profile_order'] = items; config.commit()
            return items

        order = config.get('profile_order', [])
        filtered_order = [name for name in order if name in profiles]
        existing_names = set(filtered_order)
        for name in profile_names:
            if name not in existing_names: filtered_order.append(name)
        filtered_order = [name for name in filtered_order if name in profiles]
        if len(filtered_order) != len(order) or set(filtered_order) != set(order): config['profile_order'] = filtered_order; config.commit()
        return filtered_order

    def _save_profile_order(self, order: list[str]):
        config = bs.app.config; config['profile_order'] = order; config.commit()

    def _move_selected_down(self):
        if self._is_closing or not self._selected_profile_name: return
        if self._selected_profile_name == temporary_account_name: bs.getsound('error').play(); return
        self._save_name(True); self._save_current_profile(True)
        order = self._get_profile_order()
        try: index = order.index(self._selected_profile_name)
        except ValueError: return
        if index <= 0: return
        order[index], order[index-1] = order[index-1], order[index]
        self._save_profile_order(order); self._show_profiles()
        bs.getsound('gunCocking').play()

    def _move_selected_up(self):
        if self._is_closing or not self._selected_profile_name: return
        if self._selected_profile_name == temporary_account_name: bs.getsound('error').play(); return
        self._save_name(True); self._save_current_profile(True)
        order = self._get_profile_order()
        try: index = order.index(self._selected_profile_name)
        except ValueError: return
        if index >= len(order) - 1: return
        order[index], order[index+1] = order[index+1], order[index]
        self._save_profile_order(order); self._show_profiles()
        bs.getsound('gunCocking').play()

    def _select_profile(self, name: str):
        if self._is_closing: return
        if self._pending_new_profile and name != temporary_account_name: self._delete_new_profile()
        else: self._save_name(True); self._save_current_profile(True)
        if name != temporary_account_name:
            session = ba.get_foreground_host_session()
            if session:
                activity = session.getactivity()
                if activity and hasattr(activity, 'set_profile'):
                    bs.pushcall(ba.CallPartial(self._apply_profile, activity, name))

    def _apply_profile(self, activity, name: str):
        if self._is_closing: return
        try:
            if hasattr(activity, 'set_profile'): 
                activity.set_profile(name)
                self._selected_profile_name = name
                bs.apptimer(0.1, self._show_profiles)
                bs.apptimer(0.2, self._update_editor_ui)
        except: pass

    def _show_profiles(self):
        if self._is_closing: return
        for widget in self._profile_widgets:
            try: widget.delete()
            except: pass
        self._profile_widgets.clear()
        if self._no_profiles_text:
            try: self._no_profiles_text.delete(); self._no_profiles_text = None
            except: pass

        screen_width, screen_height = bs.get_virtual_screen_size()
        profiles = bs.app.config.get('Player Profiles', {})
        order = self._get_profile_order(); has_profiles = bool(order)
        if not has_profiles:
            self._no_profiles_text = bs.textwidget(parent=self._profile_container, position=(self._container_width // 2 * 0.85, self._container_height // 2), text="No Profiles", h_align='center', v_align='center', scale=0.95, color=(0.7, 0.7, 0.7), selectable=False)
            self._profile_widgets.append(self._no_profiles_text)
            return

        session, activity, selected_profile = ba.get_foreground_host_session(), None, None
        if session: activity = session.getactivity()
        if activity and hasattr(activity, 'get_selected_profile'): selected_profile = activity.get_selected_profile()
        if selected_profile is None and order: selected_profile = order[-1]
        classic = bs.app.classic
        spaz_appearances = classic.spaz_appearances if classic else {}
        spaz_appearance_default = spaz_appearances.get('Spaz') if spaz_appearances else None
        plus = bs.app.plus
        account_name = None
        if plus is not None and plus.get_v1_account_state() == 'signed_in':
            account_name = plus.get_v1_account_display_string()

        self._selected_profile_name = selected_profile
        y_pos, spacing, sub_scroll_width = 5, 70, self._container_width
        card_w, card_h = sub_scroll_width * 0.95, 60
        for name in order:
            if name not in profiles:
                continue

            info = profiles[name]
            if name == '__account__':
                char_name = info.get('character', 'Spaz')
                if classic:
                    try: color, highlight = classic.get_player_profile_colors(name)
                    except: color, highlight = (0.5, 0.5, 0.5), (1, 1, 1)
                else: color, highlight = (0.5, 0.5, 0.5), (1, 1, 1)
                display_name = account_name if account_name else "Guest"
                is_global = True if account_name else False
            else:
                char_name = info.get('character', 'Spaz')
                color, highlight = (0.5, 0.5, 0.5), (1, 1, 1)
                if classic:
                    try: color, highlight = classic.get_player_profile_colors(name)
                    except: pass
                display_name = name
                is_global = info.get('global', False)

            is_temporary, appearance = info.get('temporary', False), spaz_appearances.get(char_name, spaz_appearance_default)
            icon_char = ''
            if name != '__account__':
                if is_global:
                    icon_char = info.get('icon', '')
                    if not icon_char: icon_char = ''
                elif classic:
                    try: icon_char = classic.get_player_profile_icon(name)
                    except: pass

            if is_global and icon_char: full_name = icon_char + display_name
            else: full_name = display_name
            if is_temporary: full_name = temporary_account_name
            is_selected = (selected_profile == name)
            info_container = bs.containerwidget(parent=self._profile_container, size=(card_w, card_h), position=(sub_scroll_width * 0.025, y_pos), background=False)
            self._profile_widgets.append(info_container)
            background_color, background_opacity = ((0.2, 0.63, 0.5), 0.45) if is_selected else ((0, 0, 0), 0.25)
            name_color = (0.9, 0.9, 1.0) if is_selected else (0.9, 0.9, 0.9)
            char_color = (0.7, 0.7, 1.0) if is_selected else (0.7, 0.7, 0.9)
            container_background = bs.imagewidget(parent=info_container, texture=bs.gettexture('white'), opacity=background_opacity, position=(-5, 10), size=(card_w, card_h * 1.08), color=background_color)
            if appearance: icon_texture = bs.gettexture(appearance.icon_texture)
            else: icon_texture = bs.gettexture('nub')

            icon = bs.imagewidget(parent=info_container, position=(5, 25), size=(35, 35), texture=icon_texture, tint_color=color, tint2_color=highlight)
            name_widget = bs.textwidget(parent=info_container, position=(50, 38), size=(180, 25), text=full_name, h_align='left', v_align='center', scale=0.85, color=name_color, selectable=False)
            if is_selected: crosshair = bs.imagewidget(parent=info_container, texture=bs.gettexture('achievementCrossHair'), position=(card_w * 0.85, card_h * 0.39), size=(40, 40), color=(0.3, 0.8, 1.0)); self._profile_widgets.append(crosshair)
            if is_temporary: status_text, status_color = 'Temporary', (1.0, 0.8, 0.2)
            else: status_text, status_color = f'Global: {"Yes" if is_global else "No"}', ((0.2, 0.8, 0.2), (0.8, 0.2, 0.2))[not is_global]
            global_widget = bs.textwidget(parent=info_container, position=(50, 20), size=(80, 20), text=status_text, h_align='left', v_align='center', scale=0.6, color=status_color, selectable=False)
            char_widget = bs.textwidget(parent=info_container, position=(150, 20), size=(120, 20), text=f'Character: {char_name}', h_align='left', v_align='center', scale=0.6, color=char_color, selectable=False)
            button = bs.buttonwidget(parent=info_container, position=(0, 0), size=(card_w, card_h), label='', color=(0, 0, 0), texture=bs.gettexture('empty'), button_type='square', on_activate_call=ba.CallPartial(self._select_profile, name))
            self._profile_widgets.extend([container_background, icon, name_widget, global_widget, char_widget, button])
            y_pos += spacing
        bs.containerwidget(edit=self._profile_container, size=(sub_scroll_width + 20, y_pos + 10))
        self._update_editor_ui()

    def _on_rotation_toggle(self, value):
        if self._is_closing: return
        if self._current_tab != InventoryWindow.TabID.PROFILES:
            try: bs.app.config['rotate_enabled'] = False; bs.app.config.commit()
            except: pass
            return

        self._save_current_profile(True)
        session = ba.get_foreground_host_session()
        if session:
            activity = session.getactivity()
            if activity and hasattr(activity, 'toggle_camera_rotation'):
                bs.pushcall(ba.CallPartial(activity.toggle_camera_rotation, value))

    def _on_light_toggle(self, value):
        if self._is_closing: return
        if self._current_tab != InventoryWindow.TabID.PROFILES:
            try: bs.app.config['light_enabled'] = False; bs.app.config.commit()
            except: pass
            return

        self._save_current_profile(True)
        session = ba.get_foreground_host_session()
        if session:
            activity = session.getactivity()
            if activity and hasattr(activity, 'toggle_character_light'):
                bs.pushcall(ba.CallPartial(activity.toggle_character_light, value))

    def set_session(self):
        session = ba.get_foreground_host_session()
        if session and isinstance(session, MainMenuSession):
            with session.context:
                activity = ba.newactivity(inventoryActivity)
                session.setactivity(activity)
                try:
                    if activity and hasattr(activity, 'get_selected_profile'):
                        profile_name = activity.get_selected_profile()
                        if profile_name:
                            profiles = bs.app.config.get('Player Profiles', {})
                            if profile_name in profiles:
                                char_name = profiles[profile_name].get('character', 'Spaz')
                                SoundManager.play_character_sound(char_name)
                except: pass

    def _close_window(self):
        self._is_closing = True
        self._selected_char_name = self._selected_icon_glyph = self._selected_minigame_name = None
        self._selected_map_name = self._selected_item_name = None
        self._char_row_widgets = {}; self._item_widgets_map = {}
        for attr in ('_item_refresh_timer', '_refresh_timer', '_rotate_switch', '_light_switch', '_no_profiles_text', '_root_widget'):
            obj = getattr(self, attr, None)
            if obj:
                try: obj.delete()
                except: pass
                setattr(self, attr, None)

        if self._pending_new_profile: self._delete_new_profile()
        else: self._save_name(True); self._save_current_profile(True)
        self._delete_icon_button(); self._clear_big_icon_preview()

        session = ba.get_foreground_host_session()
        if session and isinstance(session, MainMenuSession):
            with session.context:
                activity = session.getactivity()
                if activity:
                    if hasattr(activity, '_remove_character_light'): activity._remove_character_light()
                    if hasattr(activity, 'reset_camera'): activity.reset_camera()
                session.setactivity(ba.newactivity(MainMenuActivity))

# •━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━•

class MainWindow(bs.MainWindow):
    def __init__(self, root_widget: bs.Widget, transition: str | None = None, origin_widget: bs.Widget | None = None):
        super().__init__(root_widget, transition=transition, origin_widget=origin_widget)
        self._root_widget = root_widget

    def get_root_widget(self) -> bs.Widget:
        return self._root_widget

    def main_window_should_preserve_selection(self) -> bool:
        return False

# •━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━•

class CustomInventoryUIController(bauiv1lib.inventory.InventoryUIController):
    @override
    def create_window(self, request, uiopenstateid=None, transition='in_right', origin_widget=None):
        session = ba.get_foreground_host_session()
        if not isinstance(session, MainMenuSession):
            return super().create_window(request)
        self._window = InventoryWindow()
        return self._window.create_window(transition, origin_widget)

    @classmethod
    def get_window_extra_type_id(cls):
        return 'inventory'

# •━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━•

def patch_inventory():
    try: bauiv1lib.inventory.InventoryUIController = CustomInventoryUIController; return True
    except Exception as e:
        print(f"[ ! ] Failed to patch inventory: {e}"); return False

# •━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━•

def patch_profile_browser():
    try:
        def custom_profile_browser(transition='in_right', origin_widget=None):
            window = InventoryWindow(); main_window = window.create_window(transition, origin_widget)
            bb.app.ui_v1.set_main_window(main_window, is_top_level=True, back_state=None, suppress_warning=True)
        if hasattr(bb.app.ui_v1, 'profile_browser_window'): bb.app.ui_v1.profile_browser_window = custom_profile_browser
        return True
    except Exception as e: print(f"[ ! ] Failed to patch profile browser: {e}"); return False

# •━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━•

# ba_meta export babase.Plugin
class system(bb.Plugin):
    def plugin_information(self):
        self.name = "inventory v2"
        self.icon = "achievementFlawlessVictory"
        self.version = "2.0.1"
        self.creator = "@uwu-user"
        self.release_date = "2025/9/17"
        self.updated_date = "2026/9/18"
        self.type = "System/UI"

    def __init__(self):
        if bb.app.env.engine_build_number > 22837: print("[ inventory ] skipped — not compatible with 1.8 alpha test builds [ I dont want to! this one only for api 9 - 1.7.62 or lower ]")
        else: 
            patch_inventory(); patch_profile_browser()
            self.session = ba.get_foreground_host_session()
            if self.session and isinstance(self.session, MainMenuSession):
                with self.session.context: self.session.setactivity(ba.newactivity(inventoryActivity))

            session = ba.get_foreground_host_session()
            if session and isinstance(session, MainMenuSession):
                with session.context: session.setactivity(ba.newactivity(MainMenuActivity))