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
from utils.window_config import initialize_window
# from utils.helper_classes import print_once_per_second

def main():
    print("Loading global params...")
    pcs = [create_bear_criminal()]
    npcs = [
        create_mall_cop() for _ in range(3)
        ]

    initialize_window()

    state_handler = {
        GameState.BATTLE: lambda gs: battle(gs, pcs, npcs),
        GameState.MAIN_MENU: lambda gs: main_menu(gs),
        GameState.OVERWORLD: lambda gs: overworld(gs)
    }

    gs = GameState.MAIN_MENU

    while not rl.window_should_close():
        # print_once_per_second("gs: " + str(gs))
        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)  # Always clear at the start of each frame

        if gs in state_handler:
            gs = state_handler[gs](gs)
        else:
            print("Invalid game state")
            break

        rl.end_drawing()

    rl.close_window()

if __name__ == "__main__":
    main()