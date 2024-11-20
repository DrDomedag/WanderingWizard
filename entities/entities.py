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
        acted = False
        #print(self.actives)
        actives = random.sample(self.actives, len(self.actives))
        actives.sort(key=lambda spell: Spell.level)
        for active in actives:
            if active.should_cast():
                print(f"Should cast {active.name}.")
            else:
                print(f"Shouldn't cast {active.name}")
                actives.remove(active)
        if len(actives) > 0:
            self.use_active(actives[0])
            '''
            # TEMP
            acted = True
            self.current_actions -= 1
            pass
            '''
        # If we can't meaningfully use any of our abilities, we move towards the closest enemy.
        enemies = find_and_sort_enemies_by_distance(self)
        while len(enemies) > 0 and not acted:
            # Move
            target = enemies.pop()
            path = util.find_path(self, target.position)
            if len(path) > 0:
                self.move(path[1])
                self.current_actions -= 1
                acted = True

        if acted == False:
            # If we can't use any abilities and we can't move towards our closest enemy, we just freeze.
            # We should really improve this by going down the list of enemies instead.
            self.current_actions -= 1


    def use_active(self, active):
        if active.should_target_self:
            active.cast(self.position)
            return
        if active.should_target_allies:
            targets = []
            for entity in active.caster.world.active_entities.values:
                if entity is not None:
                    if entity.allegiance == active.caster.allegiance:
                        if active.can_cast(entity.position):
                            targets.append(entity.position)
            if len(targets) > 0:
                target = random.choice(targets)
                active.cast(target)
                return
        if active.should_target_empty:
            targets = []
            for target in active.caster.world.active_floor.keys():
                if active.caster.world.active_entities[target] is None:
                    if active.can_cast(target):
                        targets.append(target)
            if len(targets) > 0:
                target = random.choice(targets)
                active.cast(target)
                return

        targets = []
        for entity in active.caster.world.active_entities.values():
            if entity is not None:
                if entity.allegiance != active.caster.allegiance and entity.allegiance != ALLEGIANCES.NEUTRAL:
                    if active.can_cast(entity.position):
                        targets.append(entity.position)
        target = random.choice(targets)
        active.cast(target)
        return


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
