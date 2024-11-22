#region IMPORTS
import asyncio
from utils.buttons_etc import Button, DiceRoller, combatButton, slider, statBar
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union
import raylibpy as rl
import os
import json
params = json.loads(open("./resources/global_params.json").read())
WIDTH, HEIGHT = params["WIDTH"], params["HEIGHT"] 

#endregion
#region ENUMS
class Target(Enum):
    SELF = 1
    SINGLE = 2
    AOE = 3
class Slider(Enum):
    BASE = 1
    POWER = 2
class Skill_Item(Enum):
    SKILL = 1
    ITEM = 2
class Base_Power(Enum):
    BASE = 1
    POWER = 2
class BattleStage(Enum):
    SELECT_SKILL_ITEM = 1
    SELECT_ITEM = 2
    SELECT_SKILL_TYPE = 3
    SELECT_SKILL = 4
    SELECT_TARGET = 5

#endregion
#region DATACLASSES
@dataclass
class Skill:
    name: str                                                       # Skill name
    damage: int = 0                                                 # Damage dealt to the opponent
    healing: int = 0                                                # Healing applied to the user
    slider_effect: int = 0                                          # Slider effect
    roll_modifier: int = 0                                          # Modifier to a future roll
    target: Target = Target.SINGLE                                  # Target of the skill
    hover_description: str = ""                                     # Description of the skill when hovered over

@dataclass
class Item:
    def __init__(
        self, name: str, 
        quantity: int = 1, 
        slider_effect: int = 0, 
        base_power: Base_Power = Base_Power.BASE, 
        healing: int = 0, 
        damage: int = 0, 
        roll_modifier: int = 0, 
        target: Target = Target.SELF,
        description: str = ""
    ):
        self.name = name
        self.quantity = quantity
        self.slider_effect = slider_effect
        self.base_power = base_power
        self.healing = healing
        self.damage = damage
        self.roll_modifier = roll_modifier
        self.target = target
        self.description = description

    def __mul__(self, multiplier: int):
        """Support quantity multiplication for inventory setup."""
        if multiplier < 1:
            raise ValueError("Multiplier must be at least 1")
        return Item(
            name=self.name,
            quantity=self.quantity * multiplier,
            slider_effect=self.slider_effect,
            base_power=self.base_power,
            healing=self.healing,
            damage=self.damage,
            roll_modifier=self.roll_modifier,
            target=self.target,
        )

    def __repr__(self):
        """String representation for debugging."""
        return f"Item(name={self.name}, quantity={self.quantity})"

@dataclass
class ChoiceManager:
    stage: BattleStage
    selected_skill_item: Union['Skill', 'Item', None]     
    selected_skill_type: Union['Base_Power', None]
    selected_skill: Union['Skill', None]
    selected_item: Union['Item', None]
    selected_target: Union[List['Creature2'], None]

#endregion
#region HELPER FUNCTIONS
def load_ascii_art(creature_name: str) -> Dict[str, str]:
    """
    Loads ASCII art from text files in the './resources/ascii_art/' folder.
    Each file should be named after the creature (e.g., 'Bear_default.txt' and 'Bear_action.txt').
    """
    folder_path = './resources/ascii_art/'
    default_file_name = f"{creature_name}_default.txt"
    action_file_name = f"{creature_name}_action.txt"
    default_path = os.path.join(folder_path, default_file_name)
    action_path = os.path.join(folder_path, action_file_name)

    art_dict = {}

    # Load the default art if the file exists
    if os.path.isfile(default_path):
        with open(default_path, 'r') as file:
            art_dict['default'] = file.read()
    else:
        art_dict['default'] = "DEFAULT ART MISSING"

    # Load the action art if the file exists
    if os.path.isfile(action_path):
        with open(action_path, 'r') as file:
            art_dict['action'] = file.read()
    else:
        art_dict['action'] = "ACTION ART MISSING"

    return art_dict

