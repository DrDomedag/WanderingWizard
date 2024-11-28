import random
from biomes.biome import Biome
from floors import DryGrassFloorTile
from walls import Tree
import entities.entities as entities
from util import *

class Plains(Biome):
    def __init__(self, world, biome_id):
        super().__init__(world, biome_id)
        self.name = "Plains"

    def generate_floor_tile(self, coords):
        return DryGrassFloorTile(self.world)

    def generate_wall_tile(self, coords):
        if random.random() < 0.99:
            return None
        else:
            return Tree(self.world)

    def generate_entity(self, coords):
        if random.random() < 0.98:
            return None
        else:
            enemy = entities.Goblin(self.world)
            enemy.allegiance = ALLEGIANCES.ENEMY_TEAM
            return enemy
