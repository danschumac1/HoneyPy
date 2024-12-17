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
    draw_ascii_art_box, draw_ascii_art_for_creatures, draw_battle_log_box, draw_dice_box, 
    draw_enemy_stats_box, draw_player_stats_box)
from utils.dclasses2 import ChoiceManager, Creature
from utils.window_config import DI_BOX, EART_BOX, PART_BOX
from utils.enums import GameState, BattleStage
from utils.constants import PADDING

def check_if_battle_over(pcs:List[Creature], npcs:List[Creature], battle_log:List[str]):
        # Check if battle is over
        if all(not pc.is_alive for pc in pcs):
            battle_log.append("All players have been defeated! You lose!")
            gs = GameState.MAIN_MENU
        elif all(not npc.is_alive for npc in npcs):
            battle_log.append("All enemies have been defeated! You win!")
            gs = GameState.OVERWORLD
        else:
            gs = GameState.BATTLE
        return gs

def battle(gs: GameState, pcs: List[Creature], npcs: List[Creature], font):
    #region CONFIG
    for pc in pcs:
        pc.is_player = True
        pc.possible_targets = npcs
    for npc in npcs:
        npc.possible_targets = pcs
    battle_log = []
    #endregion

    while gs == GameState.BATTLE:
        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)

        for creature in pcs + npcs:
            if not creature.is_alive:
                continue

            # the creature continues to take its turn until it has made all its choices
            # this is in a while loop to allow player time to press boxes 
            #   and to animate the dice etc
            while creature.cm.stage != BattleStage.WRAP_UP:
                rl.begin_drawing()
                rl.clear_background(rl.RAYWHITE)
                draw_ascii_art_for_creatures(
                    creatures=pcs,
                    font=font,
                    box=PART_BOX,  # Total height of 450 for 3 creatures
                    padding=10,                           # 10 pixels of padding between each creature
                )

                # Example call for NPCs (right side)
                draw_ascii_art_for_creatures(
                    creatures=npcs,
                    font=font,
                    box=EART_BOX,
                    padding=10,
                )

                draw_player_stats_box(pcs[0])
                draw_dice_box(creature)
                draw_enemy_stats_box(npcs)
                draw_battle_log_box(creature.cm, battle_log)
                creature.cm = creature.take_turn()
                rl.end_drawing()

            creature.cm.partial_reset()

        rl.end_drawing()
        gs = check_if_battle_over(pcs, npcs, battle_log)

    return gs

if __name__ == "__main__":
    battle()