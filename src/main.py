"""
Created on 11/22/2024

@author: Dan
TO RUN:
python ./src/_main.py
"""
import json
from overworld import overworld
from battle import battle
from main_menu import main_menu
import raylibpy as rl
from utils.dclasses2 import GameState
from utils.creatures import bear_criminal, mall_cop

"""
Created on 11/22/2024

@author: Dan
TO RUN:
python ./src/_main.py
"""
import json
from overworld import overworld
from battle import battle
from main_menu import main_menu
import raylibpy as rl
from utils.dclasses2 import GameState
from utils.creatures import bear_criminal, mall_cop


def main():
    # CONFIG
    print("Loading global params...")
    params = json.loads(open("./resources/global_params.json").read())
    WIDTH, HEIGHT = params["WIDTH"], params["HEIGHT"]

    # TODO: DO THIS DYNAMICALLY
    print("Loading creatures...")
    pcs = [bear_criminal]
    npcs = [mall_cop, mall_cop, mall_cop]

    # Initialize game state
    print("Initializing game state...")
    gs = GameState.MAIN_MENU

    # Initialize Raylib window
    print("Initializing Raylib window...")
    rl.init_window(WIDTH, HEIGHT, "HoneyPy")
    rl.set_target_fps(60)

    # Main game loop
    print("Starting main game loop...")
    while not rl.window_should_close():
        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)

        # Handle game states
        if gs == GameState.MAIN_MENU:
            gs = main_menu(gs, WIDTH, HEIGHT)
        elif gs == GameState.OVERWORLD:
            gs = overworld(gs, WIDTH, HEIGHT)
        elif gs == GameState.BATTLE:
            gs = battle(gs, pcs, npcs)
        elif gs == GameState.QUIT:
            print("Exiting game...")
            break  # Exit the loop immediately
        else:
            print("Invalid game state")
            break
        rl.end_drawing()

    rl.close_window()  

if __name__ == "__main__":
    main()
