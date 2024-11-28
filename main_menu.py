import pygame
import sys
from util import *
from game import Game
from functools import partial

# Actions for the buttons
def start_new_game(display):
    game = Game(display)

def exit_game():
    print("Exiting game!")
    pygame.quit()
    sys.exit()


class MainMenu:
    def __init__(self):
        pygame.init()


        #self.display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.display = pygame.display.set_mode((0,0))
        self.current_display_size = self.display.get_size()
        pygame.display.set_caption('Wandering Wizard')

        # CHANGE THIS for sure
        self.font_32 = pygame.font.Font('PixelatedEleganceRegular.ttf', 32)
        self.font_20 = pygame.font.Font('PixelatedEleganceRegular.ttf', 20)
        self.font_14 = pygame.font.Font('PixelatedEleganceRegular.ttf', 14)
        # font = pygame.font.Font('PublicPixel.ttf', 32)

        self.centre_x = int(self.display.get_size()[0] / 2)
        self.centre_y = int(self.display.get_size()[1] / 2)
        #self.vertical_offset = 0

        button_width = 400
        button_height = 100
        font = self.font_20


        new_game_button = Button(
            text="New Game",
            x=self.current_display_size[0] // 2 - button_width // 2,
            y=self.current_display_size[1] // 2 - 120,
            width=button_width,
            height=button_height,
            font=font,
            base_color=COLOURS.GRAY,
            hover_color=COLOURS.YELLOW,
            action=partial(start_new_game, self.display)
        )

        exit_game_button = Button(
            text="Exit Game",
            x=self.current_display_size[0] // 2 - button_width // 2,
            y=self.current_display_size[1] // 2 + 20,
            width=button_width,
            height=button_height,
            font=font,
            base_color=COLOURS.GRAY,
            hover_color=COLOURS.YELLOW,
            action=exit_game
        )

        self.buttons = [new_game_button, exit_game_button]

        self.main_menu_loop()

    def new_game(self):
        print("New game button pressed!")

    def main_menu_loop(self):
        while True:
            self.display.fill(COLOURS.BLACK)
            for button in self.buttons:
                button.draw(self.display)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                for button in self.buttons:
                    button.check_click(event)
            pygame.display.flip()

class Button:
    """
    A class to create and manage buttons.
    """
    def __init__(self, text, x, y, width, height, font, base_color, hover_color, action=None):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color
        self.action = action

    def draw(self, surface):
        """
        Draw the button on the screen, with hover effect.
        """
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.base_color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, COLOURS.BLACK, self.rect, 3, border_radius=10)  # Border

        # Render text and center it within the button
        label = self.font.render(self.text, True, COLOURS.BLACK)
        label_rect = label.get_rect(center=self.rect.center)
        surface.blit(label, label_rect)

    def check_click(self, event):
        """
        Check if the button is clicked and trigger its action.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
            if self.rect.collidepoint(event.pos) and self.action:
                self.action()


