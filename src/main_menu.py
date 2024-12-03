"""
Created on 11/22/2024

@author: Dan
TO RUN:
python ./src/main_menu.py
"""
import os
import raylibpy as rl
from utils.enums import GameState
from utils.buttons_etc import create_buttons
from utils.window_config import WIDTH, HEIGHT, PADDING
from utils.text_utils import load_font, draw_centered_text, unload_font


def main_menu(gs) -> GameState:
    font = load_font()  # Load the font for the main menu
    button_specs = [("Start", -1), ("Quit", 1)]
    buttons = create_buttons(button_specs, WIDTH, HEIGHT, PADDING)
    main_menu_state_handler = {"Start": GameState.OVERWORLD, "Quit": GameState.QUIT}

    while gs == GameState.MAIN_MENU:
        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)

        # Draw title
        draw_centered_text(font, "HoneyPy", WIDTH // 12, HEIGHT // 10, WIDTH)

        # Draw buttons
        for button in buttons:
            button.draw()

        # Handle button logic
        for button in buttons:
            if button.is_clicked():
                gs = main_menu_state_handler[button.option_text]  # Corrected property access

        rl.end_drawing()

    unload_font(font)  # Unload the font to free memory
    return gs
