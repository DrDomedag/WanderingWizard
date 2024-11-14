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
    def __init__(self, malefactor, origin, sufferer):
        self.amount = 0
        self.type = BLUDGEONING
        self.malefactor = None
        self.origin = None

    def apply(self, target):
        target.hp -= math.floor(self.amount * (1-target.resistances[self.type]))


class HealingInstance:
    def __init__(self, origin, benefactor):
        self.amount = 0
        self.benefactor = benefactor
        self.origin = origin

    def apply(self):
        # Can rewrite this logic later to allow for overheal, healing reduction etc.
        if self.benefactor.hp == self.benefactor.max_hp:
            pass
        elif self.benefactor.hp + self.amount >= self.benefactor.max_hp:
            self.benefactor.hp = self.benefactor.max_hp
        else:
            self.benefactor.hp += self.amount

