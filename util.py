from skimage.draw import line
#import numpy as np
import heapq
from a_star import a_star_search




class Tags:
    def __init__(self, **kwargs):
        # Initialize with key-value pairs
        for key, value in kwargs.items():
            setattr(self, key, value)


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
    WIND=10,
    LIGHTNING=11,
    FIRE=12,
    NATURE=13,
    HOLY=14,
    DARK=15,
    DEATH=16,
    EARTH=17,
    DRAGON=18
)

COLOURS = Tags(
    WHITE=(255, 255, 255),
    BLACK=(0, 0, 0),
    GRAY=(200, 200, 200),
    RED=(255, 0, 0),
    GREEN=(0, 255, 0),
    BLUE=(0, 0, 255),
    CYAN=(0, 255, 255),
    YELLOW=(255, 255, 0),
    MAGENTA=(255, 0, 255)
)

# Theme ideas:
'''
Keep:
Blood (includes Demons)
Illusion (includes mind control)
Astral (Arcane, aether...)
Metal (summon dancing swords, walls of swords, robots, armour etc.)
Water
Ice
Air
Lightning
Fire
Nature
Holy
Dark / Unholy / Shadow
Death / Bone
Earth / Stone

Minor:
Draconic
Transmutation


Cut:
Light
Psionic
Spirit
Rune
Entropy
Emotion

Combo themes:
Fungus (Nature + Earth)
Steam (Fire + Water)
Rainbow (Nature + Light (or Illusion))
Robots (Lightning + Metal)
Blood Sacrifice (Blood + Holy)
Crystal (Ice + Stone or Arcane)
Fairies (Nature + Arcane)
Decay (Nature + Dark)
Poison (Nature + Blood)
Acid (Nature + Water)
Storm/Mist (Air + Water)
Rune (Arcane + Earth)
Extraterresterial (meteors etc.) (Astral + Earth)
Void beings (Astral + Dark) 
'''


# Allegiances
ALLEGIANCES = Tags(
    NEUTRAL=0,
    PLAYER_TEAM=1,
    ENEMY_TEAM=2
)




'''
# function for line generation
def bresenham(a, b):
    x1 = a[0]
    y1 = a[1]
    x2 = b[0]
    y2 = b[1]
    # This code is contributed by ash264
    # https://www.geeksforgeeks.org/bresenhams-line-generation-algorithm/
    m_new = 2 * (y2 - y1)
    slope_error_new = m_new - (x2 - x1)

    y = y1
    for x in range(x1, x2 + 1):

        print("(", x, ",", y, ")\n")

        # Add slope to increment angle formed
        slope_error_new = slope_error_new + m_new

        # Slope error reached limit, time to
        # increment y and update slope error.
        if (slope_error_new >= 0):
            y = y + 1
            slope_error_new = slope_error_new - 2 * (x2 - x1)

        # Driver code
'''



def get_top_parent(obj):
    return obj.__class__.mro()[-2]


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

def find_path(entity, target):
    grid_size = entity.world.active_tile_range - 1
    grid, centre_x, centre_y = generate_grid_centered(entity, grid_size)

    translated_start = translate_coordinates(entity.position, centre_x, centre_y, grid_size)
    translated_target = translate_coordinates(target, centre_x, centre_y, grid_size)


    path = a_star_search(grid, translated_start, translated_target)

    # Adjust path to map coordinates before returning?

    '''
        adjusted_path = []
        tr = entity.world.active_tile_range - 1
        print("Unadjusted path")
        print(path)
        for coord in path:
            adjusted_path.append((coord[0] + entity.world.current_coordinates[0] - tr, coord[1] + entity.world.current_coordinates[1] - tr))
        print("Adjusted path")
        print(adjusted_path)
        return adjusted_path
    '''

    return path




def generate_grid_centered(entity, grid_size=29):
    """
    Generate a grid centered around the character's current position for pathfinding.

    :param entity: The entity object containing position and world information.
    :param grid_size: The radius around the entity to create the grid (default 29).
    :return: A 2D list of tiles (0 for walkable, 1 for blocked).
    """
    # Center point
    center_x, center_y = entity.world.current_coordinates

    # Define grid bounds
    min_x = center_x - grid_size
    max_x = center_x + grid_size
    min_y = center_y - grid_size
    max_y = center_y + grid_size

    # Generate the grid
    grid = []
    for y in range(min_y, max_y + 1):
        row = []
        for x in range(min_x, max_x + 1):
            # Fetch the tile value from the game world (replace this logic with your game's logic)
            #tile_value = entity.world.get_tile(x, y)  # Replace with your world tile-fetching function
            #print(f"Seeing if entity can move to {(x, y)}")
            tile_value = 1 if entity.can_move((x, y)) else 0
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

'''
def active_tiles_to_traversability_grid_old(entity, target):
    #floor = world.active_floor
    #walls = world.active_walls
    #entities = world.active_entities

    tr = entity.world.active_tile_range - 1 # This adjustment seems necessary, but that's probably only because my math is wrong somewhere else. We don't really need to path far beyond what we can see anyway.
    world_side_length = 2 * tr
    grid = [[0] * world_side_length] * world_side_length

    print(f"player coordinates: {entity.world.current_coordinates}, target: {target}, len(grid): {len(grid)}, len(grid[0]): {len(grid[0])}")


    for x in range(len(grid)):
        for y in range(len(grid)):
            #print(f"x: {x}, y: {y}, current world coordinates: {entity.world.current_coordinates}")
            #print(f"Computed coordinates: {(entity.world.current_coordinates[0] - tr + x, entity.world.current_coordinates[0] - tr + y)}")
            #print(f"x: {x}, y: {y}, checking x: {entity.world.current_coordinates[0] - tr + x}, y: {entity.world.current_coordinates[1] - tr + y}")
            world_x_to_check = entity.world.current_coordinates[0] - tr + x
            world_y_to_check = entity.world.current_coordinates[1] - tr + y
            grid[y][x] = 1 if entity.can_move((world_x_to_check, world_y_to_check)) else 0
            print(f"Checking x: {world_x_to_check}, y: {world_y_to_check}, result: {grid[y][x]}")
            #print(f"Can walk: {grid[x][y]}")
    #print(grid)

    # Pretty sure these are right now.
    grid_position = (entity.position[0] - entity.world.current_coordinates[0] + tr, entity.position[1] - entity.world.current_coordinates[1] + tr)
    grid_target = (target[0] - entity.world.current_coordinates[0] + tr, target[1] - entity.world.current_coordinates[1] + tr)

    # Transpose grid?
    #grid = list(map(list, zip(*grid)))

    return grid, grid_position, grid_target
'''
