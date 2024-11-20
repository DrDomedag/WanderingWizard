from effects import *
from util import *



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

Haste
Air + Enchantment
Target gets an additional action crystal each turn for X turns.

Metabolic Overdrive
Blood + Nature + Transmutation
Target gets an additional action crystal each turn for X turns.

Resurrect (Holy)
Revive a recently killed ally.

Reanimate (Death)
Revive a recently dead enemy as a zombie.

Call Spirit (Death + Holy)
Revive a recently dead enemy as a ghost. 

Mist (Air + Water)
Creates a cloud that blocks line of sight. Immune to most damage, but is by fire.

Lightning Bond
Form a bond with up to 3 nearby allies. Lightning shoots between you each turn, damaging enemies in between.
'''



class Spell:
    range = 1
    level = 1

    def __init__(self, caster):
        self.caster = caster

        self.power = 5
        self.range = 1
        self.radius = 1
        self.num_targets = 1
        self.action_cost = 2
        self.max_charges = 5
        self.current_charges = self.max_charges
        self.duration = 0
        self.name = "Unnamed Spell"
        self.description = "Undescribed spell."
        self.level = 1
        self.schools = []
        self.upgrades = []
        self.recovery_time = 5


        self.requires_line_of_sight = True
        self.can_target_self = False
        self.must_target_entity = False
        self.cannot_target_entity = False
        self.can_target_ground = True
        self.can_target_water = True
        self.can_target_void = True
        self.can_target_wall = True

        self.should_target_self = False
        self.should_target_allies = False
        self.should_target_empty = False

        self.on_init()


    def cast(self, target):
        print(f"Cast {self.name} at {target}!")
        self.current_charges -= 1
        self.on_cast(target)
        self.caster.current_actions -= self.action_cost

    def on_cast(self, target):
        pass

    def on_init(self):
        self.recovery_turns_left = self.recovery_time
        self.current_charges = self.max_charges

    def get_targetable_tiles(self):
        targetable_tiles = []
        for tile in self.caster.world.active_floor.keys():
            if self.can_target_tile(tile):
                targetable_tiles.append(tile)
        return targetable_tiles


    def get_impacted_tiles(self, target):
        return [target]

    def can_target_tile(self, target):
        if self.caster.position == target and not self.can_target_self:
            #print("Can't target yourself with that one, Jim.")
            return False
        if self.must_target_entity and self.caster.world.active_entities[target] is None:
            #print("That one needs to target an entity, Jimmy.")
            return False
        if (not self.can_target_ground) and self.caster.world.active_entities[target] is None and self.caster.world.active_floor[target].type == "solid":
            #print("This one can't just target empty ground, Jimmy boy.")
            return False
        if (not self.can_target_water) and self.caster.world.active_entities[target] is None and self.caster.world.active_floor[target].type == "liquid":
            #print("Can't target the ocean with this one, Caligula.")
            return False
        if (not self.can_target_void) and self.caster.world.active_entities[target] is None and self.caster.world.active_floor[target].type == "void":
            #print("Literally throwing spells into the void now? Ain't gonna fly, Jimbo.")
            return False
        if self.cannot_target_entity and self.caster.world.active_entities[target] is not None:
            #print("This spell does not target entities. Please select another target.... Jimzo.")
            return False
        if self.range < util.euclidean_distance(self.caster.position, target):
            #print(f"Can't use a {self.range} spell at a distance of {self.caster.world.euclidean_distance(self.caster.position, target)} tiles, that should be obvious, Jimmy old sport.")
            return False
        if self.requires_line_of_sight and not(self.caster.can_see(target)):
            #print("Can't target what you can't see, Jimpers.")
            return False
        return True

    def can_cast(self, target):
        if not self.can_target_tile(target):
            #print(f"Can't cast that there.")
            return False
        if self.caster.current_actions < self.action_cost:
            #print(f"Can't cast a {self.action_cost} action spell with only {self.caster.current_actions} actions!")
            return False
        if self.current_charges <= 0:
            #print(f"Can't cast - no charges!")
            return False

        return True

    def should_cast(self):
        if self.should_target_self:
            return True
        if self.should_target_allies:
            for entity in self.caster.world.active_entities.values:
                if entity is not None:
                    if entity.allegiance == self.caster.allegiance:
                        if self.can_cast(entity.position):
                            return True
        if self.should_target_empty:
            for target in self.caster.world.active_floor.keys():
                if self.caster.world.active_entities[target] is None:
                    if self.can_cast(target):
                        return True
        for entity in self.caster.world.active_entities.values():
            if entity is not None:
                if entity.allegiance != self.caster.allegiance and entity.allegiance != ALLEGIANCES.NEUTRAL:
                    if self.can_cast(entity.position):
                        return True
        return False


class IronNeedle(Spell):
    def __init__(self, caster):
        super().__init__(caster)

        self.power = 5
        self.range = 6
        self.action_cost = 1
        self.max_charges = 15
        self.name = "Iron Needle"
        self.description = "Quickly fire a needle of iron."
        self.level = 1
        self.schools = [SCHOOLS.METAL, SCHOOLS.SORCERY]
        self.upgrades = []
        self.recovery_time = 5

        self.should_target_allies = False
        self.should_target_empty = False

        self.on_init()

    def on_cast(self, target):
        damage_tile(self.caster.world, self, target, self.power, DAMAGE_TYPES.PIERCING)
        if not self.caster.world.active_entities[target] is None:
            subject = self.caster.world.active_entities[target]
            damage_entity(self, subject, self.power, DAMAGE_TYPES.PIERCING)

class FireBreath(Spell):
    def __init__(self, caster):
        super().__init__(caster)

        self.power = 6
        self.range = 4
        self.action_cost = 2
        self.max_charges = 10
        self.name = "Fire Breath"
        self.description = "Spray fire, dealing damage in a cone."
        self.level = 1
        self.schools = [SCHOOLS.FIRE, SCHOOLS.SORCERY]
        self.upgrades = []
        self.recovery_time = 5

        self.should_target_allies = False
        self.should_target_empty = False

        self.on_init()

    def on_cast(self, target):
        affected_tiles = compute_cone_tiles(self.caster.position, target, self.range + 0.5, include_origin_tile=False)
        for tile in affected_tiles:
            damage_tile(self.caster.world, self.caster, tile, self.power, DAMAGE_TYPES.FIRE)
            self.caster.world.show_effect(tile, SCHOOLS.FIRE)

    def get_impacted_tiles(self, target):
        return compute_cone_tiles(self.caster.position, target, self.range + 0.5, include_origin_tile=False)

class SeismicJolt(Spell):
    def __init__(self, caster):
        super().__init__(caster)

        self.power = 9
        self.range = 0
        self.radius = 2

        self.action_cost = 2
        self.max_charges = 7
        self.name = "Seismic Jolt"
        self.description = "Deal bludgeoning damage to enemies in a two tile radius and push them back one tile."
        self.level = 2
        self.schools = [SCHOOLS.EARTH, SCHOOLS.SORCERY]
        self.upgrades = []
        self.recovery_time = 10

        self.should_target_self = True
        self.should_target_allies = False
        self.should_target_empty = False

        self.on_init()

    def can_target_tile(self, target):
        affected_tiles = disk(self.caster.position, self.radius, include_origin_tile=False)
        if target in affected_tiles:
            return True
        return False

    def on_cast(self, target):
        affected_tiles = disk(self.caster.position, self.radius, include_origin_tile=False)
        for tile in affected_tiles:
            damage_tile(self.caster.world, self.caster, tile, self.power, DAMAGE_TYPES.BLUDGEONING)
            push_tile(self.caster.world, self.caster.position, tile, 1, push_walls=True)
            #self.caster.world.show_effect(tile, SCHOOLS.FIRE) # Fix when bludgeoning damage is animated and animations work.

    def get_impacted_tiles(self, target):
        return disk(self.caster.position, self.radius, include_origin_tile=False)



class Heal(Spell):
    def __init__(self, caster):
        super().__init__(caster)

        self.power = 10
        self.range = 6
        self.action_cost = 2
        self.max_charges = 3
        self.name = "Word of Healing"
        self.level = 1
        self.schools = [SCHOOLS.HOLY, SCHOOLS.NATURE]
        self.upgrades = []
        self.recovery_time = 15

        self.can_target_self = False
        self.must_target_entity = False

        self.should_target_allies = True
        self.should_target_empty = False

        self.on_init()

    def cast(self, target):
        if not self.caster.world.active_entities[target] is None:
            subject = self.caster.world.active_entities[target]
            heal(self, subject, self.power)


class BluntMeleeAttack(Spell):
    def __init__(self, caster):
        super().__init__(caster)
        self.name = "Strike"

        self.power = 1
        self.range = 1
        self.action_cost = 1
        self.max_charges = 1000
        self.level = 0
        self.schools = []
        self.recovery_time = 1

        self.on_init()

    def cast(self, target):
        if not self.caster.world.active_entities[target] is None:
            subject = self.caster.world.active_entities[target]
            damage_entity(self, subject, self.power, DAMAGE_TYPES.BLUDGEONING)

class SlashingMeleeAttack(BluntMeleeAttack):
    def cast(self, target):
        if not self.caster.world.active_entities[target] is None:
            subject = self.caster.world.active_entities[target]
            damage_entity(self, subject, self.power, DAMAGE_TYPES.SLASHING)

class PiercingMeleeAttack(BluntMeleeAttack):
    def cast(self, target):
        if not self.caster.world.active_entities[target] is None:
            subject = self.caster.world.active_entities[target]
            damage_entity(self, subject, self.power, DAMAGE_TYPES.PIERCING)

