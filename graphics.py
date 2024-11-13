import pygame
import os
from collections import defaultdict

root_directory = "assets"
asset_dict = defaultdict(lambda : "assets/unknown.png")
assets = defaultdict(lambda : assets["unknown"])


VISUAL_RANGE = 10 # Think about this later. Probably do Manhattan and just let it be what's on screen.

def load_graphics():
    for dirpath, _, filenames in os.walk(root_directory):
        for filename in filenames:
            # Full path of the file
            file_path = os.path.join(dirpath, filename)
            # File name without the extension
            name_without_extension = os.path.splitext(filename)[0]
            # Add the tuple (file path, name without extension) to the defaultdict
            asset_dict[name_without_extension] = (file_path)

    for key in asset_dict.keys():
        assets[key] = pygame.image.load(asset_dict[key]).convert_alpha()

def render_everything(world, display):
    for coords in world.floor.keys():
        if world.calculate_distance(coords, world.current_coordinates) < VISUAL_RANGE:
            display.blit(world.floor[coords].asset, (32 * coords[0], 32 * coords[1]))

    for coords in world.entities.keys():
        if world.calculate_distance(coords, world.current_coordinates) < VISUAL_RANGE:
            display.blit(world.entities[coords].asset, (32 * coords[0], 32 * coords[1]))

    pygame.display.flip()

