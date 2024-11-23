"""
Created on 11/17/2024

@author: Dan
TO RUN:
python ./src/battle_layout
"""
import os
from typing import List
from utils.buttons_etc import DiceRoller
from utils.dclasses2 import BattleStage, ChoiceManager, Creature2, GameState, Skill_Item
from utils.window_config import (
    PART_BOX, EART_BOX, CHOICE_BOX, 
    BL_BOX, PS_BOX, ES_BOX, DI_BOX, XYWH
    )
import raylibpy as rl

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

def draw_ascii_art_box(ascii_art:str, font: rl.Font, box: rl.Rectangle, color=rl.WHITE, font_size=20):
    """
    Draw ASCII art inside a box, centering and scaling it.
    Handles even/odd longest line length and shrinks font size if necessary.
    """
    # Draw the background box
    rec = rl.Rectangle(box.x, box.y, box.width, box.height)
    rl.draw_rectangle_rec(rec, rl.BLACK)
    
    # Pad the ASCII art to ensure consistent centering
    padded_art = pad_ascii_art(ascii_art)

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
        choicemanager:ChoiceManager, 
        pc: Creature2,
        npcs: List[Creature2]
        ):
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

def draw_battle_log_box(battle_log, line_spacing=4, font_size=15):
    """Draw the battle log box showing only the last messages that fit."""
    # Define the battle log box
    outline_thickness = 30

    battle_log_box = rl.Rectangle(
        BL_BOX.x, 
        BL_BOX.y , 
        BL_BOX.width,
        BL_BOX.height - 8 * outline_thickness
    )

    # Define the thickness of the outline

    # Adjust the battle_log_box dimensions to fit within the outline
    inner_battle_log_box = rl.Rectangle(
        BL_BOX.x + outline_thickness,
        BL_BOX.y + outline_thickness,
        BL_BOX.width - 2 * outline_thickness,
        BL_BOX.height - 2 * outline_thickness
    )

    # Draw the outline

    # Draw the inner rectangle
    rl.draw_rectangle_rec(inner_battle_log_box, rl.BLACK)
    rl.draw_rectangle_lines_ex(
        battle_log_box, outline_thickness, rl.LIGHTGRAY
    )
    # Calculate how many lines can fit in the box
    lines_visible = int(inner_battle_log_box.height // (font_size + line_spacing)//2.1) 

    # Get the last messages that fit in the box
    visible_messages = battle_log[-lines_visible:]

    # Render the visible messages
    for i, message in enumerate(visible_messages):
        line_y = inner_battle_log_box.y + i * (font_size + line_spacing)
        # Render the most recent message in green
        if i == len(visible_messages) - 1:
            color = rl.GREEN
        else:
            color = rl.WHITE
        rl.draw_text(
            message,
            inner_battle_log_box.x + 10,
            line_y,
            font_size,
            color
        )

###########################################################################
def draw_dice_box(pc:Creature2):
    dice_box = rl.Rectangle(
        DI_BOX.x, DI_BOX.y, DI_BOX.width, DI_BOX.height
    )
    rl.draw_rectangle_rec(dice_box, rl.LIGHTGRAY)
    pc.dice_roller.update_and_draw()

def draw_player_stats_box(pc:Creature2):
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

def draw_enemy_stats_box(npcs:List[Creature2]):
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

# Main loop
def battle(gs: GameState, pcs:List[Creature2], npcs:List[Creature2]):
    for player in pcs:
        player.set_up_dice_roller(
            dice_roller=DiceRoller(
                x = DI_BOX.x + DI_BOX.width // 2,
                y = DI_BOX.y + DI_BOX.height // 2,
                size=DI_BOX.width // 2,
                roll_duration=0.5
                )
            )
    i=0
    player_initiative = True
    font_path = os.path.join(os.getcwd(), "resources", "font", "joystix monospace.otf")
    font = rl.load_font(font_path)
    choice_manager = ChoiceManager()
    battle_log = []

    while gs == GameState.BATTLE:
        rl.begin_drawing()
        # rl.clear_background(rl.BLACK)

        # Draw each quadrant independently
        draw_ascii_art_box(
            pcs[0].ascii_art['default'], 
            font,
            PART_BOX, 
            color=rl.GREEN if player_initiative else rl.WHITE
            )
        draw_ascii_art_box(
            npcs[0].ascii_art['default'], 
            font,
            EART_BOX, 
            color=rl.GREEN if not player_initiative else rl.WHITE
            )

        draw_player_stats_box(pcs[0])
        draw_dice_box(pcs[0])
        draw_enemy_stats_box(npcs)

        # TESTING FEATURES
        if rl.is_key_pressed(rl.KEY_SPACE):
            # flip player_turn
            if player_initiative:
                player_initiative = False
            else:
                player_initiative = True
        if rl.is_key_pressed(rl.KEY_Q):
            i+=1
            battle_log.append(f"Player pressed {i}")
        if rl.is_key_pressed(rl.KEY_W):
            pcs[0].roll_dice()
        choice_manager = draw_choice_box(choice_manager, pcs[0], npcs)
        draw_battle_log_box(battle_log)
        # check if the battle is over
        # ...

        rl.end_drawing()

if __name__ == "__main__":
    battle()