import random
import biomes.biome as biome
import floors
from entities.entities import GoblinShaman
from floors import DirtFloorTile
from walls import Tree, WoodWall
import entities.entities as entities
from util import *

class Forest(biome.Biome):
    def __init__(self, world, biome_id):
        super().__init__(world, biome_id)
        self.name = "Forest"

        self.monster_groups.append([entities.Troll, entities.Goblin, entities.Goblin, entities.Goblin])
        self.monster_group_weights.append(1)
        self.monster_groups.append([entities.Goblin] * 9)
        self.monster_group_weights.append(7)
        self.monster_group_spawn_probability = 0.002
        self.poi_spawn_rate = 0.0005
        self.pois.append(ShamanHut)
        self.poi_weights.append(1)
        self.fow_colour = (255, 255, 255)


    def generate_floor_tile(self, coords):
        return DirtFloorTile(self.world, coords)

    def generate_wall_tile(self, coords):
        if random.random() < 0.8:
            return None
        else:
            return Tree(self.world, coords)

    def generate_entity(self, coords):
        roll = random.random()
        if roll < 0.98:
            return None
        elif roll < 0.99:
            enemy = entities.Goblin(self.world)
            enemy.allegiance = ALLEGIANCES.ENEMY_TEAM
            return enemy
        else:
            enemy = entities.Troll(self.world)
            enemy.allegiance = ALLEGIANCES.ENEMY_TEAM
            return enemy



class ShamanHut(biome.PointOfInterest):
    def on_init(self):
        self.size = (6, 6)

    def draw(self):
        for x in range(-2, 3, 1):
            for y in range(-2, 3, 1):
                x_ = self.centre_tile[0] + x
                y_ = self.centre_tile[1] + y
                coords = (x_, y_)
                self.world.total_floor[coords] = floors.generic_floor_tile(self.world, coords, "Wooden floor", "wood_tile")
                if chebyshev_distance(self.centre_tile, coords) == 2 and not coords[1] == self.centre_tile[1]:
                    self.world.total_walls[coords] = WoodWall(self.world, coords)
        if self.world.game.enemy_spawns_enabled:
            shaman = GoblinShaman(self.world)
            shaman.allegiance = ALLEGIANCES.ENEMY_TEAM
            shaman.position = self.centre_tile
            self.world.total_entities[self.centre_tile] = shaman
