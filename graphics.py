import pygame
import os
from collections import defaultdict

import entities.entities

#from copy import copy

class GraphicsHandler:
    def __init__(self, display, world):
        self.display = display
        self.world = world
        self.root_directory = "assets"
        self.asset_dict = defaultdict(lambda : "assets/unknown.png")
        self.assets = defaultdict(lambda : self.assets["unknown"])

        # Hardcoding this to ensure it's loaded by the time anything needs to access this:
        self.assets["unknown"] = pygame.image.load("assets/unknown.png").convert_alpha()


        self.VISUAL_RANGE = 10 # Think about this later. Probably do Manhattan and just let it be what's on screen.

        self.SPRITE_SIZE = 32

        #self.current_display_size = pygame.Surface.get_rect

        self.centre_x = int(self.display.get_size()[0] / 2)
        self.centre_y = int(self.display.get_size()[1] / 2)

        self.load_graphics()

        # Common denominators for 1920 and 1080:
        # 1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 24, 30, 40, 60, 120
        # 32 felt a bit big. Let's try 20.

        # At 30x30 pixels per tile, the screen fits 64 x 36 tiles.
        # At 24, it's 80 x 45
        # RW2 is actually 16x16 pixels in art files, but 33x33 tiles on map.
        # Actually displaying at about 32 pixels per tile
        # Presumably scaled up 2x.
        # So maybe do 30x30 anyway. Or 31x31 to have a centre pixel.



    def load_graphics(self):
        for dirpath, _, filenames in os.walk(self.root_directory):
            for filename in filenames:
                # Full path of the file
                file_path = os.path.join(dirpath, filename)
                # File name without the extension
                name_without_extension = os.path.splitext(filename)[0]
                extension = os.path.splitext(filename)[1]
                if extension == ".png":
                    self.asset_dict[name_without_extension] = file_path

        print(f"Found {len(self.asset_dict.keys())} image files.")
        for key in self.asset_dict.keys():
            self.assets[key] = pygame.image.load(self.asset_dict[key]).convert_alpha()

        print(f"Loaded {len(self.assets.keys())} images as sprites.")
        print(self.assets.keys())



    def render_everything(self):
        #print(f"Floor tile count: {len(self.world.total_floor.keys())}")
        #print(f"Entity count: {len(self.world.total_entities.keys())}")
        #print(self.centre_x)
        #print(self.centre_y)

        # Render tiles:
        for tile_coords in self.world.active_floor.keys():
            #if world.calculate_distance(tile_coords, world.current_coordinates) < VISUAL_RANGE:
            tile = self.world.total_floor[tile_coords]
            self.display.blit(self.assets[tile.asset], (self.SPRITE_SIZE * (tile_coords[0] - self.world.current_coordinates[0]) + self.centre_x, self.SPRITE_SIZE * (tile_coords[1] - self.world.current_coordinates[1]) + self.centre_y))

        # Render walls:
        for entity_coords in self.world.active_walls.keys():
            if self.world.total_walls[entity_coords] is not None:
                wall = self.world.total_walls[entity_coords]
                if wall.layer == "wall":
                    #print(f"Rendering {entity.name} at game coords: {entity_coords}, self-registered coords: {entity.position} screen-centered x: {(entity_coords[0] - self.world.current_coordinates[0])}, screen x: {self.SPRITE_SIZE * (entity_coords[0] - self.world.current_coordinates[0]) + self.centre_x}, screen-centered y: {(entity_coords[1] - self.world.current_coordinates[1]) + self.centre_y}, screen y: {self.SPRITE_SIZE * (entity_coords[1] - self.world.current_coordinates[1]) + self.centre_y}")
                    self.display.blit(self.assets[wall.asset], (self.SPRITE_SIZE * (entity_coords[0] - self.world.current_coordinates[0]) + self.centre_x, self.SPRITE_SIZE * (entity_coords[1] - self.world.current_coordinates[1]) + self.centre_y))

        # Render entities
        for entity_coords in self.world.active_entities.keys():
            if self.world.total_entities[entity_coords] is not None:
                entity = self.world.total_entities[entity_coords]
                if entity.layer == "entity":
                    #print(f"Rendering {entity.name} at game coords: {entity_coords}, self-registered coords: {entity.position} screen-centered x: {(entity_coords[0] - self.world.current_coordinates[0])}, screen x: {self.SPRITE_SIZE * (entity_coords[0] - self.world.current_coordinates[0]) + self.centre_x}, screen-centered y: {(entity_coords[1] - self.world.current_coordinates[1]) + self.centre_y}, screen y: {self.SPRITE_SIZE * (entity_coords[1] - self.world.current_coordinates[1]) + self.centre_y}")
                    self.display.blit(self.assets[entity.asset], (self.SPRITE_SIZE * (entity_coords[0] - self.world.current_coordinates[0]) + self.centre_x, self.SPRITE_SIZE * (entity_coords[1] - self.world.current_coordinates[1]) + self.centre_y))


        pygame.display.flip()