#endregion
class Creature2:
    def __init__(
        self, 
        name: str, 
        creature_type:str, 
        current_health: int, 
        max_health: int, 
        base_slider_name: str, 
        power_slider_name: str,
        base_skills: List['Skill'], 
        power_skills: List['Skill'],
        base_int: int = 4, 
        power_int: int=4,
        dice_roller: Optional[DiceRoller] = None,
        inventory: Optional[List['Item']] = None
    ):
        # REQUIRED ON INIT
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
        self.dice_roller = dice_roller
        # POST HOC ETC
        self.ascii_art = load_ascii_art(creature_type)
        self.dice_roll = 0
        self.active_slider = Base_Power.BASE
        self.roll_modifier = 0
        self.inventory = inventory if inventory is not None else []

    def set_up_dice_roller(self, dice_roller:DiceRoller):
        """Set up the DiceRoller for this creature."""
        self.dice_roller = dice_roller

    @property
    def is_alive(self) -> bool:
        # if any of these is false, player is not alive
        return self.current_health > 0 \
        and self.base_int not in [0, 8] \
        and self.power_int not in [0, 8]

    def display_stats(self, x:int, y:int, width:int, height:int, padding=10):
        """Display creature stats with better alignment and a nicely enclosed box."""
        font_size = width // 8
        # BOX FOR STUFF TO GO IN
        rl.draw_rectangle_lines_ex(
            rl.Rectangle(x, y, width+2, height+2), 
            line_thick=3, 
            color=rl.BLACK
            )
        # fill the box with a very light gray color
        rl.draw_rectangle(
            x+1, y+1, width - 1, height - 1, 
            rl.color_from_hsv(0, 0, 0.92))
        
        # CREATURE NAME
        text_width = rl.measure_text(self.name, font_size)
        rl.draw_text(
            text=self.name, 
            pos_x = x + (width - text_width) // 2, 
            pos_y = y + padding, 
            font_size=font_size, 
            color=rl.BLACK)

        # HEALTH BAR
        statBar(
            stat_name="Health",
            x=x + padding, 
            # the quarter pad, plus the font size, plus the padding
            y= y  + font_size//3*2 + padding,
            width= width - 2*padding,
            height= height // 25,
            current_value=self.current_health, 
            max_value=self.max_health,
            font_size=font_size//4*3)
        
        # BASE AND POWER NAMES ON THE SAME LINE
        adjusted_font_size = font_size
        base_text_width = rl.measure_text(self.base_name, adjusted_font_size)
        power_text_width = rl.measure_text(self.power_name, adjusted_font_size)

        # Adjust font size if text widths are too large for the box
        while base_text_width + power_text_width + 3 * padding > width:
            adjusted_font_size -= 1
            base_text_width = rl.measure_text(self.base_name, adjusted_font_size)
            power_text_width = rl.measure_text(self.power_name, adjusted_font_size)

        # Position for base (left-aligned) and power (right-aligned)
        base_name_x = x + padding
        power_name_x = x + width - power_text_width - padding
        skills_y = y  + font_size + padding + font_size//3*2 + padding + height // 25

        # Draw base and power names
        rl.draw_text(
            text=self.base_name,
            pos_x=base_name_x,
            pos_y=skills_y,
            font_size=adjusted_font_size,
            color=rl.BLACK
        )
        rl.draw_text(
            text=self.power_name,
            pos_x=power_name_x,
            pos_y=skills_y,
            font_size=adjusted_font_size,
            color=rl.BLACK
        )

        # Draw the slider for base/power stats
        slider(
            x = x + padding,
            y = skills_y + adjusted_font_size + padding,
            width=width - 2*padding,
            height=height // 25,
            base_int=self.base_int, 
            power_int=self.power_int,
        )

        # display values for base and power
        # bind to the left
        base_value_x = x + padding
        # bind to the right
        power_value_x = x + width - rl.measure_text(str(self.power_int), adjusted_font_size) - padding

        value_y = skills_y + adjusted_font_size + padding + height // 25 + padding

        rl.draw_text(
            text=str(self.base_int),
            pos_x=base_value_x,
            pos_y=value_y,
            font_size=adjusted_font_size,
            color=rl.BLACK
        )

        rl.draw_text(
            text=str(self.power_int),
            pos_x=power_value_x,
            pos_y=value_y,
            font_size=adjusted_font_size,
            color=rl.BLACK
        )

    def select_skill_or_item(
            self, choice_manager:ChoiceManager, x, y, 
            width, height) -> ChoiceManager:
        """Display buttons for selecting a skill or item."""
        #region params
        padding = height // 10
        button_width = (width + 4*padding) // 3
        button_height = (height +4*padding) // 3
        padding = height // 10
        # Total width available for spacing
        total_spacing = width - 2 * button_width  # Space left after accounting for button widths
        # Spacing between each button and the edges
        spacing = total_spacing // 3
        skill_x = x + spacing
        y_pos = y + height // 2 - button_height // 2
        item_x = x + spacing + button_width + spacing
        #endregion
        # Create buttons for the pop-up window
        skill_button = Button(
            option_text="Use Skill", 
            x= skill_x,  # First button is placed after the first spacing
            y= y_pos,  # Keep vertical alignment as is
            width= button_width,
            height= button_height,
            button_color=rl.color_from_hsv(0, 0, 0.92)
        )

        item_button = Button(
            option_text="Use Item", 
            x= item_x,  # Place the second button after the first button + spacing
            y= y_pos,  # Keep vertical alignment as is
            width= button_width,
            height= button_height,
            button_color=rl.color_from_hsv(0, 0, 0.92)
        )

        # Check if the mouse is hovering over the buttons
        if skill_button.is_hovered():
            skill_button.button_color = rl.color_from_hsv(0, 0, 0.95)
            # check if the button is clicked
            if rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON):
                choice_manager.selected_skill_item = Skill_Item.SKILL
                choice_manager.stage = BattleStage.SELECT_SKILL_TYPE
                return choice_manager

        if item_button.is_hovered():
            item_button.button_color = rl.color_from_hsv(0, 0, 0.95)
            # check if the button is clicked
            if self.inventory:
                if rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON):
                    # check to see if the player has any items
                    choice_manager.selected_skill_item = Skill_Item.ITEM
                    choice_manager.stage = BattleStage.SELECT_ITEM
                    return choice_manager
            else:
                # hover message
                hovered_message = "No items in inventory!"
                # Draw hover message near the button (e.g., above it)
                hovered_message_length = rl.measure_text(hovered_message, 20)
                hovered_message_center_x = (width//2) - (hovered_message_length // 2)
                rl.draw_text(
                    hovered_message,
                    hovered_message_center_x,
                    y + height + 20, 15, rl.RED  # Below the box
                )

        skill_button.draw()
        item_button.draw()
        return choice_manager

    def select_skill_type(
            self, choice_manager:ChoiceManager, x, y, 
            width, height) -> ChoiceManager:
        #region PARAMS
        padding = height // 10
        button_width = (width + 4*padding) // 3
        button_height = (height +4*padding) // 3
        padding = height // 10
        # Total width available for spacing
        total_spacing = width - 2 * button_width  # Space left after accounting for button widths
        # Spacing between each button and the edges
        spacing = total_spacing // 3
        base_x = x + spacing
        y_pos = y + height // 2 - button_height // 2
        power_x = x + spacing + button_width + spacing
        #endregion    
        # Create buttons for the pop-up window
        base_button = Button(
            option_text=self.base_name, 
            x= base_x,  # First button is placed after the first spacing
            y= y_pos,  # Keep vertical alignment as is
            width= button_width,
            height= button_height,
            button_color=rl.color_from_hsv(0, 0, 0.92)
        )

        power_button = Button(
            option_text=self.power_name, 
            x= power_x,  # Place the second button after the first button + spacing
            y= y_pos,  # Keep vertical alignment as is
            width= button_width,
            height= button_height,
            button_color=rl.color_from_hsv(0, 0, 0.92)
        )

        # Check if the mouse is hovering over the buttons
        if base_button.is_hovered():
            base_button.button_color = rl.color_from_hsv(0, 0, 0.95)
            # check if the button is clicked
            if rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON):
                choice_manager.selected_skill_type = Base_Power.BASE
                choice_manager.stage = BattleStage.SELECT_SKILL
                return choice_manager

        if power_button.is_hovered():
            power_button.button_color = rl.color_from_hsv(0, 0, 0.95)
            # check if the button is clicked
            if rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON):
                choice_manager.selected_skill_type = Base_Power.POWER
                choice_manager.stage = BattleStage.SELECT_SKILL
                return choice_manager
        
        base_button.draw()
        power_button.draw()
        return choice_manager

    def select_skill(
        self, choice_manager:ChoiceManager, x: int, y: int, 
        width: int, height: int) -> ChoiceManager:
        """Display skill buttons, detect hover and click, and return the selected skill."""
        #region PARAMS
        padding = height // 10
        button_width = (width - 4 * padding) // 3
        button_height = (height +4*padding) // 3
        hovered_message = ""  # Message to display on hover
        font_size = 20 

        #endregion
        skills_list = self.base_skills \
            if choice_manager.selected_skill_type == Base_Power.BASE \
                else self.power_skills
        button_y = y + (height - button_height) // 2
        for idx, skill in enumerate(skills_list):
            # Determine row and column

            # Calculate button position
            button_x = x + padding + (idx % 3) * (button_width + padding)
            # Get mouse position
            mouse_x, mouse_y = rl.get_mouse_position()

            # Check if the mouse is hovering over the button
            is_hovered = (
                button_x <= mouse_x <= button_x + button_width
                and button_y <= mouse_y <= button_y + button_height
            )

            # Change color on hover
            button_color = rl.color_from_hsv(0, 0, 0.92) if not is_hovered else rl.color_from_hsv(0, 0, 0.95)

            # Draw the button

            button = Button(
                option_text=skill.name, 
                x=button_x, 
                y=button_y, 
                width=button_width, 
                height=button_height, 
                button_color=button_color
            )
            button.draw()

            # Display hover message
            if is_hovered:
                hovered_message = skill.hover_description
                hovered_message_length = rl.measure_text(hovered_message, font_size)

