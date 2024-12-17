from enum import Enum
class Shader(Enum):
    pass
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
    USE_SKILL_ITEM = 6
    ENEMY_TURN = 7 # TODO Implement enemy turn
    ROLL_DICE = 8
    WAIT_FOR_CONTINUE = 9
    WRAP_UP = 10
class GameState(Enum):
    MAIN_MENU = 1
    OVERWORLD = 2
    BATTLE = 3
    QUIT = 4
class Turn(Enum):
    PLAYER = 1
    ENEMY = 2