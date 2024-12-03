"""
Created on 11/22/2024

@author: Dan
TO RUN:
python ./src/main.py
"""
import json
from overworld import overworld
from battle import battle
from main_menu import main_menu
import raylibpy as rl
from utils.enums import GameState
from utils.creatures import create_bear_criminal, create_mall_cop
# from utils.helper_classes import print_once_per_second

def main():
    print("Loading global params...")
    params = json.loads(open("./resources/global_params.json").read())
    WIDTH, HEIGHT = params["WIDTH"], params["HEIGHT"]
    pcs = [create_bear_criminal()]
    npcs = [
        create_mall_cop() for _ in range(3)
        ]

    rl.init_window(WIDTH, HEIGHT, "HoneyPy")
    rl.set_target_fps(60)

    gs = GameState.MAIN_MENU

    while not rl.window_should_close():
        # print_once_per_second("gs: " + str(gs))
        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)  # Always clear at the start of each frame

        if gs == GameState.BATTLE:
            gs = battle(gs, pcs, npcs)
        elif gs == GameState.MAIN_MENU:
            gs = main_menu(gs, WIDTH, HEIGHT)
        elif gs == GameState.OVERWORLD:
            gs = overworld(gs, WIDTH, HEIGHT)
        elif gs == GameState.QUIT:
            break  # Exit the loop immediately
        else:
            print("Invalid game state")
            break

        rl.end_drawing()

    rl.close_window()

if __name__ == "__main__":
    main()