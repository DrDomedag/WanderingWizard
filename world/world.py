from entities.entities import *
import random
import util
from main import *


class World:
    def __init__(self):
        self.floor = {}
        self.entities = {}
        self.createDefaultMap()
        self.current_coordinates = (0, 0)

    def __setitem__(self, key, value):
        base_class = util.get_top_parent(value)
        # isinstance(value, Entity): doesn't work
        if str(base_class) == str(Tile):
            self.entities[key] = value
        elif str(base_class) == str(Entity):
            self.floor[key] = value
        else:
            print(value.__class__.mro())
            print("Trying to assign a non-tile, non-entity to map.")
            print(Entity)
            print(base_class)
            raise RuntimeError

    def createDefaultMap(self):
        for x in range(-10, 10, 1):
            for y in range(-10, 10, 1):
                self[(x, y)] = FloorTile()
                if random.random() > 0.9:
                    self[(x, y)] = WoodWall()



    def calculate_distance(self, a, b):
        return math.sqrt(math.pow(a[0] - b[0], 2) + math.pow(a[1] - b[1], 2))

    def calculate_manhattan_distance(self, a, b):
        return(abs(a[0] - b[0]) + abs(a[1] - b[1]))

class Tile:
    def __init__(self):
        self.name = "Floor"
        self.walkable = True
        self.flyable = True
        self.swimmable = False
        self.flammable = False
        self.onEnterEffects = []
        self.onTurnStartEffects = []
        self.onTurnEndEffects = []
        self.asset = assets["unknown"]

class FloorTile(Tile):
    def __init__(self):
        super(FloorTile, self).__init__()
        self.name = "Floor"
        self.asset = assets["dirt_tile"]

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

class Wall(Entity):
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
        self.asset = assets["stone_wall"]
        self.flammable = False
        self.resistances[BLUDGEONING] = 75
        self.resistances[PIERCING] = 90
        self.resistances[SLASHING] = 90
        self.resistances[FIRE] = 100
        self.resistances[COLD] = 100
        self.resistances[LIGHTNING] = 80
        self.resistances[POISON] = 100
        self.resistances[DARK] = 80
        self.resistances[LIGHT] = 80
        self.resistances[PSYCHIC] = 100
        self.resistances[MYSTIC] = 50


class WoodWall(Wall):
    def __init__(self):
        super().__init__()
        self.name = "Wooden Wall"
        self.hp = 50
        self.asset = assets["wood_wall"]
        self.resistances[BLUDGEONING] = 75
        self.resistances[PIERCING] = 90
        self.resistances[SLASHING] = 50
        self.resistances[FIRE] = 0
        self.resistances[COLD] = 100
        self.resistances[LIGHTNING] = 50
        self.resistances[POISON] = 100
        self.resistances[DARK] = 50
        self.resistances[LIGHT] = 80
        self.resistances[PSYCHIC] = 100
        self.resistances[MYSTIC] = 50


