"""
Created on 11/22/2024

@author: Dan
TO RUN:
python ./src/overworld.py
"""
import raylibpy as rl
from utils.enums import GameState
from utils.constants import PLAYER_SIZE, TARGET_SIZE, PLAYER_SPEED, PLAYER_COLOR, TARGET_COLOR
from utils.ovw_utils import EnemyOverworldCreature, PlayerOverworldCreature #, check_collision, handle_player_movement, draw_vision_cone, is_player_in_vision_cone # , is_player_in_vision_cone
from utils.window_config import WIDTH, HEIGHT
from utils.dcs import Entity
print(f"Screen Width: {WIDTH}, Screen Height: {HEIGHT}")

def overworld(gs: GameState) -> GameState:
    # Initialize player and enemy
    player_entity = Entity(WIDTH // 2, HEIGHT // 2, PLAYER_SIZE)
    player = PlayerOverworldCreature(player_entity, speed=PLAYER_SPEED)

    enemy_entity = Entity(WIDTH // 3, HEIGHT // 3, TARGET_SIZE)
    enemy = EnemyOverworldCreature(enemy_entity)

    while gs == GameState.OVERWORLD:
        if rl.window_should_close():
            gs = GameState.QUIT
            break

        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)

        # Handle player movement
        player.handle_movement()

        # Check if player is in enemy's vision cone
        if enemy.is_x_in_vision_cone(player.entity):
            rl.draw_text("Player Detected!", 10, 10, 20, rl.RED)
            enemy.chase(player.entity)  # Enemy chases the player if detected

        # Draw vision cone and entities
        enemy.draw_vision_cone()
        rl.draw_rectangle(player.entity.x, player.entity.y, player.entity.size, player.entity.size, PLAYER_COLOR)
        rl.draw_rectangle(enemy.entity.x, enemy.entity.y, enemy.entity.size, enemy.entity.size, TARGET_COLOR)

        if enemy.check_collision(player.entity):
            gs = GameState.BATTLE

        rl.end_drawing()

    return gs


# def overworld(gs: GameState) -> GameState:
#     """
#     Handles the overworld gameplay state where the player can move 
#     and interact with a static target.
    
#     Args:
#         gs (GameState): The current game state.
        
#     Returns:
#         GameState: The next game state.
#     """
#     # Initialize player and target as entities
#     player = Entity(WIDTH // 2, HEIGHT // 2, PLAYER_SIZE)
#     enemy = Entity(WIDTH // 3, HEIGHT // 3, TARGET_SIZE)

#     while gs == GameState.OVERWORLD:
#         if rl.window_should_close():  # Handle window close event
#             gs = GameState.QUIT
#             break

#         rl.begin_drawing()

#         rl.clear_background(rl.BLACK)
#                 # Draw enemy vision cone
#         draw_vision_cone(enemy) 

#         # Handle player movement
#         handle_player_movement(player, PLAYER_SPEED)

#         # Check for collision
#         if check_collision(player, enemy):
#             gs = GameState.BATTLE


#         # Check if player is in the enemy's vision cone
#         if is_player_in_vision_cone(player, enemy):
#             rl.draw_text("Player Detected!", 10, 10, 20, rl.RED)

#         # Draw player and target
#         rl.draw_rectangle(player.x, player.y, player.size, player.size, PLAYER_COLOR)
#         rl.draw_rectangle(enemy.x, enemy.y, enemy.size, enemy.size, TARGET_COLOR)


#         rl.end_drawing()

#     return gs
