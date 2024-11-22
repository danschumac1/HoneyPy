import asyncio
from dataclasses import dataclass, field
import json
from random import randint
from typing import Dict, List, Optional, Tuple, Union
from enum import Enum
import numpy as np
import raylibpy as rl
from utils.helper_classes import Skill, Item, Skill_Item, Base_Power, Target,load_ascii_art
from utils.buttons_etc import Button, combatButton, get_button_position, get_text_position

#endregion
class Creature:
    def __init__(
        self, name: str, creature_type:str, current_health: int, 
        max_health: int, base_slider_name: str, power_slider_name: str,
        base_skills: List['Skill'], power_skills: List['Skill'],
        base_int: int = 4, power_int: int=4,
        inventory: Optional[List['Item']] = None
    ):
        # Basic attributes
        self.name = name
        self.creture_type = creature_type
        self.current_health = current_health
        self.max_health = max_health
        self.base_name = base_slider_name
        self.power_name = power_slider_name
        self.base_int = base_int
        self.power_int = power_int
        self.base_skills = base_skills
        self.power_skills = power_skills
        self.ascii_art = load_ascii_art(creature_type)
        self.dice_roll = 0
        self.active_slider = Base_Power.BASE
        self.roll_modifier = 0
        self.dice_roller = None


        # Initialize inventory to an empty list if not provided
        self.inventory = inventory if inventory is not None else []
        # Optional attributes (set to None initially)


    def set_up_dice_roller(self, DiceRoller):
        self.dice_roller = DiceRoller

    @property
    def is_alive(self) -> bool:
        return self.current_health > 0 \
        and self.base_int not in [0, 8] \
        and self.power_int not in [0, 8]

    def display_stats(self, x, y):
        """Display creature stats with better alignment and a nicely enclosed box."""
        box_width = 400
        box_height = 150

        # Draw the enclosing box
        rl.draw_rectangle_lines_ex(rl.Rectangle(x-1, y-1, box_width+2, box_height+2), 3, rl.BLACK)
        # fill the box with a very light gray color
        rl.draw_rectangle(x, y, box_width - 1, box_height - 1, rl.color_from_hsv(0, 0, 0.92))
        # Draw the creature's name centered within the box
        text_width = rl.measure_text(self.name, 20)
        rl.draw_text(self.name, x + (box_width - text_width) // 2, y, 20, rl.BLACK)

        # Draw health bar aligned within the box
        statBar("Health", self.current_health, self.max_health, x + 10, y + 30)

        # Draw the slider for base/power stats
        slider(
            x + 10, y + 80,
            base_name=self.base_name, power_name=self.power_name,
            base=self.base_int, power=self.power_int,
            width=300, height=30
        )

    async def roll_dice(self):
        """Use the DiceRoller to roll asynchronously."""
        if not self.dice_roller.is_rolling():
            self.dice_roller.start_roll()

        # Draw and update the dice roller
        while self.dice_roller.is_rolling():
            self.dice_roller.update_and_draw()
            await asyncio.sleep(0.05)

        # Once rolling is complete, update the creature's dice_roll value
        self.dice_roll = self.dice_roller.get_result()
    
    async def select_skill_or_item(self) -> Union[Skill_Item, None]:
        """Allow the player to select a skill type or item asynchronously."""
        
        # Create buttons for the pop-up window
        skill_button = Button("Use Skill", pop_up_x + 20, pop_up_y + 80)
        item_button = Button("Use Item", pop_up_x + 20, pop_up_y + 140)
        
        # Create the pop-up window with the buttons
        pop_up = PopUpWindow([skill_button, item_button], "Select an Action")
        
        while True:
            # Draw the pop-up and wait for a selection
            selected_action = pop_up.draw()
            
            # Handle the player's selection
            if selected_action == "Use Skill":
                return Skill_Item.SKILL
            elif selected_action == "Use Item":
                if not self.inventory:
                    # Show a message if the inventory is empty and wait briefly
                    pop_up.display_message("No items in inventory!", duration=1.0)
                else:
                    return Skill_Item.ITEM

            await asyncio.sleep(0.05)

    async def select_skill_type(self) -> Tuple[List['Skill'], str]:
        """Allows the player to select the skill type asynchronously."""
        text = "Select Skill Type:"
        text_x, text_y = get_text_position(text)

        # Adjust button positions relative to the text position
        base_button_y = text_y + BUTTON_HEIGHT + PADDING

        while True:
            rl.begin_drawing()

            # Draw the prompt text
            rl.draw_text(text, text_x, text_y, 20, rl.BLACK)

            # Draw "Base" button
            if combatButton(self.base_name, *get_button_position(0, base_button_y), BUTTON_WIDTH, BUTTON_HEIGHT):
                self.active_slider = Base_Power.BASE
                rl.end_drawing()
                return self.base_skills, self.base_name

            # Draw "Power" button with consistent spacing
            if combatButton(self.power_name, *get_button_position(1, base_button_y), BUTTON_WIDTH, BUTTON_HEIGHT):
                self.active_slider = Base_Power.POWER
                rl.end_drawing()
                return self.power_skills, self.power_name

            rl.end_drawing()
            await asyncio.sleep(0.05)


    async def select_skill(self, skills: List['Skill']) -> 'Skill':
        """Allows the player to select a skill from the given list asynchronously."""
        text = "Select a Skill:"
        text_x, text_y = get_text_position(text)

        while True:
            rl.begin_drawing()

            # Draw the prompt text
            rl.draw_text(text, text_x, text_y, 20, rl.BLACK)

            # Draw buttons for each skill
            for i, skill in enumerate(skills):
                skill_button_x, skill_button_y = get_button_position(i, text_y + BUTTON_HEIGHT + PADDING)
                if combatButton(skill.name, skill_button_x, skill_button_y, BUTTON_WIDTH, BUTTON_HEIGHT):
                    rl.end_drawing()
                    return skill

            rl.end_drawing()
            await asyncio.sleep(0.05)

    async def select_target(
            self, skill_item: Union['Skill', 'Item'], 
            npcs: List['Creature']) -> List['Creature']:
        """Allows the player to select a target from the given list of NPCs."""
        text = "Select a Target:"
        text_x, text_y = get_text_position(text)

        # Handle cases where the skill targets self or all enemies
        if skill_item.target == Target.SELF:
            return [self]

        if skill_item.target == Target.AOE:
            return npcs

        while True:
            rl.begin_drawing()

            # Draw the prompt text
            rl.draw_text(text, text_x, text_y, 20, rl.BLACK)

            # Draw buttons for each NPC
            for i, npc in enumerate(npcs):
                if npc.is_alive:
                    button_x, button_y = get_button_position(i, text_y + BUTTON_HEIGHT + PADDING)
                    if combatButton(npc.name, button_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT):
                        rl.end_drawing()
                        return [npc]

            rl.end_drawing()
            await asyncio.sleep(0.05)


    @property
    def roll_success(self) -> bool:
        slider_val = self.base_int if self.active_slider == Base_Power.BASE else self.power_int
        over_under = slider_val - self.dice_roll + self.roll_modifier
        self.roll_modifier = 0  
        if over_under >= 0:
            return True, over_under
        return False, over_under

    async def use_skill(self, skill: 'Skill', targets: List['Creature']):
        """Use the selected skill on the target(s) asynchronously."""
        # Roll the dice asynchronously
        await self.roll_dice()
        success, over_under = self.roll_success()

        # If the roll is successful, apply the skill's effects
        if success:
            extra = 1 if over_under >= 2 else 0  # Extra effect if roll is significantly successful
            
            for target in targets:
                rl.begin_drawing()

                # Apply damage (if applicable)
                if skill.damage > 0:
                    effective_damage = skill.damage + max(0, over_under)
                    target.current_health = max(0, target.current_health - effective_damage)
                    
                    # Display damage on screen
                    rl.draw_text(f"{self.name} deals {effective_damage} damage to {target.name}!", 
                                10, 10, 20, rl.RED)
                    rl.end_drawing()
                    await asyncio.sleep(0.5)  # Pause to show feedback

                # Apply healing (if applicable)
                if skill.healing > 0:
                    effective_healing = skill.healing + max(0, over_under)
                    self.current_health = min(self.max_health, self.current_health + effective_healing)
                    
                    # Display healing on screen
                    rl.begin_drawing()
                    rl.draw_text(f"{self.name} heals for {effective_healing} HP!", 
                                10, 40, 20, rl.GREEN)
                    rl.end_drawing()
                    await asyncio.sleep(0.5)

                # Apply slider effect (if applicable)
                if skill.slider_effect != 0:
                    target.roll_modifier += skill.slider_effect + extra
                    
                    # Display slider effect change
                    rl.begin_drawing()
                    rl.draw_text(f"{target.name}'s roll modifier adjusted by {skill.slider_effect + extra}!", 
                                10, 70, 20, rl.YELLOW)
                    rl.end_drawing()
                    await asyncio.sleep(0.5)

                # Apply next roll modifier (if applicable)
                if skill.roll_modifier != 0:
                    target.roll_modifier += skill.roll_modifier + extra
                    
                    # Display next roll modifier change
                    rl.begin_drawing()
                    rl.draw_text(f"{target.name}'s next roll modifier adjusted by {skill.roll_modifier + extra}!", 
                                10, 100, 20, rl.CYAN)
                    rl.end_drawing()
                    await asyncio.sleep(0.5)

                # End the drawing context to ensure the game remains responsive
                rl.end_drawing()

        await asyncio.sleep(0)  # Yield control back to the event loop to keep the game responsive

    async def select_item(self) -> Union['Item', None]:
        """Allows the player to select an item from the inventory asynchronously."""
        text = "Select an Item:"
        text_x, text_y = get_text_position(text)

        while True:
            rl.begin_drawing()

            # Check if the inventory is empty
            if not self.inventory:
                no_items_text = "No items in inventory!"
                no_items_x, no_items_y = get_text_position(no_items_text, text_y + BUTTON_HEIGHT + PADDING)
                rl.draw_text(no_items_text, no_items_x, no_items_y, 20, rl.RED)
                rl.end_drawing()
                await asyncio.sleep(0.5)  # Pause briefly to avoid busy waiting
                return None

            # Draw the prompt text
            rl.draw_text(text, text_x, text_y, 20, rl.BLACK)

            # Draw buttons for each item in the inventory with its quantity
            for i, item in enumerate(self.inventory):
                item_button_x, item_button_y = get_button_position(i, base_y=text_y + BUTTON_HEIGHT + (2 * PADDING))
                
                if combatButton(f"{item.name}: {item.quantity}", item_button_x, item_button_y, BUTTON_WIDTH, BUTTON_HEIGHT):
                    # Decrease the quantity of the selected item
                    item.quantity -= 1
                    if item.quantity <= 0:
                        self.inventory.remove(item)
                    
                    rl.end_drawing()
                    return item  # Return the selected item

            # End drawing and yield control to allow for other tasks
            rl.end_drawing()
            await asyncio.sleep(0.05)



    def use_item(self, item: 'Item', target: List['Creature']):
        """Use the selected item on the target."""
        for targ in target:
            # Apply healing (only if positive)
            if item.healing > 0:
                effective_healing = item.healing
                targ.current_health = min(targ.max_health, targ.current_health + effective_healing)
                print(f"{self.name} heals {targ.name} for {effective_healing} HP!")

            # Apply damage (only if positive)
            if item.damage > 0:
                effective_damage = item.damage
                targ.current_health = max(0, targ.current_health - effective_damage)
                print(f"{self.name} deals {effective_damage} damage to {targ.name}!")

            # Apply slider effect (only if non-zero)
            if item.slider_effect != 0:
                targ.roll_modifier += item.slider_effect
                print(f"{targ.name}'s roll modifier adjusted by {item.slider_effect}!")

            # Apply next roll modifier (only if non-zero)
            if item.roll_modifier != 0:
                targ.roll_modifier += item.roll_modifier
                print(f"{targ.name}'s next roll modifier adjusted by {item.roll_modifier}!")
#