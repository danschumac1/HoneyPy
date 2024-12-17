import json
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Union
import raylibpy as rl
from utils.buttons_etc import Button, DiceRoller, slider, statBar
from utils.dclasses2_backup import Item, Skill
from utils.enums import Base_Power, BattleStage, Skill_Item, Target
from utils.helper_classes import load_ascii_art
from utils.window_config import CHOICE_BOX, DI_BOX

params = json.loads(open("./resources/global_params.json").read())
WIDTH, HEIGHT = params["WIDTH"], params["HEIGHT"] 

from dataclasses import dataclass
from typing import List, Union

@dataclass
class ChoiceManager:
    stage: BattleStage = BattleStage.SELECT_SKILL_ITEM
    player_bool: bool = True
    selected_skill_type: Union[Base_Power, None] = None
    selected_skill: Union[Skill, None] = None
    selected_item: Union[Item, None] = None
    selected_target: Union[List['Creature'], None] = None
    new_message: bool = False
    message: str = ""
    is_rolling: bool = False
    # a default factory list
    enemy_targets: List['Creature'] = field(default_factory=list)
    dice_roll: int = 0
    selected_skill_or_item_choice: Union[Skill_Item, None] = None

    def complete_reset(self):
        """Resets the ChoiceManager instance to its default state."""
        self.stage = BattleStage.SELECT_SKILL_ITEM
        self.selected_skill_or_item_choice = None
        self.selected_skill_type = None
        self.selected_skill = None
        self.selected_item = None
        self.selected_target = None
        self.new_message: bool = False
        self.message: str = ""
        self.enemy_targets = []
        self.dice_roll = 0

    def partial_reset(self):
        """Resets the ChoiceManager instance to a partial state."""
        self.stage = BattleStage.SELECT_SKILL_ITEM
        self.selected_skill_or_item_choice = None
        self.selected_skill_type = None
        self.selected_skill = None
        self.selected_item = None
        self.selected_target = None
        self.dice_roll = 0
        
