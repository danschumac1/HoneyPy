"""
Created on 11/17/2024

@author: Dan
TO RUN:
python ./src/battle_layout
"""

# Main loop
import os
from typing import List
import raylibpy as rl
from utils.buttons_etc import DiceRoller
from utils.combat_manager import (
    draw_ascii_art_box, draw_battle_log_box, draw_choice_box, draw_dice_box, 
    draw_enemy_stats_box, draw_player_stats_box)
from utils.dclasses2 import BattleStage, ChoiceManager, Creature2, GameState
from utils.window_config import DI_BOX, EART_BOX, PART_BOX

def battle(gs: GameState, pcs:List[Creature2], npcs:List[Creature2]):
    for player in pcs:
        player.set_up_dice_roller(
            dice_roller=DiceRoller(
                x = DI_BOX.x + DI_BOX.width // 2,
                y = DI_BOX.y + DI_BOX.height // 2,
                size=DI_BOX.width // 2,
                roll_duration=0.5
                )
            )
    player_turn = True
    font_path = os.path.join(os.getcwd(), "resources", "font", "joystix monospace.otf")
    font = rl.load_font(font_path)
    player_cm = ChoiceManager()
    enemy_cm = ChoiceManager(
        player_bool=False,
    )
    battle_log = []

    while gs == GameState.BATTLE:
        active_cm = player_cm if player_turn else enemy_cm
        rl.begin_drawing()
        # rl.clear_background(rl.BLACK)

        # Draw each quadrant independently
        draw_ascii_art_box(
            pcs[0].ascii_art['default'], 
            font,
            PART_BOX, 
            color=rl.GREEN if player_turn else rl.WHITE
            )
        draw_ascii_art_box(
            npcs[0].ascii_art['default'], 
            font,
            EART_BOX, 
            color=rl.GREEN if not player_turn else rl.WHITE
            )
        
        draw_player_stats_box(pcs[0])
        draw_dice_box(pcs[0])
        draw_enemy_stats_box(npcs)
        draw_battle_log_box(active_cm,battle_log)

        if player_turn:
            player_cm = draw_choice_box(player_cm, pcs[0], npcs)
            if player_cm.stage == BattleStage.WRAP_UP:
                print("Player's turn is over")
                player_cm.partial_reset()
                player_turn = False
        else:
            print("Enemy's turn")
            enemy_cm = draw_choice_box(enemy_cm, npcs[0], pcs)
            if enemy_cm.stage == BattleStage.WRAP_UP:
                player_turn = True
                enemy_cm.partial_reset()
                print("Enemy's turn is over")
                player_turn = True

        # check if the battle is over
        if not all(npc.is_alive for npc in npcs) or not all(pc.is_alive for pc in pcs):
            gs = GameState.OVERWORLD
            return gs
            print("Battle is over")
        
        rl.end_drawing()

if __name__ == "__main__":
    battle()



# TESTING FEATURES
# if rl.is_key_pressed(rl.KEY_SPACE):
#     # flip player_turn
#     if player_initiative:
#         player_initiative = False
#     else:
#         player_initiative = True
# if rl.is_key_pressed(rl.KEY_Q):
#     i+=1
#     battle_log.append(f"Player pressed {i}")
# if rl.is_key_pressed(rl.KEY_W):
#     pcs[0].roll_dice()
