from collections import defaultdict
import pygame
import skimage.draw
from skimage.draw import line
import numpy as np
import math
import heapq
from a_star import a_star_search


class Tags:
    def __init__(self, **kwargs):
        # Initialize with key-value pairs
        for key, value in kwargs.items():
            setattr(self, key, value)


BIOME_SCALE = 1000

DAMAGE_TYPES = Tags(
    BLUDGEONING=0,
    PIERCING=1,
    SLASHING=2,
    FIRE=3,
    COLD=4,
    LIGHTNING=5,
    POISON=6,
    DARK=7,
    LIGHT =8,
    PSYCHIC=9,
    ARCANE=10
)

# Damage types not appearing in this game
# Acid
# Sonic/Thunder
# Abrasive
# Bleed
# Chaos

SCHOOLS = Tags(
    SORCERY=0,
    ENCHANTMENT=1,
    CONJURATION=2,
    TRANSMUTATION=3,
    BLOOD=4,
    ILLUSION=5,
    ASTRAL=6,
    METAL=7,
    WATER=8,
    ICE=9,
    AIR=10,
    LIGHTNING=11,
    FIRE=12,
    NATURE=13,
    HOLY=14,
    DARK=15,
    DEATH=16,
    EARTH=17,
    DRAGON=18
)

SCHOOL_NAMES = [
    "Sorcery",
    "Enchantment",
    "Conjuration",
    "Transmutation",
    "Blood",
    "Illusion",
    "Astral",
    "Metal",
    "Water",
    "Ice",
    "Air",
    "Lightning",
    "Fire",
    "Nature",
    "Holy",
    "Dark",
    "Death",
    "Earth",
    "Dragon"
]

SCHOOL_COLOURS = [
    (140, 25, 255), #Sorcery
    (77,255,255), #Enchantment
    (204,153,255),#Conjuration
    (0,153,102),#Transmutation
    (179,0,30),#BLOOD=4,
    (227,197,230),#ILLUSION=5,
    (153,255,255), #ASTRAL=6,
    (169,184,204),#METAL=7,
    (51,51,255),#WATER=8,
    (77,166,255), #ICE=9,
    (191,255,179),#WIND=10,
    (255,255,25),#LIGHTNING=11,
    (230,115,0),#FIRE=12,
    (0,179,0),#NATURE=13,
    (255,234,128),#HOLY=14,
    (51,0,102),#DARK=15,
    (153,0,153),#DEATH=16,
    (153,77,0),#EARTH=17,
    (204,136,0)#DRAGON=18
]


COLOURS = Tags(
    WHITE=(255, 255, 255),
    BLACK=(0, 0, 0),
    GRAY=(200, 200, 200),
    DARK_GRAY=(100,100,100),
    RED=(255, 0, 0),
    GREEN=(0, 255, 0),
    BLUE=(0, 0, 255),
    CYAN=(0, 255, 255),
    YELLOW=(255, 255, 0),
    MAGENTA=(255, 0, 255)
)

ENTITY_TAGS = Tags(
    LIVING=0,
    UNDEAD=1,
    CONSTRUCT=2,
    EXTRAPLANAR=3,
    DEMONIC=4,
    ANGELIC=5,
    DRACONIC=6,
    MAGICAL=7,
    VOID=8,
    ELEMENTAL=9
)




# Allegiances
ALLEGIANCES = Tags(
    NEUTRAL=0,
    PLAYER_TEAM=1,
    ENEMY_TEAM=2
)

# Event types
EVENT_TYPES = Tags(
    NPC_TURN_START=0,
)

def get_top_parent(obj):
    return obj.__class__.mro()[-2]

def euclidean_distance(a, b):
    return math.floor(math.sqrt(math.pow(a[0] - b[0], 2) + math.pow(a[1] - b[1], 2)))

def euclidean_distance_rounded_up(a, b):
    return math.ceil(math.sqrt(math.pow(a[0] - b[0], 2) + math.pow(a[1] - b[1], 2)))

