from skimage.draw import line
import numpy as np

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


