import random
import biomes.biome as biome
import floors
import walls
import entities.entities as entities
from util import *

class ChurchCatacombsInner(biome.Biome):
    def __init__(self, world, biome_id):
        super().__init__(world, biome_id)
        self.name = "Catacombs"

        self.monster_groups.append([entities.Longdead] * 4)
        self.monster_group_weights.append(1)
        self.monster_groups.append([entities.Longdead] * 9)
        self.monster_group_weights.append(7)
        self.monster_group_spawn_probability = 0.002
        #self.poi_spawn_rate = 0.0005
        self.poi_spawn_rate = 0.0
        #self.pois.append(ShamanHut)
        #self.poi_weights.append(1)
        self.fow_colour = (125, 64, 125)


    def generate_floor_tile(self, coords):
        return floors.DirtFloorTile(self.world, coords)

    def generate_wall_tile(self, coords):
        if random.random() < 0.8:
            return None
        else:
            return walls.Tree(self.world, coords)

    def generate_entity(self, coords):
        roll = random.random()
        if roll < 0.98:
            return None
        elif roll < 0.99:
            enemy = entities.Longdead(self.world)
            enemy.allegiance = ALLEGIANCES.ENEMY_TEAM
            return enemy
        else:
            enemy = entities.Longdead(self.world)
            enemy.allegiance = ALLEGIANCES.ENEMY_TEAM
            return enemy