def manhattan_distance(a, b):
    return(abs(a[0] - b[0]) + abs(a[1] - b[1]))

def chebyshev_distance(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

def bresenham(a, b):
    r0 = a[0]
    c0 = a[1]
    r1 = b[0]
    c1 = b[1]
    xs, ys = line(r0, c0, r1, c1)
    #print("------- Printing xs -------")
    #print(xs)
    #print("------- Printing ys -------")
    #print(ys)
    paired_coordinates = list(zip(xs, ys))

    return paired_coordinates

def disk(target, radius, include_origin_tile=True):
    xs, ys = skimage.draw.disk(target, radius + 0.5)
    xs = xs.astype(int)
    ys = ys.astype(int)
    tiles = list(zip(xs, ys))

    if not include_origin_tile:
        final_list = []
        for tile in tiles:
            if tile != target:
                final_list.append(tile)
        return final_list
#        tiles.remove(target)
    return tiles

#def compute_cone_tiles(grid_size, origin, target, radius, angle=45):
def compute_cone_tiles(origin, target, radius, angle=45, include_origin_tile=False, fill=True):
    """
    Compute tiles affected by a cone on an infinite grid, including negative coordinates.

    :param origin: Tuple (x, y) of the cone's starting point.
    :param target: Tuple (x, y) indicating the direction of the cone.
    :param radius: Radius (length) of the cone.
    :param angle: Angle (in degrees) of the cone's width.
    :return: A set of (x, y) tuples representing affected tiles.
    """

    # Works, as long as you're in positive coordinates. Also somewhat weirdly shaped.

    #radius = euclidean_distance_rounded_up(origin, target)

    # Compute the direction vector and angle of the cone
    direction = (target[0] - origin[0], target[1] - origin[1])
    angle_rad = np.deg2rad(angle)

    # Normalize the direction vector
    direction_length = np.hypot(*direction)
    if direction_length == 0:
        return []
        #raise ValueError("Target cannot be the same as the origin.")
    unit_direction = (direction[0] / direction_length, direction[1] / direction_length)

    # Compute the cone boundary vectors
    cos_half_angle = np.cos(angle_rad / 2)
    sin_half_angle = np.sin(angle_rad / 2)
    left_boundary = (
        unit_direction[0] * cos_half_angle - unit_direction[1] * sin_half_angle,
        unit_direction[0] * sin_half_angle + unit_direction[1] * cos_half_angle,
    )
    right_boundary = (
        unit_direction[0] * cos_half_angle + unit_direction[1] * sin_half_angle,
        -unit_direction[0] * sin_half_angle + unit_direction[1] * cos_half_angle,
    )

    # Compute cone vertices
    cone_vertices = [origin]
    for boundary in (left_boundary, right_boundary):
        vertex = (
            origin[0] + boundary[0] * radius,
            origin[1] + boundary[1] * radius,
        )
        cone_vertices.append(vertex)

    # Convert vertices to grid coordinates (rounding for discrete tiles)
    cone_vertices_px = np.array(cone_vertices, dtype=float)
    cone_vertices_px = cone_vertices_px.round().astype(int)

    '''
    # Good so far
    # Use skimage.draw.polygon to compute affected tiles
    rr, cc = skimage.draw.polygon(
        [v[1] for v in cone_vertices_px],  # Row coordinates (y-axis)
        [v[0] for v in cone_vertices_px],  # Column coordinates (x-axis)
    )
    # Bad here
    # Convert results to a set of tiles with (x, y) coordinates
    affected_tiles = set(zip(cc, rr))
    '''

    affected_tiles = rasterize_polygon(cone_vertices_px, fill=fill)


    # Remove the origin tile if we intend to do so.
    if origin in affected_tiles and not include_origin_tile:
        affected_tiles.remove(origin)

    return affected_tiles

def rasterize_polygon(vertices, fill=True):
    """
    Generate a list of (x, y) coordinate pairs that make up the polygon defined by vertices.
    :param vertices: List of (x, y) tuples defining the vertices of the polygon.
    :return: List of (x, y) tuples for the filled polygon.
    """
    # Generate edge points
    edge_points = set()
    for i in range(len(vertices)):
        #x0, y0 = vertices[i]
        #x1, y1 = vertices[(i + 1) % len(vertices)]  # Wrap to the first vertex
        edge_points.update(bresenham(vertices[i], vertices[(i+1) % len(vertices)]))

    if not fill:
        return list(edge_points)

    # Find bounds of the polygon
    min_y = min(y for _, y in vertices)
    max_y = max(y for _, y in vertices)

    # Fill the polygon
    filled_points = set()
    for y in range(min_y, max_y + 1):
        # Find all x-coordinates where an edge crosses this y-value
        intersections = sorted(x for x, edge_y in edge_points if edge_y == y)
        # Pair up intersections and fill between them
        for i in range(0, len(intersections), 1): # This was 2 for some reason, making it skip every other row. Works now.
            if i + 1 < len(intersections):
                x_start, x_end = intersections[i], intersections[i + 1]
                for x in range(x_start, x_end + 1):
                    filled_points.add((x, y))

    # Combine edge points and filled points
    return list(edge_points.union(filled_points))


def find_closest_enemy(start_entity):
    possible_targets = []
    for entity in start_entity.world.active_entities.values:
        if entity is not None:
            if entity.allegiance != ALLEGIANCES.NEUTRAL and entity.allegiance != start_entity.allegiance:
                possible_targets.append(entity)

    if len(possible_targets) > 0:
        possible_targets.sort(key=euclidean_distance(start_entity, entity))
        return possible_targets[0]

    return None

def find_and_sort_enemies_by_distance(start_entity):
    enemies = []
    for entity in start_entity.world.active_entities.values():
        if entity is not None:
            if entity.allegiance != ALLEGIANCES.NEUTRAL and entity.allegiance != start_entity.allegiance:
                enemies.append(entity)
    if len(enemies) > 0:
        enemies.sort(key=lambda entity: euclidean_distance(start_entity.position, entity.position))
    enemies.reverse()
    return enemies


def find_path(entity, target):
    grid_size = entity.world.active_tile_range - 1 # Need this -1, but no more
    grid, centre_x, centre_y = generate_grid_centered(entity, grid_size)

    #print(f"Grid shape: {len(grid)}x{len(grid[0])}")
    #print(grid[24:38])


    # Rotate clockwise - did not do well.
    #grid = [list(row) for row in zip(*grid[::-1])]
    # Rotate counterclockwise - also did not do well.
    #grid = [list(row) for row in zip(*grid)][::-1]
    # Transpose grid:
    grid = list(map(list, zip(*grid)))
    # Flip horizontally:
    #grid = [row[::-1] for row in grid]
    # Flip vertically:
    #grid = grid[::-1]


    # These are clearly correct.
    translated_start = translate_coordinates(entity.position, centre_x, centre_y, grid_size)
    translated_target = translate_coordinates(target, centre_x, centre_y, grid_size)

    #print(translated_start)
    #print(translated_target)

    #print(f"entity.position: {entity.position}, translated_start: {translated_start}, target: {target}, translated_target: {translated_target}")

    # Mark starting point as passable
    grid[translated_start[0]][translated_start[1]] = 1
    # Also mark ending point as passable. Otherwise we won't be able to use this to find the path to an entity.
    grid[translated_target[0]][translated_target[1]] = 1
    #print(grid)

    path = a_star_search(grid, translated_start, translated_target)

    # Adjust path to map coordinates before returning

    adjusted_path = []

    #print("Unadjusted path")
    #print(path)
    for coord in path:
        adjusted_path.append(backtranslate_coordinates(coord, centre_x, centre_y, grid_size))
    #print("Adjusted path")
    #print(adjusted_path)
    return adjusted_path

    #return []


def flip_coordinates(coordinates):
    flipped = (coordinates[1], coordinates[0])
    return flipped

def generate_grid_centered(entity, grid_size=29):
    """
    Generate a grid centered around the character's current position for pathfinding.

    :param entity: The entity object containing position and world information.
    :param grid_size: The radius around the entity to create the grid (default 29).
    :return: A 2D list of tiles (0 for walkable, 1 for blocked).
    """
    # Center point
    #center_x, center_y = flip_coordinates(entity.world.current_coordinates)
    center_x, center_y = entity.world.current_coordinates

    #in the expected grid, the left coordinate is the x
    #it corresponds to the row, so it's
    #x = r, y = c

    #could be because it starts with checking the own tile which always counts as a 0




    # Define grid bounds
    min_x = center_x - grid_size
    max_x = center_x + grid_size
    min_y = center_y - grid_size
    max_y = center_y + grid_size

    #print(f"min_x: {min_x}, max_x: {max_x}, min_y: {min_y}, max_y: {max_y}")

    # Generate the grid
    grid = []
    for y in range(min_y, max_y + 1):
        row = []
        for x in range(min_x, max_x + 1):
            #if entity.world.active_floor[(y, x)] is None:
                #print(f"No floor at {x}, {y}")
            # Fetch the tile value from the game world (replace this logic with your game's logic)
            #tile_value = entity.world.get_tile(x, y)  # Replace with your world tile-fetching function
            #print(f"Seeing if entity can move to {(x, y)}")
            tile_value = 1 if entity.can_move((x, y)) else 0
            #tile_value = 1 if entity.position
            #print(tile_value)
            # grid[y][x] = 1 if entity.can_move((world_x_to_check, world_y_to_check)) else 0

            row.append(tile_value)
        grid.append(row)



    return grid, center_x, center_y


def translate_coordinates(world_coordinates, center_x, center_y, grid_size):
    """
    Translate world coordinates to grid coordinates.

    :param world_coordinates: Tuple (x, y) in world coordinates.
    :param center_x: X coordinate of the center in world space.
    :param center_y: Y coordinate of the center in world space.
    :param grid_size: The radius of the grid.
    :return: Tuple (x, y) in grid coordinates.
    """
    return (world_coordinates[0] - (center_x - grid_size),
            world_coordinates[1] - (center_y - grid_size))

def backtranslate_coordinates(grid_coordinates, center_x, center_y, grid_size):

    # Translate grid coordinates to world coordinates.
    # Is this right?
    return (grid_coordinates[0] + (center_x - grid_size),
            grid_coordinates[1] + (center_y - grid_size))


def compute_direction(origin, target, exact=False):
    print(origin)
    print(target)
    direction = (target[0] - origin[0], target[1] - origin[1])

    # Normalize the direction vector
    direction_length = np.hypot(*direction)
    if direction_length == 0:
        return []
        # raise ValueError("Target cannot be the same as the origin.")
    unit_direction = (direction[0] / direction_length, direction[1] / direction_length)
    if not exact:
        unit_direction = (math.floor(unit_direction[0]), math.floor(unit_direction[1]))
    return unit_direction

def relative_quadrant(point1, point2):
    # Calculate the differences in x and y
    dx = int(point2[0]) - int(point1[0])
    dy = int(point2[1]) - int(point1[1])

    # Normalize to -1, 0, or 1
    quadrant_x = (dx > 0) - (dx < 0)  # 1 if positive, -1 if negative, 0 if zero
    quadrant_y = (dy > 0) - (dy < 0)

    return (quadrant_x, quadrant_y)


def desaturate_sprite(sprite):
    """Desaturates a sprite using a blending effect."""
    # Create a grayscale-like surface (pure white to desaturate colors)
    gray_overlay = pygame.Surface(sprite.get_size())
    gray_overlay.fill((128, 128, 128))  # Gray color to reduce saturation

    # Create a copy of the sprite to modify
    desaturated_sprite = sprite.copy()

    # Blend the sprite with the gray overlay
    desaturated_sprite.blit(gray_overlay, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

    return desaturated_sprite