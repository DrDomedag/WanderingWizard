import pygame
import effects
from util import *


class TileEffect:
    def __init__(self, world, creator, position, expires, duration):
        self.world = world
        self.creator = creator
        self.position = position
        self.potency = 1
        self.expires = expires
        self.duration = duration
        self.name = "Unknown tile effect"
        self.description = "It is not known what this tile effect does."
        self.asset_name = "unknown"
        self.layer = "tile_effect"

        self.on_init()

        self.asset = world.assets[self.asset_name]
        self.sprite = ShimmeringSprite(self.asset, 113)

    def on_init(self):
        pass

    def on_enter_effect(self):
        pass

    def start_of_turn_effect(self):
        pass

    def start_of_turn(self):
        self.start_of_turn_effect()
        if self.expires:
            self.duration -= 1
            if self.duration <= 0:
                self.world.total_tile_effects = None
                self.world.active_tile_effects = None
                del self

    def draw(self, display, screen_coordinates):
        self.sprite.draw(display, screen_coordinates)



class PoisonMist(TileEffect):

    def on_init(self):
        self.potency = 2
        self.name = "Poison Mist"
        self.description = f"This mist deals {self.potency} damage to each creature in it at the start of each turn."
        self.asset_name = "mist"


    def start_of_turn_effect(self):
        effects.damage_tile(self.world, self, self.position, self.potency, DAMAGE_TYPES.POISON)


class HealingMist(TileEffect):

    def on_init(self):
        self.potency = 2
        self.name = "Healing Mist"
        self.description = f"This mist heals living creatures in it for {self.potency} at the start of each turn."
        self.asset_name = "mist"

    def start_of_turn_effect(self):
        if self.world.active_entities[self.position] is not None:
            if ENTITY_TAGS.LIVING in self.world.active_entities[self.position].tags:
                effects.heal(self, self.world.active_entities[self.position], self.potency)


'''
class ShimmeringSprite(pygame.sprite.Sprite):

    def __init__(self, asset, hue, animation_speed=1, hue_range=50):
        super().__init__()

        self.asset_name = "unknown"
        self.asset = asset
        self.base_hue = hue
        self.animation_speed = animation_speed
        self.hue_range = hue_range

        self.rect = self.asset.get_rect()
        self.colourImage = pygame.Surface(self.asset.get_size()).convert_alpha()
        self.frame_counter = 0


    def draw(self, screen_coordinates):
        self.frame_counter += self.animation_speed
        hue_mod = (math.sin(self.frame_counter) * self.hue_range + self.base_hue) % 360 # 360 is the number of hues in hsla colour representation
        colour = pygame.Color(0)
        colour.hsla = (hue_mod, 100, 50, 100)
        self.colourImage.fill(colour)

        self.asset.blit(self.colourImage, screen_coordinates, special_flags=pygame.BLEND_RGBA_MULT)
'''

class ShimmeringSprite(pygame.sprite.Sprite):
    def __init__(self, asset, hue, animation_speed=1, hue_range=50):
        super().__init__()

        self.asset = asset  # Original asset image
        self.base_hue = hue
        self.animation_speed = animation_speed
        self.hue_range = hue_range

        self.image = self.asset.copy()  # Image used for drawing
        self.rect = self.image.get_rect()

        self.colour_image = pygame.Surface(self.asset.get_size(), pygame.SRCALPHA).convert_alpha()
        self.frame_counter = 0

    def update(self):
        """
        Update the sprite's hue variation.
        """
        self.frame_counter += self.animation_speed

        # Compute the dynamic hue based on sine oscillation
        hue_mod = (math.sin(self.frame_counter / 60) * self.hue_range + self.base_hue) % 360

        # Generate a color with the computed hue
        color = pygame.Color(0)
        color.hsla = (hue_mod, 100, 50, 100)

        # Fill the color image with the hue-modified color
        self.colour_image.fill(color)

        # Blend the color image with the original asset
        self.image = self.asset.copy()
        self.image.blit(self.colour_image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    def draw(self, screen, screen_coordinates):
        """
        Draw the sprite at the given screen coordinates.
        """
        self.rect.topleft = screen_coordinates
        screen.blit(self.image, self.rect)
