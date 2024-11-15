import pygame
import sys
from world.world import *
from graphics import *
from entities import *


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

        self.world.set_current_active_tiles()

        self.graphics.render_everything()

        self.main_loop()

    def new_game(self):
        world = World()
        self.pc = PC(world)
        world.pc = self.pc
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
        for entity in self.world.active_entities.values():
            if entity is not None:
                if entity.allegiance == PLAYER_TEAM:
                    entity.startOfTurn()
        self.pc.currentActions = self.pc.actionsPerRound
        while not player_turn_ended:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a or event.key == pygame.K_KP_4:
                        print("A pressed")
                        if self.world.player_step(LEFT):
                            self.pc.currentActions-=1
                    if event.key == pygame.K_w or event.key == pygame.K_KP_8:
                        print("W pressed")
                        if self.world.player_step(UP):
                            self.pc.currentActions -= 1
                    if event.key == pygame.K_d or event.key == pygame.K_KP_6:
                        print("D pressed")
                        if self.world.player_step(RIGHT):
                            self.pc.currentActions -= 1
                    if event.key == pygame.K_s or event.key == pygame.K_KP_2:
                        print("S pressed")
                        if self.world.player_step(DOWN):
                            self.pc.currentActions -= 1
                    if event.key == pygame.K_KP_7:
                        print("S pressed")
                        if self.world.player_step(UP_LEFT):
                            self.pc.currentActions -= 1
                    if event.key == pygame.K_KP_9:
                        print("S pressed")
                        if self.world.player_step(UP_RIGHT):
                            self.pc.currentActions -= 1
                    if event.key == pygame.K_KP_1:
                        print("S pressed")
                        if self.world.player_step(DOWN_LEFT):
                            self.pc.currentActions -= 1
                    if event.key == pygame.K_KP_3:
                        print("S pressed")
                        if self.world.player_step(DOWN_RIGHT):
                            self.pc.currentActions -= 1
                if self.pc.currentActions <= 0:
                    player_turn_ended = True
                self.graphics.render_everything()

    def enemy_turn(self):
        print("The enemy does nothing during their turn.")