from noise import snoise2
import matplotlib.pyplot as plt
import numpy as np

BIOME_SCALE = 100

# Current idea:
# Define a few biomes
# For each, create a noise map measuring how intensely that biome exists in that area
# For each tile, it is considered to be of the biome where whose intensity is highest
# This allows for adding biomes later
# Decrease intensity of difficult/high level biomes for tiles close to start
# Something like 1/0.0001x depending on whatever the intensities actually are


# ooh, do a *weird* biome that uses e.g. sine waves for ground generation so that it follows strict (but weird) geometric patterns
# Can do something like that for desert dunes? Probably not easy.

# Biome ideas:
'''

Ice caverns (closed and cold)
Volcanic caverns (hot and closed)
Mushroom caverns
Crystal caverns
Catacombs

Jungle (dense trees)
Swamp (difficult to traverse, lots of water tiles)
Riverland (long streaks of water)
Ocean/beach (definitely requires swimming ability)
Canyon (winding paths)
Plains (very open)
Tundra (open and cold)

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


def get_biome(x, y):

    plains_intensity = snoise2(x / BIOME_SCALE, y / BIOME_SCALE, octaves=4)

    return plains_intensity


def generate_biome_grid(width, height, scale=100.0):
    grid = np.zeros((height, width))
    for y in range(height):
        for x in range(width):
            grid[y, x] = get_biome(x, y, scale)
    return grid


def visualize_biome_grid(grid):
    plt.figure(figsize=(8, 8))
    plt.imshow(grid, cmap='terrain')  # Using 'terrain' colormap for a nice effect
    plt.colorbar(label='Biome Type')
    plt.title('Biome Map')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.show()