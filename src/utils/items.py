from utils.enums import Base_Power, Target
from utils.dcs import Item

# Cigarette: Increases the player's base slider
Cigarette = Item(
    name="Cigarette",
    slider_effect=3,
    base_power=Base_Power.POWER,  # Moves player's slider towards base
    target=Target.SELF,
    description="+3 power"
)

# Honey: Reduces the player's base slider
Honey = Item(
    name="Honey",
    slider_effect=3,
    base_power=Base_Power.BASE,  
    target=Target.SELF,
    description="+3 base"
)

Potion = Item(
    name="Potion",
    healing=2,
    target=Target.SELF,
    description="+2 health"
)

Caltrops = Item(
    name="Caltrops",
    damage=2,
    target=Target.AOE,
    description="2 damage to all enemies"
)

FoamMiddleFinger = Item(
    name="Foam Middle Finger",
    roll_modifier=-2,
    slider_effect=-2,
    damage=1,
    base_power = Base_Power.BASE,
    target=Target.SINGLE,
    description="-2 base, -2 next roll, 1 damage"
)