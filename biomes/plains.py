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
        self.pois.append(Church)
        self.poi_weights.append(1)
        self.poi_spawn_rate = 0.005
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
    def on_init(self):
        self.size = (33, 27)

    def draw(self):

        corner_tiles = [(0, 0), (0, 32), (32, 26), (32, 0)]
        corner_tiles = self.translate_poi_coordinates_to_world(corner_tiles)
        for tile in rasterize_polygon(corner_tiles, wrap=False, fill=True):
            self.world.total_floor[tile] = DryGrassFloorTile(self.world, tile)

        fence_points = [(9, 25), (1, 25), (1, 1), (31, 1), (31, 25), (13, 25)]
        fence_points = self.translate_poi_coordinates_to_world(fence_points)
        for tile in rasterize_polygon(fence_points, wrap=False, fill=False):
            self.world.total_walls[tile] = WoodenFence(self.world, tile)

        church_wall_points = [(10, 21), (8, 21), (8, 12), (4, 12), (4, 7), (8, 7), (8, 3), (14, 3), (14, 7), (18, 7), (18, 12), (14, 12), (14, 21), (12, 21)]
        church_wall_points = self.translate_poi_coordinates_to_world(church_wall_points)
        for tile in rasterize_polygon(church_wall_points, wrap=False, fill=False):
            self.world.total_walls[tile] = StoneWall(self.world, tile)

        shed_wall_points = [(23, 18), (23, 17), (27, 17), (27, 21), (23, 21), (23, 20)]
        shed_wall_points = self.translate_poi_coordinates_to_world(shed_wall_points)
        for tile in rasterize_polygon(shed_wall_points, wrap=False, fill=False):
            self.world.total_walls[tile] = StoneWall(self.world, tile)


        '''
        if self.world.game.enemy_spawns_enabled:
            shaman = GoblinShaman(self.world)
            shaman.allegiance = ALLEGIANCES.ENEMY_TEAM
            shaman.position = self.centre_tile
            self.world.total_entities[self.centre_tile] = shaman
        '''