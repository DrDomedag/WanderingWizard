from util import *
from entities.entities import Entity

class Wall(Entity):
    def __init__(self, world, position):
        super().__init__(world)
        self.position = position
        self.layer = "wall"
        self.name = "Wall"
        self.description = "A wall."
        self.walkable = False
        self.max_hp = 50
        self.hp = self.max_hp
        self.actionsPerRound = 0
        self.stationary = True



class StoneWall(Wall):
    def __init__(self, world, position):
        super().__init__(world, position)
        self.name = "Stone Wall"
        self.description = "A solid stone wall."
        self.max_hp = 100
        self.hp = self.max_hp
        self.asset = "stone_wall"
        self.flammable = False
        self.resistances[DAMAGE_TYPES.BLUDGEONING] = 75
        self.resistances[DAMAGE_TYPES.PIERCING] = 90
        self.resistances[DAMAGE_TYPES.SLASHING] = 90
        self.resistances[DAMAGE_TYPES.FIRE] = 100
        self.resistances[DAMAGE_TYPES.COLD] = 100
        self.resistances[DAMAGE_TYPES.LIGHTNING] = 80
        self.resistances[DAMAGE_TYPES.POISON] = 100
        self.resistances[DAMAGE_TYPES.DARK] = 80
        self.resistances[DAMAGE_TYPES.LIGHT] = 80
        self.resistances[DAMAGE_TYPES.PSYCHIC] = 100
        self.resistances[DAMAGE_TYPES.ARCANE] = 50


class WoodWall(Wall):
    def __init__(self, world, position):
        super().__init__(world, position)
        self.name = "Wooden Wall"
        self.description = "A wall of sturdy wood."
        self.max_hp = 50
        self.hp = self.max_hp
        self.asset = "wood_wall"
        self.resistances[DAMAGE_TYPES.BLUDGEONING] = 75
        self.resistances[DAMAGE_TYPES.PIERCING] = 90
        self.resistances[DAMAGE_TYPES.SLASHING] = 50
        self.resistances[DAMAGE_TYPES.FIRE] = 0
        self.resistances[DAMAGE_TYPES.COLD] = 100
        self.resistances[DAMAGE_TYPES.LIGHTNING] = 50
        self.resistances[DAMAGE_TYPES.POISON] = 100
        self.resistances[DAMAGE_TYPES.DARK] = 50
        self.resistances[DAMAGE_TYPES.LIGHT] = 80
        self.resistances[DAMAGE_TYPES.PSYCHIC] = 100
        self.resistances[DAMAGE_TYPES.ARCANE] = 50

class Tree(WoodWall):
    def __init__(self, world, position):
        super().__init__(world, position)
        self.name = "Tree"
        self.description = "A tree of a type common in the area."
        self.max_hp = 25
        self.hp = self.max_hp
        self.asset = "tree"
