# ba_meta require api 9

import babase
import bauiv1 as bui
import bascenev1 as bs
import bauiv1lib.ingamemenu as ingamemenu
import math
import bascenev1lib
from bascenev1lib.actor.bomb import Bomb

EXCLUDED_PLAYERS = ["Mma", "BigFire", "TAHA1387", "Player4"]
PUNCH_RADIUS = 1.1


class TysonDuelMode:
    def __init__(self):
        self.enabled = False
        self.update_timer = None
        self.locators_dict = {}
        self.previous_in_range = set()
        self.last_activity = None

    def enable(self):
        if self.enabled: return
        self.enabled = True
        bui.screenmessage("دوعل مود فعال شد!", color=(0, 1, 0))
        self.update_timer = babase.AppTimer(0.1, self.update_logic, repeat=True)

    def disable(self):
        if not self.enabled: return
        self.enabled = False
        bui.screenmessage("دوعل مود غیر فعال شد!", color=(1, 0, 0))
        self.update_timer = None
        activity = bs.get_foreground_host_activity()
        if activity:
            with activity.context:
                self.clear_locators()
        else:
            self.locators_dict.clear()

    def clear_locators(self):
        for loc_tuple in self.locators_dict.values():
            for loc in loc_tuple:
                try:
                    if loc and loc.exists():
                        loc.delete()
                except Exception: pass
        self.locators_dict.clear()
        self.previous_in_range.clear()

    def update_logic(self):
        if not self.enabled: return
        
        activity = bs.get_foreground_host_activity()
        if not activity: 
            return
            
        if activity != self.last_activity:
            with activity.context:
                self.clear_locators()
            self.last_activity = activity

        with activity.context:
            try:
                spaz_nodes = [node for node in bs.getnodes() if node.getnodetype() == 'spaz']
                special_players_nodes = []
                target_nodes = []

                for node in spaz_nodes:
                    player_name = ""
                    try:
                        delegate = node.getdelegate(object)
                        if delegate:
                            if hasattr(delegate, 'source_player') and delegate.source_player:
                                player_name = delegate.source_player.getname(icon=False)
                            elif hasattr(delegate, 'getplayer'):
                                p = delegate.getplayer(bs.Player, False)
                                if p: player_name = p.getname(icon=False)
                    except Exception:
                        pass

                    if player_name in EXCLUDED_PLAYERS:
                        special_players_nodes.append(node)
                    else:
                        target_nodes.append(node)

                dead_nodes = []
                for t_node, loc_tuple in self.locators_dict.items():
                    try:
                        if not t_node.exists():
                            for loc in loc_tuple:
                                if loc and loc.exists():
                                    loc.delete()
                            dead_nodes.append(t_node)
                    except Exception:
                        dead_nodes.append(t_node)
                        
                for n in dead_nodes:
                    del self.locators_dict[n]

                for node in target_nodes:
                    if node not in self.locators_dict and node.exists():
                        try:
                            pos = node.position
                      
                            loc_inner = bs.newnode('locator', attrs={
                                'shape': 'circle',
                                'position': pos,
                                'color': (1, 0, 0),
                                'opacity': 0.05,
                                'draw_beauty': False,
                                'additive': False
                            })
                            
                            loc_outer = bs.newnode('locator', attrs={
                                'shape': 'circleOutline',
                                'position': pos,
                                'size': [PUNCH_RADIUS * 2.0],
                                'color': (1, 1, 0),
                                'draw_beauty': False,
                                'additive': True
                            })
                      
                            node.connectattr('position', loc_inner, 'position')
                            node.connectattr('position', loc_outer, 'position')

                    
                            bs.animate_array(loc_inner, 'size', 1, {
                                0.0: [0.0],
                                0.2: [PUNCH_RADIUS * 2.2],
                                0.25: [PUNCH_RADIUS * 2.0]
                            })
                            
                            bs.animate(loc_outer, 'opacity', {
                                0: 0.0,
                                0.4: 0.1
                            })

                            self.locators_dict[node] = (loc_inner, loc_outer)
                        except Exception:
                            pass

                current_in_range = set()
                
                for sp_node in special_players_nodes:
                    if not sp_node.exists(): continue
                    try: sp_pos = sp_node.position
                    except: continue
                    
                    for t_node in target_nodes:
                        if not t_node.exists(): continue
                        try: t_pos = t_node.position
                        except: continue
                        
                        dist = math.sqrt((sp_pos[0] - t_pos[0])**2 + (sp_pos[1] - t_pos[1])**2 + (sp_pos[2] - t_pos[2])**2)
                        
                        if dist <= PUNCH_RADIUS:
                            pair_id = (id(sp_node), id(t_node))
                            current_in_range.add(pair_id)

                for pair in current_in_range:
                    if pair not in self.previous_in_range:
                        babase.pushcall(lambda: bui.screenmessage("شما وارد محدوده شدید!", color=(1, 1, 0)), from_other_thread=False)
                        
                self.previous_in_range = current_in_range
                            
            except Exception as e:
                print(f"TysonDM Error: {e}")

