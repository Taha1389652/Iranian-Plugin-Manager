# ba_meta require api 7

import babase
import random
import bascenev1 as bs
import bauiv1 as bui
from bauiv1lib import party
import re
import json
import os
from babase import (
    clipboard_is_supported as CIS,
    clipboard_get_text as CGT,
    clipboard_has_text as CHT,
    Plugin
)
from bascenev1 import (
    disconnect_from_host as BYE,
    connect_to_party as CON,
    protocol_version as PT,
    get_game_roster as GGR
)
from typing import Any
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
    get_game_roster
)
from _babase import get_string_width as strw
from bauiv1lib import party
from babase import apptimer as teck
from bauiv1 import Call

pr = 'autoresponder_'

def get_file(button_index=None):
    if button_index is not None:
        config_path = os.path.join(os.path.dirname(__file__), f'custom_commands_button_{button_index}.json')
    else:
        config_path = os.path.join(os.path.dirname(__file__), 'custom_commands.json')
    return config_path

def load(button_index=None):
    try:
        commands_file = get_file(button_index)
        if os.path.exists(commands_file):
            with open(commands_file, 'r', encoding='utf-8') as f:
                commands_data = json.load(f)
                return commands_data
        else:
            default_texts = [
                "hug a", "e", "a chat", "sl a", "bm", "f i", "vip$", "k$", "i",
                "fish$", "spidy$", "cbb$", "g$", "z$", "fr a", "1", "2", "d a", "sol$",
                "Player 1", "Player 2", "Player 3", "Player 4", "Player 5", 
                "Player 6", "Player 7", "Player 8"
            ]
            if button_index < len(default_texts):
                default_commands = [default_texts[button_index]]
                save(default_commands, button_index)
                return default_commands
            else:
                return [buttons[button_index]["label"]]
    except Exception as e:
        return [buttons[button_index]["label"]]

