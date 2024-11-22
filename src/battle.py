"""
Created on 11/17/2024

@author: Dan
TO RUN:
python ./src/battle_layout
"""
import os
from typing import List
from utils.buttons_etc import DiceRoller
from utils.dclasses2 import BattleStage, ChoiceManager, Creature2, Skill_Item
from utils.window_config import (
    PART_BOX, EART_BOX, CHOICE_BOX, 
    BL_BOX, PS_BOX, ES_BOX, DI_BOX, XYWH
    )
from utils.creatures import bear_criminal, mall_cop
# from utils.combat_manager import display_combat_stats, enemy_turn, player_turn, combat_over
# from utils.logging import log_it
import raylibpy as rl
import json

params = json.loads(open("./resources/global_params.json").read())
WIDTH, HEIGHT = params["WIDTH"], params["HEIGHT"]
rl.init_window(WIDTH, HEIGHT, "Battle Layout")
# font_path = os.path.join(os.getcwd(), "resources", "font", "basis33.ttf")
# font = rl.load_font(font_path)

rl.set_target_fps(60)

pcs = [bear_criminal]
npcs = [mall_cop, mall_cop, mall_cop]
player_turn = True

for player in pcs:
    player.set_up_dice_roller(
        dice_roller=DiceRoller(
            x = DI_BOX.x + DI_BOX.width // 2,
            y = DI_BOX.y + DI_BOX.height // 2,
            size=DI_BOX.width // 2,
            roll_duration=0.5
            )
        )
def scale_text_to_fit_box(text, box, font, font_size):
    """
    Scale down the text size if it doesn't fit within the box.
    Continuously adjusts font size to ensure it fits both horizontally and vertically.
    """
    lines = text.split('\n')
    while True:
        # Calculate the maximum text width and total height
        max_line_width = max([rl.measure_text_ex(font, line, font_size, 2).x for line in lines])
        total_height = len(lines) * (font_size + 4)  # Account for line spacing
        
        # Check if the current font size fits within the box
        if max_line_width <= box.width and total_height <= box.height:
            break  # Font size fits, stop scaling
        
        # Reduce font size and try again
        font_size -= 1
        if font_size <= 0:
            raise ValueError("Font size cannot fit the box.")
    
    return font_size


def pad_ascii_art(ascii_art: str) -> str:
    """Pad each line of ASCII art to match the longest line length."""
    lines = ascii_art.splitlines()
    max_len = max(len(line) for line in lines)

    # Pad each line to the longest length
    padded_lines = [line.ljust(max_len) for line in lines]
    return '\n'.join(padded_lines)


def draw_ascii_art_box(art, font, box, font_size=15, color=rl.WHITE):
    """
    Draw ASCII art inside a box, centering and scaling it.
    Handles even/odd longest line length and shrinks font size if necessary.
    """
    # Draw the background box
    rec = rl.Rectangle(box.x, box.y, box.width, box.height)
    rl.draw_rectangle_rec(rec, rl.BLACK)
    
    # Pad the ASCII art to ensure consistent centering
    padded_art = pad_ascii_art(art)

    # Scale font size to fit the box
    font_size = scale_text_to_fit_box(padded_art, box, font, font_size)
    
    # Split the ASCII art into lines
    lines = padded_art.splitlines()
    total_height = len(lines) * (font_size + 4)  # Account for line spacing

    # Calculate vertical starting position for centering the block
    start_y = box.y + (box.height - total_height) // 2

    # Draw each line of ASCII art
    for i, line in enumerate(lines):
        # Measure the width of the line for horizontal centering
        line_width = rl.measure_text_ex(font, line, font_size, 2).x
        start_x = box.x + (box.width - line_width) // 2

        # Calculate the y position for this line
        line_y = start_y + i * (font_size + 4)

        # Draw the line
        rl.draw_text_ex(font, line, rl.Vector2(start_x, line_y), font_size, 2, color)

def draw_choice_box(
        choicemanager:ChoiceManager, pc: Creature2 = pcs[0]):
    """Handle the chained choice selection for skills or items."""
    # Draw the initial choice box
    choice_rect = rl.Rectangle(
        CHOICE_BOX.x, CHOICE_BOX.y, CHOICE_BOX.width, CHOICE_BOX.height
    )
    rl.draw_rectangle_rec(choice_rect, rl.LIGHTGRAY)

    # Step 1: Select Skill or Item
    if choicemanager.stage==BattleStage.SELECT_SKILL_ITEM:
        choicemanager = pc.select_skill_or_item(
            choicemanager, CHOICE_BOX.x, CHOICE_BOX.y, CHOICE_BOX.width, CHOICE_BOX.height
        )

    elif choicemanager.stage == BattleStage.SELECT_SKILL_TYPE:
        # Step 2: Select Skill Type
        choicemanager =  pc.select_skill_type(
            choicemanager, CHOICE_BOX.x, CHOICE_BOX.y, CHOICE_BOX.width, CHOICE_BOX.height
        )

    elif choicemanager.stage == BattleStage.SELECT_SKILL:
        choicemanager =  pc.select_skill(
            choicemanager, CHOICE_BOX.x, CHOICE_BOX.y, CHOICE_BOX.width, CHOICE_BOX.height
        )
        # Return the selected skill
        return choicemanager

    elif choicemanager.stage == BattleStage.SELECT_ITEM:
        # Handle item selection (if needed)
        choicemanager = pc.select_item(
            choicemanager, CHOICE_BOX.x, CHOICE_BOX.y, CHOICE_BOX.width, CHOICE_BOX.height
        )
        return choicemanager
    
    elif choicemanager.stage == BattleStage.SELECT_TARGET:
        # Handle target selection (if needed)
        choicemanager = pc.select_target(
            choicemanager, npcs, CHOICE_BOX.x, CHOICE_BOX.y, CHOICE_BOX.width, CHOICE_BOX.height
        )
        # Return the selected target
        return choicemanager

    # Default return if no selection
    return choicemanager