class Creature(ABC):
    def __init__(
        self,
        name: str,
        creature_type: str,
        current_health: int,
        max_health: int,
        base_slider_name: str,
        power_slider_name: str,
        base_skills: List['Skill'],
        power_skills: List['Skill'],
        base_int: int = 4,
        power_int: int = 4,
        dice_roller: Optional[DiceRoller] = DiceRoller(
                x = DI_BOX.x + DI_BOX.width // 2,
                y = DI_BOX.y + DI_BOX.height // 2,
                size=DI_BOX.width // 2,
                roll_duration=0.5
                ),
        inventory: Optional[List['Item']] = None,
        is_player: bool = False,
        possible_targets: List['Creature'] = [],
        cm = ChoiceManager(),
        is_light_up: bool = False
    ):
        self.name = name
        self.creature_type = creature_type
        self.current_health = current_health
        self.max_health = max_health
        self.base_name = base_slider_name
        self.power_name = power_slider_name
        self.base_int = base_int
        self.power_int = power_int
        self.base_skills = base_skills
        self.power_skills = power_skills
        self.dice_roller = dice_roller
        self.ascii_art = load_ascii_art(creature_type)
        self.active_slider = Base_Power.BASE
        self.roll_modifier = 0
        self.inventory = inventory if inventory else []
        self.is_player = is_player
        self.possible_targets = possible_targets
        self.cm = cm
        self.is_light_up = is_light_up

    @property
    def is_alive(self) -> bool:
        return self.current_health > 0 \
            and self.base_int not in [0, 8] \
            and self.power_int not in [0, 8]

    def display_stats(self, x: int, y: int, width: int, height: int, padding=10):
        font_size = width // 8
        rl.draw_rectangle_lines_ex(
            rl.Rectangle(x, y, width + 2, height + 2),
            line_thick=3,
            color=rl.BLACK
        )
        rl.draw_rectangle(
            x + 1, y + 1, width - 1, height - 1,
            rl.color_from_hsv(0, 0, 0.92)
        )
        text_width = rl.measure_text(self.name, font_size)
        rl.draw_text(
            text=self.name,
            pos_x=x + (width - text_width) // 2,
            pos_y=y + padding,
            font_size=font_size,
            color=rl.BLACK
        )
        statBar(
            stat_name="Health",
            x=x + padding,
            y=y + font_size // 3 * 2 + padding,
            width=width - 2 * padding,
            height=height // 25,
            current_value=self.current_health,
            max_value=self.max_health,
            font_size=font_size // 4 * 3
        )
        adjusted_font_size = font_size
        base_text_width = rl.measure_text(self.base_name, adjusted_font_size)
        power_text_width = rl.measure_text(self.power_name, adjusted_font_size)
        while base_text_width + power_text_width + 3 * padding > width:
            adjusted_font_size -= 1
            base_text_width = rl.measure_text(self.base_name, adjusted_font_size)
            power_text_width = rl.measure_text(self.power_name, adjusted_font_size)
        base_name_x = x + padding
        power_name_x = x + width - power_text_width - padding
        skills_y = y + font_size + padding + font_size // 3 * 2 + padding + height // 25
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
        slider(
            x=x + padding,
            y=skills_y + adjusted_font_size + padding,
            width=width - 2 * padding,
            height=height // 25,
            base_int=self.base_int,
            power_int=self.power_int
        )
        base_value_x = x + padding
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
    
    def roll_success(self) -> bool:
        slider_val = self.base_int if self.active_slider == Base_Power.BASE else self.power_int

        over_under = slider_val - self.cm.dice_roll + self.roll_modifier
        self.roll_modifier = 0  
        if over_under >= 0:
            return True, over_under
        return False, over_under
   
    def use_skill(self):
            """Use the selected skill on the target(s) asynchronously."""
            # Roll the dice asynchronously
            success, over_under = self.roll_success()

            # If the roll is successful, apply the skill's effects
            if success:
                self.power_int += 1
                self.base_int -=1
                extra = 1 if over_under >= 2 else 0  # Extra effect if roll is significantly successful
                for target in self.cm.selected_target:
                    # Apply damage (if applicable)
                    if self.cm.selected_skill.damage > 0:
                        effective_damage = self.cm.selected_skill.damage + max(0, over_under)
                        target.current_health = max(0, target.current_health - effective_damage)
                        self.cm.message = \
                            f"{self.name} deals {effective_damage} damage to {target.name}!"
                        self.cm.new_message = True
                        self.cm.stage = BattleStage.WRAP_UP

                    # Apply healing (if applicable)
                    if self.cm.selected_skill.healing > 0:
                        effective_healing = self.cm.selected_skill.healing + max(0, over_under)
                        self.current_health = min(self.max_health, self.current_health + effective_healing)
                        self.cm.message = \
                            f"{self.name} heals for {effective_healing} HP!"
                        self.cm.new_message = True
                        self.cm.stage = BattleStage.WRAP_UP

                    # Apply slider effect (if applicable)
                    if self.cm.selected_skill.slider_effect != 0:
                        target.roll_modifier += self.cm.selected_skill.slider_effect + extra
                        self.cm.message = \
                            f"{target.name}'s roll modifier adjusted by {self.cm.selected_skill.slider_effect + extra}!"
                        self.cm.new_message = True
                        self.cm.stage = BattleStage.WRAP_UP

                    # Apply next roll modifier (if applicable)
                    if self.cm.selected_skill.roll_modifier != 0:
                        target.roll_modifier += self.cm.selected_skill.roll_modifier + extra
                        self.cm.message = \
                            f"{target.name}'s next roll modifier adjusted by {self.cm.selected_skill.roll_modifier + extra}!"
                        self.cm.new_message = True
                        self.cm.stage = BattleStage.WRAP_UP
            else:
                self.base_int += 1
                self.power_int -= 1
                self.cm.message = f"{self.name} rolled too high!"
                self.cm.new_message = True
                self.cm.stage = BattleStage.WRAP_UP
            return self.cm
        
    def use_item(self):
        """Use the selected item on the target(s) asynchronously."""
        for target in self.cm.selected_target:
            # Apply damage (if applicable)
            if self.cm.selected_item.damage > 0:
                target.current_health = max(0, target.current_health - self.cm.selected_item.damage)
                self.cm.message = \
                    f"{self.name} deals {self.cm.selected_item.damage} damage to {target.name}!"
                self.cm.new_message = True
                self.cm.stage = BattleStage.WRAP_UP

            # Apply healing (if applicable)
            if self.cm.selected_item.healing > 0:
                self.current_health = min(self.max_health, self.current_health + self.cm.selected_item.healing)
                self.cm.message = \
                    f"{self.name} heals for {self.cm.selected_item.healing} HP!"
                self.cm.new_message = True
                self.cm.stage = BattleStage.WRAP_UP

            # Apply slider effect (if applicable)
            if self.cm.selected_item.slider_effect != 0:
                target.roll_modifier += self.cm.selected_item.slider_effect 
                self.cm.message = \
                    f"{target.name}'s roll modifier adjusted by {self.cm.selected_item.slider_effect}!"
                self.cm.new_message = True
                self.cm.stage = BattleStage.WRAP_UP

            # Apply next roll modifier (if applicable)
            if self.cm.selected_item.roll_modifier != 0:
                target.roll_modifier += self.cm.selected_item.roll_modifier
                self.cm.message = \
                    f"{target.name}'s next roll modifier adjusted by {self.cm.selected_item.roll_modifier}!"
                self.cm.new_message = True
                self.cm.stage = BattleStage.WRAP_UP

        # Reset the choice manager
        return self.cm
    
    def update_possible_targets(self):
        self.possible_targets = [npc for npc in self.possible_targets if npc.is_alive]
    
    def take_turn(self):
        if self.cm.stage == BattleStage.SELECT_SKILL_ITEM:
            self.is_light_up = True
            self.cm = self.select_skill_or_item(CHOICE_BOX.x, CHOICE_BOX.y, CHOICE_BOX.width, CHOICE_BOX.height)
            return self.cm

        elif self.cm.stage == BattleStage.SELECT_SKILL_TYPE:
            self.cm = self.select_skill_type(CHOICE_BOX.x, CHOICE_BOX.y, CHOICE_BOX.width, CHOICE_BOX.height)
            return self.cm

        elif self.cm.stage == BattleStage.SELECT_SKILL:
            self.cm = self.select_skill(CHOICE_BOX.x, CHOICE_BOX.y, CHOICE_BOX.width, CHOICE_BOX.height)
            return self.cm

        elif self.cm.stage == BattleStage.SELECT_TARGET:
            self.cm = self.select_target(CHOICE_BOX.x, CHOICE_BOX.y, CHOICE_BOX.width, CHOICE_BOX.height)
            return self.cm

        elif self.cm.stage == BattleStage.SELECT_ITEM:
            self.cm = self.select_item(CHOICE_BOX.x, CHOICE_BOX.y, CHOICE_BOX.width, CHOICE_BOX.height)
            return self.cm

        elif self.cm.stage == BattleStage.ROLL_DICE:
            # if the dice is done rolling, save the info and return early
            for target in self.cm.selected_target:
                target.is_light_up = True

            if self.dice_roller.is_finished_rolling:
                self.cm.dice_roll = self.dice_roller.final_number
                self.cm.stage = BattleStage.USE_SKILL_ITEM
                self.dice_roller.reset()
                for target in self.cm.selected_target:
                    target.is_light_up = False
                return self.cm 
            
            # else, start rolling the dice
            if not self.dice_roller.is_rolling:
                self.dice_roller.start_roll()

            return self.cm 

        elif self.cm.stage == BattleStage.USE_SKILL_ITEM:
            if self.cm.selected_item:
                self.cm = self.use_item()
            elif self.cm.selected_skill:
                self.cm = self.use_skill()
            else:
                raise ValueError("No skill or item selected.")

            # After using the skill or item, go to the WAIT_FOR_CONTINUE stage
            self.cm.stage = BattleStage.WAIT_FOR_CONTINUE
            return self.cm

        elif self.cm.stage == BattleStage.WAIT_FOR_CONTINUE:
            # Button dimensions and positioning
            button_width = 200
            button_height = 50
            button_x=CHOICE_BOX.x + CHOICE_BOX.width // 2 - button_width // 2
            button_y=CHOICE_BOX.y + CHOICE_BOX.height // 2 - button_height // 2

            # Get mouse position
            mouse_x, mouse_y = rl.get_mouse_position()

            # Check if the mouse is hovering over the button
            is_hovered = (
                button_x <= mouse_x <= button_x + button_width
                and button_y <= mouse_y <= button_y + button_height
            )

            # Change button color based on hover state
            button_color = rl.color_from_hsv(0, 0, 0.92) if not is_hovered else rl.color_from_hsv(0, 0, 0.95)

            # Draw button
            continue_button = Button(
                option_text="Click to Continue",
                x=button_x,
                y=button_y,
                width=button_width,
                height=button_height,
                button_color=button_color
            )

            continue_button.draw()

            # Check for button click or Enter key press
            if rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON) and is_hovered:
                self.cm.stage = BattleStage.WRAP_UP  # Proceed to wrap-up stage
                self.is_light_up = False
            elif rl.is_key_pressed(rl.KEY_ENTER):
                self.cm.stage = BattleStage.WRAP_UP  # Proceed to wrap-up stage
                self.is_light_up = False
            return self.cm
        elif self.cm.stage == BattleStage.WRAP_UP:
            self.update_possible_targets()
            return self.cm
        return self.cm  # Return ChoiceManager in case of unexpected flow

    @abstractmethod
    def select_skill_or_item(self, x, y, width, height) -> ChoiceManager:
        pass

    @abstractmethod
    def select_skill_type(self, x, y, width, height) -> ChoiceManager:
        pass

    @abstractmethod
    def select_skill(self, x, y, width, height) -> ChoiceManager:
        pass

    @abstractmethod
    def select_target(self, x, y, width, height) -> List['Creature']:
        pass

    @abstractmethod
    def select_item(self, x, y, width, height) -> ChoiceManager:
        pass