# Center the hover message globally
                hovered_message_center_x = (width//2) - (hovered_message_length // 2)
                rl.draw_text(
                    hovered_message,
                    hovered_message_center_x,
                    button_y - 20,  # Above the button
                    font_size,
                    rl.DARKGRAY,
                )

            # Detect click
            if is_hovered and rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON):
                choice_manager.selected_skill = skill
                choice_manager.stage = BattleStage.SELECT_TARGET
                return choice_manager
            
            # If no skill is clicked, display the hover message (if any)
            if hovered_message:
                rl.draw_text(
                    hovered_message, x, y + height + 20, 15, rl.DARKGRAY  # Below the box
                )

        return choice_manager       

    def select_target(
        self, 
        choice_manager: ChoiceManager, 
        npcs: List['Creature2'],
        x: int,
        y: int,
        width: int,
        height: int) -> List['Creature2']:
        """Allows the player to select a target from the given list of NPCs."""
        #region PARAMS
        padding = height // 10
        num_buttons = len(npcs)  # Number of buttons
        button_width = (width - (num_buttons + 1) * padding) // num_buttons
        button_height = (height +4*padding) // 3
        total_buttons_width = num_buttons * button_width + (num_buttons - 1) * padding
        # Center buttons horizontally
        start_x = x + (width - total_buttons_width) // 2
        # Center buttons vertically
        start_y = y + (height - button_height) // 2
        #endregion

        #region IF ELSE STATEMENTs
        if choice_manager.selected_skill:
            if choice_manager.selected_skill.target == Target.SELF:
                choice_manager.selected_target = [self]
                choice_manager.stage = BattleStage.SELECT_SKILL_ITEM
                return choice_manager
            if choice_manager.selected_skill.target == Target.AOE:
                choice_manager.selected_target = npcs
                choice_manager.stage = BattleStage.SELECT_SKILL_ITEM
                return choice_manager
        if choice_manager.selected_item:
            if choice_manager.selected_item.target == Target.SELF:
                choice_manager.selected_target = [self]
                choice_manager.stage = BattleStage.SELECT_SKILL_ITEM
                return choice_manager
            if choice_manager.selected_item.target == Target.AOE:
                choice_manager.selected_target = npcs
                choice_manager.stage = BattleStage.SELECT_SKILL_ITEM
                return choice_manager
        #endregion

        # Display the target selection box
        for idx, target in enumerate(npcs):
            # Calculate button position
            button_x = start_x + idx * (button_width + padding)
            button_y = start_y

            # Get mouse position
            mouse_x, mouse_y = rl.get_mouse_position()

            # Check if the mouse is hovering over the button
            is_hovered = (
                button_x <= mouse_x <= button_x + button_width
                and button_y <= mouse_y <= button_y + button_height
            )
            button_color = rl.color_from_hsv(0, 0, 0.92) if not is_hovered else rl.color_from_hsv(0, 0, 0.95)

            button = Button(
                option_text=target.name, 
                x=button_x, 
                y=button_y, 
                width=button_width, 
                height=button_height, 
                button_color=button_color
            )
            button.draw()

            if is_hovered and rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON):
                # Return the selected target
                choice_manager.selected_target = [target]
                choice_manager.stage = BattleStage.SELECT_SKILL_ITEM
                return choice_manager

        return choice_manager

    def select_item(
            self, choice_manager: ChoiceManager, 
            x: int, y: int, 
            width: int, height: int
        ) -> ChoiceManager:
        """Allows the player to select an item from the inventory."""
        # Parameters
        padding = height // 10
        vertical_padding = padding // 2  # Extra padding for top/bottom of each button
        max_buttons_per_row = 3
        num_buttons = len(self.inventory)
        font_size = 15

        # Calculate button dimensions
        num_rows = 2
        button_width = (width - (max_buttons_per_row + 1) * padding) // max_buttons_per_row
        button_height = (height - (num_rows - 1) * padding - 2 * vertical_padding * num_rows) // num_rows

        # Calculate total dimensions and centering adjustments
        total_width = min(num_buttons, max_buttons_per_row) * button_width + (min(num_buttons, max_buttons_per_row) - 1) * padding
        total_height = num_rows * button_height + (num_rows - 1) * padding + 2 * vertical_padding
        start_x = x + (width - total_width) // 2
        start_y = y + (height - total_height) // 2

        # Draw each button
        for idx, item in enumerate(self.inventory):
            idx_x = idx % max_buttons_per_row
            idx_y = idx // max_buttons_per_row

            # Calculate button position
            button_x = start_x + idx_x * (button_width + padding)
            button_y = start_y + idx_y * (button_height + padding) + vertical_padding

            # Get mouse position
            mouse_x, mouse_y = rl.get_mouse_position()

            # Check hover
            is_hovered = (
                button_x <= mouse_x <= button_x + button_width
                and button_y <= mouse_y <= button_y + button_height
            )
            button_color = rl.color_from_hsv(0, 0, 0.92) if not is_hovered else rl.color_from_hsv(0, 0, 0.95)

            # Draw button
            button = Button(
                option_text=f"{item.name}: {item.quantity}", 
                x=button_x, 
                y=button_y, 
                width=button_width, 
                height=button_height, 
                button_color=button_color
            )
            button.draw()

            # Handle click
            # Display hover message
            if is_hovered:
                hovered_message = item.description
                hovered_message_length = rl.measure_text(hovered_message, font_size)

                # Center the hover message globally
                hovered_message_center_x = (width//2) - (hovered_message_length // 2)
                rl.draw_text(
                    hovered_message,
                    hovered_message_center_x,
                    start_y - padding // 2, 
                    font_size,
                    rl.DARKGRAY,
                )
            if is_hovered and rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON):
                # Decrement quantity
                item.quantity -= 1
                
                # Remove item if quantity is zero
                if item.quantity <= 0:
                    self.inventory.pop(idx)
                
                # Update choice manager
                choice_manager.selected_item = item
                choice_manager.stage = BattleStage.SELECT_TARGET
                return choice_manager

            # Detect click
            if is_hovered and rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON):
                choice_manager.selected_item = item
                choice_manager.stage = BattleStage.SELECT
                return choice_manager

        return choice_manager

    def roll_dice(self):
        """Roll the dice asynchronously."""
        self.dice_roll = self.dice_roller.update_and_draw()
        return self.dice_roll

    

