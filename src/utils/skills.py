from utils.dclasses2 import Skill, Target

# =============================================================================
# BEAR SKILLS
# =============================================================================
Bite = Skill(
    name="Bite",
    damage=3,
    target=Target.SINGLE,
    hover_description="Deals 3 damage to a single target"
)

# Maul = Skill(
#     name="Maul",
#     damage=7,
#     other_effect=[ce.frustration()]  # Opponent skips next turn
# )

Hybernate = Skill(
    name="Hybernate",
    slider_effect=3,
    roll_modifier=-1,  # Next roll is easier by 1
    healing=3,
    target=Target.SELF,
    hover_description="Heals 3 health and makes the next roll easier by 1"
)

bear_skills = [Bite, Hybernate] #Maul]

# =============================================================================
# CRIMINAL SKILLS
# =============================================================================
Sneak = Skill(
    name="Sneak",
    roll_modifier=-2,  # Next roll easier by 2
    target=Target.SELF,
    hover_description="Makes the next roll easier by 2"
)

Disguise = Skill(
    name="Disguise",
    roll_modifier=2, # Target's next roll harder by 1
    target=Target.AOE,
    hover_description="Makes the next roll harder by 2 for all opponents"
)

# Caltrops = Skill(
#     name="Caltrops",
#     damage=1,
#     other_effect=[ce.every_round(), ce.AOE()]  # 1 damage every round to all targets
# )

Arson = Skill(
    name="Arson",
    damage=1,
    target=Target.AOE, # Area of effect damage to all opponents
    hover_description="Deals 1 damage to all opponents"
)

criminal_skills = [Sneak, Disguise, ] #Arson, Caltrops]

# =============================================================================
# LAZY SKILLS
# =============================================================================
PretendNotToNotice = Skill(
    name="Pretend Not To Notice",
    slider_effect=1,
    target=Target.SELF,
    hover_description="Makes the next roll easier by 1"
)

TakeABreak = Skill(
    name="Take A Break",
    healing=2,
    target=Target.SELF,
    hover_description="Heals 2 health"
)

lazy_skills = [PretendNotToNotice, TakeABreak]

# =============================================================================
# OVERZEALOUS SKILLS
# =============================================================================
Overreact = Skill(
    name="Overreact",
    damage=1,
    target = Target.SINGLE,
    hover_description="Deals 1 damage to a single target"
)

Spotlight = Skill(
    name="Spotlight",
    roll_modifier=1, # Target's next roll harder by 1
    target=Target.SINGLE,
    hover_description="Makes the next roll harder by 1 for a single target"
)

overzealous_skills = [Overreact, Spotlight]