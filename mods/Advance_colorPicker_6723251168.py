# ba_meta require api 9

# •━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━•
#
#     Version v1.0
#     Create by Unknown_#7004 - ( @uwu.user )
#         - Github https://github.com/uwu-user
#         - https://gamebanana.com/members/2496091
#
# •━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━•

from __future__ import annotations
from typing import TYPE_CHECKING, override, cast

import time
import bauiv1 as bs
import babase as bb
import bascenev1 as ba
from bauiv1lib import colorpicker
from bauiv1lib.popup import PopupWindow

if TYPE_CHECKING:
    from typing import Any, Sequence, Callable, List, Dict, Tuple, Optional, Union

# •━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━•

class ModeSlider:
    def __init__(self, parent: bs.Widget, position: tuple[float, float], size: tuple[float, float], segments: list[str], selected_index: int = 0, on_change_callback: 'Callable[[int, str], None] | None' = None):
        self._labels, self._parent_widget, self._segments, self._on_change_callback = [], parent, segments, on_change_callback; segment_width = size[0] / len(segments)
        self._selected_index = max(0, min(selected_index, len(segments) - 1)); knob_width, knob_height = segment_width * 0.95, size[1] * 0.95; self._widgets, self._alive, self._is_animating = [], True, False
        self._animation_start_time, self._animation_duration, self._color_selected, self._color_unselected = 0.0, 0.45, (0.05, 0.05, 0.05), (0.6, 0.6, 0.6); self._segment_width, self._size, self._position = segment_width, size, position
        self._track = bs.imagewidget(parent=parent, position=(position[0], position[1]), size=size, color=(0, 0, 0), opacity=0.7, texture=bs.gettexture('scrollWidget')); self._widgets.append(self._track)
        self._knob_width, self._knob_height, self._knob_y = knob_width, knob_height, position[1] + (size[1] - knob_height) / 2
        self._knob_minimum_x, self._knob_maximum_x = position[0] + (segment_width - knob_width) / 2, position[0] + size[0] - segment_width + (segment_width - knob_width) / 2
        self._current_knob_x = self._knob_minimum_x + (self._knob_maximum_x - self._knob_minimum_x) * (self._selected_index / max(1, len(segments) - 1))
        self._knob = bs.imagewidget(parent=parent, position=(self._current_knob_x, self._knob_y), size=(knob_width, knob_height), texture=bs.gettexture('chestIconEmpty'), color=(0.0, 0.8, 0.4), opacity=0.9); self._widgets.append(self._knob)
        for label_index, label_text in enumerate(segments):
            segment_x, label_color = position[0] + label_index * segment_width, self._color_selected if label_index == self._selected_index else self._color_unselected
            label_widget = bs.textwidget(parent=parent, position=(segment_x, position[1]), size=(segment_width, size[1]), text=label_text, scale=0.5, v_align='center', h_align='center', color=label_color, maxwidth=segment_width - 4.0); self._labels.append(label_widget)
            sensor_button = bs.buttonwidget(parent=parent, position=(segment_x, position[1]), size=(segment_width, size[1]), texture=bs.gettexture('empty'), label='', enable_sound=False, button_type='square', autoselect=False, on_activate_call=bs.WeakCallStrict(self._select, label_index)); self._widgets.append(sensor_button)
        self._label_colors = [self._color_selected if label_index == self._selected_index else self._color_unselected for label_index in range(len(segments))]

    def _select(self, index: int):
        if not self._alive: return
        self._selected_index = index
        target_x = self._knob_minimum_x + (self._knob_maximum_x - self._knob_minimum_x) * (index / max(1, len(self._segments) - 1))
        self._start_animation(target_x)
        if self._on_change_callback: self._on_change_callback(index, self._segments[index])

    def _start_animation(self, target_x: float):
        self._is_animating = True
        self._animation_start_time = time.time()
        self._knob_start_x, self._knob_target_x = self._current_knob_x, target_x
        self._label_start_colors = list(self._label_colors)
        self._label_end_colors = [self._color_selected if label_index == self._selected_index else self._color_unselected for label_index in range(len(self._labels))]
        self._animate()

    def _animate(self):
        if not self._is_animating or not self._alive: self._is_animating = False; return
        elapsed = time.time() - self._animation_start_time
        if elapsed >= self._animation_duration: self._is_animating = False; progress = 1.0
        else: progress = elapsed / self._animation_duration; progress = progress * progress * (3.0 - 2.0 * progress); bs.apptimer(0.005, self._animate)
        self._current_knob_x = self._knob_start_x + (self._knob_target_x - self._knob_start_x) * progress
        try:
            if self._knob: bs.imagewidget(edit=self._knob, position=(self._current_knob_x, self._knob_y))
        except: self._is_animating = False; return
        for label_index, label_widget in enumerate(self._labels):
            start_color = self._label_start_colors[label_index]
            end_color = self._label_end_colors[label_index]
            label_color = ColorSystem.lerp_color(start_color, end_color, progress)
            self._label_colors[label_index] = label_color
            try: bs.textwidget(label_widget, color=label_color)
            except: pass

    def delete(self):
        self._alive = False; self._is_animating = False
        for widget in self._widgets:
            try:
                if widget and hasattr(widget, 'delete'): widget.delete()
            except: pass
        self._widgets.clear(); self._labels.clear()
        self._parent_widget = self._track = self._knob = None
        self._on_change_callback = None

