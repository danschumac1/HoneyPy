import raylibpy as rl

from utils.dcs import Entity

def handle_player_movement(player: Entity, speed: int):
    if rl.is_key_down(rl.KEY_W):  # Move up
        player.y -= speed
    if rl.is_key_down(rl.KEY_S):  # Move down
        player.y += speed
    if rl.is_key_down(rl.KEY_A):  # Move left
        player.x -= speed
    if rl.is_key_down(rl.KEY_D):  # Move right
        player.x += speed

def check_collision(entity1: Entity, entity2: Entity) -> bool:
    return (
        entity1.x < entity2.x + entity2.size and
        entity1.x + entity1.size > entity2.x and
        entity1.y < entity2.y + entity2.size and
        entity1.y + entity1.size > entity2.y
    )