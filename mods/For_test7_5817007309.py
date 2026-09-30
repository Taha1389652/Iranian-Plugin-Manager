# Released under the MIT License. See LICENSE for details.
#
"""by hwp, don't edit this map unless I allow you to."""
# ba_meta require api 9
# pylint: disable=too-many-lines

from __future__ import annotations

from typing import TYPE_CHECKING

import babase
import bascenev1 as bs
import bauiv1 as bui
from bascenev1 import _map
from bascenev1lib.gameutils import SharedObjects
from bascenev1lib.maps import *
import random

if TYPE_CHECKING:
    from typing import Any, Dict, Sequence

class CustomModel(bs.Actor):

    def __init__(self, position: Sequence[float] = (0, 0, 0),model: str = '', texture: str = '', scale: float = 1.0):
        super().__init__()

        shared = SharedObjects.get()

        self._collide_custom=bs.Material()
        self.dont_collide=bs.Material()

        self._collide_custom.add_actions(conditions=('they_are_different_node_than_us', ),actions=(('modify_part_collision', 'collide', False)))
        self._collide_custom.add_actions(conditions=('they_have_material', self.dont_collide), actions=(('modify_part_collision', 'collide', True)))

        self.dont_collide.add_actions(conditions=('they_are_different_node_than_us', ),actions=(('modify_part_collision', 'collide', False)))
        self.dont_collide.add_actions(conditions=('they_have_material', self._collide_custom), actions=(('modify_part_collision', 'collide', True)))

        self.position = position
        self.node = bs.newnode('prop',
                attrs={'body': 'puck','position':self.position,
                       'mesh': bs.getmesh(model), 'color_texture': bs.gettexture(texture),
                       'mesh_scale': scale, 'body_scale': 0.0,
                       'shadow_size': 0.0, 'gravity_scale':1.0,'reflection': 'soft', 'reflection_scale': [0.0], 'is_area_of_interest': False, 'materials': [self.dont_collide]})
        self.node.extra_acceleration = (0,21.5,0)
        self.region = bs.newnode('region',attrs={'position': (self.position[0],self.position[1]-0.6,self.position[2]-0.54),'scale': (3,0.5,0.5),'type': 'box','materials': (self._collide_custom,)})
        self.region1 = bs.newnode('region',attrs={'position': (self.position[0],self.position[1]+1,self.position[2]+0.54),'scale': (3,0.5,0.5),'type': 'box','materials': (self._collide_custom,)})

        def stop():
            self.node.extra_acceleration = (0,0,0)
            self.node.velocity = (0,0,0)
            self.node.gravity_scale = 0

        def move():
            bs.animate_array(self.region,'scale',3,{0:(3,0.5,0.5),0.03:(3,4,0.5)})
            bs.animate_array(self.region1,'scale',3,{0:(3,0.5,0.5),0.03:(3,4,0.5)})
            bs.timer(0.035,stop)
        bs.timer(0.001,move)

class FadeEffect():
    def __init__(self, map_tint = (1,1,1)):
        gnode = bs.getactivity().globalsnode
        bs.animate_array(gnode,'tint',3,{0:(0,0,0),3:(0,0,0),3.2:map_tint})

        text = bs.newnode('text',
                              attrs={
                                    'position': (0,250),
                                    'text': 'Loading...',
                                    'color': (0,0.45,1),
                                    'h_align': 'center','v_align': 'center', 'vr_depth': 410, 'maxwidth': 600, 'shadow': 1.0, 'flatness': 1.0, 'scale':1, 'h_attach': 'center', 'v_attach': 'bottom', 'big': True})
        bs.animate(text,'opacity',{0:0,0.3:1,0.5:1,3:0})
        bs.timer(5,text.delete)

        text = bs.newnode('text',
                              attrs={
                                    'position': (0,270),
                                    'text': 'by HWProgram',
                                    'color': (0,0.55,0),
                                    'h_align': 'center','v_align': 'center', 'vr_depth': 410, 'maxwidth': 600, 'shadow': 1.0, 'flatness': 1.0, 'scale':1.5, 'h_attach': 'center', 'v_attach': 'bottom'})
        bs.animate(text,'opacity',{0:0,0.3:1,0.5:1,3:0})
        bs.timer(5,text.delete)