def save(commands_data, button_index=None):
    try:
        commands_file = get_file(button_index)
        with open(commands_file, 'w', encoding='utf-8') as f:
            json.dump(commands_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        return False

kj = []
player_buttons = []

def update_players():
    global kj
    df = []
    kj = []
    gh = GGR()
    for i in gh:
        for j in i:
            if j == 'players':
                df.append((i['players'], i['client_id']))
    
    for u in range(1, len(df)):
        try:
            kj.append((df[u][0][0]['name'], df[u][1]))
        except:
            kj.append(('None', ' '))
    
    while 8 > len(kj):
        kj.append(('None', ' '))

def update_player_buttons():
    global player_buttons, kj
    
    update_players()
    
    for i, btn_data in enumerate(player_buttons):
        if i < len(kj):
            player_name = kj[i][0]
            player_id = kj[i][1]
            
            if len(player_name) > 8:
                display_name = player_name[:8] + '...'
            else:
                display_name = player_name
                
            btn_data['button'].label = display_name
            
            if player_id != ' ':
                btn_data['button'].color = (0.6, 0.8, 1)
            else:
                btn_data['button'].color = (0.5, 0.5, 0.5)

def send_commands(client_id, button_index=None, playername=None):
    if client_id == " ":
        player_commands = load(button_index)
        
        if len(player_commands) == 1 and '|' in player_commands[0]:
            commands = [cmd.strip() for cmd in player_commands[0].split('|') if cmd.strip()]
            for cmd in commands:
                bs.chatmessage(cmd)
        else:
            for cmd in player_commands:
                bs.chatmessage(cmd)
    else:
        player_commands = load(button_index)
        
        if len(player_commands) == 1 and '|' in player_commands[0]:
            commands = [cmd.strip() for cmd in player_commands[0].split('|') if cmd.strip()]
            for cmd in commands:
                CM(f'%{cmd} {client_id}')
        else:
            for cmd in player_commands:
                CM(f'%{cmd} {client_id}')

class ButtonWindow:
    def __init__(self, button_index, button_label="Button", button_type="chat"):
        self.window = None
        self.input_field = None
        self.button_index = button_index
        self.button_label = button_label
        self.button_type = button_type
    
    def show(self):
        if self.window:
            try:
                self.window.delete()
            except:
                pass
        
        button_commands = load(self.button_index)
        
        self.window = cw(
            size=(400, 300),
            parent=bui.get_special_widget('overlay_stack'),
            position=(200, 200),
            background=True,
            on_outside_click_call=self.close
        )
        
        title_text = f"Button {self.button_index + 1}"
        if self.button_type == "player":
            title_text += " - Player Button"
        else:
            title_text += " - Chat Button"
            
        title = tw(
            parent=self.window,
            text=title_text,
            position=(175, 270),
            scale=1.0,
            color=(1, 1, 1),
            h_align='center'
        )
        
        self.input_field = tw(
            parent=self.window,
            text=button_commands[0] if button_commands else '',
            editable=True,
            position=(50, 200),
            size=(300, 40),
            scale=0.8,
            color=(1, 1, 1),
            h_align='left',
            v_align='center',
            max_chars=200
        )
        
        def save_commands():
            if self.input_field:
                new_text = tw(query=self.input_field).strip()
                
                if new_text:
                    new_commands = [new_text]
                    
                    if save(new_commands, self.button_index):
                        bui.screenmessage(f"Commands saved", color=(0, 1, 0))
                        self.close()
                    else:
                        bui.screenmessage("Error", color=(1, 0, 0))
                else:
                    bui.screenmessage("Enter commands", color=(1, 0, 0))
        
        save_btn = bw(
            parent=self.window,
            position=(80, 140),
            size=(100, 40),
            label="Save",
            on_activate_call=save_commands
        )
        
        cancel_btn = bw(
            parent=self.window,
            position=(220, 140),
            size=(100, 40),
            label="Cancel",
            on_activate_call=self.close
        )
        
        def reset_default():
            default_texts = [
                "hug a", "e", "a chat", "sl a", "bm", "f i", "vip$", "k$", "i",
                "fish$", "spidy$", "cbb$", "g$", "z$", "fr a", "1", "2", "d a", "sol$",
                "Player 1", "Player 2", "Player 3", "Player 4", "Player 5", 
                "Player 6", "Player 7", "Player 8"
            ]
            if self.button_index < len(default_texts):
                default_commands = [default_texts[self.button_index]]
            else:
                default_commands = [buttons[self.button_index]["label"]]
                
            if save(default_commands, self.button_index):
                bui.screenmessage(f"Reset", color=(0, 1, 0))
                self.close()
            else:
                bui.screenmessage("Error", color=(1, 0, 0))
        
        reset_btn = bw(
            parent=self.window,
            position=(150, 90),
            size=(100, 30),
            label="Reset to Default",
            on_activate_call=reset_default
        )
    
    def close(self):
        if self.window:
            self.window.delete()
            self.window = None
            self.input_field = None

buttons = [
    {"label": "hug a", "x": -190, "y": 50, "width": 130, "height": 43, "type": "chat"},
    {"label": "e", "x": -190, "y": 83, "width": 130, "height": 43, "type": "chat"},
    {"label": "a chat", "x": -190, "y": 116, "width": 130, "height": 43, "type": "chat"},
    {"label": "sl a", "x": -190, "y": 149, "width": 130, "height": 43, "type": "chat"},
    {"label": "bm", "x": -190, "y": 182, "width": 130, "height": 43, "type": "chat"},
    {"label": "f i", "x": -190, "y": 215, "width": 130, "height": 43, "type": "chat"},
    {"label": "vip$", "x": -190, "y": 248, "width": 130, "height": 43, "type": "chat"},
    {"label": "k$", "x": -190, "y": 281, "width": 130, "height": 43, "type": "chat"},
    {"label": "i", "x": -190, "y": 314, "width": 130, "height": 43, "type": "chat"},
    {"label": "fish$", "x": -300, "y": 50, "width": 130, "height": 43, "type": "chat"},
    {"label": "spidy$", "x": -300, "y": 83, "width": 130, "height": 43, "type": "chat"},
    {"label": "cbb$", "x": -300, "y": 116, "width": 130, "height": 43, "type": "chat"},
    {"label": "g$", "x": -300, "y": 149, "width": 130, "height": 43, "type": "chat"},
    {"label": "z$", "x": -300, "y": 182, "width": 130, "height": 43, "type": "chat"},
    {"label": "fr a", "x": -300, "y": 215, "width": 130, "height": 43, "type": "chat"},
    {"label": "1", "x": -300, "y": 248, "width": 130, "height": 43, "type": "chat"},
    {"label": "2", "x": -300, "y": 281, "width": 130, "height": 43, "type": "chat"},
    {"label": "d a", "x": -300, "y": 314, "width": 130, "height": 43, "type": "chat"},
    {"label": "sol$", "x": -300, "y": 347, "width": 130, "height": 43, "type": "chat"},
    {"label": "Player 1", "x": -90, "y": 10, "width": 100, "height": 43, "type": "player"},
    {"label": "Player 2", "x": -10, "y": 10, "width": 100, "height": 43, "type": "player"},
    {"label": "Player 3", "x": 70, "y": 10, "width": 100, "height": 43, "type": "player"},
    {"label": "Player 4", "x": 150, "y": 10, "width": 100, "height": 43, "type": "player"},
    {"label": "Player 5", "x": 230, "y": 10, "width": 100, "height": 43, "type": "player"},
    {"label": "Player 6", "x": 310, "y": 10, "width": 100, "height": 43, "type": "player"},
    {"label": "Player 7", "x": 390, "y": 10, "width": 100, "height": 43, "type": "player"},
    {"label": "Player 8", "x": 470, "y": 10, "width": 100, "height": 43, "type": "player"},
]

# ba_meta export plugin
class Plugin(babase.Plugin):
    def __init__(self):
        super().__init__()
        o = party.PartyWindow.__init__
        self.update_timer = None
        
        def custom_party_iniit(s_party, *a, **k):
            global root_widget, menu_button, kj, player_buttons
            
            rr = o(s_party, *a, **k)
            root_widget = s_party._root_widget
            update_players()
            player_buttons = [] 
            button_windows = []
            
            for i, btn in enumerate(buttons):
                button_window = ButtonWindow(i, btn["label"], btn["type"])
                button_windows.append(button_window)
                
                if btn["type"] == "player":
                    player_index = i - 19  
                    if player_index < len(kj):
                        player_name = kj[player_index][0]
                        player_id = kj[player_index][1]
                        
                        if len(player_name) > 8:
                            display_name = player_name[:8] + '...'
                        else:
                            display_name = player_name
                    else:
                        display_name = "None"
                        player_id = " "

                    player_button = bw(
                        parent=s_party._root_widget,
                        position=(btn["x"], s_party._height - btn["y"]),
                        size=(btn["width"], btn["height"]),
                        on_activate_call=Call(send_commands, player_id, i, display_name),
                        label=display_name,
                        color=(0.6, 0.8, 1) if player_id != ' ' else (0.5, 0.5, 0.5),
                        autoselect=True,
                        button_type='square',
                        scale=0.7,
                        iconscale=1.2
                    )

                    player_buttons.append({
                        'button': player_button,
                        'index': player_index,
                        'original_index': i
                    })
                    
                else:
                    button_commands = load(i)
                    display_text = button_commands[0] if button_commands else btn["label"]
                    if len(display_text) > 12:
                        display_text = display_text[:12] + '...'
                    
                    chat_button = bw(
                        parent=s_party._root_widget,
                        position=(btn["x"], s_party._height - btn["y"]),
                        size=(btn["width"], btn["height"]),
                        label=display_text,
                        autoselect=True,
                        button_type='square',
                        on_activate_call=Call(send_commands, " ", i),  
                        color=(-10, -10, -10),
                        scale=0.7,
                        iconscale=1.2
                    )

                edit_btn = bw(
                    parent=s_party._root_widget,
                    position=(btn["x"] + btn["width"] - 40, s_party._height - btn["y"] + 20),
                    size=(20, 20),
                    label="E",
                    on_activate_call=button_window.show,
                    color=(0.8, 0.8, 1),
                    text_scale=0.5,
                    textcolor=(0, 0, 0)
                )

            self.start_update_timer()
            
            return rr
        
        party.PartyWindow.__init__ = custom_party_iniit
    
    def start_update_timer(self):
        def update_cycle():
            if player_buttons: 
                update_player_buttons()
            self.update_timer = teck(1.0, update_cycle)
        self.update_timer = teck(1.0, update_cycle)
    
    def on_app_running(self):
        bui.screenmessage("BsRush_LifeMod loaded \nTelegram : @BsRush_Mod", color=(0, 1, 0))