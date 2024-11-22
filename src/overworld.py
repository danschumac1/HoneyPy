"""
Created on 11/22/2024

@author: Dan
TO RUN:
python ./src/overworld.py
"""

import raylibpy as rl

# Window dimensions
WIDTH = 800
HEIGHT = 600

# Player and target dimensions
PLAYER_SIZE = 30
TARGET_SIZE = 30

def overworld():
    # Initialize Raylib
    rl.init_window(WIDTH, HEIGHT, "Overworld")
    rl.set_target_fps(60)

    # Player setup
    player_x = WIDTH // 2
    player_y = HEIGHT // 2
    player_speed = 5

    # Target setup (orange square)
    target_x = WIDTH // 3
    target_y = HEIGHT // 3

    while not rl.window_should_close():
        # Handle input for player movement
        if rl.is_key_down(rl.KEY_W):  # Move up
            player_y -= player_speed
        if rl.is_key_down(rl.KEY_S):  # Move down
            player_y += player_speed
        if rl.is_key_down(rl.KEY_A):  # Move left
            player_x -= player_speed
        if rl.is_key_down(rl.KEY_D):  # Move right
            player_x += player_speed

        # Check for collision (player overlaps with target)
        if (
            player_x < target_x + TARGET_SIZE and
            player_x + PLAYER_SIZE > target_x and
            player_y < target_y + TARGET_SIZE and
            player_y + PLAYER_SIZE > target_y
        ):
            print("Battle Start")

        # Drawing logic
        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)

        # Draw the player (red square)
        rl.draw_rectangle(player_x, player_y, PLAYER_SIZE, PLAYER_SIZE, rl.RED)

        # Draw the target (orange square)
        rl.draw_rectangle(target_x, target_y, TARGET_SIZE, TARGET_SIZE, rl.ORANGE)

        rl.end_drawing()

    rl.close_window()

if __name__ == '__main__':
    overworld()
