"""
Created on 11/22/2024

@author: Dan
TO RUN:
python ./src/main_menu.py
"""
import os
from utils.buttons_etc import BUTTON_WIDTH, Button
import raylibpy as rl
import json

from utils.dclasses2 import GameState

# params = json.loads(open("./resources/global_params.json").read())
# WIDTH, HEIGHT = params["WIDTH"], params["HEIGHT"]

def main_menu(gs, WIDTH, HEIGHT):
    PADDING = HEIGHT // 25
    font_path = os.path.join(os.getcwd(), "resources", "font", "joystix monospace.otf")
    font = rl.load_font(font_path)
    #check if exists

    start_button = Button( # TODO fix global params
        "Start", WIDTH//2 - BUTTON_WIDTH//2, HEIGHT//2 - PADDING
        )
    quit_button = Button(
        "Quit", WIDTH//2 - BUTTON_WIDTH//2, HEIGHT//2 + PADDING
        )

    while not rl.window_should_close():
        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)
        
        # Write title in big letters and custom font
        text = "HoneyPy"
        font_size = 50
        text_len = rl.measure_text(text, font_size)

        rl.draw_text_ex(
            font=font, 
            text="HoneyPy", 
            position=rl.Vector2(
                WIDTH//2 - text_len//2,
                HEIGHT//10), 
            font_size= font_size, 
            spacing=0, 
            tint=rl.BLACK
            )

        start_button.draw()
        quit_button.draw()

        if start_button.is_clicked():
            return GameState.OVERWORLD
        if quit_button.is_clicked():
            return GameState.QUIT
        rl.end_drawing()
    return gs