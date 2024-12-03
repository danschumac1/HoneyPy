"""
Created on 11/22/2024

@author: Dan
TO RUN:
python ./src/overworld.py
"""
import raylibpy as rl
from utils.enums import GameState
from utils.constants import PLAYER_SIZE, TARGET_SIZE, PLAYER_SPEED, PLAYER_COLOR, TARGET_COLOR
from utils.ovw_utils import check_collision, handle_player_movement
from utils.window_config import WIDTH, HEIGHT
from utils.dcs import Entity

def overworld(gs: GameState) -> GameState:
    """
    Handles the overworld gameplay state where the player can move 
    and interact with a static target.
    
    Args:
        gs (GameState): The current game state.
        
    Returns:
        GameState: The next game state.
    """
    # Initialize player and target as entities
    player = Entity(WIDTH // 2, HEIGHT // 2, PLAYER_SIZE)
    target = Entity(WIDTH // 3, HEIGHT // 3, TARGET_SIZE)

    while gs == GameState.OVERWORLD:
        if rl.window_should_close():  # Handle window close event
            gs = GameState.QUIT
            break

        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)

        # Handle player movement
        handle_player_movement(player, PLAYER_SPEED)

        # Check for collision
        if check_collision(player, target):
            gs = GameState.BATTLE

        # Draw player and target
        rl.draw_rectangle(player.x, player.y, player.size, player.size, PLAYER_COLOR)
        rl.draw_rectangle(target.x, target.y, target.size, target.size, TARGET_COLOR)

        rl.end_drawing()

    return gs
