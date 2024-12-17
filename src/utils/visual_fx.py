from enum import Enum
import random
import numpy as np
import raylibpy as rl
from typing import Any, List
from utils.constants import WIDTH, HEIGHT

# Color palettes
FALL_COLORS = [
    rl.Color(255, 223, 0, 255),   # Yellow
    rl.Color(255, 165, 0, 255),   # Orange
    rl.Color(255, 87, 34, 255),   # Deep Orange
    rl.Color(255, 193, 7, 255),   # Amber
]

FOREST_COLORS = [
    rl.Color(0, 128, 0, 255),      # Dark Green
    rl.Color(34, 139, 34, 255),    # Forest Green
    rl.Color(107, 142, 35, 255),   # Olive Drab
    rl.Color(85, 107, 47, 255),    # Dark Olive Green
    rl.Color(144, 238, 144, 255),  # Light Green
]

class VisualEffect(Enum):
    """Enumeration of visual effects to display during the game."""
    RAIN = "rain"
    FIREFLIES = "fireflies"
    LEAVES = "leaves"

    def create_effect(self, width: int, height: int) -> Any:
        """Factory method to create instances of visual effects."""
        if self == VisualEffect.RAIN:
            return Droplet.spawn(width, height)
        elif self == VisualEffect.FIREFLIES:
            return Firefly.spawn(10, width, height)  # Spawn 10 fireflies
        elif self == VisualEffect.LEAVES:
            return Leaf.spawn(10, width, height)     # Spawn 10 leaves
        else:
            raise ValueError(f"Unknown visual effect: {self}")

class VisualEffect(Enum):
    """Enumeration of visual effects to display during the game."""
    RAIN = "rain"
    FIREFLIES = "fireflies"
    LEAVES = "leaves"

    def create_effect(self, width: int, height: int) -> Any:
        """Factory method to create instances of visual effects."""
        if self == VisualEffect.RAIN:
            return Rain(width, height)
        elif self == VisualEffect.FIREFLIES:
            return Firefly.spawn(10, width, height)  # Spawn 10 fireflies
        elif self == VisualEffect.LEAVES:
            return Leaf.spawn(10, width, height)     # Spawn 10 leaves
        else:
            raise ValueError(f"Unknown visual effect: {self}")

class VisualEffectsManager:
    """Manages the lifecycle of visual effects in the game."""

    def __init__(self):
        self.effects: List[Any] = []

    def add_effect(self, visual_effect: VisualEffect, width: int = WIDTH, height: int = HEIGHT):
        """Add a new visual effect to the manager."""
        effect_instance = visual_effect.create_effect(width, height)
        if isinstance(effect_instance, list):
            self.effects.extend(effect_instance)
        else:
            self.effects.append(effect_instance)

    def update_and_draw(self):
        """Update and draw all active visual effects."""
        for effect in self.effects:
            effect.update_and_draw()
        self.effects = [e for e in self.effects if not e.finished]

class Rain:
    """Class to represent a rainfall effect with multiple droplets."""

    def __init__(self, width, height, num_droplets=20, radius_range=(50, 150), growth_range=(0.5, 2)):
        self.droplets = [self._create_droplet(width, height, radius_range, growth_range) for _ in range(num_droplets)]
        self.width = width
        self.height = height
        self.radius_range = radius_range
        self.growth_range = growth_range
        self.finished = False

    def _create_droplet(self, width, height, radius_range, growth_range):
        """Create a single droplet with random properties."""
        x = random.randint(0, width)
        y = random.randint(0, height)
        initial_radius = 0
        radius_limit = random.uniform(*radius_range)
        growth_rate = random.uniform(*growth_range)
        alpha = 255
        start_color = self._random_blue_color()
        end_color = self._random_blue_color()
        return Droplet(x, y, initial_radius, growth_rate, radius_limit, start_color, end_color, alpha)

    def update_and_draw(self):
        """Update and draw all droplets in the rain effect."""
        for droplet in self.droplets:
            droplet.update_and_draw()
        self.droplets = [d for d in self.droplets if not d.finished]

        # Respawn finished droplets to maintain continuous rain
        while len(self.droplets) < 20:
            self.droplets.append(self._create_droplet(self.width, self.height, self.radius_range, self.growth_range))

    @staticmethod
    def _random_blue_color():
        """Generate a random shade of blue."""
        return rl.Color(random.randint(0, 50), random.randint(0, 50), random.randint(150, 255), 255)

