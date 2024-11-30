import effects
from util import *


class FloorTile:
    def __init__(self, world, position):
        self.world = world
        self.position = position
        self.description = ""
        self.layer = "floor"
        self.name = "Floor"
        self.type = "solid"
        self.walkable = True
        self.flyable = True
        self.swimmable = False
        self.flammable = False
        self.asset = "unknown"

    def on_start_of_turn_effect(self):
        pass

    def on_enter_effect(self, entity):
        pass


class BurningGround(FloorTile):
    def __init__(self, world, position):
        super().__init__(world, position)
        self.name = "Burning Ground"
        self.asset = "burning_ground"
        self.description = "This tile deals 1 damage to any non-flying that enters it, and 1 at the start of each turn."

    def on_start_of_turn_effect(self):
        if self.world.total_entities[self.position] is not None:
            entity = self.world.total_entities[self.position]
            if not entity.flying:
                effects.damage_entity(self, entity, 1, DAMAGE_TYPES.FIRE)
                self.world.show_effect(entity.position, "fire_explosion")

    def on_enter_effect(self, entity):
        if self.world.total_entities[self.position] is not None:
            entity = self.world.total_entities[self.position]
            if not entity.flying:
                effects.damage_entity(self, entity, 1, DAMAGE_TYPES.FIRE)
                self.world.show_effect(entity.position, "fire_explosion")

class Portal(FloorTile):
    def __init__(self, home_world, away_world, home_world_coordinates, away_world_coordinates=(0, 0), paired_portal=None):
        super().__init__(home_world, home_world_coordinates)
        self.layer = "floor"
        self.name = "Portal"
        self.asset = "portal_tile"

        self.home_world = home_world

        if paired_portal is None:
            self.home_world_coordinates = home_world_coordinates
            self.away_world_coordinates = away_world_coordinates
            self.away_world = away_world
            self.away_world.total_floor[self.away_world_coordinates] = Portal(self.away_world, self.home_world, self.away_world_coordinates, away_world_coordinates=self.home_world_coordinates, paired_portal=self)
            #print(f"Created unpaired portal. Home/Away world coordinates: {self.home_world_coordinates} / {self.away_world_coordinates}")
        else:

            self.home_world_coordinates = paired_portal.away_world_coordinates
            self.away_world_coordinates = paired_portal.home_world_coordinates
            self.away_world = paired_portal.home_world
            #print(f"Created paired portal. Home/Away world coordinates: {self.home_world_coordinates} / {self.away_world_coordinates}")


    def on_enter_effect(self, entity):
        if entity == self.world.game.pc:
            self.away_world.game.pc.position = self.away_world_coordinates
            self.away_world.total_entities[self.away_world.game.pc.position] = self.home_world.game.pc
            self.away_world.set_current_active_tiles()
            entity.world = self.away_world
            self.home_world.game.ui.world = self.away_world
            self.home_world.game.world = self.away_world


class DirtFloorTile(FloorTile):
    def __init__(self, world, position):
        super().__init__(world, position)
        self.name = "Floor"
        self.asset = "dirt_tile"

class DryGrassFloorTile(FloorTile):
    def __init__(self, world, position):
        super().__init__(world, position)
        self.name = "Floor"
        self.asset = "dry_grass_tile"

class PortalStoneFloorTile(FloorTile):
    def __init__(self, world, position):
        super().__init__(world, position)
        self.name = "Floor"
        self.asset = "portal_stone_tile"

class LavaFloorTile(FloorTile):
    def __init__(self, world, position):
        super().__init__(world, position)
        self.name = "Lava"
        self.type = "liquid"
        self.walkable = False
        self.swimmable = True
        #self.onEnterEffects.append() Deal fire damage

    def on_start_of_turn_effect(self):
        effects.damage_tile(self.world, self, self.position, 5, DAMAGE_TYPES.FIRE)

    def on_enter_effect(self, entity):
        effects.damage_entity(self, entity, 5, DAMAGE_TYPES.FIRE)
        self.world.show_effect(entity.position, "fire_explosion")


class WaterFloorTile(FloorTile):
    def __init__(self, world, position):
        super().__init__(world, position)
        self.name = "Water"
        self.type = "liquid"
        self.asset = "water_tile"
        self.walkable = False
        self.swimmable = True
        # Make this turn into ice when hit by cold damage, which thaws when hit by fire damage

class ChasmFloorTile(FloorTile):
    def __init__(self,world, position):
        super().__init__(world, position)
        self.name = "Chasm"
        self.type = "void"
        self.asset = "chasm_tile"
        self.walkable = False
        self.swimmable = False

class WoodenFloorTile(FloorTile):
    def __init__(self, world, position):
        super().__init__(world, position)
        self.name = "Wooden floor"
        self.type = "solid"
        self.asset = "wood_tile"

def generic_floor_tile(world, position, name, asset_name):
    tile = FloorTile(world, position)
    tile.name = name
    tile.asset = asset_name
    return tile