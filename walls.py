from util import *
from entities.entities import Entity


class Wall(Entity):
    def __init__(self, world, position):
        self.blocks_vision = True
        self.walkable = False
        self.flyable = False
        self.swimmable = False
        self.openable = False
        self.is_open = False
        self.blocks_line_of_effect = True

        super().__init__(world)
        self.position = position
        self.layer = "wall"
        self.actionsPerRound = 0

    def on_init(self):
        self.name = "Wall"
        self.description = "A wall."
        self.max_hp = 50
        self.hp = self.max_hp
        self.stationary = True

    def on_enter_effect(self):
        pass

    def die(self):
        self.world.total_walls[self.position] = None
        self.world.active_walls[self.position] = None
        self.on_death()

    def expire(self):
        self.world.total_walls[self.position] = None
        self.world.active_walls[self.position] = None
        self.on_expire()


class StoneWall(Wall):
    def on_init(self):
        self.name = "Stone Wall"
        self.description = "A solid stone wall."
        self.max_hp = 100
        self.hp = self.max_hp
        self.asset_name = "stone_wall"
        self.flammable = False
        self.resistances = RESISTANCE_SETS.STONE


class WoodWall(Wall):
    def on_init(self):
        self.name = "Wooden Wall"
        self.description = "A wall of sturdy wood."
        self.max_hp = 50
        self.hp = self.max_hp
        self.asset_name = "wood_wall"
        self.resistances = RESISTANCE_SETS.DEAD_WOOD

class Tree(WoodWall):
    def on_init(self):
        self.name = "Tree"
        self.description = "A tree of a type common in the area."
        self.max_hp = 25
        self.hp = self.max_hp
        self.asset_name = "tree"
        self.resistances = RESISTANCE_SETS.LIVING_WOOD

class WoodenFence(WoodWall):
    def on_init(self):
        self.name = "Wooden fence"
        self.description = "Suitable for keeping livestock in and wolves out."
        self.max_hp = 10
        self.hp = self.max_hp
        self.asset_name = "wood_fence"
        self.blocks_vision = False
        self.blocks_line_of_effect = False
        self.flyable = True
        self.resistances = RESISTANCE_SETS.DEAD_WOOD

class Gravestone(StoneWall):
    def on_init(self):
        self.name = "Gravestone"
        self.description = "Pity the dead."
        self.max_hp = 15
        self.hp = self.max_hp
        self.asset_name = "gravestone"
        self.blocks_vision = False
        self.blocks_line_of_effect = False
        self.flyable = True
        self.resistances = RESISTANCE_SETS.STONE

class ChurchAltar(StoneWall):
    def on_init(self):
        self.name = "Altar"
        self.description = "A place for prayer, sermons and sacrifice."
        self.max_hp = 20
        self.hp = self.max_hp
        self.asset_name = "church_altar"
        self.blocks_vision = False
        self.blocks_line_of_effect = False
        self.flyable = True
        self.resistances = RESISTANCE_SETS.STONE

class Door(Wall):
    def __init__(self, world, position, is_open=False):
        self.is_open = is_open
        super().__init__(world, position)
        self.set_asset()

    def on_init(self):
        self.name = "Door"
        self.description = "What lies beyond?"
        self.max_hp = 20
        self.hp = self.max_hp
        self.asset_name = "wooden_door_in_stone"

        self.openable = True

        self.resistances = RESISTANCE_SETS.DEAD_WOOD


        self.blocks_vision = not self.is_open
        self.blocks_line_of_effect = not self.is_open
        self.walkable = self.is_open
        self.flyable = self.is_open
        self.swimmable = self.is_open

    def open(self):
        self.is_open = True
        self.blocks_vision = not self.is_open
        self.blocks_line_of_effect = not self.is_open
        self.walkable = self.is_open
        self.flyable = self.is_open
        self.swimmable = self.is_open

        self.set_asset()

    def close(self):
        self.is_open = False
        self.blocks_vision = not self.is_open
        self.blocks_line_of_effect = not self.is_open
        self.walkable = self.is_open
        self.flyable = self.is_open
        self.swimmable = self.is_open

        self.set_asset()

    def toggle_state(self):
        self.is_open = not self.is_open
        self.blocks_vision = not self.is_open
        self.blocks_line_of_effect = not self.is_open
        self.walkable = self.is_open
        self.flyable = self.is_open
        self.swimmable = self.is_open

        self.set_asset()

    def set_asset(self):
        if self.is_open:
            self.asset = self.world.game.assets[self.asset_name + "_open"]
        else:
            self.asset = self.world.game.assets[self.asset_name + "_closed"]


    def on_enter_effect(self):
        if self.world.active_entities[self.position] is not None:
            entity = self.world.active_entities[self.position]
            if not entity.intangible:
                self.open()

