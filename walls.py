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
        self.flyable = False
        self.swimmable = False
        self.blocks_vision = True
        self.openable = False
        self.max_hp = 50
        self.hp = self.max_hp
        self.actionsPerRound = 0
        self.stationary = True

    def on_enter_effect(self):
        pass



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

class WoodenFence(WoodWall):
    def __init__(self, world, position):
        super().__init__(world, position)
        self.name = "Wooden fence"
        self.description = "Suitable for keeping livestock in and wolves out."
        self.max_hp = 10
        self.hp = self.max_hp
        self.asset = "wood_fence"
        self.blocks_vision = False
        self.flyable = True

class Gravestone(StoneWall):
    def __init__(self, world, position):
        super().__init__(world, position)
        self.name = "Gravestone"
        self.description = "Pity the dead."
        self.max_hp = 15
        self.hp = self.max_hp
        self.asset = "gravestone"
        self.blocks_vision = False
        self.flyable = True

class Door(Wall):
    def __init__(self, world, position, is_open=False):
        super().__init__(world, position)
        self.name = "Door"
        self.description = "What lies beyond?"
        self.max_hp = 20
        self.hp = self.max_hp
        self.asset = "wooden_door_in_stone"

        self.openable = True

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

        self.is_open = is_open
        self.blocks_vision = not is_open
        self.walkable = is_open
        self.flyable = is_open
        self.swimmable = is_open

    def open(self):
        self.is_open = True
        self.blocks_vision = not self.is_open
        self.walkable = self.is_open
        self.flyable = self.is_open
        self.swimmable = self.is_open

    def close(self):
        self.is_open = False
        self.blocks_vision = not self.is_open
        self.walkable = self.is_open
        self.flyable = self.is_open
        self.swimmable = self.is_open

    def toggle_state(self):
        self.is_open = not self.is_open
        self.blocks_vision = not self.is_open
        self.walkable = self.is_open
        self.flyable = self.is_open
        self.swimmable = self.is_open

    def on_enter_effect(self):
        if self.world.active_entities[self.position] is not None:
            entity = self.world.active_entities[self.position]
            if not entity.intangible:
                self.open()

