from utils.dcs import Entity
from utils.ovw_utils import EnemyOverworldCreature, PlayerOverworldCreature
from utils.constants import PLAYER_SPEED

player_entity = Entity(35, 35, 5)
player = PlayerOverworldCreature(player_entity, speed=PLAYER_SPEED)

enemy_entity = Entity(10, 10, 2)
enemy = EnemyOverworldCreature(enemy_entity)