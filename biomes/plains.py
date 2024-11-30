import random
from biomes.biome import Biome
from biomes.biome import PointOfInterest
from floors import *
from walls import *
import entities.entities as entities
from util import *

class Plains(Biome):
    def __init__(self, world, biome_id):
        super().__init__(world, biome_id)
        self.name = "Plains"
        self.monster_groups.append([entities.Goblin])
        self.monster_group_weights.append(3)
        self.monster_groups.append([entities.Goblin, entities.Goblin, entities.Goblin])
        self.monster_group_weights.append(1)
        self.monster_group_spawn_probability = 0.002
        self.poi_spawn_rate = 0.0
        self.fow_colour = (255, 255, 255)

    def generate_floor_tile(self, coords):
        return DryGrassFloorTile(self.world, coords)

    def generate_wall_tile(self, coords):
        if random.random() < 0.99:
            return None
        else:
            return Tree(self.world, coords)

    def generate_entity(self, coords):
        if random.random() < 0.98:
            return None
        else:
            enemy = entities.Goblin(self.world)
            enemy.allegiance = ALLEGIANCES.ENEMY_TEAM
            return enemy


class Church(PointOfInterest):
    def __init__(self, world, coordinates):
        super().__init__(world, coordinates)
        self.size = (5, 5)

    def draw(self):
        for x in range(-2, 3, 1):
            for y in range(-2, 3, 1):
                x_ = self.centre_tile[0] + x
                y_ = self.centre_tile[1] + y
                coords = (x_, y_)
                self.world.total_floor[coords] = generic_floor_tile(self.world, coords, "Wooden floor", "wood_tile")
                if chebyshev_distance(self.centre_tile, coords) == 2 and not coords[1] == self.centre_tile[1]:
                    self.world.total_walls[coords] = WoodWall(self.world, coords)
        if self.world.game.enemy_spawns_enabled:
            shaman = GoblinShaman(self.world)
            shaman.allegiance = ALLEGIANCES.ENEMY_TEAM
            shaman.position = self.centre_tile
            self.world.total_entities[self.centre_tile] = shaman