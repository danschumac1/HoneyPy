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
from utils.text_utils import load_font
from utils.window_config import initialize_window
# from utils.helper_classes import print_once_per_second

def main():
    """
    The main function initializes the game window, sets up the game state handler, and runs the game loop.
    It performs the following steps:
    1. Prints a message indicating that global parameters are being loaded.
    2. Creates player characters (pcs) and non-player characters (npcs).
    3. Initializes the game window.
    4. Defines a state handler dictionary that maps game states to their corresponding functions.
    5. Sets the initial game state to MAIN_MENU.
    6. Enters the game loop, which continues until the window should close:
        - Clears the screen at the start of each frame.
        - Calls the appropriate function based on the current game state.
        - Ends the drawing for the current frame.
    7. Closes the game window when the loop exits.
    """
    initialize_window()
    font = load_font()
    pcs = [create_bear_criminal() for _ in range(2)]
    npcs = [create_mall_cop() for _ in range(3)]

    state_handler = {
        GameState.BATTLE: lambda gs: battle(gs, pcs, npcs, font),
        GameState.MAIN_MENU: lambda gs: main_menu(gs),
        GameState.OVERWORLD: lambda gs: overworld(gs)
    }

    gs = GameState.MAIN_MENU

    while not rl.window_should_close():

        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)  # Always clear at the start of each frame

        if gs in state_handler:
            gs = state_handler[gs](gs)
        else:
            print("Invalid game state")
            break

        rl.end_drawing()
    rl.unload_font(font)
    rl.close_window()

if __name__ == "__main__":
    main()