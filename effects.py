from entities.entities import *
from util import *
import math


def damage_tile(world, source, target, amount, type):
    if world.active_entities[target] is not None:
        return damage_entity(source, world.active_entities[target], amount, type)
    if world.active_walls[target] is not None:
        return damage_entity(source, world.active_walls[target], amount, type)

def damage_entity(source, target, amount, type):
    # Could make it ceil if one would like highly resisted damage to still do *something*.
    effective_damage = math.floor(amount * (100-target.resistances[type])/100)
    dealt_damage = min(effective_damage, target.hp)
    #print(f"{target.name} suffered {amount} damage of type {type}. It resisted it by {target.resistances[type]}%, and effectively took only {effective_damage} damage.  ")
    target.hp -= effective_damage
    target.on_suffer_damage(source, amount, type)
    return dealt_damage

def summon_minions(spell, entity_class, number, target, duration=0):
    summons = spell.caster.world.summon_entity(entity_class, number, target, spell.caster.allegiance)
    for summon in summons:
        summon.owner = spell.caster
        summon.max_hp = spell.minion_health
        summon.hp = summon.max_hp
        if duration > 0:
            summon.expires = True
            summon.duration = duration
        for active in summon.actives:
            if active.name == "Strike":
                active.power = spell.minion_damage

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

def push_tile(world, origin, target, distance, push_walls=False):
    # Pick affected things.
    entity = None
    wall = None
    if world.active_entities[target] is not None:
        entity = world.active_entities[target]
    if push_walls and world.active_walls[target] is not None:
        wall = world.active_walls[target]

    # Compute direction
    direction = compute_8_direction(origin, target)

    i = distance
    while i > 0:
        # Push entity
        if entity is not None:
            target_tile = (entity.position[0] + direction[0], entity.position[1] + direction[1])
            entity.world.push_entity(entity, target_tile)
        if wall is not None:
            target_tile = (wall.position[0] + direction[0], wall.position[1] + direction[1])
            wall.world.push_entity(wall, target_tile)
        i -= 1
    return i

def compute_8_direction(origin, target):
    """
    Compute the direction from origin to target on an 8-direction grid.

    :param origin: Tuple (x1, y1) of the starting coordinates.
    :param target: Tuple (x2, y2) of the target coordinates.
    :return: A string representing the direction (e.g., "N", "NE", etc.).
    """
    # Compute difference vector
    dx = target[0] - origin[0]
    dy = target[1] - origin[1]

    # Normalize the difference vector to -1, 0, 1
    nx = 0 if dx == 0 else (1 if dx > 0 else -1)
    ny = 0 if dy == 0 else (1 if dy > 0 else -1)

    # Map normalized vector to directions
    direction_map = {
        (-1, -1): "NW",
        ( 0, -1): "N",
        ( 1, -1): "NE",
        (-1,  0): "W",
        ( 0,  0): None,  # Same tile, no movement
        ( 1,  0): "E",
        (-1,  1): "SW",
        ( 0,  1): "S",
        ( 1,  1): "SE"
    }

    #return direction_map[(nx, ny)]
    push_coords = (nx, ny)
    return push_coords
