import json
from dataclasses import dataclass
import raylibpy as rl
from utils.constants import WIDTH, HEIGHT
from utils.dcs import XYWH

def initialize_window():
    rl.init_window(WIDTH, HEIGHT, "HoneyPy")
    rl.set_target_fps(60)

PART_BOX = XYWH(
    x=0, 
    y=0, 
    width=WIDTH // 3, 
    height=HEIGHT // 4 * 3)

EART_BOX = XYWH(
    x=PART_BOX.width, 
    y=0, 
    width=WIDTH // 3, 
    height=HEIGHT // 4 * 3)

CHOICE_BOX = XYWH(
    x=0, 
    y=PART_BOX.height, 
    width=PART_BOX.width + EART_BOX.width, 
    height=HEIGHT - PART_BOX.height)

BL_BOX = XYWH(
    x=PART_BOX.width + EART_BOX.width,
    y=HEIGHT // 3 * 2 ,
    width=WIDTH - CHOICE_BOX.width,
    height=HEIGHT // 3 * 2)

PS_BOX = XYWH(
    x=PART_BOX.width + EART_BOX.width,
    y=0,
    width= WIDTH //6,
    height= HEIGHT - BL_BOX.height)

DI_BOX = XYWH(
    x=PART_BOX.width + EART_BOX.width,
    y=PS_BOX.height,
    width= PS_BOX.width,
    height= PS_BOX.height)

ES_BOX = XYWH(
    x=DI_BOX.x+DI_BOX.width,
    y=0,
    width= PS_BOX.width,
    height= PS_BOX.height + DI_BOX.height)