# •━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━•

class ColorSlider:
    def __init__(self, parent: bs.Widget, position: tuple[float, float], size: tuple[float, float], hue: float = 0.0, value: float = 1.0, on_hue_change: 'Callable[[float], None] | None' = None, on_value_change: 'Callable[[float], None] | None' = None, on_hue_live: 'Callable[[float], None] | None' = None, on_value_live: 'Callable[[float], None] | None' = None):
        self._parent_widget, self._size, self._position, self._widgets, self._alive = parent, size, position, [], True
        self._hue, self._value = hue, value; padding = 9; cap_size = 17.05; bar_height = 17
        self._on_hue_change, self._on_value_change = on_hue_change, on_value_change
        self._on_hue_live, self._on_value_live = on_hue_live, on_value_live
        self._hue_animating, self._value_animating, self._animation_duration = False, False, 0.6
        self._background = bs.imagewidget(parent=parent, position=position, size=size, color=(0, 0, 0), opacity=0.7, texture=bs.gettexture('scrollWidget')); self._widgets.append(self._background)
        bar_width = size[0] - padding * 2 - cap_size * 2 + (padding - 3); top_y = position[1] + size[1] - bar_height - padding; bottom_y = position[1] + padding
        self._bar_x = (position[0] - 3) + padding + cap_size
        self._bar_width, self._bar_height = bar_width, bar_height
        self._top_y, self._bottom_y, self._cap_size = top_y, bottom_y, cap_size
        cap_top_y, cap_bottom_y, cap_left_x, cap_right_x = top_y + bar_height / 2 - cap_size / 2, bottom_y + bar_height / 2 - cap_size / 2, position[0] + padding + 6, self._bar_x + bar_width - 7.5
        self._hue_cap_left = bs.imagewidget(parent=parent, position=(cap_left_x, cap_top_y), size=(cap_size, cap_size), texture=bs.gettexture('circle'), color=ColorSystem.hsv_to_rgb(0.0, 1.0, 1.0))
        self._hue_cap_right = bs.imagewidget(parent=parent, position=(cap_right_x, cap_top_y), size=(cap_size, cap_size), texture=bs.gettexture('circle'), color=ColorSystem.hsv_to_rgb(1.0, 1.0, 1.0))
        self._value_cap_left = bs.imagewidget(parent=parent, position=(cap_left_x, cap_bottom_y), size=(cap_size, cap_size), texture=bs.gettexture('circle'), color=(0, 0, 0))
        self._value_cap_right = bs.imagewidget(parent=parent, position=(cap_right_x, cap_bottom_y), size=(cap_size, cap_size), texture=bs.gettexture('circle'), color=ColorSystem.hsv_to_rgb(self._hue, 1.0, 1.0))
        self._widgets += [self._hue_cap_left, self._hue_cap_right, self._value_cap_left, self._value_cap_right]
        number_of_tiles = 240; tile_width = bar_width / number_of_tiles
        self._number_of_tiles = number_of_tiles
        self._hue_tiles, self._value_tiles = [], []
        for tile_index in range(number_of_tiles):
            tile_color = ColorSystem.hsv_to_rgb(tile_index / number_of_tiles, 1.0, 1.0)
            tile_widget = bs.imagewidget(parent=parent, position=(self._bar_x + tile_index * tile_width, top_y), size=(tile_width + 0.5, bar_height), texture=bs.gettexture('white'), color=tile_color)
            self._hue_tiles.append(tile_widget); self._widgets.append(tile_widget)
        for tile_index in range(number_of_tiles):
            tile_color = ColorSystem.hsv_to_rgb(self._hue, 1.0, tile_index / number_of_tiles)
            tile_widget = bs.imagewidget(parent=parent, position=(self._bar_x + tile_index * tile_width, bottom_y), size=(tile_width + 0.5, bar_height), texture=bs.gettexture('white'), color=tile_color)
            self._value_tiles.append(tile_widget); self._widgets.append(tile_widget)
        knob_size, sensor_columns = bar_height + 6, 20
        self._knob_size = knob_size
        self._hue_knob_x = self._bar_x + bar_width * self._hue - knob_size / 2
        self._hue_knob_y = top_y + bar_height / 2 - knob_size / 2
        self._value_knob_x = self._bar_x + bar_width * self._value - knob_size / 2
        self._value_knob_y = bottom_y + bar_height / 2 - knob_size / 2
        self._hue_knob = bs.imagewidget(parent=parent, position=(self._hue_knob_x, self._hue_knob_y), size=(knob_size, knob_size), texture=bs.gettexture('chestIconEmpty'), color=(1, 1, 1), opacity=0.95)
        self._value_knob = bs.imagewidget(parent=parent, position=(self._value_knob_x, self._value_knob_y), size=(knob_size, knob_size), texture=bs.gettexture('chestIconEmpty'), color=(1, 1, 1), opacity=0.95)
        self._widgets += [self._hue_knob, self._value_knob]
        self._sensor_columns = sensor_columns
        sensor_width = bar_width / sensor_columns
        for sensor_index in range(sensor_columns):
            hue_sensor = bs.buttonwidget(parent=parent, position=(self._bar_x + sensor_index * sensor_width, top_y), size=(sensor_width, bar_height), texture=bs.gettexture('empty'), label='', enable_sound=False, button_type='square', autoselect=False, on_activate_call=bs.WeakCallStrict(self._on_hue_tap, sensor_index)); self._widgets.append(hue_sensor)
            value_sensor = bs.buttonwidget(parent=parent, position=(self._bar_x + sensor_index * sensor_width, bottom_y), size=(sensor_width, bar_height), texture=bs.gettexture('empty'), label='', enable_sound=False, button_type='square', autoselect=False, on_activate_call=bs.WeakCallStrict(self._on_value_tap, sensor_index)); self._widgets.append(value_sensor)

    def _on_hue_tap(self, sensor_index: int):
        if not self._alive: return
        target_value = (sensor_index + 0.5) / self._sensor_columns
        self._start_hue_animation(target_value)

    def _on_value_tap(self, sensor_index: int):
        if not self._alive: return
        target_value = (sensor_index + 0.5) / self._sensor_columns
        self._start_value_animation(target_value)

    def _start_hue_animation(self, target_value: float):
        self._hue_animating = True
        self._hue_animation_start_time = time.time()
        self._hue_from, self._hue_to = self._hue, target_value
        self._hue_tick()

    def _hue_tick(self):
        if not self._hue_animating or not self._alive: self._hue_animating = False; return
        elapsed = time.time() - self._hue_animation_start_time
        if elapsed >= self._animation_duration: self._hue_animating = False; progress = 1.0
        else: progress = elapsed / self._animation_duration; progress = progress * progress * (3.0 - 2.0 * progress); bs.apptimer(0.005, self._hue_tick)
        self._hue = self._hue_from + (self._hue_to - self._hue_from) * progress
        self._apply_hue()
        if self._on_hue_live: self._on_hue_live(self._hue)
        if progress >= 1.0 and self._on_hue_change: self._on_hue_change(self._hue)

    def _apply_hue(self):
        knob_x = self._bar_x + self._bar_width * self._hue - self._knob_size / 2
        try: bs.imagewidget(self._hue_knob, position=(knob_x, self._hue_knob_y))
        except: self._hue_animating = False; return
        try: bs.imagewidget(self._value_cap_right, color=ColorSystem.hsv_to_rgb(self._hue, 1.0, 1.0))
        except: pass
        for tile_index, tile_widget in enumerate(self._value_tiles):
            tile_color = ColorSystem.hsv_to_rgb(self._hue, 1.0, tile_index / self._number_of_tiles)
            try: bs.imagewidget(tile_widget, color=tile_color)
            except: pass

    def set_hue(self, hue: float, fire: bool = False):
        if self._hue_animating: return
        self._hue = max(0.0, min(1.0, hue))
        self._apply_hue()
        if fire and self._on_hue_change: self._on_hue_change(self._hue)

    def _start_value_animation(self, target_value: float):
        self._value_animating = True
        self._value_animation_start_time = time.time()
        self._value_from, self._value_to = self._value, target_value
        self._value_tick()

    def _value_tick(self):
        if not self._value_animating or not self._alive: self._value_animating = False; return
        elapsed = time.time() - self._value_animation_start_time
        if elapsed >= self._animation_duration: self._value_animating = False; progress = 1.0
        else: progress = elapsed / self._animation_duration; progress = progress * progress * (3.0 - 2.0 * progress); bs.apptimer(0.005, self._value_tick)
        self._value = self._value_from + (self._value_to - self._value_from) * progress
        self._apply_value()
        if self._on_value_live: self._on_value_live(self._value)
        if progress >= 1.0 and self._on_value_change: self._on_value_change(self._value)

    def _apply_value(self):
        knob_x = self._bar_x + self._bar_width * self._value - self._knob_size / 2
        try: bs.imagewidget(self._value_knob, position=(knob_x, self._value_knob_y))
        except: self._value_animating = False

    def set_value(self, value: float, fire: bool = False):
        if self._value_animating: return
        self._value = max(0.0, min(1.0, value))
        self._apply_value()
        if fire and self._on_value_change: self._on_value_change(self._value)

    def delete(self):
        self._alive = False; self._hue_animating = False; self._value_animating = False
        for widget in self._widgets:
            try:
                if widget and hasattr(widget, 'delete'): widget.delete()
            except: pass
        self._widgets.clear(); self._hue_tiles.clear(); self._value_tiles.clear()
        self._parent_widget = self._background = None
        self._hue_cap_left = self._hue_cap_right = None
        self._value_cap_left = self._value_cap_right = None
        self._hue_knob = self._value_knob = None
        self._on_hue_change = None; self._on_value_change = None
        self._on_hue_live = None; self._on_value_live = None

