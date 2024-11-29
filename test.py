import raylibpy as rl
import random
import time
from typing import Union

from src.utils.buttons_etc import DiceRoller

# Include the DiceRoller class definition here

# Initialize the window
rl.init_window(800, 600, "Dice Roller Example")
rl.set_target_fps(60)

# Create the DiceRoller instance
dice_roller = DiceRoller(
    x=400, y=300, size=50, roll_duration=.5
    )

# Main game loop
while not rl.window_should_close():
    # Start dice roll on space press
    if rl.is_key_pressed(rl.KEY_SPACE):
        dice_roller.start_roll()
    
    # Begin drawing
    rl.begin_drawing()
    rl.clear_background(rl.BLACK)

    # Update and draw the dice roller
    dice_roller.update_and_draw()

    # End drawing
    rl.end_drawing()

# Close the window
rl.close_window()
