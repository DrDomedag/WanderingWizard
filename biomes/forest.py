import random
from biomes.biome import Biome
from floors import DirtFloorTile
from walls import Tree


class Forest(Biome):
    def __init__(self, world, biome_id):
        super().__init__(world, biome_id)
        self.name = "Forest"


    def generate_floor_tile(self, coords):
        return DirtFloorTile()

    def generate_wall_tile(self, coords):
        if random.random() < 0.8:
            return None
        else:
            return Tree(self.world)