# •━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━•

class ColorSystem: # from stackoverflow.com/colors/css import everything
    @staticmethod
    def hsv_to_rgb(hue: float, saturation: float, value: float) -> Tuple[float, float, float]:
        if saturation == 0.0: return value, value, value
        hue_sector = int(hue * 6.0); fraction = (hue * 6.0) - hue_sector
        pure_value = value * (1.0 - saturation); blend_a = value * (1.0 - saturation * fraction); blend_b = value * (1.0 - saturation * (1.0 - fraction))
        hue_sector = hue_sector % 6
        if hue_sector == 0: return value, blend_b, pure_value
        if hue_sector == 1: return blend_a, value, pure_value
        if hue_sector == 2: return pure_value, value, blend_b
        if hue_sector == 3: return pure_value, blend_a, value
        if hue_sector == 4: return blend_b, pure_value, value
        if hue_sector == 5: return value, pure_value, blend_a
        return 0, 0, 0

    @staticmethod
    def rgb_to_hsv(red: float, green: float, blue: float) -> Tuple[float, float, float]:
        maximum = max(red, green, blue); minimum = min(red, green, blue); value = maximum
        if minimum == maximum: return 0.0, 0.0, value
        saturation = (maximum - minimum) / maximum
        red_channel = (maximum - red) / (maximum - minimum)
        green_channel = (maximum - green) / (maximum - minimum)
        blue_channel = (maximum - blue) / (maximum - minimum)
        if red == maximum: hue = blue_channel - green_channel
        elif green == maximum: hue = 2.0 + red_channel - blue_channel
        else: hue = 4.0 + green_channel - red_channel
        hue = (hue / 6.0) % 1.0
        return hue, saturation, value

    @staticmethod
    def rgb_to_hsl(red: float, green: float, blue: float) -> Tuple[float, float, float]:
        maximum = max(red, green, blue); minimum = min(red, green, blue); lightness = (maximum + minimum) / 2.0
        if maximum == minimum: return 0.0, 0.0, lightness
        if lightness < 0.5: saturation = (maximum - minimum) / (maximum + minimum)
        else: saturation = (maximum - minimum) / (2.0 - maximum - minimum)
        red_channel = (maximum - red) / (maximum - minimum)
        green_channel = (maximum - green) / (maximum - minimum)
        blue_channel = (maximum - blue) / (maximum - minimum)
        if red == maximum: hue = blue_channel - green_channel
        elif green == maximum: hue = 2.0 + red_channel - blue_channel
        else: hue = 4.0 + green_channel - red_channel
        hue = (hue / 6.0) % 1.0
        return hue, saturation, lightness

    @staticmethod
    def hsl_to_rgb(hue: float, saturation: float, lightness: float) -> Tuple[float, float, float]:
        if saturation == 0.0: return lightness, lightness, lightness
        if lightness < 0.5: q = lightness * (1.0 + saturation)
        else: q = lightness + saturation - lightness * saturation
        p = 2.0 * lightness - q
        def hue_to_rgb(p: float, q: float, t: float) -> float:
            if t < 0.0: t += 1.0
            if t > 1.0: t -= 1.0
            if t < 1.0 / 6.0: return p + (q - p) * 6.0 * t
            if t < 1.0 / 2.0: return q
            if t < 2.0 / 3.0: return p + (q - p) * (2.0 / 3.0 - t) * 6.0
            return p
        return (hue_to_rgb(p, q, hue + 1.0 / 3.0), hue_to_rgb(p, q, hue), hue_to_rgb(p, q, hue - 1.0 / 3.0))

    @staticmethod
    def hex_to_color(hex_color: str) -> tuple:
        if hex_color.startswith('#'): hex_color = hex_color.lstrip('#')
        hex_length = len(hex_color)
        if hex_length not in [3, 4, 6, 8]: raise ValueError(f'[ ! ] Invalid HEX: "{hex_color}"')
        if hex_length in [3, 4]: hex_color = ''.join([character * 2 for character in hex_color]); hex_length *= 2
        red = int(hex_color[0:2], 16); green = int(hex_color[2:4], 16); blue = int(hex_color[4:6], 16)
        alpha = int(hex_color[6:8], 16) if hex_length == 8 else 255
        return red / 255.0, green / 255.0, blue / 255.0, alpha / 255.0

    @staticmethod
    def color_to_hex(red: float, green: float, blue: float, alpha: float | None = None) -> str:
        red_value, green_value, blue_value = [round(min(255, max(0, value * 255))) for value in (red, green, blue)]
        return f'#{red_value:02X}{green_value:02X}{blue_value:02X}'

    @staticmethod
    def bss_to_str(red: float, green: float, blue: float) -> str:
        return f"{red:.2f}, {green:.2f}, {blue:.2f}"

    @staticmethod
    def parse_bss(text: str) -> Tuple[float, float, float]:
        parts = [part.strip() for part in text.split(',')]
        if len(parts) != 3: raise ValueError('[ ! ] needs 3 floats')
        red, green, blue = (float(parts[0]), float(parts[1]), float(parts[2]))
        if not (0.0 <= red <= 1.0 and 0.0 <= green <= 1.0 and 0.0 <= blue <= 1.0): raise ValueError('[ ! ] values must be 0.0 - 1.0')
        return red, green, blue

    @staticmethod
    def lerp_color(start_color: tuple, end_color: tuple, progress: float) -> tuple:
        red = start_color[0] + (end_color[0] - start_color[0]) * progress
        green = start_color[1] + (end_color[1] - start_color[1]) * progress
        blue = start_color[2] + (end_color[2] - start_color[2]) * progress
        return red, green, blue

