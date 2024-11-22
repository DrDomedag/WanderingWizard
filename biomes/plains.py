import random
from biomes.biome import Biome
from floors import DryGrassFloorTile
from walls import Tree

class Plains(Biome):
    def __init__(self, world, biome_id):
        super().__init__(world, biome_id)
        self.name = "Plains"

    def generate_floor_tile(self, coords):
        return DryGrassFloorTile()

    def generate_wall_tile(self, coords):
        if random.random() < 0.99:
            return None
        else:
            return Tree(self.world)
