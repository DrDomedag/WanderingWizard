import pygame
import os
import math
from collections import defaultdict
import entities.entities
from util import *

SIDE_MENU_WIDTH = 400

# Consider this for animated sprites:
# https://stackoverflow.com/questions/14044147/animated-sprite-from-few-images


class UI:
    def __init__(self, display, world):
        self.display = display
        self.world = world
        self.root_directory = "assets"
        self.asset_dict = defaultdict(lambda : "assets/unknown.png")
        self.assets = defaultdict(lambda : self.assets["unknown"])

        # This is real ugly, but it's the best I can think of right now.
        self.left_click = False
        self.right_click = False

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
        # Let's just stick to 32x32. It fits a decent amount of tiles and

        self.selected_spell = None



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

        #print(f"Found {len(self.asset_dict.keys())} image files.")
        for key in self.asset_dict.keys():
            self.assets[key] = pygame.image.load(self.asset_dict[key]).convert_alpha()

        #print(f"Loaded {len(self.assets.keys())} images as sprites.")



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

        # Render items

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

        # Render effects

        hovered_tile = self.find_tile_at_screen_coords(pygame.mouse.get_pos())

        # Highlight LoS tiles if holding L key
        if pygame.key.get_pressed()[pygame.K_l]:
            self.show_LoS_at_cursor()

        # Just always highlight mouseover'd tile

        self.display.blit(self.assets["target_tile"], (
            self.SPRITE_SIZE * (hovered_tile[0] - self.world.current_coordinates[0]) + self.centre_x,
            self.SPRITE_SIZE * (hovered_tile[1] - self.world.current_coordinates[1]) + self.centre_y))

        # Highlight affected tiles if holding down right mouse button

        if pygame.mouse.get_pressed(num_buttons=3)[2] and self.selected_spell is not None:
            #print(f"Holding down right mouse button.")
            tile_sprite = self.assets["impacted_tile"]
            for tile in self.selected_spell.get_impacted_tiles(hovered_tile):
                self.display.blit(tile_sprite, (
                    self.SPRITE_SIZE * (tile[0] - self.world.current_coordinates[0]) + self.centre_x,
                    self.SPRITE_SIZE * (tile[1] - self.world.current_coordinates[1]) + self.centre_y))

            if self.left_click:
                if self.selected_spell.can_cast(hovered_tile):
                    self.selected_spell.cast(hovered_tile)

        # Draw menus

        self.draw_left_side_menu()
        self.draw_right_side_menu()

        self.left_click = False
        self.right_click = False

        pygame.display.flip()


    def draw_left_side_menu(self):
        bg_rect = pygame.Rect(0, 0, SIDE_MENU_WIDTH, self.display.get_size()[1])
        pygame.draw.rect(self.display, COLOURS.BLACK, bg_rect)
        button_offset = 20
        buttons = 0
        button_height = 20
        button_width = SIDE_MENU_WIDTH - 10
        for spell in self.world.pc.actives:
            spellButton = Button(self, f"{spell.name} - {spell.current_charges}/{spell.max_charges}", (5, button_offset + (buttons * button_height)), (button_width, button_height), COLOURS.RED, COLOURS.MAGENTA, COLOURS.YELLOW, self.select_spell, spell)
            spellButton.draw(self.display)

    def draw_right_side_menu(self):
        bg_rect = pygame.Rect(self.display.get_size()[0] - SIDE_MENU_WIDTH, 0, 400, self.display.get_size()[1])
        pygame.draw.rect(self.display, COLOURS.BLACK, bg_rect)

    def show_LoS_at_cursor(self):
        origin_tile = self.find_tile_at_screen_coords(pygame.mouse.get_pos())
        tiles_to_highlight = self.world.get_visible_tiles(origin_tile)
        #print(tiles_to_highlight)
        tile_sprite = self.assets["visible_tile"]
        for tile in tiles_to_highlight:
            self.display.blit(tile_sprite, (
            self.SPRITE_SIZE * (tile[0] - self.world.current_coordinates[0]) + self.centre_x,
            self.SPRITE_SIZE * (tile[1] - self.world.current_coordinates[1]) + self.centre_y))

            #highlight_rect = pygame.Rect((tile[0] * self.SPRITE_SIZE) + self.centre_x, (tile[1] * self.SPRITE_SIZE) + self.centre_y, self.SPRITE_SIZE/2, self.SPRITE_SIZE/2)
            #pygame.draw.rect(self.display, (255, 255, 255), highlight_rect)

    def find_tile_at_screen_coords(self, coords):
        world_x = math.floor(((coords[0] - self.centre_x) // self.SPRITE_SIZE) + self.world.current_coordinates[0])
        world_y = math.floor(((coords[1] - self.centre_y) // self.SPRITE_SIZE) + self.world.current_coordinates[1])
        return (world_x, world_y)

    def select_spell(self, spell):
        print(f"Selected spell: {spell.name}")
        self.selected_spell = spell



class Button:
    def __init__(self, ui, text, pos, size, colour, hover_colour, selected_colour, action=None, selected_object=None):
        self.ui = ui
        self.selected_object = selected_object
        self.text = text
        self.pos = pos
        self.size = size
        self.colour = colour
        self.hover_colour = hover_colour
        self.selected_colour = selected_colour
        self.action = action
        self.selected = False
        self.rect = pygame.Rect(pos, size)
        self.font = pygame.font.Font(None, 36)


    def draw(self, screen):
        # Change colour when hovering
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.hover_colour, self.rect)
        elif self.selected:
            pygame.draw.rect(screen, self.selected_colour, self.rect)
        else:
            pygame.draw.rect(screen, self.colour, self.rect)
        # Draw text on the button
        text_surface = self.font.render(self.text, True, COLOURS.BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        self.check_click()
        screen.blit(text_surface, text_rect)

    def check_click(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            if self.ui.left_click:
                if self.action:
                    if self.selected_object:
                        self.action(self.selected_object)
                    else:
                        self.action()

