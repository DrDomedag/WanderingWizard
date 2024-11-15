import util
from passives import *
from spells import *
from effects import *

from collections import defaultdict





class Entity:
    def __init__(self, world):
        self.world = world
        self.layer = "entity"
        self.name = "Nameless Entity"
        self.max_hp = 10
        self.hp = self.max_hp
        self.actives = []
        self.passives = []
        self.actions_per_round = 3
        self.current_actions = 0
        self.stationary = False
        self.allegiance = ALLEGIANCES.NEUTRAL
        self.resistances = defaultdict(lambda: 0)
        self.asset = "unknown"
        self.flammable = True
        self.walking = True
        self.flying = False
        self.swimming = False
        self.intangible = False
        self.position = None
        self.owner = None


    def start_of_turn(self):
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

    def on_suffer_damage(self, source, amount, type):
        print(f"{self.name} took {amount} damage from {source.name}.")
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


class PC(Entity):
    def __init__(self, world):
        super().__init__(world)
        self.name = "Wizard"
        self.max_hp = 50
        self.hp = self.max_hp
        self.allegiance = ALLEGIANCES.PLAYER_TEAM
        self.asset = "wizard"
        # TEMP
        self.actives.append(IronNeedle(self))

class Troll(Entity):
    def __init__(self, world):
        super().__init__(world)
        self.name = "Troll"
        self.max_hp = 30
        self.hp = self.max_hp
        self.passives.append(TrollRegen())
        self.asset = "troll"
        self.actives.append(BluntMeleeAttack(world))

class Goblin(Entity):
    def __init__(self, world):
        super().__init__(world)
        self.name = "Goblin"
        self.max_hp = 5
        self.hp = self.max_hp
        self.asset = "goblin"
        self.actives.append(PiercingMeleeAttack(world))