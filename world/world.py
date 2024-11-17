from entities.entities import *
from entities.entities import PC
from collections import defaultdict
from effects import *
import random
#import util
import math
#from main import *

UP_LEFT = 7
UP = 8
UP_RIGHT = 9
LEFT = 4
WAIT = 5
RIGHT = 6
DOWN_LEFT = 1
DOWN = 2
DOWN_RIGHT = 3

class World:
    def __init__(self):
        self.total_floor = defaultdict(lambda: None)
        self.total_walls = defaultdict(lambda: None)
        self.total_entities = defaultdict(lambda: None)
        self.total_tile_effects = defaultdict(lambda: None)
        self.total_items = defaultdict(lambda: None)
        self.active_floor = defaultdict(lambda: None)
        self.active_walls = defaultdict(lambda: None)
        self.active_entities = defaultdict(lambda: None)
        self.active_tile_effects = defaultdict(lambda: None)
        self.active_items = defaultdict(lambda: None)
        self.pc = None
        self.assets = None
        self.active_tile_range = 30 # Consider changing
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
                #if random.random() > 0.9:
                    #self[(x, y)] = StoneWall()
        #self.total_entities[self.current_coordinates] = self.pc
        #self.active_entities[(0, 0)] = self.pc



    def euclidean_distance(self, a, b):
        return math.floor(math.sqrt(math.pow(a[0] - b[0], 2) + math.pow(a[1] - b[1], 2)))

    def manhattan_distance(self, a, b):
        return(abs(a[0] - b[0]) + abs(a[1] - b[1]))

    def chebyshev_distance(self, a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def check_can_move(self, entity, target):
        if self.active_entities[target] is not None:
            #print(f"{entity.name} could not move because {self.active_entities[target].name} blocked the way.")
            return False # Change down the line to allow PC to walk into ally spaces.
        if self.active_walls[target] is not None and not entity.intangible:
            #print(f"Could not move because a wall blocked the way and {entity.name} is not intangible.")
            return False
        if self.active_floor[target].walkable and entity.walking:
            #print(f"{entity.name} could move because it can walk and the target tile is walkable.")
            return True
        if self.active_floor[target].flyable and entity.flying:
            #print(f"{entity.name} could move because it can fly and the target tile is flyable.")
            return True
        if self.active_floor[target].swimmable and entity.swimming:
            #print(f"{entity.name} could move because it can swim and the target tile is swimmable.")
            return True

        #print(f"{entity.name} could not because it has no movement type appropriate for the tile.")
        return False

    def player_step(self, direction):
        if direction == UP_LEFT:
            return self.move_player((self.current_coordinates[0] - 1, self.current_coordinates[1] - 1))
        if direction == UP:
            return self.move_player((self.current_coordinates[0], self.current_coordinates[1] - 1))
        if direction == UP_RIGHT:
            return self.move_player((self.current_coordinates[0] + 1, self.current_coordinates[1] - 1))
        if direction == LEFT:
            return self.move_player((self.current_coordinates[0] - 1, self.current_coordinates[1]))
        if direction == RIGHT:
            return self.move_player((self.current_coordinates[0] + 1, self.current_coordinates[1]))
        if direction == DOWN_LEFT:
            return self.move_player((self.current_coordinates[0] - 1, self.current_coordinates[1] + 1))
        if direction == DOWN:
            return self.move_player((self.current_coordinates[0], self.current_coordinates[1] + 1))
        if direction == DOWN_RIGHT:
            return self.move_player((self.current_coordinates[0] + 1, self.current_coordinates[1] + 1))


    def move_player(self, target):
        #print(f"Attempting to move from {self.current_coordinates} to {target}")
        if self.move_entity(self.pc, target):
            self.current_coordinates = target
            self.set_current_active_tiles()
            return True
        return False


    def set_current_active_tiles(self):
        self.active_walls = defaultdict(lambda: None)
        self.active_floor = defaultdict(lambda: None)
        self.active_entities = defaultdict(lambda: None)

        generated_tiles = 0

        for x in range(self.current_coordinates[0] - self.active_tile_range,
                       self.current_coordinates[0] + self.active_tile_range):
            for y in range(self.current_coordinates[1] - self.active_tile_range,
                           self.current_coordinates[1] + self.active_tile_range):
                coords = (x, y)
                if coords not in self.total_floor.keys():
                    if self.total_floor[coords] is None:
                        generated_tiles += 1
                        floor = self.generate_floor_tile()
                        self.total_floor[coords] = floor
                    if self.total_walls[coords] is None:
                        wall = self.generate_wall_tile()
                        if wall is not None:
                            self.total_walls[coords] = wall
                            wall.position = coords
                    if self.total_entities[coords] is None and self.total_walls[coords] is None:
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
            return StoneWall(self)

    def generate_enemy(self):
        if random.random() < 0.98:
            return None
        else:
            enemy = Goblin(self)
            enemy.allegiance = ALLEGIANCES.ENEMY_TEAM
            return enemy

    def can_see(self, x, y):
        line_tiles = util.bresenham(x, y)
        if x == y:
            return True
        for coords in line_tiles:
            if self.active_walls[coords] is not None and coords != y:
                return False
        return True

    def get_visible_tiles(self, target):
        visible_tiles = []
        for tile in self.active_floor.keys():
            if self.can_see(target, tile):
                visible_tiles.append(tile)
        return visible_tiles

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
        self.type = "solid"
        self.asset = "dirt_tile"

class LavaTile(Tile):
    def __init__(self):
        super().__init__()
        self.name = "Lava"
        self.type = "liquid"
        self.walkable = False
        self.swimmable = True
        #self.onEnterEffects.append() Deal fire damage

class WaterTile(Tile):
    def __init__(self):
        super().__init__()
        self.name = "Water"
        self.type = "liquid"
        self.asset = "water_tile"
        self.walkable = False
        self.swimmable = True

class ChasmTile(Tile):
    def __init__(self):
        super().__init__()
        self.name = "Chasm"
        self.type = "void"
        self.walkable = False
        self.swimmable = False

class Wall(Entity):
    def __init__(self, world):
        super().__init__(world)
        self.layer = "wall"
        self.name = "Wall"
        self.walkable = False
        self.hp = 50
        self.actionsPerRound = 0
        self.stationary = True



class StoneWall(Wall):
    def __init__(self, world):
        super().__init__(world)
        self.name = "Stone Wall"
        self.hp = 100
        self.asset = "stone_wall"
        self.flammable = False
        self.resistances[DAMAGE_TYPES.BLUDGEONING] = 75
        self.resistances[DAMAGE_TYPES.PIERCING] = 90
        self.resistances[DAMAGE_TYPES.SLASHING] = 90
        self.resistances[DAMAGE_TYPES.FIRE] = 100
        self.resistances[DAMAGE_TYPES.COLD] = 100
        self.resistances[DAMAGE_TYPES.LIGHTNING] = 80
        self.resistances[DAMAGE_TYPES.POISON] = 100
        self.resistances[DAMAGE_TYPES.DARK] = 80
        self.resistances[DAMAGE_TYPES.LIGHT] = 80
        self.resistances[DAMAGE_TYPES.PSYCHIC] = 100
        self.resistances[DAMAGE_TYPES.ARCANE] = 50


class WoodWall(Wall):
    def __init__(self, world):
        super().__init__(world)
        self.name = "Wooden Wall"
        self.hp = 50
        self.asset = "wood_wall"
        self.resistances[DAMAGE_TYPES.BLUDGEONING] = 75
        self.resistances[DAMAGE_TYPES.PIERCING] = 90
        self.resistances[DAMAGE_TYPES.SLASHING] = 50
        self.resistances[DAMAGE_TYPES.FIRE] = 0
        self.resistances[DAMAGE_TYPES.COLD] = 100
        self.resistances[DAMAGE_TYPES.LIGHTNING] = 50
        self.resistances[DAMAGE_TYPES.POISON] = 100
        self.resistances[DAMAGE_TYPES.DARK] = 50
        self.resistances[DAMAGE_TYPES.LIGHT] = 80
        self.resistances[DAMAGE_TYPES.PSYCHIC] = 100
        self.resistances[DAMAGE_TYPES.ARCANE] = 50