class PlayerCreature(Creature):
    def select_skill_or_item(
            self, x, y, 
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
                self.cm.selected_skill_or_item_choice = Skill_Item.SKILL
                self.cm.stage = BattleStage.SELECT_SKILL_TYPE
                return self.cm

        if item_button.is_hovered():
            item_button.button_color = rl.color_from_hsv(0, 0, 0.95)
            # check if the button is clicked
            if self.inventory:
                if rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON):
                    # check to see if the player has any items
                    self.cm.selected_skill_or_item_choice = Skill_Item.ITEM
                    self.cm.stage = BattleStage.SELECT_ITEM
                    return self.cm
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
        return self.cm

    def select_skill_type(
            self, x, y, 
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
                self.cm.selected_skill_type = Base_Power.BASE
                self.cm.stage = BattleStage.SELECT_SKILL
                return self.cm

        if power_button.is_hovered():
            power_button.button_color = rl.color_from_hsv(0, 0, 0.95)
            # check if the button is clicked
            if rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON):
                self.cm.selected_skill_type = Base_Power.POWER
                self.cm.stage = BattleStage.SELECT_SKILL
                return self.cm

        base_button.draw()
        power_button.draw()
        return self.cm

    def select_skill(
        self, x: int, y: int, 
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
            if self.cm.selected_skill_type == Base_Power.BASE \
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
                self.cm.selected_skill = skill
                self.cm.stage = BattleStage.SELECT_TARGET
                return self.cm
            
            # If no skill is clicked, display the hover message (if any)
            if hovered_message:
                rl.draw_text(
                    hovered_message, x, y + height + 20, 15, rl.DARKGRAY  # Below the box
                )

        return self.cm       

    def select_target(
        self, 
        x: int,
        y: int,
        width: int,
        height: int) -> List[Creature]:
        """Allows the player to select a target from the given list of NPCs."""
        #region PARAMS
        padding = height // 10
        num_buttons = len(self.possible_targets)  # Number of buttons
        if num_buttons == 0:
            num_buttons = 1
            self.cm.message = "No enemies to target!"
        button_width = (width - (num_buttons + 1) * padding) // num_buttons
        button_height = (height +4*padding) // 3
        total_buttons_width = num_buttons * button_width + (num_buttons - 1) * padding
        # Center buttons horizontally
        start_x = x + (width - total_buttons_width) // 2
        # Center buttons vertically
        start_y = y + (height - button_height) // 2
        #endregion

        #region IF ELSE STATEMENTs
        if self.cm.selected_skill:
            if self.cm.selected_skill.target == Target.SELF:
                self.cm.selected_target = [self]
                self.cm.stage = BattleStage.ROLL_DICE
                self.cm.message = f"{self.name} uses {self.cm.selected_skill.name} on themselves!"
                self.cm.new_message = True
                return self.cm
            elif self.cm.selected_skill.target == Target.AOE:
                # select all possible targets
                self.cm.selected_target = self.cm.enemy_targets
                self.cm.stage = BattleStage.ROLL_DICE
                self.cm.message = f"{self.name} uses {self.cm.selected_skill.name} on all enemies!"
                self.cm.new_message = True
                return self.cm
            elif self.cm.selected_skill.target == Target.SINGLE:
                for idx, target in enumerate(self.possible_targets):
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
                    if is_hovered:
                        target.is_light_up = True
                    else:
                        target.is_light_up = False
                    # draw an outline around the enemy stats 
                    
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
                        self.cm.selected_target = [target]
                        if self.cm.selected_skill:
                            self.cm.message = f"{self.name} uses {self.cm.selected_skill.name} on {target.name}!"
                            self.cm.new_message = True
                        if self.cm.selected_item:
                            self.cm.message = f"{self.name} uses {self.cm.selected_item.name} on {target.name}!"
                            self.cm.new_message = True
                        # move onto the next stage
                        self.cm.stage = BattleStage.ROLL_DICE
                        return self.cm
        elif self.cm.selected_item:
            if self.cm.selected_item.target == Target.SELF:
                self.cm.selected_target = [self]
                self.cm.stage = BattleStage.USE_SKILL_ITEM
                self.cm.message = f"{self.name} uses {self.cm.selected_item.name} on themselves!"
                self.cm.new_message = True
                return self.cm
            elif self.cm.selected_item.target == Target.AOE:
                # select all possible targets
                self.cm.selected_target = self.cm.enemy_targets
                self.cm.stage = BattleStage.USE_SKILL_ITEM
                self.cm.message = f"{self.name} uses {self.cm.selected_item.name} on all enemies!"
                return self.cm
            elif self.cm.selected_item.target == Target.SINGLE:
                for idx, target in enumerate(self.possible_targets):
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
                    # draw an outline around the enemy stats 
                    
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
                        self.cm.selected_target = [target]
                        if self.cm.selected_skill:
                            self.cm.message = f"{self.name} uses {self.cm.selected_skill.name} on {target.name}!"
                            self.cm.new_message = True
                        if self.cm.selected_item:
                            self.cm.message = f"{self.name} uses {self.cm.selected_item.name} on {target.name}!"
                            self.cm.new_message = True
                        # move onto the next stage
                        self.cm.stage = BattleStage.USE_SKILL_ITEM
                        return self.cm
            
        # Display the target selection box
        
        return self.cm

    def select_item(
            self,
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
                self.cm.selected_item = item
                self.cm.stage = BattleStage.SELECT_TARGET
                return self.cm

            # Detect click
            if is_hovered and rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON):
                self.cm.selected_item = item
                self.cm.stage = BattleStage.SELECT_TARGET
                return self.cm
        return self.cm

    # def use_skill(self, cm:ChoiceManager):
    #     """Use the selected skill on the target(s) asynchronously."""
    #     # Roll the dice asynchronously
    #     success, over_under = self.roll_success(cm)

        # # If the roll is successful, apply the skill's effects
        # if success:
        #     self.power_int += 1
        #     self.base_int -= 1
        #     extra = 1 if over_under >= 2 else 0  # Extra effect if roll is significantly successful
        #     for target in cm.selected_target:
        #         # Apply damage (if applicable)
        #         if cm.selected_skill.damage > 0:
        #             effective_damage = cm.selected_skill.damage + max(0, over_under)
        #             target.current_health = max(0, target.current_health - effective_damage)

        #             cm.message = \
        #                 f"{self.name} deals {effective_damage} damage to {target.name}!"
        #             cm.new_message = True
        #             cm.stage = BattleStage.WRAP_UP

        #         # Apply healing (if applicable)
        #         if cm.selected_skill.healing > 0:
        #             effective_healing = cm.selected_skill.healing + max(0, over_under)
        #             self.current_health = min(self.max_health, self.current_health + effective_healing)
        #             cm.message = \
        #                 f"{self.name} heals for {effective_healing} HP!"
        #             cm.new_message = True
        #             cm.stage = BattleStage.WRAP_UP

        #         # Apply slider effect (if applicable)
        #         if cm.selected_skill.slider_effect != 0:
        #             target.roll_modifier += cm.selected_skill.slider_effect + extra
        #             cm.message = \
        #                 f"{target.name}'s roll modifier adjusted by {cm.selected_skill.slider_effect + extra}!"
        #             cm.new_message = True
        #             cm.stage = BattleStage.WRAP_UP

        #         # Apply next roll modifier (if applicable)
        #         if cm.selected_skill.roll_modifier != 0:
        #             target.roll_modifier += cm.selected_skill.roll_modifier + extra
        #             cm.message = \
        #                 f"{target.name}'s next roll modifier adjusted by {cm.selected_skill.roll_modifier + extra}!"
        #             cm.new_message = True
        #             cm.stage = BattleStage.WRAP_UP
        # else:
        #     self.power_int -= 1
        #     self.base_int += 1
        #     cm.message = f"{self.name} rolled too high!"
        #     cm.new_message = True
        #     cm.stage = BattleStage.WRAP_UP
        # # Reset the choice manager
        # return cm
    
    def use_item(self):
        """Use the selected item on the target(s) asynchronously."""
        for target in self.cm.selected_target:
            # Apply damage (if applicable)
            if self.cm.selected_item.damage > 0:
                target.current_health = max(0, target.current_health - self.cm.selected_item.damage)
                self.cm.message = \
                    f"{self.name} deals {self.cm.selected_item.damage} damage to {target.name}!"
                self.cm.new_message = True
                self.cm.stage = BattleStage.WRAP_UP

            # Apply healing (if applicable)
            if self.cm.selected_item.healing > 0:
                self.current_health = min(self.max_health, self.current_health + self.cm.selected_item.healing)
                self.cm.message = \
                    f"{self.name} heals for {self.cm.selected_item.healing} HP!"
                self.cm.new_message = True
                self.cm.stage = BattleStage.WRAP_UP

            # Apply slider effect (if applicable)
            if self.cm.selected_item.slider_effect != 0:
                target.roll_modifier += self.cm.selected_item.slider_effect 
                self.cm.message = \
                    f"{target.name}'s roll modifier adjusted by {self.cm.selected_item.slider_effect}!"
                self.cm.new_message = True
                self.cm.stage = BattleStage.WRAP_UP

            # Apply next roll modifier (if applicable)
            if self.cm.selected_item.roll_modifier != 0:
                target.roll_modifier += self.cm.selected_item.roll_modifier
                self.cm.message = \
                    f"{target.name}'s next roll modifier adjusted by {self.cm.selected_item.roll_modifier}!"
                self.cm.new_message = True
                self.cm.stage = BattleStage.WRAP_UP

        # Reset the choice manager
        return self.cm

class EnemyCreature(Creature):
    def select_skill_or_item(
            self, x, y, 
            width, height) -> ChoiceManager:
        '''randomly selects a skill or item'''
        if self.inventory:
            self.cm.selected_skill_or_item_choice = random.choice([Skill_Item.SKILL, Skill_Item.ITEM])
        else:
            self.cm.selected_skill_or_item_choice = Skill_Item.SKILL
        self.cm.stage = BattleStage.SELECT_SKILL_TYPE
        return self.cm

    def select_skill_type(
            self, x, y, 
            width, height) -> ChoiceManager:
        self.cm.selected_skill_type = random.choice([Base_Power.BASE, Base_Power.POWER])
        self.cm.stage = BattleStage.SELECT_SKILL
        return self.cm

    def select_skill(
        self, x: int, y: int, 
        width: int, height: int) -> ChoiceManager:

        #endregion
        skills_list = self.base_skills \
            if self.cm.selected_skill_type == Base_Power.BASE \
                else self.power_skills
        
        self.cm.selected_skill = random.choice(skills_list)
        self.cm.stage = BattleStage.SELECT_TARGET
        self.cm.message = f"{self.name} will use {self.cm.selected_skill.name}!"
        # self.cm.new_message = True
        return self.cm

    def select_target(
        self, 
        x: int,
        y: int,
        width: int,
        height: int) -> List[Creature]:
        
        #region IF ELSE STATEMENTs
        if self.cm.selected_skill:
            if self.cm.selected_skill.target == Target.SELF:
                self.cm.selected_target = [self]
                self.cm.stage = BattleStage.ROLL_DICE
                self.cm.message = f"{self.name} uses {self.cm.selected_skill.name} on themselves!"
                self.cm.new_message = True
                return self.cm

            if self.cm.selected_skill.target == Target.AOE:
                # select all possible targets
                self.cm.selected_target = self.cm.enemy_targets
                self.cm.stage = BattleStage.ROLL_DICE
                self.cm.message = f"{self.name} uses {self.cm.selected_skill.name} on all enemies!"
                self.cm.new_message = True
                return self.cm

        if self.cm.selected_item:
            if self.cm.selected_item.target == Target.SELF:
                self.cm.selected_target = [self]
                self.cm.stage = BattleStage.USE_SKILL_ITEM
                self.cm.message = f"{self.name} uses {self.cm.selected_item.name} on themselves!"
                self.cm.new_message = True
                return self.cm

            if self.cm.selected_item.target == Target.AOE:
                # select all possible targets
                self.cm.selected_target = self.cm.enemy_targets
                self.cm.stage = BattleStage.USE_SKILL_ITEM
                self.cm.message = f"{self.name} uses {self.cm.selected_item.name} on all enemies!"
                self.cm.new_message = True   
                return self.cm

        # Display the target selection box
        self.cm.selected_target = [random.choice(self.possible_targets)]
        self.cm.stage = BattleStage.ROLL_DICE
        return self.cm

    def select_item(
            self, 
            x: int, y: int, 
            width: int, height: int
        ) -> ChoiceManager:
        self.cm.selected_item = random.choice(self.inventory)
        # Decrement quantity
        self.cm.selected_item.quantity -= 1
        # Remove item if quantity is zero
        if self.cm.selected_item.quantity <= 0:
            self.inventory.remove(self.cm.selected_item)
        self.cm.stage = BattleStage.SELECT_TARGET
        self.cm.message = f"{self.name} will use {self.cm.selected_item.name}!"
        self.cm.new_message = True
        return self.cm
