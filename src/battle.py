"""
Created on 11/17/2024

@author: Dan
TO RUN:
python ./src/battle_layout
"""

# Battle loop
import os
from typing import List
import raylibpy as rl
from utils.buttons_etc import DiceRoller
from utils.combat_manager import (
    draw_ascii_art_box, draw_battle_log_box, draw_dice_box, 
    draw_enemy_stats_box, draw_player_stats_box)
from utils.dclasses2 import ChoiceManager, Creature
from utils.window_config import DI_BOX, EART_BOX, PART_BOX
from utils.enums import GameState, BattleStage

def battle(gs: GameState, pcs: List[Creature], npcs: List[Creature]):
    #region CONFIG
    font_path = os.path.join(os.getcwd(), "resources", "font", "joystix monospace.otf")
    font = rl.load_font(font_path)
    for pc in pcs:
        pc.is_player = True
        pc.possible_targets = npcs
    for npc in npcs:
        npc.possible_targets = pcs
    player_cm = ChoiceManager()
    enemy_cm = ChoiceManager()
    battle_log = []
    #endregion

    while gs == GameState.BATTLE:
        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)

        # Player turns
        for pc in pcs:
            if not pc.is_alive:
                continue
            while player_cm.stage != BattleStage.WRAP_UP:
                rl.begin_drawing()
                rl.clear_background(rl.RAYWHITE)
                draw_ascii_art_box(
                    pc.ascii_art['default'], 
                    font,
                    PART_BOX, 
                    color=rl.GREEN
                )
                draw_ascii_art_box(
                    npc.ascii_art['default'], 
                    font,
                    EART_BOX, 
                    color=rl.WHITE
                )
                draw_player_stats_box(pc)
                draw_dice_box(pc)
                draw_enemy_stats_box(npcs)
                draw_battle_log_box(player_cm, battle_log)
                player_cm = pc.take_turn(player_cm)
                rl.end_drawing()

            player_cm.partial_reset()

        # Enemy turns
        for npc in npcs:
            if not npc.is_alive:
                continue
            while enemy_cm.stage != BattleStage.WRAP_UP:
                rl.begin_drawing()
                rl.clear_background(rl.RAYWHITE)
                draw_ascii_art_box(
                    pc.ascii_art['default'], 
                    font,
                    PART_BOX, 
                    color=rl.WHITE
                )
                draw_ascii_art_box(
                    npc.ascii_art['default'], 
                    font,
                    EART_BOX, 
                    color=rl.RED
                )
                draw_player_stats_box(pcs[0])  # Assuming you display stats of the first player
                draw_enemy_stats_box(npcs)
                draw_battle_log_box(enemy_cm, battle_log)
                draw_dice_box(npc)

                # rl.begin_drawing()
                enemy_cm = npc.take_turn(enemy_cm)
                rl.end_drawing()

            enemy_cm.partial_reset()

        # Check if battle is over
        if all(not pc.is_alive for pc in pcs):
            battle_log.append("All players have been defeated! You lose!")
            gs = GameState.MAIN_MENU
        elif all(not npc.is_alive for npc in npcs):
            battle_log.append("All enemies have been defeated! You win!")
            gs = GameState.OVERWORLD
        rl.end_drawing()

    return gs

if __name__ == "__main__":
    battle()

# def battle(gs: GameState, pcs:List[Creature], npcs:List[Creature]):
#     #region CONFIG
#     font_path = os.path.join(os.getcwd(), "resources", "font", "joystix monospace.otf")
#     font = rl.load_font(font_path)
#     for pc in pcs:
#         pc.is_player = True
#         pc.possible_targets = npcs
#     for npc in npcs:
#         npc.possible_targets = pcs
#     player_cm = ChoiceManager()
#     enemy_cm = ChoiceManager()
#     battle_log = []
#     player_turn = True
#     #endregion
#     while gs == GameState.BATTLE:
#         rl.begin_drawing()
#         # take all player turns
#         rl.clear_background(rl.RAYWHITE)

#         active_cm = player_cm if player_turn else enemy_cm
#         draw_ascii_art_box(
#             pcs[0].ascii_art['default'], 
#             font,
#             PART_BOX, 
#             color=rl.GREEN if player_turn else rl.WHITE
#             )
#         draw_ascii_art_box(
#             npcs[0].ascii_art['default'], 
#             font,
#             EART_BOX, 
#             color=rl.GREEN if not player_turn else rl.WHITE
#             )
#         draw_player_stats_box(pcs[0])
#         draw_dice_box(pcs[0]) # THIS IS WHERE UPDATE_AND_DRAW IS CALLED
#         draw_enemy_stats_box(npcs)
#         draw_battle_log_box(active_cm, battle_log)
#         draw_dice_box(pcs[0])
#         # active_cm = pcs[0].take_turn(active_cm)
#         active_cm = pcs[0].take_turn(active_cm)
#         rl.end_drawing()
#     return gs