class ArenaCombatMapData():
    points = {}
    boxes = {}
    boxes['area_of_interest_bounds'] = (
        (0.3544110667, 5.616383286, 6.066055072)
        + (0.0, 0.0, 0.0)
        + (50, 50, 50)
    )
    boxes['edge_box'] = (
        (0.3544110667, 5.438284793, -4.100357672)
        + (0.0, 0.0, 0.0)
        + (12.57718032, 4.645176013, 3.605557343)
    )
    points['ffa_spawn1'] = (7.941690444946289, 0.203672409057617, -10.778594017028809) + (
        2.0,
        1.0,
        0.3402012662,
    )
    points['ffa_spawn2'] = (-7.941690444946289, 0.203672409057617, -10.778594017028809) + (
        2.0,
        1.0,
        0.3402012662,
    )
    points['ffa_spawn3'] = (7.941690444946289, 0.203672409057617, 5) + (
        2.0,
        1.0,
        0.0,
    )
    points['ffa_spawn4'] = (-7.941690444946289, 0.203672409057617, 5) + (
        2.0,
        1.0,
        0.0,
    )
    points['ffa_spawn5'] = (-2.4439516067504883, 1.3461859226226807, -3.0181164741516113) + (
        0,
        0,
        2,
    )
    points['ffa_spawn6'] = (2.4439516067504883, 1.3461859226226807, -3.0181164741516113) + (
        0,
        0,
        2,
    )


    points['flag1'] = (-11.211543560028076, -0.2036149948835373, -2.759970188140869)
    points['flag2'] = (11.360891342163086, -0.20362165570259094, -2.759970188140869)
    points['flag_default'] = (0.21244560182094574, 1.3467398881912231, -2.7434356212615967)
    boxes['map_bounds'] = (
        (0.4528955042, 4.899663734, -3.543675157)
        + (0.0, 0.0, 0.0)
        + (60, 60, 60)
    )
    points['powerup_spawn1'] = (-8.462557792663574, 0.203629970550537, -6.088696479797363)
    points['powerup_spawn2'] = (-8.477666854858398, -0.20353515446186066, -2.981415033340454)
    points['powerup_spawn3'] = (-8.560944557189941, 0.203898906707764, 0.43137887120246887)
    points['powerup_spawn4'] = (8.462557792663574, 0.203629970550537, -6.088696479797363)
    points['powerup_spawn5'] = (8.477666854858398, -0.20353515446186066, -2.981415033340454)
    points['powerup_spawn6'] = (8.21454906463623, -0.2034543752670288, 0.3469674587249756)
    points['powerup_spawn7'] = (0.17930641770362854, 0.203766822814941, 3.233539581298828)
    points['powerup_spawn8'] = (0.17930641770362854, 0.203766822814941, -10.233539581298828)
    points['powerup_spawn9'] = (-1.506983757019043, 1.346657633781433, -4.067911624908447)
    points['powerup_spawn10'] = (-1.5502398014068604, 1.3460551500320435, -1.5622622966766357)
    points['powerup_spawn11'] = (2.05, 1.346657633781433, -4.067911624908447)
    points['powerup_spawn12'] = (2.05, 1.3460551500320435, -1.5622622966766357)
    points['powerup_spawn13'] = (-5.155104160308838, 6.346006393432617, -2.828307628631592)
    points['powerup_spawn14'] = (5.626911163330078, 6.346072673797607, -2.8498446941375732)
    points['shadow_lower_bottom'] = (5.580073911, 9.136491026, 5.341226521)
    points['shadow_lower_top'] = (5.580073911, 10.321758709, 5.341226521)
    points['shadow_upper_bottom'] = (5.274539479, 14.425373402, 5.341226521)
    points['shadow_upper_top'] = (5.274539479, 16.93458162, 5.341226521)
    points['spawn1'] = (-10.211543560028076, -0.2036149948835373, -3.759970188140869) + (
        0.9186962739,
        1.0,
        0.5153189341,
    )
    points['spawn2'] = (10.360891342163086, -0.20362165570259094, -3.759970188140869) + (
        0.9186962739,
        1.0,
        0.5153189341,
    )
    points['tnt1'] = (0.12427891045808792, -0.20374798774719238, 1.4640417098999023)

