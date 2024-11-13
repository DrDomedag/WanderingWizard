from entities.entities import *
import math

# Damage types
BLUDGEONING = 0
PIERCING = 1
SLASHING = 2
FIRE = 3
COLD = 4
LIGHTNING = 5
POISON = 6
DARK = 7
LIGHT = 8
PSYCHIC = 9
MYSTIC = 10
# Acid
# Sonic/Thunder
# Abrasive
# Bleed
# Chaos


class Spell:
    def __init__(self):
        self.power = 0
        self.range = 0
        self.area = 0
        self.duration = 0
        self.owner = None


class DamageInstance:
    def __init__(self):
        self.amount = 0
        self.type = BLUDGEONING
        self.malefactor = None
        self.origin = None

    def apply(self, target):
        target.hp -= math.floor(self.amount * (1-target.resistances[self.type]))


class HealingInstance:
    def __init__(self):
        self.amount = 0
        self.benefactor = None
        self.origin = None

    def apply(self, target):
        # Can rewrite this logic later to allow for overheal, healing reduction etc.
        if target.hp == target.max_hp:
            pass
        elif target.hp + self.amount >= target.max_hp:
            target.hp = target.max_hp
        else:
            target.hp += self.amount

