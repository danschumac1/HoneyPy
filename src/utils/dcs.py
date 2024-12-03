from dataclasses import dataclass

from utils.enums import Target, Base_Power

@dataclass
class Entity:
    x: int
    y: int
    size: int

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
            description=self.description
        )

    def __repr__(self):
        """String representation for debugging."""
        return f"Item(name={self.name}, quantity={self.quantity})"