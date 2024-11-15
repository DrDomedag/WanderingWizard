import util
from passives import *
from spells import *
from effects import *

from collections import defaultdict
from copy import copy

# Allegiances
NEUTRAL = 0
PLAYER_TEAM = 1
ENEMY_TEAM = 2

class Entity:
    def __init__(self, world):
        self.world = world
        self.layer = "entity"
        self.name = "Nameless Entity"
        self.max_hp = 10
        self.hp = self.max_hp
        self.actives = []
        self.passives = []
        self.actionsPerRound = 3
        self.currentActions = 0
        self.stationary = False
        self.allegiance = NEUTRAL
        self.resistances = defaultdict(lambda: 0)
        self.asset = "unknown"
        self.flammable = True
        self.walking = True
        self.flying = False
        self.swimming = False
        self.intangible = False
        self.position = None
        self.owner = None


    def startOfTurn(self):
        self.currentActions = self.actionsPerRound
        for p in self.passives:
            p.startOfTurnEffect()

    def canSee(self, target):
        line_tiles = util.bresenham(self.position, target)
        for coords in line_tiles:
            if self.world.active_walls[coords] is not None and coords != target:
                return False
        return True



class PC(Entity):
    def __init__(self, world):
        super().__init__(world)
        self.name = "Wizard"
        self.max_hp = 50
        self.hp = self.max_hp
        self.allegiance = PLAYER_TEAM
        self.asset = "wizard"

class Troll(Entity):
    def __init__(self, world):
        super().__init__(world)
        self.name = "Troll"
        self.max_hp = 30
        self.hp = self.max_hp
        self.passives.append(TrollRegen())
        self.asset = "troll"

class Goblin(Entity):
    def __init__(self, world):
        super().__init__(world)
        self.name = "Goblin"
        self.max_hp = 5
        self.hp = self.max_hp
        self.asset = "goblin"