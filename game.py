import pygame
import sys

from spells import *
from world.world import *
from ui import *
import entities.entities as entities


class Game:
    def __init__(self):
        pygame.init()
        # display = pygame.display.set_mode((800, 600))
        display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.current_display_size = display.get_size()
        #print(f"current_display_size: {current_display_size}")
        pygame.display.set_caption('Wandering Wizard')

        self.root_directory = "assets"
        #self.asset_dict = defaultdict(lambda: "assets/unknown.png")
        self.asset_dict = defaultdict(lambda: None)
        #self.asset_dict = {"unknown": "assets/unknown.png"}
        #self.assets = {"unknown": pygame.image.load("assets/unknown.png").convert_alpha()}
        #self.assets = defaultdict(lambda: self.assets["unknown"])
        self.assets = defaultdict(lambda: None)

        # Hardcoding this to ensure it's loaded by the time anything needs to access this:

        self.load_graphics()

        self.states = defaultdict(lambda : False)

        self.pc = None

        #self.available_spell_list = AvailableSpellList()

        self.world = self.new_game()

        self.available_entities = {
            "Longdead": entities.Longdead,
            "Goblin": entities.Goblin,
            "Troll": entities.Troll,
            "Kindling": entities.Kindling
        }

        self.ui = UI(display, self.world)

        self.world.set_current_active_tiles()

        self.ui.render_everything()

        self.main_loop()



    def new_game(self):
        world = World(self)
        world.assets = self.assets
        self.pc = PC(world)
        self.pc.position = (0, 0)
        self.pc_available_spell_list = PCAvailableSpellList(self.pc)

        # TEMP
        self.pc.actives.append(IronNeedle(self.pc))
        self.pc.actives.append(FireBreath(self.pc))
        self.pc.actives.append(SeismicJolt(self.pc))
        self.pc.actives.append(RaiseLongdead(self.pc))
        self.pc.actives.append(LightningBolt(self.pc))


        #world.active_floor = world.total_floor
        return world

    def main_loop(self):
        while True:
            #for event in pygame.event.get():
            #    if event.type == pygame.QUIT:
            #        pygame.quit()
            #        sys.exit()

            print(f"Start of player turn. Player at coordinates {self.world.current_coordinates}")
            self.player_turn()
            self.side_turn(ALLEGIANCES.PLAYER_TEAM)
            self.side_turn(ALLEGIANCES.ENEMY_TEAM)


    def player_turn(self):
        player_turn_ended = False
        for entity in self.world.active_entities.values():
            if entity is not None:
                if entity.allegiance == ALLEGIANCES.PLAYER_TEAM:
                    entity.start_of_turn()
        while not player_turn_ended:
            #self.graphics.find_tile_at_screen_coords(pygame.mouse.get_pos())
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.ui.left_click = True
                    if event.button == 2:
                        # This is a middle button/scroll wheel click
                        pass
                    if event.button == 3:
                        self.ui.right_click = True
                    if event.button == 4:
                        self.ui.scroll_up = True
                    if event.button == 5:
                        self.ui.scroll_down = True

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a or event.key == pygame.K_KP_4:
                        if self.world.player_step(LEFT):
                            self.pc.current_actions-=1
                    if event.key == pygame.K_w or event.key == pygame.K_KP_8:
                        if self.world.player_step(UP):
                            self.pc.current_actions -= 1
                    if event.key == pygame.K_d or event.key == pygame.K_KP_6:
                        if self.world.player_step(RIGHT):
                            self.pc.current_actions -= 1
                    if event.key == pygame.K_s or event.key == pygame.K_KP_2:
                        if self.world.player_step(DOWN):
                            self.pc.current_actions -= 1
                    if event.key == pygame.K_KP_5:
                            self.pc.current_actions = 0
                    if event.key == pygame.K_KP_7:
                        if self.world.player_step(UP_LEFT):
                            self.pc.current_actions -= 1
                    if event.key == pygame.K_KP_9:
                        if self.world.player_step(UP_RIGHT):
                            self.pc.current_actions -= 1
                    if event.key == pygame.K_KP_1:
                        if self.world.player_step(DOWN_LEFT):
                            self.pc.current_actions -= 1
                    if event.key == pygame.K_KP_3:
                        if self.world.player_step(DOWN_RIGHT):
                            self.pc.current_actions -= 1
                if self.pc.current_actions <= 0:
                    player_turn_ended = True
            self.ui.render_everything()

    def side_turn(self, allegiance):
        #print(f"{allegiance} turn starts.")
        pygame.time.set_timer(EVENT_TYPES.NPC_TURN_START, 20)

        initiative_queue = []

        for entity in self.world.active_entities.values():
            if entity is not None:
                #print(f"Acting entity: {entity.name}")
                #pygame.time.delay(10)
                if entity.allegiance == allegiance and entity is not self.pc:
                    initiative_queue.append(entity)

        random.shuffle(initiative_queue) # Possible to do stuff like "always acts immediately after Wizard" and stuff like that with this.

        while len(initiative_queue) > 0:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == EVENT_TYPES.NPC_TURN_START and len(initiative_queue) > 0:
                    active_entity = initiative_queue.pop()
                    #print(f"{active_enemy.name}'s turn")
                    active_entity.start_of_turn()
                    while active_entity.current_actions > 0:
                        active_entity.act()
                        self.ui.render_everything()
                        pygame.time.delay(5)
                    active_entity.end_of_turn()

            self.ui.render_everything()
        pygame.time.set_timer(EVENT_TYPES.NPC_TURN_START, 0)

        self.ui.render_everything()
        #print(f"{allegiance} turn ended.")




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