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
        self.poi_spawn_rate = 0.0005
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
        self.name = "Church"

    def draw(self):

        corner_tiles = [(0, 0), (32, 0), (32, 26), (0, 26)]
        corner_tiles = self.translate_poi_coordinates_to_world(corner_tiles)
        for tile in rasterize_polygon(corner_tiles, wrap=True, fill=True):
            #self.world.total_floor[tile] = WoodenFloorTile(self.world, tile) # This is what I'd want to do, but apparently not setting the active floor comes with big, scary side effects for some reason probably related to monster spawns.
            floor = DryGrassFloorTile(self.world, tile)
            self.world.total_floor[tile] = floor
            self.world.active_floor[tile] = floor

        fence_points = [(9, 25), (1, 25), (1, 1), (31, 1), (31, 25), (13, 25)]
        fence_points = self.translate_poi_coordinates_to_world(fence_points)
        for tile in rasterize_polygon(fence_points, wrap=False, fill=False):
            if random.random() < 0.99:
                self.world.total_walls[tile] = WoodenFence(self.world, tile)

        church_wall_points = [(10, 21), (8, 21), (8, 12), (4, 12), (4, 7), (8, 7), (8, 3), (14, 3), (14, 7), (18, 7), (18, 12), (14, 12), (14, 21), (12, 21)]
        church_wall_points = self.translate_poi_coordinates_to_world(church_wall_points)
        for tile in rasterize_polygon(church_wall_points, wrap=False, fill=False):
            self.world.total_walls[tile] = StoneWall(self.world, tile)
        for tile in rasterize_polygon(church_wall_points, wrap=True, fill=True):
            floor = StoneFloorTile(self.world, tile)
            self.world.total_floor[tile] = floor
            self.world.active_floor[tile] = floor

        pillar_points = [(10, 13), (10, 15), (10, 17), (10, 19), (12, 13), (12, 15), (12, 17), (12, 19)]
        pillar_points = self.translate_poi_coordinates_to_world(pillar_points)
        for tile in pillar_points:
            if random.random() < 0.95:
                self.world.total_walls[tile] = StoneWall(self.world, tile)

        shed_wall_points = [(23, 18), (23, 17), (27, 17), (27, 21), (23, 21), (23, 20)]
        shed_wall_points = self.translate_poi_coordinates_to_world(shed_wall_points)
        for tile in rasterize_polygon(shed_wall_points, wrap=False, fill=False):
            self.world.total_walls[tile] = StoneWall(self.world, tile)
        for tile in rasterize_polygon(shed_wall_points, wrap=True, fill=True):
            floor = DirtFloorTile(self.world, tile)
            self.world.total_floor[tile] = floor
            self.world.active_floor[tile] = floor

        carpet_points = [(11, 6), (11, 21)]
        carpet_points = self.translate_poi_coordinates_to_world(carpet_points)
        for tile in bresenham(carpet_points[0], carpet_points[1]):
            floor = RedCarpetTile(self.world, tile)
            self.world.total_floor[tile] = floor
            self.world.active_floor[tile] = floor

        grave_tiles = []
        for x in range(22, 30, 2):
            for y in range(7, 15, 2):
                if random.random() < 0.5:
                    grave_tiles.append((x, y))

        grave_tiles = self.translate_poi_coordinates_to_world(grave_tiles)
        for tile in grave_tiles:
            self.world.total_walls[tile] = Gravestone(self.world, tile)

        door_pos = self.translate_poi_coordinates_to_world((11, 21))

        self.world.total_walls[door_pos] = Door(self.world, door_pos, False)

        # Spawn enemies. Use monstergroup for everything but the priest, since we eventually want monstergroup
        # to scale with a difficulty/monster frequency slider.

        '''
        if self.world.game.enemy_spawns_enabled:
            shaman = GoblinShaman(self.world)
            shaman.allegiance = ALLEGIANCES.ENEMY_TEAM
            shaman.position = self.centre_tile
            self.world.total_entities[self.centre_tile] = shaman
        '''