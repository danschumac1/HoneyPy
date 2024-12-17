"""
Created on 11/22/2024

@author: Dan
TO RUN:
python ./src/overworld.py
"""
import raylibpy as rl
from utils.enums import GameState
from utils.constants import PLAYER_SIZE, TARGET_SIZE, PLAYER_SPEED, PLAYER_COLOR, TARGET_COLOR
from utils.visual_fx import VisualEffect, VisualEffectsManager
from utils.window_config import WIDTH, HEIGHT
from utils.dcs import Entity
from utils.logging import Logger
from utils.ovw_creatures import player, enemy

def overworld(gs: GameState) -> GameState:
    logger = Logger(
        log_path="logs/overworld.log",
    )
    effects_manager = VisualEffectsManager()

    # Add some initial effects
    effects_manager.add_effect(VisualEffect.RAIN)
    # effects_manager.add_effect(VisualEffect.FIREFLIES)
    # effects_manager.add_effect(VisualEffect.LEAVES)


    logger.info(player)
    logger.info(enemy)

    logger.info("Starting overworld gameplay loop")
    while gs == GameState.OVERWORLD:
        if rl.window_should_close():
            gs = GameState.QUIT
            break

        rl.begin_drawing()
        rl.clear_background(rl.BLACK)

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

        effects_manager.update_and_draw()
        rl.end_drawing()

    return gs