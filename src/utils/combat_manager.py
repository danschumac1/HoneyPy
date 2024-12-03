from typing import List
from utils.dclasses2 import ChoiceManager, Creature  
from utils.enums import BattleStage
from utils.window_config import (
    CHOICE_BOX, BL_BOX, PS_BOX, ES_BOX, DI_BOX,
    )
import raylibpy as rl

# params = json.loads(open("./resources/global_params.json").read())
# WIDTH, HEIGHT = params["WIDTH"], params["HEIGHT"]

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
def draw_battle_log_box(cm: ChoiceManager, battle_log, line_spacing=4, font_size=15):
    """Draw the battle log box showing only the last messages that fit."""
    if cm.new_message:
        battle_log.append(cm.message)
        cm.new_message = False

    # Define the battle log box
    outline_thickness = 30

    battle_log_box = rl.Rectangle(
        BL_BOX.x,
        BL_BOX.y,
        BL_BOX.width,
        BL_BOX.height - 8 * outline_thickness
    )

    # Adjust the battle_log_box dimensions to fit within the outline
    inner_battle_log_box = rl.Rectangle(
        BL_BOX.x + outline_thickness,
        BL_BOX.y + outline_thickness,
        BL_BOX.width - 2 * outline_thickness,
        BL_BOX.height - 2 * outline_thickness
    )

    # Draw the inner rectangle and outline
    rl.draw_rectangle_rec(
        inner_battle_log_box, rl.BLACK
        )
    rl.draw_rectangle_lines_ex(
        battle_log_box, outline_thickness, rl.LIGHTGRAY
    )

    # Calculate the maximum vertical space for lines
    max_line_count = int(
        inner_battle_log_box.height // (font_size + outline_thickness)
        )

    # Dynamically determine which lines fit in the box
    total_lines = 0
    visible_lines = []

    # Start from the most recent message and move backward
    for message in reversed(battle_log):
        # Split the message into lines if it exceeds the box width
        if rl.measure_text(message, font_size) > inner_battle_log_box.width - outline_thickness:
            words = message.split(' ')
            lines = ['']
            for word in words:
                if rl.measure_text(lines[-1] + word, font_size) > inner_battle_log_box.width - outline_thickness:
                    lines.append(word)
                else:
                    lines[-1] += ' ' + word
            lines = [line.strip() for line in lines]
        else:
            lines = [message]

        # Add the lines to the visible list, but stop if we've exceeded max_line_count
        if total_lines + len(lines) > max_line_count:
            # Add only as many lines as fit
            visible_lines = lines[-(max_line_count - total_lines):] + visible_lines
            break
        else:
            visible_lines = lines + visible_lines
            total_lines += len(lines)

    # Render the visible lines
    current_line_y = inner_battle_log_box.y
    for i, line in enumerate(visible_lines):
        color = rl.GREEN if i == 0 else rl.WHITE
        rl.draw_text(
            line,
            inner_battle_log_box.x + 10,
            current_line_y,
            font_size,
            color
        )
        current_line_y += font_size + line_spacing



    # Render the visible lines
    current_line_y = inner_battle_log_box.y
    for line in visible_lines:
        if current_line_y + font_size > inner_battle_log_box.y + inner_battle_log_box.height:
            break  # Avoid drawing outside the box
        rl.draw_text(
            line,
            inner_battle_log_box.x + 10,
            current_line_y,
            font_size,
            rl.WHITE
        )
        current_line_y += font_size + line_spacing



def draw_dice_box(pc: Creature):
    dice_box = rl.Rectangle(
        DI_BOX.x, DI_BOX.y, DI_BOX.width, DI_BOX.height
    )
    rl.draw_rectangle_rec(dice_box, rl.LIGHTGRAY)
    pc.dice_roller.update_and_draw()


def draw_player_stats_box(pc:Creature):
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

def draw_enemy_stats_box(npcs:List[Creature]):
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