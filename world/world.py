import entities.entities as entities
from collections import defaultdict
import effects
import random

import util
from util import *
import math
#from main import *
import items
from world_generator import WorldGenerator

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
    def __init__(self, game, biome_list):
        self.game = game
        self.world_generator = WorldGenerator(self, biome_list)
        #self.total_tiles = defaultdict(lambda: None)
        #self.active_tiles = defaultdict(lambda: None)
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
        self.has_seen = defaultdict(lambda: False)
        self.active_tile_range = 30 # Consider changing
        self.current_coordinates = (0, 0)
        self.effect_queue = []



    def show_effect(self, target, effect_type, delay):
        self.effect_queue.append((None, target, effect_type, delay))

    def show_projectile(self, origin, target, projectile_type, delay):
        self.effect_queue.append((origin, target, projectile_type, delay))

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
            self.active_entities[key] = value
            if key in self.active_entities.keys():
                self.active_entities[key] = value
        elif value.layer == "tile_effect":
            self.total_tile_effects[key] = value
            if key in self.active_tile_effects.keys():
                self.total_tile_effects[key] = value
        elif value.layer == "item":
            self.total_items[key] = value
            if key in self.total_items.keys():
                self.active_items[key] = value
        else:
            print(value.__class__.mro())
            print("Trying to assign a non-tile, non-entity, non-item, non-tile-effect to map.")
            raise RuntimeError

    '''
    def createDefaultMap(self):
        for x in range(-10, 10, 1):
            for y in range(-10, 10, 1):
                self[(x, y)] = DirtFloorTile()
                #if random.random() > 0.9:
                    #self[(x, y)] = StoneWall()
        #self.total_entities[self.current_coordinates] = self.pc
        #self.active_entities[(0, 0)] = self.pc

        #self[(0, -2)] = items.Spellbook(self, 2, (0, -2))
        #self[(0, 2)] = items.Spellbook(self, 2, (0, 2))
        #self[(2, 2)] = items.Spellbook(self, 1, (2, 2))
        #self[(-2, -2)] = items.Spellbook(self, 1, (-2, -2))
    '''

    def generate_tile(self, coords):
        self.world_generator.generate_tile(coords)

    def check_can_move(self, entity, target):
        if self.total_floor[target] is None:
            self.generate_tile(target)
        if self.total_entities[target] is not None:
            #print(f"{entity.name} could not move because {self.active_entities[target].name} blocked the way.")
            return False # Change down the line to allow PC to walk into ally spaces.
        if self.total_walls[target] is not None and not entity.intangible:
            #print(f"Could not move because a wall blocked the way and {entity.name} is not intangible.")
            if not (self.total_walls[target].openable and entity.opens_doors):
                if not (self.total_walls[target].walkable and entity.walking) or (self.total_walls[target].flyable and entity.flying) or (self.total_walls[target].swimmable and entity.swimming):
                    return False
        if self.total_floor[target].walkable and entity.walking:
            #print(f"{entity.name} could move because it can walk and the target tile is walkable.")
            return True
        if self.total_floor[target].flyable and entity.flying:
            #print(f"{entity.name} could move because it can fly and the target tile is flyable.")
            return True
        if self.total_floor[target].swimmable and entity.swimming:
            #print(f"{entity.name} could move because it can swim and the target tile is swimmable.")
            return True

        #print(f"{entity.name} could not because it has no movement type appropriate for the tile.")
        return False

    def check_can_be_pushed(self, entity, target):
        if entity.layer == "entity":
            if self.active_entities[target] is not None:
                return False
            if self.total_walls[target] is not None and not entity.intangible:
                if not (self.total_walls[target].walkable and entity.walking) or (self.total_walls[target].flyable and entity.flying) or (self.total_walls[target].swimmable and entity.swimming):
                    return False
            return True
        elif entity.layer == "wall":
            if self.active_entities[target] is not None or self.total_walls[target] is not None:
                return False
            return True

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
        if self.move_entity(self.game.pc, target):
            self.current_coordinates = target
            self.set_current_active_tiles()
            if self.total_items[self.current_coordinates] is not None:
                item = self.total_items[self.current_coordinates]
                item.on_pickup()
            visible_tiles = self.get_visible_tiles(self.game.pc.position)
            for tile in visible_tiles:
                if chebyshev_distance(self.game.pc.position, tile) <= 18: # 18 is the number of tiles that are actually shown with the current settings, though I imagine it's actually resolution dependent. Ah, well. Fix it if it needs fixing later.
                    self.has_seen[tile] = True
            return True
        return False


    def set_current_active_tiles(self):
        self.active_walls = defaultdict(lambda: None)
        self.active_floor = defaultdict(lambda: None)
        self.active_entities = defaultdict(lambda: None)

        for x in range(self.current_coordinates[0] - self.active_tile_range,
                       self.current_coordinates[0] + self.active_tile_range):
            for y in range(self.current_coordinates[1] - self.active_tile_range,
                           self.current_coordinates[1] + self.active_tile_range):
                coords = (x, y)
                if self.total_floor[coords] is None:
                    self.generate_tile(coords)
                if chebyshev_distance(coords, self.current_coordinates) < self.active_tile_range:
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
            for item in entity.items:
                item.position = target
            if self.active_tile_effects[target] is not None:
                self.active_tile_effects[target].on_enter_effect()
            if self.active_walls[target] is not None:
                self.active_walls[target].on_enter_effect()
            self.active_floor[target].on_enter_effect(entity)

            return True
        else:
            return False

    def push_entity(self, entity, target):
        if entity.layer == "entity":
            if self.check_can_be_pushed(entity, target):
                self.active_entities[entity.position] = None
                self.total_entities[entity.position] = None
                self.active_entities[target] = entity
                self.total_entities[target] = entity
                entity.position = target
                return True
            else:
                return False
        elif entity.layer == "wall":
            if self.check_can_be_pushed(entity, target):
                self.active_walls[entity.position] = None
                self.total_walls[entity.position] = None
                self.active_walls[target] = entity
                self.total_walls[target] = entity
                entity.position = target
                return True
            else:
                return False

    def can_see_and_no_fow(self, x, y):
        line_tiles = bresenham(x, y)
        if x == y:
            return True
        for coords in line_tiles:
            if self.active_walls[coords] is not None and coords != y:
                if self.active_walls[coords].blocks_vision:
                    return False
            if not self.game.pc.can_see(coords) and not self.has_seen[coords]:
                return False
        return True

    def can_see(self, x, y):
        line_tiles = bresenham(x, y)
        if x == y:
            return True
        for coords in line_tiles:
            if self.active_walls[coords] is not None and coords != y:
                if self.active_walls[coords].blocks_vision:
                    return False
        return True

    def get_visible_tiles(self, target, treat_fow_as_wall=False):
        visible_tiles = []
        if treat_fow_as_wall:
            for tile in self.active_floor.keys():
                if self.can_see_and_no_fow(target, tile):
                    visible_tiles.append(tile)
        else:
            for tile in self.active_floor.keys():
                if self.can_see(target, tile):
                    visible_tiles.append(tile)
        return visible_tiles


    def summon_entity_from_class(self, entity_class, count, target, allegiance):
        summoned_entities = 0
        max_range = 5
        current_range = 1
        entities = []
        while summoned_entities < count and current_range <= max_range:
            entity = entity_class(self)
            entity.allegiance = allegiance
            proposed_tiles = disk(target, current_range, include_origin_tile=True)
            random.shuffle(proposed_tiles)
            placed = False
            while not placed and len(proposed_tiles) > 0:
                tile = proposed_tiles.pop()
                if self.total_entities[tile] is None and entity.can_move(tile):
                    entity.position = tile
                    self.total_entities[tile] = entity
                    self.active_entities[tile] = entity
                    summoned_entities += 1
                    placed = True
                    entities.append(entity)
            current_range += 1

        return entities

    def summon_entities_from_instance(self, entity_group, target, precise=True, radius=4):
        for entity in entity_group:
            if not precise:
                proposed_tiles = disk(target, radius, include_origin_tile=True)
                #print(len(proposed_tiles)) # 69 tiles should be more than enough for most scenarios.
                random.shuffle(proposed_tiles)
                placed = False
                while not placed and len(proposed_tiles) > 0:
                    tile = proposed_tiles.pop()
                    if self.total_floor[tile] is None:
                        self.generate_tile(tile)
                    if self.total_entities[tile] is None and entity.can_move(tile):
                        entity.position = tile
                        self.total_entities[tile] = entity
                        self.active_entities[tile] = entity
                        placed = True
            else:
                placed = False
                current_radius = 0
                while not placed and current_radius <= radius:
                    proposed_tiles = disk(target, current_radius, include_origin_tile=True)
                    # print(len(proposed_tiles)) # 69 tiles should be more than enough for most scenarios.
                    random.shuffle(proposed_tiles)
                    placed = False
                    while not placed and len(proposed_tiles) > 0:
                        tile = proposed_tiles.pop()
                        if self.total_floor[tile] is None:
                            self.generate_tile(tile)
                        if self.total_entities[tile] is None and entity.can_move(tile):
                            entity.position = tile
                            self.total_entities[tile] = entity
                            self.active_entities[tile] = entity
                            placed = True
                    current_radius += 1

    def place_tile_effect(self, tile_effect, coordinates):
        if self.total_tile_effects[coordinates] is None:
            self.total_tile_effects[coordinates] = tile_effect
            self.active_tile_effects[coordinates] = tile_effect
        else:
            if random.random() < 0.5:
                self.total_tile_effects[coordinates] = tile_effect
                self.active_tile_effects[coordinates] = tile_effect

    def place_item(self, item, coordinates):
        if self.total_items[coordinates] is None and self.total_walls[coordinates] is None:
            self.total_items[coordinates] = item
            self.active_items[coordinates] = item
        else:
            possible_tiles = disk(coordinates, 3, False)
            random.shuffle(possible_tiles)
            for tile in possible_tiles:
                if self.total_items[tile] is None and self.total_walls[tile] is None:
                    self.total_items[tile] = item
                    self.active_items[tile] = item
                    return

    def place_monster_group(self, monster_group, coordinates):
        #direction_from_player = compute_direction(self.game.pc.position, coordinates, exact=True)
        direction_from_player = relative_quadrant(self.game.pc.position, coordinates)
        #print(f"direction_from_player: {direction_from_player}, self.game.pc.position: {self.game.pc.position}, target coordinates: {coordinates}")

        target_x = int(coordinates[0] - 4 * direction_from_player[0])
        target_y = int(coordinates[1] - 4 * direction_from_player[1])
        target = (target_x, target_y)
        #print(f"Final target coordinates: {target}")
        self.summon_entities_from_instance(monster_group, target, precise=False)



    def filter_line_of_effect(self, origin, tiles, include_blocking_tile=True):
        """
        Filter tiles based on line of effect from the caster.

        Parameters:
            origin (tuple): The (x, y) coordinates of the caster.
            tiles (list of tuple): The list of (x, y) tiles affected by the spell.
            is_blocking (callable): A function that takes (x, y) and returns True if the tile blocks the line of effect.
            include_blocking_tile (bool): Whether to include the first blocking tile in the result.

        Returns:
            list of tuple: The tiles that are within the line of effect.
        """
        result = []

        for target in tiles:
            # Use Bresenham's line algorithm to get the line from caster to the target
            line_x, line_y = line(origin[0], origin[1], target[0], target[1])
            line_coords = list(zip(line_x, line_y))

            # Check each tile along the line
            blocked = False
            for i, (x, y) in enumerate(line_coords):
                wall = self.total_walls[(x, y)]
                if wall is not None:
                    if wall.blocks_line_of_effect:
                        if include_blocking_tile and i == len(line_coords) - 1:
                            result.append((x, y))  # Add the blocking tile if it's the target
                        blocked = True
                        break

            # If not blocked, add the target tile
            if not blocked:
                result.append(target)

        return result

