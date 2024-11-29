import os
from typing import Dict
import raylibpy as rl

def print_once_per_second(msg: str):
    if rl.get_time() % 1 < 0.01:
        print(msg)

def load_ascii_art(creature_name: str) -> Dict[str, str]:
    """
    Loads ASCII art from text files in the './resources/ascii_art/' folder.
    Each file should be named after the creature (e.g., 'Bear_default.txt' and 'Bear_action.txt').
    """
    folder_path = './resources/ascii_art/'
    default_file_name = f"{creature_name}_default.txt"
    action_file_name = f"{creature_name}_action.txt"
    default_path = os.path.join(folder_path, default_file_name)
    action_path = os.path.join(folder_path, action_file_name)

    art_dict = {}

    # Load the default art if the file exists
    if os.path.isfile(default_path):
        with open(default_path, 'r') as file:
            art_dict['default'] = file.read()
    else:
        art_dict['default'] = "DEFAULT ART MISSING"

    # Load the action art if the file exists
    if os.path.isfile(action_path):
        with open(action_path, 'r') as file:
            art_dict['action'] = file.read()
    else:
        art_dict['action'] = "ACTION ART MISSING"

    return art_dict