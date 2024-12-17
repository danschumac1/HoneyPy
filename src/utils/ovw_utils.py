import math
import raylibpy as rl
from abc import ABC, abstractmethod
from utils.dcs import Entity
from utils.constants import (
    WIDTH, HEIGHT, VISION_FOV, VISION_RANGE, SEMI_TRANSPARENT_YELLOW, SEMI_TRANSPARENT_RED)

def bind_to_screen(entity: Entity, width: int=WIDTH, height: int=HEIGHT):
    """Bind the entity to the screen by adjusting its position."""
    if entity.x < 0:
        entity.x = 0
    if entity.x + entity.size > width:
        entity.x = width - entity.size
    if entity.y < 0:
        entity.y = 0
    if entity.y + entity.size > height:
        entity.y = height - entity.size

class OverworldCreature(ABC):
    def __init__(
            self, entity: Entity, 
            speed: float = 1,
            fov: float = VISION_FOV, 
            view_range: float = VISION_RANGE, 
            rotation_angle: float = 0):
        self.entity = entity
        self.speed = speed
        self.fov = fov
        self.range = view_range
        self.rotation_angle = rotation_angle
        self.player_in_sight = False
        self.is_player = False
    def __repr__(self):
        """Detailed string representation for debugging purposes."""
        return (
            f"{self.__class__.__name__}\n"
            f"entity={self.entity},\n"
            f"speed={self.speed},\n"
            f"fov={self.fov}, \n"
            f"range={self.range},\n"
            f"rotation_angle={self.rotation_angle},\n"
            f"player_in_sight={self.player_in_sight},\n"
            f"is_player={self.is_player})"
        )

    def __str__(self):
        """User-friendly string representation."""
        return (
            f"\t{'Player' if self.is_player else 'Enemy'} at \n"
            f"\t({self.entity.x}, {self.entity.y}), \n"
            f"\tSpeed: {self.speed}, \tFOV: {self.fov}, Range: {self.range}, \n"
            f"\tRotation: {self.rotation_angle:.2f}°, \n"
            f"\tPlayer in Sight: {self.player_in_sight}"
        )

    def draw_vision_cone(self):
        """
        Draw a vision cone for the enemy using DrawCircleSector.

        The cone is drawn as a filled sector of a circle based on the creature's rotation angle.
        """
        # Calculate the center of the entity
        entity_center_x = self.entity.x + self.entity.size // 2
        entity_center_y = self.entity.y + self.entity.size // 2
        entity_center = rl.Vector2(entity_center_x, entity_center_y)

        # The color of the vision cone based on whether the player is detected
        color = SEMI_TRANSPARENT_YELLOW if not self.player_in_sight else SEMI_TRANSPARENT_RED

        # Define the start and end angles for the vision cone
        start_angle = self.rotation_angle - self.fov / 2
        end_angle = self.rotation_angle + self.fov / 2

        # Number of segments (higher values result in smoother curves)
        segments = 36

        # Draw the vision cone using DrawCircleSector
        rl.draw_circle_sector(entity_center, self.range, start_angle, end_angle, segments, color)

    def is_x_in_vision_cone(self, other: Entity):
        other_center = rl.Vector2(other.x + other.size // 2, other.y + other.size // 2)
        entity_center = rl.Vector2(self.entity.x + self.entity.size // 2, self.entity.y + self.entity.size // 2)

        to_other = rl.Vector2(other_center.x - entity_center.x, other_center.y - entity_center.y)
        distance = math.sqrt(to_other.x ** 2 + to_other.y ** 2)

        if distance > self.range:
            self.player_in_sight = False
            return False

        angle_to_player = math.degrees(math.atan2(to_other.y, to_other.x))
        angle_difference = (angle_to_player - self.rotation_angle + 180) % 360 - 180

        self.player_in_sight = abs(angle_difference) <= self.fov / 2
        return self.player_in_sight
    
    def check_collision(self, other: Entity) -> bool:
        return not (
            self.entity.x > other.x + other.size or
            self.entity.x + self.entity.size < other.x or
            self.entity.y > other.y + other.size or  # Corrected typo
            self.entity.y + self.entity.size < other.y
        )
    
    @abstractmethod
    def handle_movement(self):
        pass

class PlayerOverworldCreature(OverworldCreature):
    def __init__(self, entity: Entity, speed: float = 1):
        super().__init__(entity, speed)
        self.is_player = True

    def handle_movement(self):
        if rl.is_key_down(rl.KEY_W):  # Move up
            self.entity.y -= self.speed
        if rl.is_key_down(rl.KEY_S):  # Move down
            self.entity.y += self.speed
        if rl.is_key_down(rl.KEY_A):  # Move left
            self.entity.x -= self.speed
        if rl.is_key_down(rl.KEY_D):  # Move right
            self.entity.x += self.speed

        bind_to_screen(self.entity)

class EnemyOverworldCreature(OverworldCreature):
    def __init__(self, entity: Entity, speed: float = 1, fov: float = VISION_FOV, view_range: float = VISION_RANGE, rotation_angle: float = 0):
        super().__init__(entity, speed, fov, view_range, rotation_angle)
        self.patrol_points = [(entity.x, entity.y), (entity.x + 100, entity.y)]  # Example patrol points
        self.current_patrol_index = 0
        self.give_up_distance = self.range * 1.5  # Distance at which the enemy gives up chasing
        self.player_in_sight = False

    def patrol(self):
        """Move between predefined patrol points."""
        target_x, target_y = self.patrol_points[self.current_patrol_index]
        
        # Move towards the current patrol point
        if self.entity.x < target_x:
            self.entity.x += self.speed
        if self.entity.x > target_x:
            self.entity.x -= self.speed
        if self.entity.y < target_y:
            self.entity.y += self.speed
        if self.entity.y > target_y:
            self.entity.y -= self.speed

        # Check if the enemy has reached the patrol point
        if abs(self.entity.x - target_x) < 5 and abs(self.entity.y - target_y) < 5:
            self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)

    def chase(self, player: Entity, rotation_speed: float = 5.0):
        """
        Gradually rotate and move towards the player when they are detected.

        Args:
            player (Entity): The player entity to chase.
            rotation_speed (float): The maximum degrees to rotate per frame.
        """
        # Calculate the direction vector to the player
        dx = player.x - self.entity.x
        dy = player.y - self.entity.y

        # Calculate the target angle to face the player
        target_angle = math.degrees(math.atan2(dy, dx))

        # Calculate the shortest angular difference
        angle_diff = (target_angle - self.rotation_angle + 180) % 360 - 180

        # Gradually adjust the rotation angle towards the target angle
        if abs(angle_diff) < rotation_speed:
            self.rotation_angle = target_angle
        else:
            self.rotation_angle += rotation_speed if angle_diff > 0 else -rotation_speed

        # Normalize the direction vector for movement
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance != 0:
            dx /= distance
            dy /= distance

        # Move a maximum of 'self.speed' units per frame
        step_size = min(self.speed, distance)
        self.entity.x += dx * step_size
        self.entity.y += dy * step_size

    def give_up(self, player: Entity):
        """Return to apatrol if the player is out of range."""
        distance_to_player = math.hypot(player.x - self.entity.x, player.y - self.entity.y)
        if distance_to_player > self.give_up_distance:
            self.player_in_sight = False

    def handle_movement(self, player: Entity):
        """Handle the enemy's movement based on the player's position."""
        if self.is_x_in_vision_cone(player):
            self.chase(player)
        else:
            self.give_up(player)
            if not self.player_in_sight:
                self.patrol()