battle_log = []     # List of messages for the battle log
scroll_offset = 0   # Tracks scroll position
line_spacing = 4    # Space between lines
font_size = 15      # Default font size for battle log text

def add_battle_log_message(message):
    """Add a new message to the battle log."""
    global battle_log
    battle_log.append(message)

def draw_battle_log_box():
    """Draw the battle log box showing only the last messages that fit."""
    global battle_log

    # Define the battle log box
    battle_log_box = rl.Rectangle(
        BL_BOX.x, BL_BOX.y, BL_BOX.width, BL_BOX.height
    )
    # draw grey outline
    # Define the thickness of the outline
    outline_thickness = 30

    # Adjust the battle_log_box dimensions to fit within the outline
    inner_battle_log_box = rl.Rectangle(
        BL_BOX.x + outline_thickness, 
        BL_BOX.y + outline_thickness, 
        BL_BOX.width - 2 * outline_thickness, 
        BL_BOX.height - 2 * outline_thickness * 6
    )

    # Draw the inner rectangle AFTER the outline
    rl.draw_rectangle_lines_ex(
        rl.Rectangle(
            BL_BOX.x, 
            BL_BOX.y, 
            BL_BOX.width, 
            BL_BOX.height //2
        ), 
        outline_thickness, 
        rl.LIGHTGRAY
    )
    rl.draw_rectangle_rec(inner_battle_log_box, rl.BLACK)

    # Calculate how many lines can fit in the box
    lines_visible = (BL_BOX.height - 2 * outline_thickness) // (font_size + line_spacing) // 2

    # Get the last messages that fit in the box
    visible_messages = battle_log[-lines_visible+1:]

    # Render the visible messages
    for i, message in enumerate(visible_messages):
        # if it is the most recent message, draw it in green
        line_y = (BL_BOX.y + BL_BOX.height//100 + outline_thickness) + i * (font_size + line_spacing)
        if message == visible_messages[-1]:
            rl.draw_text(message, BL_BOX.x + outline_thickness + 10, BL_BOX.y + outline_thickness + i * (font_size + line_spacing), font_size, rl.GREEN)
        else:
            rl.draw_text(message, BL_BOX.x + outline_thickness + 10, line_y, font_size, rl.WHITE)

###########################################################################
def draw_dice_box(pc:Creature2=pcs[0]):
    dice_box = rl.Rectangle(
        DI_BOX.x, DI_BOX.y, DI_BOX.width, DI_BOX.height
    )
    rl.draw_rectangle_rec(dice_box, rl.LIGHTGRAY)
    pc.dice_roller.update_and_draw()

def draw_player_stats_box(pc:Creature2=pcs[0]):
    player_stats_box = rl.Rectangle(
        PS_BOX.x, PS_BOX.y, PS_BOX.width, PS_BOX.height
    )

    rl.draw_rectangle_rec(player_stats_box, rl.LIGHTGRAY)
    padding = 10
    pc.display_stats(
        x=PS_BOX.x + padding, 
        y=PS_BOX.y + padding, 
        width=PS_BOX.width - 2 * padding, 
        height=PS_BOX.height - 2 * padding
    )

def draw_enemy_stats_box(npcs:List[Creature2]=npcs):
    enemy_stats_box = rl.Rectangle(
        ES_BOX.x, ES_BOX.y, ES_BOX.width, ES_BOX.height
    )
    rl.draw_rectangle_rec(enemy_stats_box,rl.LIGHTGRAY)
    padding = 10
    for i, npc in enumerate(npcs):
        npc.display_stats(
        x=ES_BOX.x + padding,                               # pad on left
        y=ES_BOX.y + padding + i * (ES_BOX.height // 3),    # up to 3 enemies
        width=ES_BOX.width - 2 * padding,                   # pad on left and right
        height=(ES_BOX.height // 3) - 2 * padding           # up to 3 enemies
        )

def reset_choice_manager():
    return ChoiceManager(
        stage=BattleStage.SELECT_SKILL_ITEM,
        selected_skill_item=None,
        selected_skill_type=None,
        selected_skill=None,
        selected_item=None,
        selected_target=None
    )

# Main loop
def battle():
    i=0
    player_turn = True
    font_path = os.path.join(os.getcwd(), "resources", "font", "joystix monospace.otf")
    font = rl.load_font(font_path)
    choice_manager = reset_choice_manager()

    while not rl.window_should_close():
        rl.begin_drawing()
        rl.clear_background(rl.BLACK)

        # Draw each quadrant independently
        draw_ascii_art_box(
            pcs[0].ascii_art['default'], 
            font,
            PART_BOX, 
            color=rl.GREEN if player_turn else rl.WHITE
            )
        draw_ascii_art_box(
            npcs[0].ascii_art['default'], 
            font,
            EART_BOX, 
            color=rl.GREEN if not player_turn else rl.WHITE
            )

        draw_player_stats_box()
        draw_dice_box()
        draw_enemy_stats_box()

        # TESTING FEATURES
        if rl.is_key_pressed(rl.KEY_SPACE):
            # flip player_turn
            if player_turn:
                player_turn = False
            else:
                player_turn = True
        if rl.is_key_pressed(rl.KEY_Q):
            i+=1
            add_battle_log_message(f"Player pressed {i}")
        if rl.is_key_pressed(rl.KEY_W):
            pcs[0].roll_dice()
        choice_manager = draw_choice_box(choice_manager)
        draw_battle_log_box()

        rl.end_drawing()

    rl.close_window()

if __name__ == "__main__":
    battle()