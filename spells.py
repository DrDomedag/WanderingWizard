

SORCERY = 0
ENCHANTMENT = 1
CONJURATION = 2


# Theme ideas:
'''
Keep:
Blood (includes Demons)
Illusion (includes mind control)
Astral (Arcane, aether...)
Metal (summon dancing swords, walls of swords, robots, armour etc.)
Water / Ice
Air / Lightning
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


'''
Spell ideas:

Bloody Sacrament
Blood + Holy
Expend life to gain a charge of another random spell. Channelable, or upgrade to channel. 

Summon Longdead
t1 Necro
Create a skeletal servant.
Upgrade to summon more per casting or to enable channeling.

Summon Longdead Beast
t3 necro
Like Longdead but it's a random animal.

Iron Needle
Fire a metallic needle.
Only costs one action.
Upgrade to fire more needles, or (hear me out) to fire *even more needles*.

Bone Spike
Pay health to fire one of your own bones. Short range.

Banish
Instantly unmake a summoned creature.

Flickerstep
Move two squares per step, ignoring intervening walls/entities.

'''


class Spell:
    def __init__(self, world):
        self.world = world

        self.power = 5
        self.range = 1
        self.radius = 1
        self.num_targets = 1
        self.action_cost = 2
        self.max_charges = 5
        self.duration = 0
        self.name = "Unnamed Spell"
        self.level = 1
        self.tags = []
        self.upgrades = []
        self.recovery_time = 5

        self.caster = None

        self.requires_line_of_sight = True
        self.can_target_self = False
        self.must_target_entity = False
        self.cannot_target_entity = False
        self.can_target_ground = True
        self.can_target_water = True
        self.can_target_void = True
        self.can_target_wall = True

        self.should_target_allies = False
        self.should_target_empty = False

        self.on_init()


    def cast(self, target):
        pass

    def on_init(self):
        pass

    def get_targetable_tiles(self):
        pass

    def can_target_tile(self, target):
        if self.caster.position == target and not self.can_target_self:
            return False
        if self.must_target_entity and self.world.active_entities[target] is None:
            return False
        if (not self.can_target_ground) and self.world.active_entities[target] is None and self.world.active_floor[target].type == "solid":
            return False
        if (not self.can_target_water) and self.world.active_entities[target] is None and self.world.active_floor[target].type == "liquid":
            return False
        if (not self.can_target_void) and self.world.active_entities[target] is None and self.world.active_floor[target].type == "void":
            return False
        if self.cannot_target_entity and self.world.active_entities[target] is not None:
            return False

        if self.range < self.world.euclidean_distance(self.caster.position, target):
            return False
        if self.requires_line_of_sight and not(self.caster.canSee(target)):
            return False



class MeleeAttack(Spell):
    def __init__(self):
        super().__init__()
        self.name = "Strike"

