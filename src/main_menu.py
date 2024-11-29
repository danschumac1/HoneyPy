"""
Created on 11/22/2024

@author: Dan
TO RUN:
python ./src/main_menu.py
"""
import os
import raylibpy as rl
from utils.enums import GameState
from utils.buttons_etc import BUTTON_WIDTH, Button

def main_menu(gs, WIDTH, HEIGHT):
    PADDING = HEIGHT // 25
    font_path = os.path.join(os.getcwd(), "resources", "font", "joystix monospace.otf")
    font = rl.load_font(font_path)

    start_button = Button("Start", WIDTH // 2 - BUTTON_WIDTH // 2, HEIGHT // 2 - PADDING)
    quit_button = Button("Quit", WIDTH // 2 - BUTTON_WIDTH // 2, HEIGHT // 2 + PADDING)

    while gs == GameState.MAIN_MENU:
        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)
        # Draw title
        text = "HoneyPy"
        font_size = 50
        text_len = rl.measure_text_ex(font, text, font_size, 0).x
        rl.draw_text_ex(
            font=font,
            text=text,
            position=rl.Vector2(WIDTH // 2 - text_len // 2, HEIGHT // 10),
            font_size=font_size,
            spacing=0,
            tint=rl.BLACK,
        )

        # Draw buttons
        start_button.draw()
        quit_button.draw()

        # Handle button logic
        if start_button.is_clicked():
            gs = GameState.OVERWORLD
        if quit_button.is_clicked():
            gs = GameState.QUIT
        rl.end_drawing()
    return gs