duel_manager = TysonDuelMode()


original_ingame_menu_init = ingamemenu.InGameMenuWindow.__init__

def new_ingame_menu_init(self, *args, **kwargs):
    original_ingame_menu_init(self, *args, **kwargs)
    self._dm_button = bui.buttonwidget(
        parent=self._root_widget,
        position=(-70, self._height - 70),
        size=(55, 55),
        label='DM',
        button_type='square',
        color=(0.2, 0.4, 0.7),
        on_activate_call=self.open_dm_options
    )

def open_dm_options(self):
    DMPopupWindow(position=self._dm_button.get_screen_space_center())

ingamemenu.InGameMenuWindow.__init__ = new_ingame_menu_init
ingamemenu.InGameMenuWindow.open_dm_options = open_dm_options

class DMPopupWindow(bui.Window):
    def __init__(self, position):
        width = 150
        height = 170
        uiscale = bui.app.ui_v1.uiscale
        scale_origin = position
        super().__init__(root_widget=bui.containerwidget(
            size=(width, height),
            transition='scale_in',
            scale_origin_stack_offset=scale_origin,
            scale=1.5 if uiscale is babase.UIScale.SMALL else 1.2
        ))
        bui.buttonwidget(
            parent=self._root_widget,
            position=(20, 115),
            size=(110, 40),
            label='Enable',
            color=(0.1, 0.8, 0.1),
            on_activate_call=self._enable_mod
        )
        bui.buttonwidget(
            parent=self._root_widget,
            position=(20, 65),
            size=(110, 40),
            label='Disable',
            color=(0.8, 0.1, 0.1),
            on_activate_call=self._disable_mod
        )
        bui.buttonwidget(
            parent=self._root_widget,
            position=(20, 15),
            size=(110, 40),
            label='بستن',
            color=(0.5, 0.5, 0.5),
            on_activate_call=self._close_menu
        )

    def _enable_mod(self):
        duel_manager.enable()
        self._close_menu()

    def _disable_mod(self):
        duel_manager.disable()
        self._close_menu()

    def _close_menu(self):
        if self._root_widget:
            self._root_widget.delete()


# ba_meta export babase.Plugin
class TysonModPlugin(babase.Plugin):
    
    def new_bomb_init(func):
        def wrapper(*args, **kwargs):
       
            func(*args, **kwargs)

            args[0].radius_visualizer = bs.newnode('locator',
                                                   owner=args[0].node,
                                                   attrs={
                                                       'shape': 'circle',
                                                       'color': (1, 0, 0),
                                                       'opacity': 0.05,
                                                       'draw_beauty': False,
                                                       'additive': False
                                                   })
            args[0].node.connectattr('position', args[0].radius_visualizer, 'position')
            
            bs.animate_array(args[0].radius_visualizer, 'size', 1, {
                0.0: [0.0],
                0.2: [args[0].blast_radius * 2.2],
                0.25: [args[0].blast_radius * 2.0]
            })


            args[0].radius_visualizer_circle = bs.newnode('locator',
                                                          owner=args[0].node,
                                                          attrs={
                                                              'shape': 'circleOutline',
                                                              'size': [args[0].blast_radius * 2.0],
                                                              'color': (1, 1, 0),
                                                              'draw_beauty': False,
                                                              'additive': True
                                                          })
            args[0].node.connectattr('position', args[0].radius_visualizer_circle, 'position')
            
            bs.animate(
                args[0].radius_visualizer_circle, 'opacity', {
                    0: 0.0,
                    0.4: 0.1
                })
        return wrapper

    bascenev1lib.actor.bomb.Bomb.__init__ = new_bomb_init(bascenev1lib.actor.bomb.Bomb.__init__)

    def on_app_running(self):
        pass