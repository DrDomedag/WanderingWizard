from passives import *
from actives import *
from effects import *
from graphics import assets
from collections import defaultdict

# Allegiances
NEUTRAL = 0
PLAYER_TEAM = 1
ENEMY_TEAM = 2

class Entity:
    def __init__(self):
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
        self.asset = assets["unknown"]
        self.flammable = True



class PC(Entity):
    def __init__(self):
        super().__init__()
        self.name = "Wizard"
        self.max_hp = 50
        self.hp = self.max_hp
        self.allegiance = PLAYER_TEAM
        self.asset = assets["wizard"]

class Troll(Entity):
    def __init__(self):
        super().__init__()
        self.name = "Troll"
        self.max_hp = 30
        self.hp = self.max_hp
        self.passives.append(TrollRegen())
        self.asset = assets["troll"]