class Droplet:
    """A class to represent an expanding droplet with synchronized fading and growth."""

    def __init__(self, x, y, initial_radius, growth_rate, radius_limit, start_color, end_color, alpha=255):
        self.x = x
        self.y = y
        self.radius = initial_radius
        self.growth_rate = growth_rate
        self.radius_limit = radius_limit
        self.alpha = alpha
        self.start_color = start_color
        self.end_color = end_color
        self.finished = False
        self.fade_rate = self.alpha / (self.radius_limit / self.growth_rate)

    def interpolate_color(self):
        """Interpolate between the start and end color based on the current radius."""
        t = self.radius / self.radius_limit
        red = int((1 - t) * self.start_color.r + t * self.end_color.r)
        green = int((1 - t) * self.start_color.g + t * self.end_color.g)
        blue = int((1 - t) * self.start_color.b + t * self.end_color.b)
        return rl.Color(red, green, blue, int(self.alpha))

    def update_and_draw(self):
        """Update the droplet's radius and alpha, and draw it."""
        if not self.finished:
            self.radius += self.growth_rate
            self.alpha -= self.fade_rate
            self.alpha = max(0, self.alpha)

            color = self.interpolate_color()
            rl.draw_circle(self.x, self.y, self.radius, color)

            if self.radius >= self.radius_limit or self.alpha <= 0:
                self.finished = True


class Firefly:
    """Represents a flickering, drifting firefly with a glowing effect."""

    def __init__(self, x, y, size, speed, glow_speed):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.alpha = random.randint(50, 255)
        self.glow_speed = glow_speed
        self.alpha_direction = 1
        self.drift_angle = random.uniform(0, 2 * np.pi)
        self.base_color = random.choice(FALL_COLORS)
        self.finished = False

    def update_and_draw(self):
        """Update and draw the firefly."""
        self.alpha += self.glow_speed * self.alpha_direction
        if self.alpha >= 255:
            self.alpha = 255
            self.alpha_direction = -1
        elif self.alpha <= 50:
            self.alpha = 50
            self.alpha_direction = 1

        self.x += self.speed * np.cos(self.drift_angle)
        self.y += self.speed * np.sin(self.drift_angle)

        if self.x < 0: self.x = WIDTH
        if self.x > WIDTH: self.x = 0
        if self.y < 0: self.y = HEIGHT
        if self.y > HEIGHT: self.y = 0

        rl.draw_circle(self.x, self.y, self.size, rl.Color(self.base_color.r, self.base_color.g, self.base_color.b, self.alpha))

    @classmethod
    def spawn(cls, num_fireflies, width, height):
        """Spawn fireflies with random properties."""
        return [cls(random.randint(0, width), random.randint(0, height), random.uniform(2, 5), random.uniform(0.1, 0.5), random.uniform(1, 3)) for _ in range(num_fireflies)]

class Leaf:
    """Represents a falling leaf with rotation, drifting effect, and leaf shape."""

    def __init__(self, x, y, size, fall_speed, sway_speed, rotation_speed, color):
        self.x = x
        self.y = y
        self.size = size
        self.fall_speed = fall_speed
        self.sway_speed = sway_speed
        self.rotation_speed = rotation_speed
        self.angle = random.uniform(0, 360)
        self.color = color
        self.finished = False

    def update_and_draw(self):
        """Update and draw the leaf."""
        self.y += self.fall_speed
        self.x += self.sway_speed * np.sin(self.y / 50.0)
        self.angle += self.rotation_speed

        if self.y > HEIGHT:
            self.y = -self.size
            self.x = random.randint(0, WIDTH)

        rl.draw_rectangle_pro(
            rl.Rectangle(self.x, self.y, self.size, self.size),
            rl.Vector2(self.size / 2, self.size / 2),
            self.angle,
            self.color
        )

    @classmethod
    def spawn(cls, num_leaves, width, height):
        """Spawn leaves with random properties."""
        return [cls(random.randint(0, width), random.randint(-height, 0), random.uniform(10, 20), random.uniform(1, 3), random.uniform(0.5, 1.5), random.uniform(-2, 2), random.choice(FOREST_COLORS)) for _ in range(num_leaves)]

# The main function to test the visual effects
def main():
    rl.init_window(WIDTH, HEIGHT, "Visual Effects Manager")
    manager = VisualEffectsManager()
    manager.add_effect(VisualEffect.RAIN)
    manager.add_effect(VisualEffect.FIREFLIES)
    manager.add_effect(VisualEffect.LEAVES)

    while not rl.window_should_close():
        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)
        manager.update_and_draw()
        rl.end_drawing()

    rl.close_window()

if __name__ == "__main__":
    main()
