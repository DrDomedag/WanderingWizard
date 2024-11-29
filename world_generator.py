from noise import snoise2
import matplotlib.pyplot as plt
import numpy as np
import random
from util import Tags
from walls import *
from floors import *
import entities.entities as entities
from biomes.biome import *
from biomes.plains import Plains
from biomes.forest import Forest


# Current idea:
# Define a few biomes
# For each, create a noise map measuring how intensely that biome exists in that area
# For each tile, it is considered to be of the biome where whose intensity is highest
# This allows for adding biomes later
# Decrease intensity of difficult/high level biomes for tiles close to start
# Something like 1/0.0001x depending on whatever the intensities actually are


# ooh, do a *weird* biome that uses e.g. sine waves for ground generation so that it follows strict (but weird) geometric patterns
# Can do something like that for desert dunes? Probably not easy.

# Dimension ideas:
'''
The Abyss
Heaven
Elemental Plane of X
Future world, electric and metal
Void
Fae lands
Realm of Shadow
Origin Realm (where dragons live)
'''

# Biome ideas:
'''

Ice caverns (closed and cold)
Volcanic caverns (hot and closed)
Mushroom caverns
Crystal caverns
Catacombs

Ruined city

Jungle (dense trees)
Swamp (difficult to traverse, lots of water tiles)
Riverland (long streaks of water)
Ocean/beach (definitely requires swimming/flying ability)
Canyon (winding paths)
Plains (very open)
Tundra (open and cold)
Burnt forest

Fairy forest
Lost lands (lots of chasms, remnants of houses, extraplanar entities)
Graveyard
Wasteland (red sand, demons)
Installation (like sc1 map editor - metal interior, sf)
Sacred land (angels and churches and stuff)
Flesh forest


Probably skip height, so no:
Volcanic peaks (calderas of lava, chasms)
Mountaintops (lots of chasms, air theme)

Could alternatively do something like
temperature x humidity x magic

'''


BIOME_IDS = Tags(
    STARTER_BIOME=0,
    PLAINS=1,
    FOREST=2,
    #VOLCANO_CAVERNS=3,
    #CANYON=4
)

# This has to be kept in the right order, which sucks, but who ever said good programming practices were a thing?
BIOMES = [
    StarterBiome,
    Plains,
    Forest
]

class WorldGenerator():
    def __init__(self, world):
        self.world = world
        self.biomes = {}
        for biome_name, biome_id in BIOME_IDS.__dict__.items():
            self.biomes[biome_id] = BIOMES[biome_id](self.world, biome_id)

    def get_biome_object_from_tile(self, coordinates):
        biome_id = self.get_biome_id(coordinates)
        return self.biomes[biome_id]

    def get_biome_id(self, coords):

        biome_intensity = {}
        for biome_name, biome_id in BIOME_IDS.__dict__.items():
            biome_intensity[biome_id] = self.persistent_noise(coords, BIOME_SCALE, self.biomes[biome_id].seed, octaves=4) * self.biomes[biome_id].intensity_weight(coords) + self.biomes[biome_id].intensity_bias(coords)
            #print(f"coordinates: {coords}, distance: {euclidean_distance((0, 0), coords)}, biome_id: {biome_id}, biome_intensity[biome_id]: {biome_intensity[biome_id]}")

        final_biome_id = max(biome_intensity, key=lambda key: biome_intensity[key])

        return final_biome_id

    def generate_tile(self, coords):
        biome = self.biomes[self.get_biome_id(coords)]

        if self.world.total_floor[coords] is None:
            self.world.total_floor[coords] = biome.generate_floor_tile(coords)
            self.world.total_walls[coords] = biome.generate_wall_tile(coords)
            self.world.total_tile_effects[coords] = biome.generate_tile_effect(coords)
            self.world.total_items[coords] = biome.generate_item(coords)
            if self.world.game.enemy_spawns_enabled:
                biome.generate_monster_group(coords)
            biome.generate_poi(coords)

    def generate_biome_grid(self, width, height):
        grid = np.zeros((height, width))
        for y in range(height):
            for x in range(width):
                grid[y, x] = self.get_biome_id((x - (width // 2), y - (height // 2)))
        return grid


    def visualize_biome_grid(self, grid):
        plt.figure(figsize=(8, 8))
        plt.imshow(grid, cmap='terrain')  # Using 'terrain' colormap for a nice effect
        plt.colorbar(label='Biome Type')
        plt.title('Biome Map')
        plt.xlabel('X Coordinate')
        plt.ylabel('Y Coordinate')
        plt.show()

    def persistent_noise(self, coords, scale, seed, octaves=4):
        """
        Generate persistent 2D noise using Simplex noise.
        """
        # Adjust input coordinates with seed for persistence
        return snoise2((coords[0] + seed) / scale, (coords[1] + seed) / scale, octaves=octaves)

'''
wg = WorldGenerator()
grid = wg.generate_biome_grid(100, 100)
#print(grid)
wg.visualize_biome_grid(grid)
'''