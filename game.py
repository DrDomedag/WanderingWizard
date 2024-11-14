import pygame
import sys
from world.world import *
from graphics import *


class Game:
    def __init__(self):
        pygame.init()
        # display = pygame.display.set_mode((800, 600))
        display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.current_display_size = display.get_size()
        #print(f"current_display_size: {current_display_size}")
        pygame.display.set_caption('Wandering Wizard')

        self.pc = None

        self.world = self.new_game()

        self.graphics = GraphicsHandler(display, self.world)

        self.graphics.render_everything()

        self.main_loop()

    def new_game(self):
        self.pc = PC()
        world = World(self.pc)
        world.createDefaultMap()

        world.active_floor = world.total_floor
        return world

    def main_loop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            print(f"Start of player turn. Player at coordinates {self.world.current_coordinates}")
            self.player_turn()
            self.enemy_turn()


    def player_turn(self):
        player_turn_ended = False
        self.pc.currentActions = self.pc.actionsPerRound
        while not player_turn_ended:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        print("A pressed")
                        if self.world.move_player_left():
                            self.pc.currentActions-=1
                    if event.key == pygame.K_w:
                        print("W pressed")
                        if self.world.move_player_up():
                            self.pc.currentActions -= 1
                    if event.key == pygame.K_d:
                        print("D pressed")
                        if self.world.move_player_right():
                            self.pc.currentActions -= 1
                    if event.key == pygame.K_s:
                        print("S pressed")
                        if self.world.move_player_down():
                            self.pc.currentActions -= 1
                if self.pc.currentActions <= 0:
                    player_turn_ended = True
                self.graphics.render_everything()

    def enemy_turn(self):
        print("The enemy does nothing during their turn.")