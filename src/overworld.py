"""
Created on 11/22/2024

@author: Dan
TO RUN:
python ./src/overworld.py
"""
from utils.dclasses2 import GameState
import raylibpy as rl

def overworld(gs: GameState, WIDTH: int, HEIGHT: int):
    # Player setup
    PLAYER_SIZE = WIDTH // 20
    TARGET_SIZE = WIDTH // 20
    player_x = WIDTH // 2
    player_y = HEIGHT // 2
    player_speed = 5

    # Target setup (orange square)
    target_x = WIDTH // 3
    target_y = HEIGHT // 3

    while gs == GameState.OVERWORLD:
        # Handle input for player movement
        if rl.is_key_down(rl.KEY_W):  # Move up
            player_y -= player_speed
        if rl.is_key_down(rl.KEY_S):  # Move down
            player_y += player_speed
        if rl.is_key_down(rl.KEY_A):  # Move left
            player_x -= player_speed
        if rl.is_key_down(rl.KEY_D):  # Move right
            player_x += player_speed

        # Check for collision
        if (
            player_x < target_x + TARGET_SIZE and
            player_x + PLAYER_SIZE > target_x and
            player_y < target_y + TARGET_SIZE and
            player_y + PLAYER_SIZE > target_y
        ):
            gs = GameState.BATTLE

        # Drawing logic
        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)

        # Draw player (red square)
        rl.draw_rectangle(player_x, player_y, PLAYER_SIZE, PLAYER_SIZE, rl.RED)

        # Draw target (orange square)
        rl.draw_rectangle(target_x, target_y, TARGET_SIZE, TARGET_SIZE, rl.ORANGE)

        rl.end_drawing()

    return gs