#     @property
#     def roll_success(self) -> bool:
#         slider_val = self.base_int if self.active_slider == Base_Power.BASE else self.power_int
#         over_under = slider_val - self.dice_roll + self.roll_modifier
#         self.roll_modifier = 0  
#         if over_under >= 0:
#             return True, over_under
#         return False, over_under

#     async def use_skill(self, skill: 'Skill', targets: List['Creature']):
#         """Use the selected skill on the target(s) asynchronously."""
#         # Roll the dice asynchronously
#         await self.roll_dice()
#         success, over_under = self.roll_success()

#         # If the roll is successful, apply the skill's effects
#         if success:
#             extra = 1 if over_under >= 2 else 0  # Extra effect if roll is significantly successful
            
#             for target in targets:
#                 rl.begin_drawing()

#                 # Apply damage (if applicable)
#                 if skill.damage > 0:
#                     effective_damage = skill.damage + max(0, over_under)
#                     target.current_health = max(0, target.current_health - effective_damage)
                    
#                     # Display damage on screen
#                     rl.draw_text(f"{self.name} deals {effective_damage} damage to {target.name}!", 
#                                 10, 10, 20, rl.RED)
#                     rl.end_drawing()
#                     await asyncio.sleep(0.5)  # Pause to show feedback

#                 # Apply healing (if applicable)
#                 if skill.healing > 0:
#                     effective_healing = skill.healing + max(0, over_under)
#                     self.current_health = min(self.max_health, self.current_health + effective_healing)
                    
