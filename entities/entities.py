import ui
import util
import random
from collections import defaultdict

from passives import *
from spells import *
from effects import *



class Entity:
    def __init__(self, world):
        self.world = world

        self.asset_name = "unknown"
        self.asset = world.assets[self.asset_name]
        self.idle_asset = [self.asset]
        self.acting_asset = [self.asset]
        self.current_frame = 0
        self.animation_frames = 30
        self.asset_index = 0

        self.layer = "entity"

        self.name = "Nameless Entity"
        self.max_hp = 10
        self.hp = self.max_hp
        self.actives = []
        self.passives = []
        self.actions_per_round = 3
        self.current_actions = 0
        self.allegiance = ALLEGIANCES.NEUTRAL
        self.resistances = defaultdict(lambda: 0)

        self.stationary = False
        self.flammable = True
        self.walking = True
        self.flying = False
        self.swimming = False
        self.intangible = False
        self.position = None
        self.owner = None



    def load_assets(self):
        i = 1
        if self.world.assets[f"{self.asset_name}_idle_{i}"]:
            self.idle_asset = []
            while self.world.assets[f"{self.asset_name}_idle_{i}"]:
                self.idle_asset.append(self.world.assets[f"{self.asset_name}_idle_{i}"])
                i += 1
        i = 1
        if self.world.assets[f"{self.asset_name}_acting_{i}"]:
            self.acting_asset = []
            while self.world.assets[f"{self.asset_name}_acting_{i}"]:
                self.acting_asset.append(self.world.assets[f"{self.asset_name}_acting_{i}"])
                i += 1


    def draw(self, display, screen_coords):

        self.current_frame += 1
        # If idle. Similar logic for if acted later.
        if self.current_frame >= self.animation_frames:
            self.current_frame = 0
            self.asset_index = (self.asset_index + 1) % len(self.idle_asset)
            self.asset = self.idle_asset[self.asset_index]

        # print(f"Rendering {entity.name} at game coords: {entity_coords}, self-registered coords: {entity.position} screen-centered x: {(entity_coords[0] - self.world.current_coordinates[0])}, screen x: {self.SPRITE_SIZE * (entity_coords[0] - self.world.current_coordinates[0]) + self.centre_x}, screen-centered y: {(entity_coords[1] - self.world.current_coordinates[1]) + self.centre_y}, screen y: {self.SPRITE_SIZE * (entity_coords[1] - self.world.current_coordinates[1]) + self.centre_y}")
        display.blit(self.asset, screen_coords)

    def start_of_turn(self):
        #print(f"{self.name}'s turn started.")
        self.current_actions = self.actions_per_round
        for active in self.actives:
            if active.current_charges < active.max_charges:
                active.recovery_turns_left -= 1
                if active.recovery_turns_left <= 0 and active.current_charges < active.max_charges:
                    active.current_charges += 1
                    active.recovery_turns_left = active.recovery_time
        for p in self.passives:
            p.start_of_turn_effect()

    def can_see(self, target):
        line_tiles = util.bresenham(self.position, target)
        for coords in line_tiles:
            if self.world.active_walls[coords] is not None and coords != target:
                return False
        return True

    def can_move(self, target):
        return self.world.check_can_move(self, target)

    def can_be_pushed(self, target):
        return self.world.check_can_be_pushed(self, target)

    def move(self, target):
        return self.world.move_entity(self, target)

    def on_suffer_damage(self, source, amount, type):
        #print(f"{self.name} took {amount} damage from {source.name}.")
        for passive in self.passives:
            passive.on_suffer_damage_effect(source, amount, type)
        if self.hp <= 0:
            self.die()

    def on_death(self):
        for passive in self.passives:
            passive.on_death_effect()

    def die(self):
        print(f"{self.name} died!")
        self.world.total_entities[self.position] = None
        self.world.active_entities[self.position] = None
        self.on_death()
        del self


    def act(self):
        #print(self.actives)
        actives = random.sample(self.actives, len(self.actives))
        actives.sort(key=lambda spell: Spell.level)
        #print(actives)


class PC(Entity):
    def __init__(self, world):
        super().__init__(world)
        self.name = "Wizard"
        self.max_hp = 50
        self.hp = self.max_hp
        self.allegiance = ALLEGIANCES.PLAYER_TEAM
        self.asset_name = "wizard"
        self.load_assets()
        self.current_actions = self.actions_per_round

    def move(self, target):
        return self.world.move_player(target)

class Troll(Entity):
    def __init__(self, world):
        super().__init__(world)
        self.name = "Troll"
        self.max_hp = 30
        self.hp = self.max_hp
        self.passives.append(TrollRegen(self, self))
        self.asset_name = "troll"
        self.load_assets()
        self.actives.append(BluntMeleeAttack(self))

class Goblin(Entity):
    def __init__(self, world):
        super().__init__(world)
        self.name = "Goblin"
        self.max_hp = 5
        self.hp = self.max_hp
        self.asset_name = "goblin"
        self.load_assets()
        self.actives.append(PiercingMeleeAttack(self))
