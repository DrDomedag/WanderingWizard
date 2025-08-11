import pygame
import sys

from spells import *
from world.world import *
from ui import *
import passives
import entities.entities as entities
from util import *


class Game:
    def __init__(self, display):

        # Debug settings
        self.enemy_spawns_enabled = True
        self.infinite_spells = False
        self.massive_regen = True

        #pygame.init()
        # display = pygame.display.set_mode((800, 600))
        self.display = display
        self.current_display_size = self.display.get_size()
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

        self.pc_available_spell_list = None
        #self.available_spell_list = AvailableSpellList()

        self.world = self.new_game()



        self.available_entities = entities.get_all_entities()


        self.ui = UI(display, self.world)


        self.world.set_current_active_tiles()

        self.ui.render_everything()

        self.main_loop()



    def new_game(self):
        overworld_biome_list = [BIOME_IDS.PLAINS, BIOME_IDS.FOREST, BIOME_IDS.STARTER_BIOME]
        world = World(self, overworld_biome_list)
        world.assets = self.assets
        self.pc = entities.PC(world)
        self.pc.position = (0, 0)
        world.total_entities[(0, 0)] = self.pc  # Dunno why it was so very wonky when I did this earlier, but i'm not going to complain that it works now.

        if self.massive_regen:
            regen = passives.Regeneration(self.pc, self.pc)
            regen.duration = None
            regen.power = 50
            regen.nature = passives.INHERENT
            self.pc.passives.append(regen)

        self.pc_available_spell_list = PCAvailableSpellList(self.pc)

        # TEMP
        irne = IronNeedle(self.pc)
        irne.innovations["Twin Needles"].unlocked = False
        irne.innovations["Iron Storm"].unlocked = False
        irne.innovations["Iron Spear"].unlocked = True
        irne.innovations["Silver Spear"].unlocked = True
        self.pc.actives.append(irne)
        fb = FireBreath(self.pc)
        fb.range = 15
        fb.power = 20
        self.pc.actives.append(fb)
        sj = SeismicJolt(self.pc)
        sj.power = 9
        self.pc.actives.append(sj)
        rl = RaiseLongdead(self.pc)
        rl.minion_count = 5
        rl.minion_damage = 5
        self.pc.actives.append(rl)
        self.pc.actives.append(LightningBolt(self.pc))
        pm = PoisonMist(self.pc)
        pm.power = 3
        self.pc.actives.append(pm)
        tw = TidalWave(self.pc)
        self.pc.actives.append(tw)
        al = ArcaneLesson(self.pc)
        self.pc.actives.append(al)
        fs = Flickerstep(self.pc)
        self.pc.actives.append(fs)


        return world

    def game_over(self):
        print("You lost.")

    def main_loop(self):
        while True:
            #for event in pygame.event.get():
            #    if event.type == pygame.QUIT:
            #        pygame.quit()
            #        sys.exit()

            print(f"Start of player turn. Player at coordinates {self.world.current_coordinates}")
            self.floor_effects()
            self.tile_effects()
            pygame.event.clear() # Clear any old inputs before starting the player's turn.
            self.player_turn()
            self.side_turn(ALLEGIANCES.PLAYER_TEAM)
            self.side_turn(ALLEGIANCES.ENEMY_TEAM)

    def floor_effects(self):
        for floor_tile in self.world.active_floor:
            if self.world.active_floor[floor_tile] is not None:
                self.world.active_floor[floor_tile].on_start_of_turn_effect()

    def tile_effects(self):
        for tile_effect in self.world.active_tile_effects:
            if self.world.active_tile_effects[tile_effect] is not None:
                self.world.active_tile_effects[tile_effect].start_of_turn()

    def check_for_mouse_input(self, event):
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

    def player_turn(self):
        player_turn_ended = False

        self.pc.start_of_turn()
        if self.infinite_spells:
            for active in self.pc.actives:
                active.current_charges = active.max_charges

        while not player_turn_ended:
            #self.graphics.find_tile_at_screen_coords(pygame.mouse.get_pos())
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                self.check_for_mouse_input(event)

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
                        # Add logic here for doing one turn of recovery for a random spell per action used.
                        while self.pc.current_actions > 0:
                            self.pc.current_actions -= 1
                            actives_for_consideration = []
                            for active in self.pc.actives:
                                if active.recovery_turns_left > 0 and active.current_charges < active.max_charges:
                                    actives_for_consideration.append(active)
                            if len(actives_for_consideration) > 0:
                                active = random.choice(actives_for_consideration)
                                active.turn_recovery()

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

        # Make sure only creatures that are currently on active tiles get their turn.
        # Otherwise the game crashes when trying to pathfind.
        self.world.set_current_active_tiles()

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


                # This technically kind of works, but it is very sluggish.
                # It also ends up queuing up commands - the click isn't actually processed until between entity moves.
                # It *also* means that the Wizard can do things like move out of turn at no action cost, so that's bad.
                #self.check_for_mouse_input(event)


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

        # Create a few variations of the allegiance indicator since doing for every enemy turns out to be pretty computationally intense.
        allegiance_indicator_sprite = self.assets["allegiance_indicator"].copy()

        self.assets["enemy_allegiance_indicator"] = tint_sprite(allegiance_indicator_sprite, COLOURS.RED)
        self.assets["ally_allegiance_indicator"] = tint_sprite(allegiance_indicator_sprite, COLOURS.CYAN)
        self.assets["neutral_allegiance_indicator"] = tint_sprite(allegiance_indicator_sprite, COLOURS.GRAY)
        self.assets["other_allegiance_indicator"] = tint_sprite(allegiance_indicator_sprite, COLOURS.MAGENTA)

        #print(f"Loaded {len(self.assets.keys())} images as sprites.")