#                     # Display healing on screen
#                     rl.begin_drawing()
#                     rl.draw_text(f"{self.name} heals for {effective_healing} HP!", 
#                                 10, 40, 20, rl.GREEN)
#                     rl.end_drawing()
#                     await asyncio.sleep(0.5)

#                 # Apply slider effect (if applicable)
#                 if skill.slider_effect != 0:
#                     target.roll_modifier += skill.slider_effect + extra
                    
#                     # Display slider effect change
#                     rl.begin_drawing()
#                     rl.draw_text(f"{target.name}'s roll modifier adjusted by {skill.slider_effect + extra}!", 
#                                 10, 70, 20, rl.YELLOW)
#                     rl.end_drawing()
#                     await asyncio.sleep(0.5)

#                 # Apply next roll modifier (if applicable)
#                 if skill.roll_modifier != 0:
#                     target.roll_modifier += skill.roll_modifier + extra
                    
#                     # Display next roll modifier change
#                     rl.begin_drawing()
#                     rl.draw_text(f"{target.name}'s next roll modifier adjusted by {skill.roll_modifier + extra}!", 
#                                 10, 100, 20, rl.CYAN)
#                     rl.end_drawing()
#                     await asyncio.sleep(0.5)

#                 # End the drawing context to ensure the game remains responsive
#                 rl.end_drawing()