# •━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━•

class AdvancedColorPicker(PopupWindow):
    def __init__(self, parent: bs.Widget, position: tuple[float, float], *, initial_color: Sequence[float] = (0.45, 0.2, 0.9), delegate: Any = None, scale: float | None = None, offset: tuple[float, float] = (0.0, 0.0), tag: Any = ''):
        assert bs.app.classic is not None
        uiscale = bs.app.ui_v1.uiscale
        if scale is None: scale = (2.3 if uiscale is bs.UIScale.SMALL else 1.65 if uiscale is bs.UIScale.MEDIUM else 1.23)
        self._delegate, self._transitioning_out, self._cleaned_up = delegate, False, False
        self._tag = tag; width, height, padding, block_height, canvas_padding = 260, 320, 10, 200, 10
        self._color = [initial_color[0], initial_color[1], initial_color[2]]
        self._hsv = ColorSystem.rgb_to_hsv(*self._color)
        self._format, self._format_index, self._last_painted_hue = 'HEX', 0, -1.0
        self._cursor_animating, self._cursor_animation_duration = False, 0.6
        self._cursor_saturation, self._cursor_value = self._hsv[1], self._hsv[2]
        super().__init__(position=position, size=(width, height), scale=scale, focus_position=(8, 8), focus_size=(width - 16, height - 16), bg_color=(0.5, 0.5, 0.5), offset=offset)
        block_y = height - padding - block_height
        self._block_position, self._block_size = (padding, block_y), (width - padding * 2, block_height)
        bs.imagewidget(parent=self.root_widget, position=self._block_position, size=self._block_size, color=(0, 0, 0), opacity=0.7, texture=bs.gettexture('scrollWidget'))
        self.canvas_position = (self._block_position[0] + canvas_padding, self._block_position[1] + self._block_size[1] - canvas_padding - 110)
        self.canvas_size = (self._block_size[0] - canvas_padding * 2, 110)
        self.canvas_columns, self.canvas_rows = 30, 30
        self._canvas_cells = []
        cell_width, cell_height = self.canvas_size[0] / self.canvas_columns, self.canvas_size[1] / self.canvas_rows
        for row_index in range(self.canvas_rows):
            for column_index in range(self.canvas_columns):
                saturation, value = column_index / (self.canvas_columns - 1), row_index / (self.canvas_rows - 1)
                cell_color = ColorSystem.hsv_to_rgb(self._hsv[0], saturation, value)
                cell_widget = bs.imagewidget(parent=self.root_widget, position=(self.canvas_position[0] + column_index * cell_width, self.canvas_position[1] + row_index * cell_height), size=(cell_width + 0.5, cell_height + 0.5), texture=bs.gettexture('white'), color=cell_color); self._canvas_cells.append(cell_widget)
                bs.buttonwidget(parent=self.root_widget, position=(self.canvas_position[0] + column_index * cell_width, self.canvas_position[1] + row_index * cell_height), size=(cell_width, cell_height), texture=bs.gettexture('empty'), label='', enable_sound=False, button_type='square', autoselect=False, on_activate_call=bs.WeakCallStrict(self._on_canvas_click, column_index, row_index))
        self._last_painted_hue = self._hsv[0]
        self._canvas_cursor = bs.imagewidget(parent=self.root_widget, position=(self.canvas_position[0] + self.canvas_size[0] * self._cursor_saturation - 4, self.canvas_position[1] + self.canvas_size[1] * self._cursor_value - 4), size=(8, 8), texture=bs.gettexture('circle'), color=(1, 1, 1))
        slider_y = self._block_position[1] + 8
        self._color_slider = ColorSlider(parent=self.root_widget, position=(self._block_position[0] + canvas_padding, slider_y), size=(self._block_size[0] - canvas_padding * 2, 60), hue=self._hsv[0], value=self._hsv[2], on_hue_change=self._on_hue_change, on_value_change=self._on_value_change, on_hue_live=self._on_hue_live, on_value_live=self._on_value_live)
        self.formats = ['HEX', 'BSS', 'RGB', 'HSL', 'HSB']
        mode_y = block_y - 30; input_y = mode_y - 27
        self._format_control = ModeSlider(parent=self.root_widget, position=(padding, mode_y), size=(width - padding * 2, 24), segments=self.formats, selected_index=0, on_change_callback=self._change_format)
        self._input_textbox = bs.textwidget(parent=self.root_widget, position=(padding * 1.3, input_y), size=((width - padding) * 0.6, 20), text='', h_align='center', v_align='center', maxwidth=70, editable=True, max_chars=20, color=(0.9, 0.9, 0.9), glow_type='uniform')
        bs.buttonwidget(parent=self.root_widget, position=(width - padding - 70, input_y + 2), size=(60, 20), color=(0.6, 0.6, 0.6), textcolor=(1.0, 1.0, 1.0), text_scale=0.45, label=bs.Lstr(resource='applyText'), autoselect=True, enable_sound=False, on_activate_call=bs.WeakCallStrict(self._apply_input))
        done_button = bs.buttonwidget(parent=self.root_widget, position=(width * 0.5 - 60, 15), size=(120, 30), text_scale=0.55, color=(0.6, 0.6, 0.6), textcolor=(1.0, 1.0, 1.0), label=bs.Lstr(resource='doneText'), enable_sound=False, on_activate_call=bs.WeakCallStrict(self._transition_out), autoselect=True)
        bs.containerwidget(edit=self.root_widget, start_button=done_button)
        self._update_ui()

    def get_tag(self) -> Any:
        return self._tag

    def _change_format(self, index: int, format_name: str):
        self._format_index, self._format = index, format_name
        self._update_ui()

    def _on_canvas_click(self, column_index: int, row_index: int):
        target_saturation = column_index / (self.canvas_columns - 1)
        target_value = row_index / (self.canvas_rows - 1)
        self._cursor_animating = True
        self._cursor_animation_start_time = time.time()
        self._cursor_saturation_from, self._cursor_value_from = self._cursor_saturation, self._cursor_value
        self._cursor_saturation_to, self._cursor_value_to = target_saturation, target_value
        if self._color_slider: self._color_slider._start_value_animation(target_value)
        self._hsv = (self._hsv[0], target_saturation, target_value)
        self._cursor_tick()

    def _cursor_tick(self):
        if not self._cursor_animating or self._transitioning_out: self._cursor_animating = False; return
        elapsed = time.time() - self._cursor_animation_start_time
        if elapsed >= self._cursor_animation_duration: self._cursor_animating = False; progress = 1.0
        else: progress = elapsed / self._cursor_animation_duration; progress = progress * progress * (3.0 - 2.0 * progress); bs.apptimer(0.005, self._cursor_tick)
        self._cursor_saturation = self._cursor_saturation_from + (self._cursor_saturation_to - self._cursor_saturation_from) * progress
        self._cursor_value = self._cursor_value_from + (self._cursor_value_to - self._cursor_value_from) * progress
        cursor_x = self.canvas_position[0] + self._cursor_saturation * self.canvas_size[0] - 4
        cursor_y = self.canvas_position[1] + self._cursor_value * self.canvas_size[1] - 4
        try: bs.imagewidget(edit=self._canvas_cursor, position=(cursor_x, cursor_y))
        except: self._cursor_animating = False; return
        self._color = list(ColorSystem.hsv_to_rgb(self._hsv[0], self._cursor_saturation, self._cursor_value))
        self._repaint_ui_live()
        if progress >= 1.0 and self._delegate is not None: self._delegate.color_picker_selected_color(self, tuple(self._color))

    def _on_hue_live(self, hue: float):
        self._hsv = (hue, self._hsv[1], self._hsv[2])
        self._color = list(ColorSystem.hsv_to_rgb(*self._hsv))
        self._update_canvas_colors_live(hue)
        self._repaint_ui_live()

    def _on_value_live(self, value: float):
        self._hsv, self._cursor_value = (self._hsv[0], self._hsv[1], value), value
        self._color = list(ColorSystem.hsv_to_rgb(*self._hsv))
        cursor_x, cursor_y = self.canvas_position[0] + self._cursor_saturation * self.canvas_size[0] - 4, self.canvas_position[1] + self._cursor_value * self.canvas_size[1] - 4
        try: bs.imagewidget(edit=self._canvas_cursor, position=(cursor_x, cursor_y))
        except: pass
        self._repaint_ui_live()

    def _on_hue_change(self, hue: float):
        self._hsv = (hue, self._hsv[1], self._hsv[2])
        self._color = list(ColorSystem.hsv_to_rgb(*self._hsv))
        self._update_canvas_colors_live(hue)
        self._repaint_ui_live()
        if self._delegate is not None: self._delegate.color_picker_selected_color(self, tuple(self._color))

    def _on_value_change(self, value: float):
        self._hsv = (self._hsv[0], self._hsv[1], value)
        self._color = list(ColorSystem.hsv_to_rgb(*self._hsv))
        self._update_ui()
        if self._delegate is not None: self._delegate.color_picker_selected_color(self, tuple(self._color))

    def _update_canvas_colors_live(self, hue: float):
        if not self._canvas_cells: return
        self._last_painted_hue = hue
        for row_index in range(self.canvas_rows):
            for column_index in range(self.canvas_columns):
                saturation = column_index / (self.canvas_columns - 1)
                value = row_index / (self.canvas_rows - 1)
                cell_color = ColorSystem.hsv_to_rgb(hue, saturation, value)
                cell_index = row_index * self.canvas_columns + column_index
                try: bs.imagewidget(edit=self._canvas_cells[cell_index], color=cell_color)
                except: return

    def _format_text(self, red: float, green: float, blue: float) -> str:
        if self._format == 'HEX': return ColorSystem.color_to_hex(red, green, blue)
        elif self._format == 'BSS': return ColorSystem.bss_to_str(red, green, blue)
        elif self._format == 'RGB': return f"{int(red * 255)}, {int(green * 255)}, {int(blue * 255)}"
        elif self._format == 'HSL':
            hue, saturation, lightness = ColorSystem.rgb_to_hsl(red, green, blue)
            return f"{int(hue * 360)}, {int(saturation * 100)}%, {int(lightness * 100)}%"
        elif self._format == 'HSB':
            hue, saturation, value = self._hsv
            return f"{int(hue * 360)}, {int(saturation * 100)}%, {int(value * 100)}%"
        return ""

    def _repaint_ui_live(self):
        if not self.root_widget or self._transitioning_out: return
        red, green, blue = self._color
        display_text = self._format_text(red, green, blue)
        try: bs.textwidget(edit=self._input_textbox, text=display_text)
        except: pass

    def _apply_input(self):
        try:
            current_text = cast(str, bs.textwidget(query=self._input_textbox))
            target_color = None
            if self._format == 'HEX': parsed = ColorSystem.hex_to_color(current_text); target_color = [parsed[0], parsed[1], parsed[2]]
            elif self._format == 'BSS': red_value, green_value, blue_value = ColorSystem.parse_bss(current_text); target_color = [red_value, green_value, blue_value]
            elif self._format == 'RGB':
                parts = [float(part.strip()) / 255.0 for part in current_text.split(',')]
                if len(parts) == 3: target_color = parts
            elif self._format == 'HSL':
                parts = current_text.replace('%', '').split(',')
                if len(parts) == 3:
                    hue, saturation, lightness = float(parts[0]) / 360.0, float(parts[1]) / 100.0, float(parts[2]) / 100.0
                    target_color = list(ColorSystem.hsl_to_rgb(hue, saturation, lightness))
            elif self._format == 'HSB':
                parts = current_text.replace('%', '').split(',')
                if len(parts) == 3:
                    hue, saturation, value = float(parts[0]) / 360.0, float(parts[1]) / 100.0, float(parts[2]) / 100.0
                    target_color = list(ColorSystem.hsv_to_rgb(hue, saturation, value))
            if target_color is None: return
            current_red, current_green, current_blue = self._color
            target_red, target_green, target_blue = target_color
            if abs(current_red - target_red) < 0.001 and abs(current_green - target_green) < 0.001 and abs(current_blue - target_blue) < 0.001: return
            target_hue, target_saturation, target_value = ColorSystem.rgb_to_hsv(*target_color)
            self._hsv = (target_hue, target_saturation, target_value)
            self._color = [target_red, target_green, target_blue]
            self._update_canvas_colors_live(target_hue)
            self._repaint_ui_live()
            if self._delegate is not None: self._delegate.color_picker_selected_color(self, tuple(self._color))
            if self._color_slider: self._color_slider._start_hue_animation(target_hue); self._color_slider._start_value_animation(target_value)
            self._cursor_animating = True
            self._cursor_animation_start_time = time.time()
            self._cursor_saturation_from, self._cursor_value_from = self._cursor_saturation, self._cursor_value
            self._cursor_saturation_to, self._cursor_value_to = target_saturation, target_value
            self._cursor_tick()
        except: pass

    def _update_ui(self):
        if not self.root_widget or self._transitioning_out: return
        red, green, blue = self._color
        hue, saturation, value = self._hsv
        if not self._cursor_animating:
            self._cursor_saturation, self._cursor_value = saturation, value
            cursor_x, cursor_y = self.canvas_position[0] + (saturation * self.canvas_size[0]) - 4, self.canvas_position[1] + (value * self.canvas_size[1]) - 4
            try: bs.imagewidget(edit=self._canvas_cursor, position=(cursor_x, cursor_y))
            except: pass
        if self._color_slider: self._color_slider.set_hue(hue, fire=False); self._color_slider.set_value(value, fire=False) 
        try: bs.textwidget(edit=self._input_textbox, text=self._format_text(red, green, blue))
        except: pass

    def _transition_out(self) -> None:
        if self._transitioning_out: return
        self._transitioning_out = True
        self._input_timer = None; self._cursor_animating = False
        if self._format_control: self._format_control._on_change_callback = None
        if self._color_slider: self._color_slider._on_hue_change = None; self._color_slider._on_value_change = None; self._color_slider._on_hue_live = None; self._color_slider._on_value_live = None; self._color_slider._alive = False
        if self._delegate is not None: self._delegate.color_picker_closing(self); self._delegate = None
        try: bs.containerwidget(edit=self.root_widget, transition='out_scale')
        except: pass
        bs.apptimer(0.6, self._final_cleanup)

    def _final_cleanup(self):
        if self._cleaned_up: return
        self._cleaned_up = True
        if self._color_slider:
            try: self._color_slider.delete()
            except: pass
            self._color_slider = None
        if self._format_control:
            try: self._format_control.delete()
            except: pass
            self._format_control = None
        self._canvas_cells = []; self._canvas_cursor = None
        self._input_textbox = None; self._input_timer = None; self._delegate = None

    @override
    def on_popup_cancel(self) -> None:
        self._transition_out()

