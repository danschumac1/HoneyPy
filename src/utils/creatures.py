from utils.dclasses2 import EnemyCreature, PlayerCreature
from utils.items import Cigarette, Honey, Potion, Caltrops, FoamMiddleFinger
from utils.skills import (
    bear_skills, criminal_skills, lazy_skills, overzealous_skills
)

# Grizzle: Bear vs. Criminal
def create_bear_criminal():
    return PlayerCreature(
        name="Grizzle",
        creature_type="bear",
        current_health=20, # XXX Should be 20
        max_health=20,
        base_slider_name="Bear",
        power_slider_name="Criminal",
        base_skills=bear_skills,
        power_skills=criminal_skills,
        inventory=[Cigarette*6, Honey, Potion, Caltrops, FoamMiddleFinger]
    )

# Mall Cop: Lazy vs. Overzealous
def create_mall_cop():
    return EnemyCreature(
        name="Baul Plart",
        creature_type="mall_cop",
        current_health=10, # XXX Should be 10
        max_health=10,
        base_slider_name="Lazy",
        power_slider_name="Overzealous",
        base_skills=lazy_skills,
        power_skills=overzealous_skills
    )