#         await asyncio.sleep(0)  # Yield control back to the event loop to keep the game responsive

#     async def select_item(self) -> Union['Item', None]:
#         """Allows the player to select an item from the inventory asynchronously."""
#         text = "Select an Item:"
#         text_x, text_y = get_text_position(text)

#         while True:
#             rl.begin_drawing()

#             # Check if the inventory is empty
#             if not self.inventory:
#                 no_items_text = "No items in inventory!"
#                 no_items_x, no_items_y = get_text_position(no_items_text, text_y + BUTTON_HEIGHT + PADDING)
#                 rl.draw_text(no_items_text, no_items_x, no_items_y, 20, rl.RED)
#                 rl.end_drawing()
#                 await asyncio.sleep(0.5)  # Pause briefly to avoid busy waiting
#                 return None

#             # Draw the prompt text
#             rl.draw_text(text, text_x, text_y, 20, rl.BLACK)

#             # Draw buttons for each item in the inventory with its quantity
#             for i, item in enumerate(self.inventory):
#                 item_button_x, item_button_y = get_button_position(i, base_y=text_y + BUTTON_HEIGHT + (2 * PADDING))
                
#                 if combatButton(f"{item.name}: {item.quantity}", item_button_x, item_button_y, BUTTON_WIDTH, BUTTON_HEIGHT):
#                     # Decrease the quantity of the selected item
#                     item.quantity -= 1
#                     if item.quantity <= 0:
#                         self.inventory.remove(item)
                    
#                     rl.end_drawing()
#                     return item  # Return the selected item

#             # End drawing and yield control to allow for other tasks
#             rl.end_drawing()
#             await asyncio.sleep(0.05)



#     def use_item(self, item: 'Item', target: List['Creature']):
#         """Use the selected item on the target."""
#         for targ in target:
#             # Apply healing (only if positive)
#             if item.healing > 0:
#                 effective_healing = item.healing
#                 targ.current_health = min(targ.max_health, targ.current_health + effective_healing)
#                 print(f"{self.name} heals {targ.name} for {effective_healing} HP!")

#             # Apply damage (only if positive)
#             if item.damage > 0:
#                 effective_damage = item.damage
#                 targ.current_health = max(0, targ.current_health - effective_damage)
#                 print(f"{self.name} deals {effective_damage} damage to {targ.name}!")

#             # Apply slider effect (only if non-zero)
#             if item.slider_effect != 0:
#                 targ.roll_modifier += item.slider_effect
#                 print(f"{targ.name}'s roll modifier adjusted by {item.slider_effect}!")

#             # Apply next roll modifier (only if non-zero)
#             if item.roll_modifier != 0:
#                 targ.roll_modifier += item.roll_modifier
#                 print(f"{targ.name}'s next roll modifier adjusted by {item.roll_modifier}!")
# #
