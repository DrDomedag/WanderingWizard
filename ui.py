import pygame
import os
import math
from collections import defaultdict

from Tools.scripts.verify_ensurepip_wheels import verify_wheel

import entities.entities
import util
from util import *

SIDE_MENU_WIDTH = 400

# Consider this for animated sprites:
# https://stackoverflow.com/questions/14044147/animated-sprite-from-few-images


class UI:
    def __init__(self, display, world):
        self.display = display
        self.world = world

        self.ongoing_effects = pygame.sprite.Group()
        self.clock = pygame.time.Clock()

        # This is real ugly, but it's the best I can think of right now.
        self.left_click = False
        self.right_click = False
        self.scroll_down = False
        self.scroll_up = False
        self.hovered_spell = None

        self.mouse_over_game_area = False

        # CHANGE THIS for sure
        self.font_32 = pygame.font.Font('PixelatedEleganceRegular.ttf', 32)
        self.font_20 = pygame.font.Font('PixelatedEleganceRegular.ttf', 20)
        self.font_14 = pygame.font.Font('PixelatedEleganceRegular.ttf', 14)
        # font = pygame.font.Font('PublicPixel.ttf', 32)


        self.VISUAL_RANGE = 10 # Think about this later. Probably do Manhattan and just let it be what's on screen.

        self.SPRITE_SIZE = 32

        #self.current_display_size = pygame.Surface.get_rect

        self.centre_x = int(self.display.get_size()[0] / 2)
        self.centre_y = int(self.display.get_size()[1] / 2)

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

    def render_everything(self):
        #print(f"Floor tile count: {len(self.world.total_floor.keys())}")
        #print(f"Entity count: {len(self.world.total_entities.keys())}")
        #print(self.centre_x)
        #print(self.centre_y)

        # Fill screen with black. Could change to a nice fog image or something later.
        self.display.fill(COLOURS.BLACK)

        # Create new effects
        while len(self.world.effect_queue) > 0:
            target_tile, effect_type = self.world.effect_queue.pop()

            target_coords = self.tile_to_screen_coords(target_tile, offset_by_half_a_tile=True)

            if effect_type == SCHOOLS.FIRE:
                new_sprite = ExplosionEffect(self.world, "fire", target_coords, self.ongoing_effects)
                self.ongoing_effects.add(new_sprite)


        # Render tiles:
        for tile_coords in self.world.active_floor.keys():
            #if world.calculate_distance(tile_coords, world.current_coordinates) < VISUAL_RANGE:
            tile = self.world.active_floor[tile_coords]
            if tile is not None and self.world.game.pc.can_see(tile_coords):
                self.display.blit(self.world.assets[tile.asset], self.tile_to_screen_coords(tile_coords))

        # Render items
        for item_coords in self.world.active_walls.keys():
            if self.world.total_items[item_coords] is not None and self.world.game.pc.can_see(item_coords):
                item = self.world.total_items[item_coords]
                if item.layer == "item":
                    #print(f"Rendering {entity.name} at game coords: {entity_coords}, self-registered coords: {entity.position} screen-centered x: {(entity_coords[0] - self.world.current_coordinates[0])}, screen x: {self.SPRITE_SIZE * (entity_coords[0] - self.world.current_coordinates[0]) + self.centre_x}, screen-centered y: {(entity_coords[1] - self.world.current_coordinates[1]) + self.centre_y}, screen y: {self.SPRITE_SIZE * (entity_coords[1] - self.world.current_coordinates[1]) + self.centre_y}")
                    self.display.blit(self.world.assets[item.asset], self.tile_to_screen_coords(item_coords))

        # Render walls:
        for entity_coords in self.world.active_walls.keys():
            if self.world.total_walls[entity_coords] is not None and self.world.game.pc.can_see(entity_coords):
                wall = self.world.total_walls[entity_coords]
                if wall.layer == "wall":
                    #print(f"Rendering {entity.name} at game coords: {entity_coords}, self-registered coords: {entity.position} screen-centered x: {(entity_coords[0] - self.world.current_coordinates[0])}, screen x: {self.SPRITE_SIZE * (entity_coords[0] - self.world.current_coordinates[0]) + self.centre_x}, screen-centered y: {(entity_coords[1] - self.world.current_coordinates[1]) + self.centre_y}, screen y: {self.SPRITE_SIZE * (entity_coords[1] - self.world.current_coordinates[1]) + self.centre_y}")
                    self.display.blit(self.world.assets[wall.asset], self.tile_to_screen_coords(entity_coords))

        # Render entities
        for entity_coords in self.world.active_entities.keys():
            if self.world.total_entities[entity_coords] is not None and self.world.game.pc.can_see(entity_coords):
                entity = self.world.total_entities[entity_coords]
                if entity.layer == "entity":
                    entity.draw(self.display, self.tile_to_screen_coords(entity_coords))
                    #print(f"Rendering {entity.name} at game coords: {entity_coords}, self-registered coords: {entity.position} screen-centered x: {(entity_coords[0] - self.world.current_coordinates[0])}, screen x: {self.SPRITE_SIZE * (entity_coords[0] - self.world.current_coordinates[0]) + self.centre_x}, screen-centered y: {(entity_coords[1] - self.world.current_coordinates[1]) + self.centre_y}, screen y: {self.SPRITE_SIZE * (entity_coords[1] - self.world.current_coordinates[1]) + self.centre_y}")
                    #self.display.blit(self.assets[entity.asset], (self.SPRITE_SIZE * (entity_coords[0] - self.world.current_coordinates[0]) + self.centre_x, self.SPRITE_SIZE * (entity_coords[1] - self.world.current_coordinates[1]) + self.centre_y))

        # Render tile effects:
        for tile_effect_coords in self.world.active_tile_effects.keys():
            if self.world.total_tile_effects[tile_effect_coords] is not None and self.world.game.pc.can_see(tile_effect_coords):
                tile_effect_sprite = self.world.total_tile_effects[tile_effect_coords].sprite
                screen_coords = self.tile_to_screen_coords(tile_effect_coords)
                tile_effect_sprite.update()
                tile_effect_sprite.draw(self.display, screen_coords)


        # Update and render effects
        self.ongoing_effects.update()
        self.ongoing_effects.draw(self.display)
        #print(f"len(self.ongoing_effects): {len(self.ongoing_effects)}")

        hovered_tile = self.find_tile_at_screen_coords(pygame.mouse.get_pos())

        self.mouse_over_game_area = False
        if SIDE_MENU_WIDTH < pygame.mouse.get_pos()[0] < self.display.get_size()[0] - SIDE_MENU_WIDTH:
            self.mouse_over_game_area = True

        if self.mouse_over_game_area:

            # Highlight LoS tiles if holding L key
            if pygame.key.get_pressed()[pygame.K_l]:
                self.show_LoS_at_cursor()

            # Just always highlight mouseover'd tile
            self.display.blit(self.world.assets["target_tile"], self.tile_to_screen_coords(hovered_tile))

            # Highlight affected tiles if holding down right mouse button

            if pygame.mouse.get_pressed(num_buttons=3)[2] and self.selected_spell is not None:
                tile_sprite = self.world.assets["targetable_tile"]
                for tile in self.selected_spell.get_targetable_tiles():
                    self.display.blit(tile_sprite, self.tile_to_screen_coords(tile))
                tile_sprite = self.world.assets["impacted_tile"]
                for tile in self.selected_spell.get_impacted_tiles(hovered_tile):
                    self.display.blit(tile_sprite, self.tile_to_screen_coords(tile))


                if self.left_click:
                    if self.selected_spell.can_cast(hovered_tile):
                        self.selected_spell.cast(hovered_tile)

            # End turn if pressing own tile:
            elif self.left_click and not pygame.mouse.get_pressed(num_buttons=3)[2] and self.world.game.pc.position == hovered_tile:
                self.world.game.pc.current_actions = 0

            # Walk on clicking adjacent tile:
            elif self.left_click and not pygame.mouse.get_pressed(num_buttons=3)[2] and util.chebyshev_distance(self.world.game.pc.position, hovered_tile) == 1:
                if self.world.game.pc.move(hovered_tile):
                    self.world.game.pc.current_actions -= 1

            # Walk on clicking distant tile
            if self.left_click and not pygame.mouse.get_pressed(num_buttons=3)[2] and util.chebyshev_distance(self.world.game.pc.position, hovered_tile) > 1 and self.world.game.pc.can_see(hovered_tile):
                path = util.find_path(self.world.game.pc, hovered_tile)
                #print(path)
                if len(path) > 0:
                    if self.world.game.pc.move(path[1]):
                        self.world.game.pc.current_actions -= 1

        if self.scroll_down and len(self.world.game.pc.actives) > 0:
            self.select_next_spell()
        if self.scroll_up:
            self.select_previous_spell()


        # Draw menus
        self.hovered_spell = None
        self.draw_left_side_menu()
        self.draw_right_side_menu(hovered_tile)

        self.left_click = False
        self.right_click = False
        self.scroll_down = False
        self.scroll_up = False

        pygame.display.flip()

        self.clock.tick(60)

    def select_next_spell(self):
        if self.selected_spell == None:
            self.selected_spell = self.world.game.pc.actives[0]
        elif self.world.game.pc.actives.index(self.selected_spell) + 1 >= len(self.world.game.pc.actives):
            self.selected_spell = self.world.game.pc.actives[0]
        else:
            self.selected_spell = self.world.game.pc.actives[self.world.game.pc.actives.index(self.selected_spell) + 1]

    def select_previous_spell(self):
        if self.selected_spell == None:
            self.selected_spell = self.world.game.pc.actives[-1]
        else:
            self.selected_spell = self.world.game.pc.actives[self.world.game.pc.actives.index(self.selected_spell) - 1]

    def tile_to_screen_coords(self, coords, offset_by_half_a_tile=False):
        x = self.SPRITE_SIZE * (coords[0] - self.world.current_coordinates[0]) + self.centre_x
        y = self.SPRITE_SIZE * (coords[1] - self.world.current_coordinates[1]) + self.centre_y
        if offset_by_half_a_tile:
            x += self.SPRITE_SIZE//2
            y += self.SPRITE_SIZE//2
        coords = (x, y)
        return coords

    def draw_left_side_menu(self):
        bg_rect = pygame.Rect(0, 0, SIDE_MENU_WIDTH, self.display.get_size()[1])
        pygame.draw.rect(self.display, COLOURS.BLACK, bg_rect)
        if self.world.game.pc.hp < 25:
            text = self.font_32.render(f"HP: {self.world.game.pc.hp}/{self.world.game.pc.max_hp}", True, COLOURS.RED, COLOURS.DARK_GRAY)
        elif self.world.game.pc.hp < 50:
            text = self.font_32.render(f"HP: {self.world.game.pc.hp}/{self.world.game.pc.max_hp}", True, COLOURS.YELLOW, COLOURS.DARK_GRAY)
        else:
            text = self.font_32.render(f"HP: {self.world.game.pc.hp}/{self.world.game.pc.max_hp}", True, COLOURS.WHITE, COLOURS.DARK_GRAY)
        textRect = text.get_rect()
        textRect.center = (120, 25)
        self.display.blit(text, textRect)

        # Action crystals
        full_crystal = self.world.assets["action_crystal_full"]
        empty_crystal = self.world.assets["action_crystal_empty"]
        for i in range(self.world.game.pc.actions_per_round):
            if i >= self.world.game.pc.current_actions:
                # Render empty action crystal
                self.display.blit(empty_crystal, (5 + i * 30, 60))
            else:
                # Render full action crystal
                self.display.blit(full_crystal, (5 + i * 30, 60))


        button_offset = 120
        button_height = 20
        button_width = SIDE_MENU_WIDTH - 10
        for i, spell in enumerate(self.world.game.pc.actives):
            spellButton = SpellSelectorButton(self, f"{spell.name} - {spell.current_charges}/{spell.max_charges}", (5, button_offset + (i * button_height)), (button_width, button_height), COLOURS.RED, COLOURS.MAGENTA, COLOURS.YELLOW, self.select_spell, spell)
            spellButton.draw(self.display)

    def draw_right_side_menu(self, hovered_tile):
        left_end = self.display.get_size()[0] - SIDE_MENU_WIDTH
        width = 400
        height = self.display.get_size()[1]
        bg_rect = pygame.Rect(left_end, 0, width, self.display.get_size()[1])
        pygame.draw.rect(self.display, COLOURS.BLACK, bg_rect)
        if self.mouse_over_game_area and self.world.game.pc.can_see(hovered_tile):
            vertical_offset = 30
            entity = self.world.active_entities[hovered_tile]
            if entity is None:
                entity = self.world.active_walls[hovered_tile]
            if entity is not None:
                name = self.font_32.render(f"{entity.name}", True, COLOURS.WHITE, COLOURS.DARK_GRAY)
                nameRect = name.get_rect()
                nameRect.center = (left_end + width // 2, vertical_offset)
                vertical_offset += 30
                self.display.blit(name, nameRect)
                if entity.hp <= entity.max_hp // 4:
                    hp = self.font_32.render(f"HP: {entity.hp}/{entity.max_hp}", True, COLOURS.RED, COLOURS.DARK_GRAY)
                elif entity.hp <= entity.max_hp // 2:
                    hp = self.font_32.render(f"HP: {entity.hp}/{entity.max_hp}", True, COLOURS.YELLOW, COLOURS.DARK_GRAY)
                else:
                    hp = self.font_32.render(f"HP: {entity.hp}/{entity.max_hp}", True, COLOURS.WHITE, COLOURS.DARK_GRAY)
                hpRect = hp.get_rect()
                hpRect.center = (left_end + width // 2, vertical_offset)
                vertical_offset += 30
                self.display.blit(hp, hpRect)

                # Action crystals
                full_crystal = self.world.assets["action_crystal_full"]
                empty_crystal = self.world.assets["action_crystal_empty"]
                for i in range(entity.actions_per_round):
                    if i >= entity.current_actions:
                        # Render empty action crystal
                        self.display.blit(empty_crystal, (left_end + i * 30, vertical_offset))
                    else:
                        # Render full action crystal
                        self.display.blit(full_crystal, (left_end + i * 30, vertical_offset))
                vertical_offset += 40
                vertical_offset = blit_text(self.display, entity.description,
                                            (left_end + 5, vertical_offset), self.font_14, COLOURS.WHITE)
                vertical_offset += 20

                if entity != self.world.game.pc:
                    # Show abilities
                    for passive in entity.passives:
                        name = self.font_20.render(f"{passive.name}", True, COLOURS.WHITE, COLOURS.DARK_GRAY)
                        nameRect = name.get_rect()
                        nameRect.center = (left_end + width // 2, vertical_offset)
                        self.display.blit(name, nameRect)
                        vertical_offset += 30
                        vertical_offset = blit_text(self.display, passive.description,
                                                    (left_end + 5, vertical_offset), self.font_14, COLOURS.WHITE)

                    for active in entity.actives:
                        name = self.font_20.render(f"{active.name}", True, COLOURS.WHITE, COLOURS.DARK_GRAY)
                        nameRect = name.get_rect()
                        nameRect.center = (left_end + width // 2, vertical_offset)
                        self.display.blit(name, nameRect)
                        vertical_offset += 30

                        power = self.font_14.render(f"Power: {active.power}", True, COLOURS.WHITE, COLOURS.DARK_GRAY)
                        power_rect = name.get_rect()
                        power_rect.center = (left_end + width // 2, vertical_offset)
                        self.display.blit(power, power_rect)
                        vertical_offset += 16

                        active_range = self.font_14.render(f"Range: {active.range}", True, COLOURS.WHITE, COLOURS.DARK_GRAY)
                        active_range_rect = name.get_rect()
                        active_range_rect.center = (left_end + width // 2, vertical_offset)
                        self.display.blit(active_range, active_range_rect)
                        vertical_offset += 16

                        action_cost = self.font_14.render(f"Action cost:", True, COLOURS.WHITE, COLOURS.DARK_GRAY)
                        action_cost_rect = name.get_rect()
                        action_cost_rect.center = (left_end + width // 2, vertical_offset)
                        self.display.blit(action_cost, action_cost_rect)

                        for i in range(active.action_cost):
                            if i >= entity.current_actions:
                                self.display.blit(full_crystal, (left_end + (width // 2) + 40 + i * 30, vertical_offset - 15))

                        vertical_offset += 20

                        vertical_offset = blit_text(self.display, active.description,
                                                    (left_end + 5, vertical_offset), self.font_14, COLOURS.WHITE)
                        vertical_offset += 50




            if entity is None:
                entity = self.world.active_floor[hovered_tile]
                if entity is not None:
                    name = self.font_32.render(f"{entity.name}", True, COLOURS.WHITE, COLOURS.DARK_GRAY)
                    nameRect = name.get_rect()
                    nameRect.center = (left_end + width // 2, vertical_offset)
                    self.display.blit(name, nameRect)
                    vertical_offset += 30
                    type = self.font_32.render(f"{entity.type}", True, COLOURS.WHITE, COLOURS.DARK_GRAY)
                    typeRect = type.get_rect()
                    typeRect.center = (left_end + width // 2, vertical_offset)
                    self.display.blit(type, typeRect)
                    vertical_offset += 40
                    # Would be cool with boots/fins/wings icons here to show passability using these different types of movement.
            hovered_tile_effect = self.world.active_tile_effects[hovered_tile]
            if hovered_tile_effect is not None:
                name = self.font_32.render(f"{hovered_tile_effect.name}", True, COLOURS.WHITE, COLOURS.DARK_GRAY)
                nameRect = name.get_rect()
                nameRect.center = (left_end + width // 2, vertical_offset)
                self.display.blit(name, nameRect)
                vertical_offset += 40
                vertical_offset = blit_text(self.display, hovered_tile_effect.description, (left_end + 5, vertical_offset), self.font_14, COLOURS.WHITE)

        else:
            if self.hovered_spell is not None:
                vertical_offset = 30
                name = self.font_32.render(f"{self.hovered_spell.name}", True, COLOURS.WHITE, COLOURS.DARK_GRAY)
                nameRect = name.get_rect()
                nameRect.center = (left_end + width // 2, vertical_offset)
                vertical_offset += 30
                self.display.blit(name, nameRect)
                for i in range(len(self.hovered_spell.schools)):
                    name = self.font_20.render(f"{SCHOOL_NAMES[self.hovered_spell.schools[i]]}", True, SCHOOL_COLOURS[self.hovered_spell.schools[i]], COLOURS.BLACK)
                    nameRect = name.get_rect()
                    nameRect.center = (left_end + width // 2, vertical_offset)
                    vertical_offset += 20
                    self.display.blit(name, nameRect)
                '''
                descr = self.font_14.render(f"{self.hovered_spell.description}", True, COLOURS.WHITE, COLOURS.BLACK)
                descrRect = descr.get_rect()
                descrRect.center = (left_end + width // 2, vertical_offset)
                vertical_offset += 40
                self.display.blit(descr, descrRect)
                '''
                pos = (left_end + 5, vertical_offset)
                blit_text(self.display, self.hovered_spell.description, pos, self.font_14, color=COLOURS.GRAY)

    def show_LoS_at_cursor(self):
        origin_tile = self.find_tile_at_screen_coords(pygame.mouse.get_pos())
        #tiles_visible_from_origin = set(self.world.get_visible_tiles(origin_tile))
        tiles_to_highlight = self.world.get_visible_tiles(origin_tile, treat_fow_as_wall=True)

        #tiles_to_highlight = tiles_visible_from_origin.intersection(visible_tiles)

        #print(tiles_to_highlight)
        tile_sprite = self.world.assets["visible_tile"]
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



class SpellSelectorButton:
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
        #self.font = pygame.font.Font('PixelatedEleganceRegular.ttf', 32)


    def draw(self, screen):
        # Change colour when hovering
        mouse_pos = pygame.mouse.get_pos()
        if self.ui.selected_spell is not None:
            if self.rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, self.hover_colour, self.rect)
            elif self.selected_object.name == self.ui.selected_spell.name:
                pygame.draw.rect(screen, self.selected_colour, self.rect)
            else:
                pygame.draw.rect(screen, self.colour, self.rect)
        else:
            if self.rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, self.hover_colour, self.rect)
            else:
                pygame.draw.rect(screen, self.colour, self.rect)

        if self.rect.collidepoint(mouse_pos):
            self.ui.hovered_spell = self.selected_object

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


class ExplosionEffect(pygame.sprite.Sprite):
    def __init__(self, world, asset_name, position, *groups):
        """
        Creates an explosion effect that animates through a list of sprites and deletes itself.

        :param sprites: List of PyGame surfaces or sprite frames.
        :param position: Tuple (x, y) for the position of the effect.
        :param delay: Time in milliseconds between frames.
        :param groups: PyGame sprite groups to which this effect belongs.
        """
        super().__init__(*groups)
        self.world = world
        self.asset_name = asset_name
        self.sprite = self.get_sprites()
        self.position = position
        self.delay = 100
        self.current_frame = 0
        self.last_update_time = pygame.time.get_ticks()
        self.image = self.sprite[self.current_frame]
        self.rect = self.image.get_rect(center=self.position)

    def get_sprites(self):
        i = 0
        '''
        print(self.world.assets.keys())
        print(self.asset_name)
        print(f"{self.asset_name}_0")
        print(self.world.assets["fire_0"])
        print(self.world.assets[f"{self.asset_name}_{i}"])
        '''
        sprite_list = []
        if self.world.assets[f"{self.asset_name}_{i}"]:
            #print(f"Determined that there is a frame {i}")
            while self.world.assets[f"{self.asset_name}_{i}"]:
                #print(f"Found sprite frame {i}")
                sprite_list.append(self.world.assets[f"{self.asset_name}_{i}"])
                i += 1
        else:
            sprite_list.append(self.world.assets[f"{self.asset_name}"])
        return sprite_list

    def update(self):
        """
        Updates the explosion animation by switching frames and removing itself when done.
        """
        now = pygame.time.get_ticks()

        if now - self.last_update_time >= self.delay:
            self.last_update_time = now
            self.current_frame += 1

            # Check if the animation is complete
            if self.current_frame >= len(self.sprite):
                self.kill()  # Remove itself from all sprite groups
            else:
                # Update to the next frame
                self.image = self.sprite[self.current_frame]
                self.rect = self.image.get_rect(center=self.position)


# Consider moving this into the UI class. It works fine like this, tbf.
def blit_text(surface, text, pos, font, color=pygame.Color('black')):
    words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
    space = font.size(' ')[0]  # The width of a space.
    max_width, max_height = surface.get_size()
    x, y = pos
    for line in words:
        for word in line:
            word_surface = font.render(word, 0, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width:
                x = pos[0]  # Reset the x.
                y += word_height  # Start on new row.
            surface.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]  # Reset the x.
        y += word_height  # Start on new row.
    return y
