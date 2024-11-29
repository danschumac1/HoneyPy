import raylibpy as rl
import random
import time
import json
from typing import List, Tuple, Union

class DiceRoller:
    """A class to handle dice rolling animation with a spinning octagon and random numbers."""
    def __init__(self, x: int, y: int, size: int, roll_duration: int = 1):
        self.x = x
        self.y = y
        self.size = size
        self.angle = 0
        self.number = random.randint(1, 8)
        self.final_number = None
        self.roll_duration = roll_duration
        self.cycle_speed = 0.1  # Time interval for changing numbers
        self.is_rolling = False
        self.is_finished_rolling = False
        self.start_time = None

    def start_roll(self):
        """Start the dice rolling animation."""
        self.is_rolling = True
        self.is_finished_rolling = False
        self.start_time = time.time()
        self.cycle_speed = 0.1  # Reset cycle speed
        self.number = random.randint(1, 8)  # Initial random number
        self.final_number = None

    def draw_octagon(self):
        """Draw a spinning octagon centered at (x, y)."""
        num_sides = 8
        rl.draw_poly(
            rl.Vector2(self.x, self.y),
            num_sides,
            self.size,
            self.angle,
            rl.RED.fade(0.5)
        )

    def update_and_draw(self):
        """Update the dice roller state and draw the spinning octagon with numbers."""
        if self.is_rolling:
            # Rotate the octagon
            self.angle += 7.5

            # Update time
            current_time = time.time()
            elapsed_time = current_time - self.start_time

            # Randomly change the number until rolling stops
            if elapsed_time < self.roll_duration:
                if elapsed_time > self.cycle_speed:
                    self.number = random.randint(1, 8)
                    self.cycle_speed += 0.1  # Slow down gradually
            else:
                # Rolling is done, finalize the number
                self.final_number = self.number
                self.is_rolling = False
                self.is_finished_rolling = True
                print(f"Dice rolling finished. Final number: {self.final_number}")
                
        # Draw the spinning octagon
        self.draw_octagon()

        # Draw the current number in the center of the octagon
        number_text = str(self.number if self.is_rolling else self.final_number)
        text_width = rl.measure_text(number_text, 40)
        rl.draw_text(number_text, self.x - text_width // 2, self.y - 20, 40, rl.RAYWHITE)


    def reset(self):
        """Reset the dice roller state."""
        self.is_rolling = False
        self.is_finished_rolling = False
        # self.final_number = None
        # self.number = random.randint(1, 8)  # Reset to a random number


def slider(
        x: int, y: int, 
        base_name: str, power_name: str, 
        base: int, power: int, 
        width: int, height: int, 
        font_size: int = 20, 
        base_color: rl.Color = rl.LIGHTGRAY, 
        power_color: rl.Color = rl.BLUE):

    # Validate that base + power = 8
    if not (0 <= base <= 8 and 0 <= power <= 8):
        raise ValueError("Base and Power values must be between 0 and 8")
    if base + power != 8:
        raise ValueError("Base and Power values must sum to 8")
    
    # Draw outline of the slider
    rl.draw_rectangle_lines(x, y, width, height, rl.BLACK)
        
    # Calculate width of each section
    base_width = (base * width) // 8
    power_width = (power * width) // 8

    # Draw the left portion (base) of the slider
    rl.draw_rectangle(x, y, base_width, height, base_color)

    # Draw the right portion (power) of the slider
    rl.draw_rectangle(x + base_width, y, power_width, height, power_color)

    # Draw a border around the entire slider for clarity
    rl.draw_rectangle_lines(x, y, width, height, rl.BLACK)

    # Get the text width for positioning
    base_text_width = rl.measure_text(str(base), font_size)
    power_text_width = rl.measure_text(str(power), font_size)

    # Position the base value in the top-left corner of the base section
    base_text_x = x + 5  # Add some padding from the left
    base_text_y = y + 5  # Add some padding from the top
    rl.draw_text(str(base), base_text_x, base_text_y, font_size, rl.BLACK)

    # Position the power value in the bottom-right corner of the power section
    power_text_x = x + base_width + power_width - power_text_width - 5  # Align to the right with padding
    power_text_y = y + height - font_size - 5  # Align to the bottom with padding
    rl.draw_text(str(power), power_text_x, power_text_y, font_size, rl.BLACK)
    # Draw the labels for base and power
    rl.draw_text(base_name, x, y - font_size, font_size, rl.BLACK)
    rl.draw_text(power_name, x + width - rl.measure_text(power_name, font_size), y - font_size, font_size, rl.BLACK)

# Load global parameters
params = json.loads(open("./resources/global_params.json").read())
WIDTH, HEIGHT = params["WIDTH"], params["HEIGHT"]

BUTTON_WIDTH = WIDTH // 10
BUTTON_HEIGHT = HEIGHT // 20
PADDING = HEIGHT // 75

def get_button_position(index: int, base_y: int = HEIGHT // 2) -> Tuple[int, int]:
    """
    Calculate button x and y positions based on index and base_y.
    
    Parameters:
        index (int): The index of the button (0 for the first button, 1 for the second, etc.).
        base_y (int): The vertical starting position for the buttons. Defaults to middle of screen.
    
    Returns:
        Tuple[int, int]: The (x, y) coordinates of the button.
    """
    button_x = (WIDTH - BUTTON_WIDTH) // 2
    button_y = base_y + index * (BUTTON_HEIGHT + PADDING)
    return button_x, button_y

def get_text_position(
        text: str, offset_y: int = HEIGHT - HEIGHT // 2.5,
        font_size: int = 20) -> Tuple[int, int]:
    """
    Calculate the text x and y positions centered on the screen with an adjustable offset.
    
    Parameters:
        text (str): The text to measure.
        offset_y (int): The vertical offset to move the text lower on the screen.
        font_size (int): The font size for the text.
    
    Returns:
        Tuple[int, int]: The (x, y) coordinates of the text.
    """
    text_width = rl.measure_text(text, font_size)
    text_x = (WIDTH - text_width) // 2
    text_y = offset_y
    return text_x, text_y

class Button:
    def __init__(
        self, option_text: str, x: int, y: int, 
        button_choice  = None,
        width: int = BUTTON_WIDTH, height: int = BUTTON_HEIGHT, 
        button_color: rl.Color = rl.LIGHTGRAY,
        font_size: int = 20, text_color: rl.Color = rl.BLACK,
        
    ):
        self.option_text = option_text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.button_color = button_color
        self.font_size = font_size
        self.text_color = text_color
        self.button_rect = rl.Rectangle(self.x, self.y, self.width, self.height)

    def draw(self):
        """Draw the button with text."""
        # Draw the button background and border
        rl.draw_rectangle_rec(self.button_rect, self.button_color)
        rl.draw_rectangle_lines_ex(self.button_rect, 2, rl.BLACK)

        # Draw the text centered in the button
        text_width = rl.measure_text(self.option_text, self.font_size)
        text_x = self.x + (self.width - text_width) // 2
        text_y = self.y + (self.height - self.font_size) // 2
        rl.draw_text(self.option_text, text_x, text_y, self.font_size, self.text_color)

    def is_hovered(self) -> bool:
        """Check if the mouse is hovering over the button."""
        mouse_x, mouse_y = rl.get_mouse_x(), rl.get_mouse_y()
        return (
            self.button_rect.x <= mouse_x <= self.button_rect.x + self.button_rect.width and
            self.button_rect.y <= mouse_y <= self.button_rect.y + self.button_rect.height
        )
    def is_clicked(self) -> bool:
        """Check if the button is clicked."""
        return self.is_hovered() and rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON)

def statBar(
        # REQUIRED
        stat_name: str, 
        x: int, 
        y: int, 
        width:int, 
        height:int, 
        current_value: int, 
        max_value: int,  
        # OPTIONAL
        font_size=20, 
        padding=10, 
        font_color=rl.BLACK, 
        bar_color=rl.RED, 
        outline_color=rl.BLACK
        ):
    """
    Draws a stat bar with a label, filled portion based on current/max, and a value indicator.
    """
    # Ensure max is not zero to avoid division by zero
    if max_value == 0:
        max_value = 1

    # Draw the text label above the bar
    rl.draw_text(
        text=stat_name, 
        pos_x=x, 
        pos_y= y + padding,#- (font_size), 
        font_size=font_size, 
        color=font_color
        )

    # Draw the outline of the stat bar
    rl.draw_rectangle_lines_ex(
        rl.Rectangle(
            x=x, 
            y=y + padding + font_size, 
            width=width, 
            height=height), 
        line_thick=1, 
        color=outline_color
        )
    rl.draw_rectangle_lines(
        pos_x=x-1, 
        pos_y=(y + padding + font_size) - 1, 
        width=width+2, 
        height=height+2, 
        color=rl.BLACK
        )
    # # Calculate the percentage of the current value
    percentage = current_value / max_value

    # # Draw the filled portion of the bar
    rl.draw_rectangle(x, y + padding + font_size, int(width * percentage), height, bar_color)

def slider(
        # REQUIRED
        x: int, 
        y: int,
        width: int,
        height: int,
        base_int: int, 
        power_int: int, 
        # OPTIONAL
        base_color: rl.Color = rl.LIGHTGRAY, 
        power_color: rl.Color = rl.BLUE):
    # Validate that base + power = 8
    if not (0 <= base_int <= 8 and 0 <= power_int <= 8):
        raise ValueError("Base and Power values must be between 0 and 8")
    if base_int + power_int != 8:
        raise ValueError("Base and Power values must sum to 8")
    
    # Draw outline of the slider
    rl.draw_rectangle_lines(x-1, y-1, width+2, height+2, rl.BLACK)
        
    # Calculate width of each section
    base_width = (base_int * width) // 8
    power_width = (power_int * width) // 8

    # Draw the left portion (base) of the slider
    rl.draw_rectangle(x, y, base_width, height, base_color)

    # Draw the right portion (power) of the slider
    rl.draw_rectangle(x + base_width, y, power_width, height, power_color)
