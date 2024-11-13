from entities.entities import *
from entities.pc import *
from world.world import *
import graphics
import pygame
import sys

def init_game():
    world = World()
    world.createDefaultMap()
    for key in world.floor.keys():
        display.blit(world.floor[key].asset, key)
    return world

def main_loop():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # checking if key "A" was pressed
                if event.key == pygame.K_a:
                    print("Key A has been pressed")
                print("A key has been pressed")



# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    pygame.init()
    display = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('image')

    graphics.load_graphics()

    world = init_game()

    graphics.render_everything(world, display)

    main_loop()


