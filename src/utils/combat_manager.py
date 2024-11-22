import asyncio
from utils.dclasses2 import Skill_Item, Target
from utils.logging import log_it
import json
import random
params = json.loads(open("./resources/global_params.json").read())
WIDTH, HEIGHT = params["WIDTH"], params["HEIGHT"]

def display_combat_stats(pcs, npcs):
    """Display stats for both player characters and NPCs."""
      # Log the display of combat stats
    for i, pc in enumerate(pcs):
        log_it(f"Displaying stats for {pc.name}")
        x_position = 20
        y_position = HEIGHT // 40 + i * 160
        pc.display_stats(x_position, y_position)

    for i, npc in enumerate(npcs):
        log_it(f"Displaying stats for {npc.name}")
        x_position = WIDTH - 450
        y_position = HEIGHT // 40 + i * 160
        npc.display_stats(x_position, y_position)
    
async def player_turn(pc, pcs, npcs):
    """Handle player's turn asynchronously."""
    log_it(f"entered player_turn function")
    skill_item_choice = await pc.select_skill_or_item()
    log_it(f"Player {pc.name} chose {skill_item_choice}")
    if skill_item_choice == Skill_Item.SKILL:
        skill_list, skill_type = await pc.select_skill_type()
        skill = await pc.select_skill(skill_list)
        target = await pc.select_target(skill, npcs)
        pc.use_skill(skill, target)

    elif skill_item_choice == Skill_Item.ITEM:
        item = await pc.select_item()
        target = await pc.select_target(item, npcs)
        pc.use_item(item, target)

async def enemy_turn(npc, pcs):
    """Enemy turn with random skill and target selection."""
    if not npc.is_alive:
        return

    skill_list = random.choice(
        [npc.base_skills, npc.power_skills]) \
        if npc.base_skills and npc.power_skills \
        else (npc.base_skills or npc.power_skills)
    skill = random.choice(skill_list)

    if skill.target == Target.SELF:
        target = [npc]
    elif skill.target == Target.AOE:
        target = pcs
    else:
        target = [random.choice(pcs)]

    npc.use_skill(skill, target)

def combat_over(pcs, npcs):
    """Check if combat is over."""
    return all(not pc.is_alive for pc in pcs) or all(not npc.is_alive for npc in npcs)
