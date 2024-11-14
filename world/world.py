from entities.entities import *
from entities.entities import PC
from collections import defaultdict
from effects import *
import random
#import util
import math
#from main import *


class World:
    def __init__(self, pc):
        self.total_floor = defaultdict(lambda: None)
        self.total_walls = defaultdict(lambda: None)
        self.total_entities = defaultdict(lambda: None)
        self.total_tile_effects = defaultdict(lambda: None)
        self.active_floor = defaultdict(lambda: None)
        self.active_walls = defaultdict(lambda: None)
        self.active_entities = defaultdict(lambda: None)
        self.active_tile_effects = defaultdict(lambda: None)
        self.pc = pc
        self.active_tile_range = 30 # Consider setting to a greater number later
        self.current_coordinates = (0, 0)


    def __setitem__(self, key, value):
        #base_class = util.get_top_parent(value)
        # isinstance(value, Entity): doesn't work
        if value.layer == "floor":
            self.total_floor[key] = value
            if key in self.active_floor.keys():
                self.active_floor[key] = value
        elif value.layer == "wall":
            self.total_walls[key] = value
            if key in self.active_walls.keys():
                self.active_walls[key] = value
        elif value.layer == "entity":
            self.total_entities[key] = value
            if key in self.active_entities.keys():
                self.active_entities[key] = value
        elif value.layer == "tile_effect":
            self.total_tile_effects[key] = value
            if key in self.active_tile_effects.keys():
                self.active_tile_effects[key] = value
        else:
            print(value.__class__.mro())
            print("Trying to assign a non-tile, non-entity, non-tile-effect to map.")
            raise RuntimeError

    def createDefaultMap(self):
        for x in range(-10, 10, 1):
            for y in range(-10, 10, 1):
                self[(x, y)] = FloorTile()
                if random.random() > 0.9:
                    self[(x, y)] = StoneWall()


    def euclidean_distance(self, a, b):
        return math.sqrt(math.pow(a[0] - b[0], 2) + math.pow(a[1] - b[1], 2))

    def manhattan_distance(self, a, b):
        return(abs(a[0] - b[0]) + abs(a[1] - b[1]))

    def chebyshev_distance(self, a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def check_can_move(self, entity, target):
        if self.active_entities[target] is not None:
            print(f"{entity.name} could not move because {self.active_entities[target].name} blocked the way.")
            return False # Change down the line to allow PC to walk into ally spaces.
        if self.active_walls[target] is not None and not entity.intangible:
            print(f"Could not move because a wall blocked the way and {entity.name} is not intangible.")
            return False
        if self.active_floor[target].walkable and entity.walking:
            print(f"{entity.name} could move because it can walk and the target tile is walkable.")
            return True
        if self.active_floor[target].flyable and entity.flying:
            print(f"{entity.name} could move because it can fly and the target tile is flyable.")
            return True
        if self.active_floor[target].swimmable and entity.swimming:
            print(f"{entity.name} could move because it can swim and the target tile is swimmable.")
            return True

        print(f"{entity.name} could not because it has no movement type appropriate for the tile.")
        return False


    def move_player_left(self):
        return self.move_player((self.current_coordinates[0] - 1, self.current_coordinates[1]))

    def move_player_right(self):
        return self.move_player((self.current_coordinates[0] + 1, self.current_coordinates[1]))

    def move_player_up(self):
        return self.move_player((self.current_coordinates[0], self.current_coordinates[1] - 1))

    def move_player_down(self):
        return self.move_player((self.current_coordinates[0], self.current_coordinates[1] + 1))

    def move_player(self, target):
        print(f"Attempting to move from {self.current_coordinates} to {target}")
        if self.move_entity(self.pc, target):
            self.current_coordinates = target
            self.set_current_active_tiles()
            return True
        return False


    def set_current_active_tiles(self):
        self.active_walls = defaultdict(lambda: None)
        self.active_floor = defaultdict(lambda: None)
        self.active_entities = defaultdict(lambda: None)

        for x in range(self.current_coordinates[0] - self.active_tile_range,
                       self.current_coordinates[0] + self.active_tile_range):
            for y in range(self.current_coordinates[1] - self.active_tile_range,
                           self.current_coordinates[0] + self.active_tile_range):
                coords = (x, y)
                if coords not in self.total_floor.keys():
                    if self.total_floor[coords] is None:
                        floor = self.generate_floor_tile()
                        self.total_floor[coords] = floor
                    if self.total_walls[coords] is None:
                        wall = self.generate_wall_tile()
                        if wall is not None:
                            self.total_walls[coords] = wall
                            wall.position = coords
                    if self.total_entities[coords] is None:
                        enemy = self.generate_enemy()
                        if enemy is not None:
                            self.total_entities[coords] = enemy
                            enemy.position = coords
                if self.chebyshev_distance(coords, self.current_coordinates) < self.active_tile_range:
                    self.active_floor[coords] = self.total_floor[coords]
                    self.active_walls[coords] = self.total_walls[coords]
                    self.active_entities[coords] = self.total_entities[coords]


    def move_entity(self, entity, target):
        if self.check_can_move(entity, target):
            self.active_entities[entity.position] = None
            self.total_entities[entity.position] = None
            self.active_entities[target] = entity
            self.total_entities[target] = entity
            entity.position = target
            return True
        else:
            return False

    def generate_floor_tile(self):
        if random.random() < 0.9:
            return FloorTile()
        else:
            return WaterTile()

    def generate_wall_tile(self):
        if random.random() < 0.9:
            return None
        else:
            return StoneWall()

    def generate_enemy(self):
        if random.random() < 0.95:
            return None
        else:
            return Goblin()

class Tile:
    def __init__(self):
        self.layer = "floor"
        self.name = "Floor"
        self.walkable = True
        self.flyable = True
        self.swimmable = False
        self.flammable = False
        self.onEnterEffects = []
        self.onTurnStartEffects = []
        self.onTurnEndEffects = []
        self.asset = "unknown"

class FloorTile(Tile):
    def __init__(self):
        super(FloorTile, self).__init__()
        self.name = "Floor"
        self.asset = "dirt_tile"

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
        self.asset = "water_tile"
        self.walkable = False
        self.swimmable = True

class ChasmTile(Tile):
    def __init__(self):
        super().__init__()
        self.name = "Chasm"
        self.walkable = False
        self.swimmable = False

class Wall(Entity):
    def __init__(self):
        super().__init__()
        self.layer = "wall"
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
        self.asset = "stone_wall"
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
        self.asset = "wood_wall"
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