class ArenaCombat(bs.Map):
    """ 'WWE' ahh map."""
    defs = ArenaCombatMapData()
    name = 'Arena Combat'

    @override
    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        return ['melee', 'keep_away', 'team_flag']

    @override
    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'doomShroomBGColor'

    @override
    @classmethod
    def on_preload(cls) -> Any:
        data: dict[str, Any] = {
            'bgtex': bs.gettexture('menuBG'),
            'bgmesh': bs.getmesh('thePadBG'),
            'vr_fill_mesh': bs.getmesh('thePadVRFillMound'),
        }
        return data

    def __init__(self) -> None:
        super().__init__(vr_overlay_offset=(0, 0, 2))
        shared = SharedObjects.get()
        self.collide_material = bs.Material()
        self.collide_material.add_actions(
            conditions=('we_are_older_than', 1),
            actions=('modify_part_collision', 'collide', True))
        self.dont_collide=bs.Material()
        self.dont_collide.add_actions(conditions=('they_are_different_node_than_us', ),actions=(('modify_part_collision', 'collide', False)))


        self.bg = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['bgmesh'],
                'lighting': False,
                'background': True,
                'color_texture': self.preloaddata['bgtex'],
                'color': (0.45, 0.45, 0.45),
            },
        )
        bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['vr_fill_mesh'],
                'lighting': False,
                'vr_only': True,
                'background': True,
                'color_texture': self.preloaddata['bgtex'],
            },
        )
        self.collision_region = bs.newnode(
            'region',
            attrs={
                'position': (0.0, -1, -3),
                'type': 'box',
                'scale': (24, 1.0, 24),
                'materials': [self.collide_material,
                              shared.footing_material]
            })
        self.locator_region = bs.newnode(
            'locator',
            attrs={
                'position': (0.0, -1, -3),
                'shape': 'box',
                'size': (24, 1.0, 24),
                'color':(1,0,0),
                'opacity':1,
                'draw_beauty':True,
                'additive':False,
            })
        bs.animate_array(self.locator_region, 'color', 3, {0:(0,0,0), 1.5:(0,0,0), 2.00:(0,0,0), 2.05:(1,1,1), 2.1:(0,0,0), 2.15:(1,1,1), 2.2:(0,0,0), 2.25:(1,1,1), 2.3:(0,0,0), 2.35:(1,1,1), 2.4:(0,0,0), 2.45:(1,1,1), 2.50:(0,0,0), 2.55:(0,0,1)}, loop=False)
        self.visible_platform = bs.newnode(
            'prop',
            attrs={
                'position': (0.0, -0.55, -3),
                'mesh': bs.getmesh('image1x1'),
                'color_texture': bs.gettexture('powerupIceBombs'),
                'mesh_scale': 24,
                'body': 'puck',
                'body_scale': 0.0,
                'gravity_scale': 0.0,
                'shadow_size': 0.0,
                'reflection': 'soft',
                'reflection_scale': [0.45],
                'damping': float("inf"),
                'density': float("inf"),
                'materials': [self.dont_collide]
            })
        self.crate = CustomModel(position=(0.2, -3, -3), model = 'tnt', texture = 'doomShroomBGColor', scale = 11.7)
        self.crate_floor = CustomModel(position=(0.2, -2.9, -3), model = 'powerupSimple', texture = 'flagColor', scale = 13.8)
        self.net1 = bs.newnode(
            'locator',
            attrs={
                'position': (-3.6, 2.346185922622680, 0.8),
                'shape': 'box',
                'size': (0.4, 2.4, 0.4),
                'color':(1,0,0),
                'opacity':1,
                'draw_beauty':True,
                'additive':False,
            })
        self.net2 = bs.newnode(
            'locator',
            attrs={
                'position': (3.95, 2.3461859226226807, 0.8),
                'shape': 'box',
                'size': (0.4, 2.4, 0.4),
                'color':(1,0,0),
                'opacity':1,
                'draw_beauty':True,
                'additive':False,
            })
        self.net3 = bs.newnode(
            'locator',
            attrs={
                'position': (-3.6, 2.3461859226226807, -6.85),
                'shape': 'box',
                'size': (0.4, 2.4, 0.4),
                'color':(1,0,0),
                'opacity':1,
                'draw_beauty':True,
                'additive':False,
            })
        self.net4 = bs.newnode(
            'locator',
            attrs={
                'position': (3.95, 2.3461859226226807, -6.85),
                'shape': 'box',
                'size': (0.4, 2.4, 0.4),
                'color':(1,0,0),
                'opacity':1,
                'draw_beauty':True,
                'additive':False,
            })
        self.net_gate1 = bs.newnode(
            'locator',
            attrs={
                'position': (-3.6, 2.346185922622680, -1.8),
                'shape': 'box',
                'size': (0.4, 2.4, 0.4),
                'color':(1,0,0),
                'opacity':1,
                'draw_beauty':True,
                'additive':False,
            })
        self.net_gate2 = bs.newnode(
            'locator',
            attrs={
                'position': (3.95, 2.3461859226226807, -1.8),
                'shape': 'box',
                'size': (0.4, 2.4, 0.4),
                'color':(1,0,0),
                'opacity':1,
                'draw_beauty':True,
                'additive':False,
            })
        self.net_gate3 = bs.newnode(
            'locator',
            attrs={
                'position': (-3.6, 2.3461859226226807, -4.15),
                'shape': 'box',
                'size': (0.4, 2.4, 0.4),
                'color':(1,0,0),
                'opacity':1,
                'draw_beauty':True,
                'additive':False,
            })
        self.net_gate4 = bs.newnode(
            'locator',
            attrs={
                'position': (3.95, 2.3461859226226807, -4.15),
                'shape': 'box',
                'size': (0.4, 2.4, 0.4),
                'color':(1,0,0),
                'opacity':1,
                'draw_beauty':True,
                'additive':False,
            })

        self.net_connection1 = bs.newnode(
            'locator',
            attrs={
                'position': (0.2, 2.80, 0.8),
                'shape': 'box',
                'size': (7.18, 0.2, 0.2),
                'color':(1,0,0),
                'opacity':1,
                'draw_beauty':True,
                'additive':False,
            })
        self.net_connection2 = bs.newnode(
            'locator',
            attrs={
                'position': (0.2, 2.80, -6.85),
                'shape': 'box',
                'size': (7.18, 0.2, 0.2),
                'color':(1,0,0),
                'opacity':1,
                'draw_beauty':True,
                'additive':False,
            })
        self.net_connection_blue1 = bs.newnode(
            'locator',
            attrs={
                'position': (0.2, 2.25, 0.8),
                'shape': 'box',
                'size': (7.18, 0.2, 0.2),
                'color':(0,0,1),
                'opacity':1,
                'draw_beauty':True,
                'additive':False,
            })
        self.net_connection_blue2 = bs.newnode(
            'locator',
            attrs={
                'position': (0.2, 2.25, -6.85),
                'shape': 'box',
                'size': (7.18, 0.2, 0.2),
                'color':(0,0,1),
                'opacity':1,
                'draw_beauty':True,
                'additive':False,
            })
        self.net_connection_white1 = bs.newnode(
            'locator',
            attrs={
                'position': (0.2, 1.75, 0.8),
                'shape': 'box',
                'size': (7.18, 0.2, 0.2),
                'color':(1,1,1),
                'opacity':1,
                'draw_beauty':True,
                'additive':False,
            })
        self.net_connection_white2 = bs.newnode(
            'locator',
            attrs={
                'position': (0.2, 1.75, -6.85),
                'shape': 'box',
                'size': (7.18, 0.2, 0.2),
                'color':(1,1,1),
                'opacity':1,
                'draw_beauty':True,
                'additive':False,
            })
        self.net_connection3 = bs.newnode(
            'locator',
            attrs={
                'position': (-3.60, 2.80, -0.50),
                'shape': 'box',
                'size': (0.2, 0.2, 2.20),
                'color':(1,0,0),
                'opacity':1,
                'draw_beauty':True,
                'additive':False,
            })
        self.net_connection4 = bs.newnode(
            'locator',
            attrs={
                'position': (-3.60, 2.80, -5.50),
                'shape': 'box',
                'size': (0.2, 0.2, 2.25),
                'color':(1,0,0),
                'opacity':1,
                'draw_beauty':True,
                'additive':False,
            })
        self.net_connection_blue3 = bs.newnode(
            'locator',
            attrs={
                'position': (-3.60, 2.25, -0.50),
                'shape': 'box',
                'size': (0.2, 0.2, 2.20),
                'color':(0,0,1),
                'opacity':1,
                'draw_beauty':True,
                'additive':False,
            })
        self.net_connection_blue4 = bs.newnode(
            'locator',
            attrs={
                'position': (-3.60, 2.25, -5.50),
                'shape': 'box',
                'size': (0.2, 0.2, 2.25),
                'color':(0,0,1),
                'opacity':1,
                'draw_beauty':True,
                'additive':False,
            })
        self.net_connection_white3 = bs.newnode(
            'locator',
            attrs={
                'position': (-3.60, 1.75, -0.50),
                'shape': 'box',
                'size': (0.2, 0.2, 2.20),
                'color':(1,1,1),
                'opacity':1,
                'draw_beauty':True,
                'additive':False,
            })
        self.net_connection_white4 = bs.newnode(
            'locator',
            attrs={
                'position': (-3.60, 1.75, -5.50),
                'shape': 'box',
                'size': (0.2, 0.2, 2.25),
                'color':(1,1,1),
                'opacity':1,
                'draw_beauty':True,
                'additive':False,
            })
        self.net_connection5 = bs.newnode(
            'locator',
            attrs={
                'position': (3.95, 2.80, -0.50),
                'shape': 'box',
                'size': (0.2, 0.2, 2.20),
                'color':(1,0,0),
                'opacity':1,
                'draw_beauty':True,
                'additive':False,
            })
        self.net_connection6 = bs.newnode(
            'locator',
            attrs={
                'position': (3.95, 2.80, -5.50),
                'shape': 'box',
                'size': (0.2, 0.2, 2.25),
                'color':(1,0,0),
                'opacity':1,
                'draw_beauty':True,
                'additive':False,
            })
        self.net_connection_blue5 = bs.newnode(
            'locator',
            attrs={
                'position': (3.95, 2.25, -0.50),
                'shape': 'box',
                'size': (0.2, 0.2, 2.20),
                'color':(0,0,1),
                'opacity':1,
                'draw_beauty':True,
                'additive':False,
            })
        self.net_connection_blue6 = bs.newnode(
            'locator',
            attrs={
                'position': (3.95, 2.25, -5.50),
                'shape': 'box',
                'size': (0.2, 0.2, 2.25),
                'color':(0,0,1),
                'opacity':1,
                'draw_beauty':True,
                'additive':False,
            })
        self.net_connection_white5 = bs.newnode(
            'locator',
            attrs={
                'position': (3.95, 1.75, -0.50),
                'shape': 'box',
                'size': (0.2, 0.2, 2.20),
                'color':(1,1,1),
                'opacity':1,
                'draw_beauty':True,
                'additive':False,
            })
        self.net_connection_white6 = bs.newnode(
            'locator',
            attrs={
                'position': (3.95, 1.75, -5.50),
                'shape': 'box',
                'size': (0.2, 0.2, 2.25),
                'color':(1,1,1),
                'opacity':1,
                'draw_beauty':True,
                'additive':False,
            })
        self.net1collide = bs.newnode(
            'region',
            attrs={
                'position': (-3.6, 2.346185922622680, 0.8),
                'type': 'box',
                'scale': (0.4, 2.4, 0.4),
                'materials': [self.collide_material,
                             shared.footing_material]
            })
        self.net2collide = bs.newnode(
            'region',
            attrs={
                'position': (3.95, 2.3461859226226807, 0.8),
                'type': 'box',
                'scale': (0.4, 2.4, 0.4),
                'materials': [self.collide_material,
                             shared.footing_material]
            })
        self.net3collide = bs.newnode(
            'region',
            attrs={
                'position': (-3.6, 2.3461859226226807, -6.85),
                'type': 'box',
                'scale': (0.4, 2.4, 0.4),
                'materials': [self.collide_material,
                             shared.footing_material]
            })
        self.net4collide = bs.newnode(
            'region',
            attrs={
                'position': (3.95, 2.3461859226226807, -6.85),
                'type': 'box',
                'scale': (0.4, 2.4, 0.4),
                'materials': [self.collide_material,
                             shared.footing_material]
            })
        self.net_gate1collide = bs.newnode(
            'region',
            attrs={
                'position': (-3.6, 2.346185922622680, -1.8),
                'type': 'box',
                'scale': (0.4, 2.4, 0.4),
                'materials': [self.collide_material,
                             shared.footing_material]
            })
        self.net_gate2collide = bs.newnode(
            'region',
            attrs={
                'position': (3.95, 2.3461859226226807, -1.8),
                'type': 'box',
                'scale': (0.4, 2.4, 0.4),
                'materials': [self.collide_material,
                             shared.footing_material]
            })
        self.net_gate3collide = bs.newnode(
            'region',
            attrs={
                'position': (-3.6, 2.3461859226226807, -4.15),
                'type': 'box',
                'scale': (0.4, 2.4, 0.4),
                'materials': [self.collide_material,
                             shared.footing_material]
            })
        self.net_gate4collide = bs.newnode(
            'region',
            attrs={
                'position': (3.95, 2.3461859226226807, -4.15),
                'type': 'box',
                'scale': (0.4, 2.4, 0.4),
                'materials': [self.collide_material,
                             shared.footing_material]
            })

        self.net_connection1collide = bs.newnode(
            'region',
            attrs={
                'position': (0.2, 2.80, 0.8),
                'type': 'box',
                'scale': (7.18, 0.2, 0.2),
                'materials': [self.collide_material,
                             shared.footing_material]
            })
        self.net_connection2collide = bs.newnode(
            'region',
            attrs={
                'position': (0.2, 2.80, -6.85),
                'type': 'box',
                'scale': (7.18, 0.2, 0.2),
                'materials': [self.collide_material,
                             shared.footing_material]
            })
        self.net_connection_blue1collide = bs.newnode(
            'region',
            attrs={
                'position': (0.2, 2.25, 0.8),
                'type': 'box',
                'scale': (7.18, 0.2, 0.2),
                'materials': [self.collide_material,
                             shared.footing_material]
            })
        self.net_connection_blue2collide = bs.newnode(
            'region',
            attrs={
                'position': (0.2, 2.25, -6.85),
                'type': 'box',
                'scale': (7.18, 0.2, 0.2),
                'materials': [self.collide_material,
                             shared.footing_material]
            })
        self.net_connection_white1collide = bs.newnode(
            'region',
            attrs={
                'position': (0.2, 1.75, 0.8),
                'type': 'box',
                'scale': (7.18, 0.2, 0.2),
                'materials': [self.collide_material,
                             shared.footing_material]
            })
        self.net_connection_white2collide = bs.newnode(
            'region',
            attrs={
                'position': (0.2, 1.75, -6.85),
                'type': 'box',
                'scale': (7.18, 0.2, 0.2),
                'materials': [self.collide_material,
                             shared.footing_material]
            })
        self.net_connection3collide = bs.newnode(
            'region',
            attrs={
                'position': (-3.60, 2.80, -0.50),
                'type': 'box',
                'scale': (0.2, 0.2, 2.20),
                'materials': [self.collide_material,
                             shared.footing_material]
            })
        self.net_connection4collide = bs.newnode(
            'region',
            attrs={
                'position': (-3.60, 2.80, -5.50),
                'type': 'box',
                'scale': (0.2, 0.2, 2.25),
                'materials': [self.collide_material,
                             shared.footing_material]
            })
        self.net_connection_blue3collide = bs.newnode(
            'region',
            attrs={
                'position': (-3.60, 2.25, -0.50),
                'type': 'box',
                'scale': (0.2, 0.2, 2.20),
                'materials': [self.collide_material,
                             shared.footing_material]
            })
        self.net_connection_blue4collide = bs.newnode(
            'region',
            attrs={
                'position': (-3.60, 2.25, -5.50),
                'type': 'box',
                'scale': (0.2, 0.2, 2.25),
                'materials': [self.collide_material,
                             shared.footing_material]
            })
        self.net_connection_white3collide = bs.newnode(
            'region',
            attrs={
                'position': (-3.60, 1.75, -0.50),
                'type': 'box',
                'scale': (0.2, 0.2, 2.20),
                'materials': [self.collide_material,
                             shared.footing_material]
            })
        self.net_connection_white4collide  = bs.newnode(
            'region',
            attrs={
                'position': (-3.60, 1.75, -5.50),
                'type': 'box',
                'scale': (0.2, 0.2, 2.25),
                'materials': [self.collide_material,
                             shared.footing_material]
            })
        self.net_connection5collide = bs.newnode(
            'region',
            attrs={
                'position': (3.95, 2.80, -0.50),
                'type': 'box',
                'scale': (0.2, 0.2, 2.20),
                'materials': [self.collide_material,
                             shared.footing_material]
            })
        self.net_connection6collide = bs.newnode(
            'region',
            attrs={
                'position': (3.95, 2.80, -5.50),
                'type': 'box',
                'scale': (0.2, 0.2, 2.25),
                'materials': [self.collide_material,
                             shared.footing_material]
            })
        self.net_connection_blue5collide = bs.newnode(
            'region',
            attrs={
                'position': (3.95, 2.25, -0.50),
                'type': 'box',
                'scale': (0.2, 0.2, 2.20),
                'materials': [self.collide_material,
                             shared.footing_material]
            })
        self.net_connection_blue6collide = bs.newnode(
            'region',
            attrs={
                'position': (3.95, 2.25, -5.50),
                'type': 'box',
                'scale': (0.2, 0.2, 2.25),
                'materials': [self.collide_material,
                             shared.footing_material]
            })
        self.net_connection_white5collide = bs.newnode(
            'region',
            attrs={
                'position': (3.95, 1.75, -0.50),
                'type': 'box',
                'scale': (0.2, 0.2, 2.20),
                'materials': [self.collide_material,
                             shared.footing_material]
            })
        self.net_connection_white6collide = bs.newnode(
            'region',
            attrs={
                'position': (3.95, 1.75, -5.50),
                'type': 'box',
                'scale': (0.2, 0.2, 2.25),
                'materials': [self.collide_material,
                             shared.footing_material]
            })
        carrier = bs.newnode('locator',
                                    attrs={'shape':'box',
                                    'position':(-5.2, -0.5, -3.0),
                                    'color':(1,1,1),
                                    'opacity':1,'draw_beauty':True,'additive':False,'size':[2.5,0.1,2.5]})
        carrier_collide = bs.newnode('region',attrs={'position': (-5.2, -0.5, -3.0),'scale': (2.5,0.1,2.5),'type': 'box','materials': (shared.footing_material, self.collide_material)})
        bs.animate_array(carrier, 'position', 3, {0:(-5.2, 1, -3.0), 3:(-5.2, -0.5, -3.0), 5:(-5.2, -0.5, -3.0), 8:(-5.2, 1, -3.0), 10:(-5.2, 1, -3.0)}, loop=True)
        bs.animate_array(carrier, 'color', 3, {0:(0,0,0), 1.5:(0,0,0), 2.00:(0,0,0), 2.05:(1,1,1), 2.1:(0,0,0), 2.15:(1,1,1), 2.2:(0,0,0), 2.25:(1,1,1), 2.3:(0,0,0), 2.35:(1,1,1), 2.4:(0,0,0), 2.45:(1,1,1), 2.50:(0,0,0), 2.55:(0,0.45,1)}, loop=False)
        bs.animate_array(carrier_collide, 'position', 3, {0:(-5.2, 1, -3.0), 3:(-5.2, -0.5, -3.0), 5:(-5.2, -0.5, -3.0), 8:(-5.2, 1, -3.0), 10:(-5.2, 1, -3.0)}, loop=True)
        carrier2 = bs.newnode('locator',
                                    attrs={'shape':'box',
                                    'position':(5.6, 1, -3.0),
                                    'color':(1,1,1),
                                    'opacity':1,'draw_beauty':True,'additive':False,'size':[2.5,0.1,2.5]})
        carrier_collide2 = bs.newnode('region',attrs={'position': (5.6, 1, -3.0),'scale': (2.5,0.1,2.5),'type': 'box','materials': (shared.footing_material, self.collide_material)})
        bs.animate_array(carrier2, 'position', 3, {0:(5.6, -0.5, -3.0), 3:(5.6, 1, -3.0), 5:(5.6, 1, -3.0), 8:(5.6, -0.5, -3.0), 10:(5.6, -0.5, -3.0)}, loop=True)
        bs.animate_array(carrier2, 'color', 3, {0:(0,0,0), 1.5:(0,0,0), 2.00:(0,0,0), 2.05:(1,1,1), 2.1:(0,0,0), 2.15:(1,1,1), 2.2:(0,0,0), 2.25:(1,1,1), 2.3:(0,0,0), 2.35:(1,1,1), 2.4:(0,0,0), 2.45:(1,1,1), 2.50:(0,0,0), 2.55:(0,1,0)}, loop=False)
        bs.animate_array(carrier_collide2, 'position', 3, {0:(5.6, -0.5, -3.0), 3:(5.6, 1, -3.0), 5:(5.6, 1, -3.0), 8:(5.6, -0.5, -3.0), 10:(5.6, -0.5, -3.0)}, loop=True)
        extra = bs.newnode('locator',
                                    attrs={'shape':'box',
                                    'position':(-5.2, 6, -3.0),
                                    'color':(1,1,1),
                                    'opacity':1,'draw_beauty':True,'additive':False,'size':[2.5,0.1,2.5]})
        extra_collide = bs.newnode('region',attrs={'position': (-5.2, 6, -3.0),'scale': (2.5,0.1,2.5),'type': 'box','materials': (shared.footing_material, self.collide_material)})
        carrier_extra = bs.newnode('locator',
                                    attrs={'shape':'box',
                                    'position':(-3.4, 1.15, -2.95),
                                    'color':(1,1,1),
                                    'opacity':1,'draw_beauty':True,'additive':False,'size':[1,0.1,1.9]})
        carrier_collide_extra = bs.newnode('region',attrs={'position': (-3.4, 1.15, -2.95),'scale': (1,0.1,1.9),'type': 'box','materials': (shared.footing_material, self.collide_material)})
        bs.animate_array(carrier_extra, 'position', 3, {0:(-3.4, 6, -2.95), 3:(-3.4, 1.15, -2.95), 5:(-3.4, 1.15, -2.95), 8:(-3.4, 6, -2.95), 10:(-3.4, 6, -2.95)}, loop=True)
        bs.animate_array(carrier_extra, 'color', 3, {0:(0,0,0), 1.5:(0,0,0), 2.00:(0,0,0), 2.05:(1,1,1), 2.1:(0,0,0), 2.15:(1,1,1), 2.2:(0,0,0), 2.25:(1,1,1), 2.3:(0,0,0), 2.35:(1,1,1), 2.4:(0,0,0), 2.45:(1,1,1), 2.50:(0,0,0), 2.55:(0,1,0)}, loop=False)
        bs.animate_array(carrier_collide_extra, 'position', 3, {0:(-3.4, 6, -2.95), 3:(-3.4, 1.15, -2.95), 5:(-3.4, 1.15, -2.95), 8:(-3.4, 6, -2.95), 10:(-3.4, 6, -2.95)}, loop=True)
        extra2 = bs.newnode('locator',
                                    attrs={'shape':'box',
                                    'position':(5.6, 6, -3.0),
                                    'color':(1,1,1),
                                    'opacity':1,'draw_beauty':True,'additive':False,'size':[2.5,0.1,2.5]})
        extra_collide2 = bs.newnode('region',attrs={'position': (5.6, 6, -3.0),'scale': (2.5,0.1,2.5),'type': 'box','materials': (shared.footing_material, self.collide_material)})
        carrier_extra2 = bs.newnode('locator',
                                    attrs={'shape':'box',
                                    'position':(3.8, 6, -2.95),
                                    'color':(1,1,1),
                                    'opacity':1,'draw_beauty':True,'additive':False,'size':[1,0.1,1.9]})
        carrier_collide_extra2 = bs.newnode('region',attrs={'position': (3.8, 6, -2.95),'scale': (1,0.1,1.9),'type': 'box','materials': (shared.footing_material, self.collide_material)})
        bs.animate_array(carrier_extra2, 'position', 3, {0:(3.8, 1.15, -2.95), 3:(3.8, 6, -2.95), 5:(3.8, 6, -2.95), 8:(3.8, 1.15, -2.95), 10:(3.8, 1.15, -2.95)}, loop=True)
        bs.animate_array(carrier_extra2, 'color', 3, {0:(0,0,0), 1.5:(0,0,0), 2.00:(0,0,0), 2.05:(1,1,1), 2.1:(0,0,0), 2.15:(1,1,1), 2.2:(0,0,0), 2.25:(1,1,1), 2.3:(0,0,0), 2.35:(1,1,1), 2.4:(0,0,0), 2.45:(1,1,1), 2.50:(0,0,0), 2.55:(0,0.45,1)}, loop=False)
        bs.animate_array(carrier_collide_extra2, 'position', 3, {0:(3.8, 1.15, -2.95), 3:(3.8, 6, -2.95), 5:(3.8, 6, -2.95), 8:(3.8, 1.15, -2.95), 10:(3.8, 1.15, -2.95)}, loop=True)
        self.extra_floor = bs.newnode(
            'prop',
            attrs={
                'position': (-5.2, 6.04, -3.0),
                'mesh': bs.getmesh('image1x1'),
                'color_texture': bs.gettexture('powerupPunch'),
                'mesh_scale': 2.5,
                'body': 'puck',
                'body_scale': 0.0,
                'gravity_scale': 0.0,
                'shadow_size': 0.0,
                'reflection': 'soft',
                'reflection_scale': [0.45],
                'damping': float("inf"),
                'density': float("inf"),
                'materials': [self.dont_collide]
            })
        self.extra_floor2 = bs.newnode(
            'prop',
            attrs={
                'position': (5.6, 6.04, -3.0),
                'mesh': bs.getmesh('image1x1'),
                'color_texture': bs.gettexture('powerupSpeed'),
                'mesh_scale': 2.5,
                'body': 'puck',
                'body_scale': 0.0,
                'gravity_scale': 0.0,
                'shadow_size': 0.0,
                'reflection': 'soft',
                'reflection_scale': [0.45],
                'damping': float("inf"),
                'density': float("inf"),
                'materials': [self.dont_collide]
            })
        carrier_floor = bs.newnode(
            'prop',
            attrs={
                'position': (-5.2, 1.04, -3.0),
                'mesh': bs.getmesh('image1x1'),
                'color_texture': bs.gettexture('powerupIceBombs'),
                'mesh_scale': 2.5,
                'body': 'puck',
                'body_scale': 0.0,
                'gravity_scale': 0.0,
                'shadow_size': 0.0,
                'reflection': 'soft',
                'reflection_scale': [0.45],
                'damping': float("inf"),
                'density': float("inf"),
                'materials': [self.dont_collide]
            })
        bs.animate_array(carrier_floor, 'position', 3, {0:(-5.2, 1.04, -3.0), 3:(-5.2, -0.54, -3.0), 5:(-5.2, -0.54, -3.0), 8:(-5.2, 1.04, -3.0), 10:(-5.2, 1.04, -3.0)}, loop=True)
        carrier_floor2 = bs.newnode(
            'prop',
            attrs={
                'position': (5.6, -0.54, -3.0),
                'mesh': bs.getmesh('image1x1'),
                'color_texture': bs.gettexture('powerupStickyBombs'),
                'mesh_scale': 2.5,
                'body': 'puck',
                'body_scale': 0.0,
                'gravity_scale': 0.0,
                'shadow_size': 0.0,
                'reflection': 'soft',
                'reflection_scale': [0.45],
                'damping': float("inf"),
                'density': float("inf"),
                'materials': [self.dont_collide]
            })
        bs.animate_array(carrier_floor2, 'position', 3, {0:(5.6, -0.54, -3.0), 3:(5.6, 1.04, -3.0), 5:(5.6, 1.04, -3.0), 8:(5.6, -0.54, -3.0), 10:(5.6, -0.54, -3.0)}, loop=True)
        self.main_skull = CustomModel(position=(0.1404125839471817, 2.5, -6.236794471740723), model = 'bonesHead', texture = 'bonesColor', scale = 2.7)
        def sparks():
            bs.emitfx(position=(0.1404125839471817, 2.7, -6.236794471740723),
		             count=int(500),
		    	     scale=2,
		    	     spread=5,
	                 chunk_type='spark')


        def explosions():
            bs.newnode('explosion',attrs={
                     'position': (0.1404125839471817, 2.6, -6.236794471740723),
                     'color': (1, 0.50, 0),
                     'radius':2
                    })


        self.explosions = bs.timer(0.3,bs.CallPartial(explosions), repeat=True)
        self.sparks = bs.timer(0.001,bs.CallPartial(sparks), repeat=True)

        self.collision_crate = bs.newnode(
            'region',
            attrs={
                'position': (0.2, -2.9, -3),
                'type': 'box',
                'scale': (8.1, 8.1, 8.1),
                'materials': [self.collide_material,
                              shared.footing_material]
            })

        gnode = bs.getactivity().globalsnode
        gnode.tint = (1.2, 1.1, 0.97)
        gnode.ambient_color = (1.3, 1.2, 1.03)
        gnode.vignette_outer = (0.62, 0.64, 0.69)
        gnode.vignette_inner = (0.97, 0.95, 0.93)
        FadeEffect(gnode.tint)

    @override
    def is_point_near_edge(self, point: bs.Vec3, running: bool = False) -> bool:
        box_position = self.defs.boxes['edge_box'][0:3]
        box_scale = self.defs.boxes['edge_box'][6:9]
        xpos = (point.x - box_position[0]) / box_scale[0]
        zpos = (point.z - box_position[2]) / box_scale[2]
        return xpos < -0.5 or xpos > 0.5 or zpos < -0.5 or zpos > 0.5

# ba_meta export babase.Plugin
class HWProgram(bs.Plugin):
    _map.register_map(ArenaCombat)
