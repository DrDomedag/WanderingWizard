from entities.entities import *
import random

class Map:
    def __init__(self):
        self.floor = {}
        self.entities = {}
        self.createDefaultMap()

    def createDefaultMap(self):
        for x in range(-10, 10, 1):
            for y in range(-10, 10, 1):
                if random.random() > 0.1:
                    self.floor[(x, y)] = FloorTile()
                else:
                    self.floor[(x, y)] = WoodWall()


class Tile:
    def __init__(self):
        self.name = "Floor"
        self.walkable = True
        self.flyable = True
        self.swimmable = False
        self.onEnterEffects = []
        self.onTurnStartEffects = []
        self.onTurnEndEffects = []

class FloorTile(Tile):
    def __init__(self):
        super(FloorTile, self).__init__()
        self.name = "Floor"


class LavaTile(Tile):
    def __init__(self):
        super().__init__()
        self.name = "Lava"
        self.walkable = False
        self.swimmable = True
        #self.onEnterEffects.append() Deal fire damage

class WaterTile(Tile):
    def __init__(self):
        super().__init__()
        self.name = "Water"
        self.walkable = False
        self.swimmable = True

class Wall(entity):
    def __init__(self):
        super().__init__()
        self.name = "Wall"
        self.walkable = False
        self.hp = 50
        self.actionsPerRound = 0
        self.stationary = True

class StoneWall(Wall):
    def __init__(self):
        super().__init__()
        self.name = "Stone Wall"
        self.hp = 100

class WoodWall(Wall):
    def __init__(self):
        super().__init__()
        self.name = "Wooden Wall"
        self.hp = 50

