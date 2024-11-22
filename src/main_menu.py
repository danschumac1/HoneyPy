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

params = json.loads(open("./resources/global_params.json").read())
WIDTH, HEIGHT = params["WIDTH"], params["HEIGHT"]

def main_menu():
    rl.init_window(WIDTH, HEIGHT, "Battle Layout")
    rl.set_target_fps(60)
    padding = HEIGHT // 25
    font_path = os.path.join(os.getcwd(), "resources", "font", "joystix monospace.otf")
    font = rl.load_font(font_path)
    #check if exists

    start_button = Button( # TODO fix global params
        "Start", WIDTH//2 - BUTTON_WIDTH//2, HEIGHT//2 - padding
        )
    quit_button = Button(
        "Quit", WIDTH//2 - BUTTON_WIDTH//2, HEIGHT//2 + padding
        )


    while not rl.window_should_close():
        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)
        
        # Write title in big letters and custom font
        text = "HoneyPy"
        font_size = 50
        text_len = rl.measure_text(text, font_size)

        rl.draw_text_ex(
            font, 
            "HoneyPy", 
            rl.Vector2(
                WIDTH//2 - text_len//2,
                HEIGHT//10), 
            font_size, 
            0, 
            rl.BLACK
            )

        start_button.draw()
        quit_button.draw()

        if start_button.is_clicked():
            print("Start button pressed")
        if quit_button.is_clicked():
            rl.close_window()
            break

        rl.end_drawing()
        

if __name__ == '__main__':
    main_menu()