# •━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━•

class ColorPicker(PopupWindow):
    def __init__(self, parent: bs.Widget, position: tuple[float, float], *, initial_color: Sequence[float] = (1.0, 1.0, 1.0), delegate: Any = None, scale: float | None = None, offset: tuple[float, float] = (0.0, 0.0), tag: Any = ''):
        assert bs.app.classic is not None
        raw_colors = bs.app.classic.get_player_colors()
        self.colors = [raw_colors[0:4], raw_colors[4:8], raw_colors[8:12], raw_colors[12:16]]
        uiscale = bs.app.ui_v1.uiscale
        if scale is None: scale = (2.3 if uiscale is bs.UIScale.SMALL else 1.65 if uiscale is bs.UIScale.MEDIUM else 1.23)
        self._parent, self._position, self._scale, self._offset = parent, position, scale, offset
        self._delegate, self._transitioning_out, self._tag = delegate, False, tag
        self._initial_color = initial_color
        super().__init__(position=position, size=(210, 240), scale=scale, focus_position=(10, 10), focus_size=(190, 220), bg_color=(0.5, 0.5, 0.5), offset=offset)
        rows, closest_distance, closest_position = [], 9999.0, (0, 0)
        for row_index in range(4):
            current_row = []; rows.append(current_row)
            for column_index in range(4):
                current_color = self.colors[row_index][column_index]; color_distance = abs(current_color[0] - initial_color[0]) + abs(current_color[1] - initial_color[1]) + abs(current_color[2] - initial_color[2])
                if color_distance < closest_distance: closest_position, closest_distance = (column_index, row_index), color_distance
                swatch_button = bs.buttonwidget(parent=self.root_widget, position=(22 + 45 * column_index, 185 - 45 * row_index), size=(35, 40), label='', button_type='square', on_activate_call=bs.WeakCallStrict(self._select, column_index, row_index), autoselect=True, color=current_color, extra_touch_border_scale=0.0, enable_sound=False); current_row.append(swatch_button)
        advanced_button = bs.buttonwidget(parent=self.root_widget, position=(105 - 60, 13), color=(0.7, 0.7, 0.7), text_scale=0.5, textcolor=(0.8, 0.8, 0.8), size=(120, 30), label=bs.Lstr(resource=f'settingsWindow.advancedText'), autoselect=True, enable_sound=False, on_activate_call=bs.WeakCallStrict(self._select_advanced_picker))
        if closest_distance < 0.03: bs.containerwidget(edit=self.root_widget, selected_child=rows[closest_position[1]][closest_position[0]])
        else: bs.containerwidget(edit=self.root_widget, selected_child=advanced_button)

    def get_tag(self) -> Any:
        return self._tag

    def _select_advanced_picker(self) -> None:
        AdvancedColorPicker(parent=self._parent, position=self._position, initial_color=self._initial_color, delegate=self._delegate, scale=self._scale, offset=self._offset, tag=self._tag)
        self._delegate = None; self._transition_out()

    def _select(self, column_index: int, row_index: int) -> None:
        if self._delegate: self._delegate.color_picker_selected_color(self, self.colors[row_index][column_index])
        bs.apptimer(0.05, self._transition_out)

    def _transition_out(self) -> None:
        if not self._transitioning_out:
            self._transitioning_out = True
            if self._delegate is not None: self._delegate.color_picker_closing(self); self._delegate = None
            try: bs.containerwidget(edit=self.root_widget, transition='out_scale')
            except Exception: pass

    @override
    def on_popup_cancel(self) -> None:
        self._transition_out()

# •━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━•

# ba_meta export babase.Plugin
class system(bb.Plugin):
    def plugin_information(self):
        self.name = "pickero"
        self.icon = "achievementMine"
        self.version = 1.0
        self.creator = "@uwu-user"
        self.release_date = "2026/9/29"
        self.type = "System/UI"

    def __init__(self) -> None:
        if bb.app.env.engine_build_number > 22837: print("[ colorpicker ] skipped — not compatible with 1.8 alpha test builds [ I dont want to! this one only for api 9 - 1.7.62 or lower ]")
        else: colorpicker.ColorPicker = ColorPicker