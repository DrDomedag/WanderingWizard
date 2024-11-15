from entities.entities import *
from util import *
import math




def deal_damage(source, target, amount, type):
    effective_damage = math.floor(amount * (1-target.resistances[type]))
    dealt_damage = min(effective_damage, target.hp)
    target.hp -= effective_damage
    target.on_suffer_damage(source, amount, type)
    return dealt_damage

'''
class DamageInstance:
    def __init__(self, malefactor, sufferer):
        self.amount = 0
        self.type = DAMAGE_TYPES.BLUDGEONING
        self.malefactor = malefactor
        self.sufferer = sufferer

    def apply(self):
        self.sufferer.hp -= math.floor(self.amount * (1-self.sufferer.resistances[self.type]))
'''

def heal(source, target, amount):
    if target.hp == target.max_hp:
        pass
    elif target.hp + amount >= target.max_hp:
        target.hp = target.max_hp
    else:
        target.hp += amount

'''
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
'''
