import effects
import tile_effects
from effects import *
from util import *
#import entities.entities as entities
import random


class PCAvailableSpellList:
    def __init__(self, pc):
        self.pc = pc
        self.spells = [IronNeedle, RaiseLongdead, SeismicJolt, FireBreath, LightningBolt, TidalWave, PoisonMist, ArcaneLesson, WordOfHealing, RegenerationSpell, Flickerstep, Decrepify]

    def get_random_spells_of_tier(self, level, count, schools=None):
        candidates = []
        for candidate in self.spells:
            # Check that it's not a spell we already know. Going by name for now - doesn't feel future-proof, but I can't see right now why it wouldn't work.
            known = False
            for active in self.pc.actives:
                if candidate.name == active.name:
                    known = True
                    break
            if known:
                continue
            # Check whether it is an allowed school
            if schools is not None:
                for s in schools:
                    if candidate.level == level and s in candidate.schools:
                        candidates.append(candidate)
            # If not, just make sure it's the right level
            else:
                if candidate.level == level:
                    candidates.append(candidate)
        if len(candidates) > 0:
            return random.choices(candidates, k=count)
        return []

    def remove(self, spell):
        self.spells.remove(spell)


class Spell:
    name = "Unnamed Spell"
    level = 1
    schools = []
    def __init__(self, caster):
        self.caster = caster

        self.power = 5
        self.range = 1
        self.radius = 1
        self.num_targets = 1
        self.action_cost = 2
        self.max_charges = 5
        self.duration = 0
        self.name = "Unnamed Spell"
        self.description = "Undescribed spell."
        self.level = 1
        self.schools = []
        self.upgrades = []
        self.recovery_time = 5

        self.minion_damage = 1
        self.minion_health = 1
        self.minion_count = 1

        self.requires_line_of_sight = True
        self.can_target_self = False
        self.must_target_entity = False
        self.cannot_target_entity = False
        self.can_target_ground = True
        self.can_target_water = True
        self.can_target_void = True
        self.can_target_wall = True

        self.target_must_have_tag = []

        self.should_target_enemies = True
        self.should_target_self = False
        self.should_target_allies = False
        self.should_target_empty = False

        self.on_init()

        self.current_charges = self.max_charges
        self.recovery_turns_left = self.recovery_time


    def on_init(self):
        pass

    def get_description(self):
        return self.description

    def get_relevant_stats(self):
        return {}


    def cast(self, target):
        #print(f"Cast {self.name} at {target}!")
        self.current_charges -= 1
        self.on_cast(target)
        self.caster.current_actions -= self.action_cost

    def on_cast(self, target):
        pass

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
        if self.range < int(euclidean_distance(self.caster.position, target)):
            #print(f"Can't use a {self.range} spell at a distance of {self.caster.world.euclidean_distance(self.caster.position, target)} tiles, that should be obvious, Jimmy old sport.")
            return False
        if self.requires_line_of_sight and not(self.caster.can_see(target)):
            #print("Can't target what you can't see, Jimpers.")
            return False
        if len(self.target_must_have_tag) > 0:
            entity = self.caster.world.total_entities[target]
            if entity is not None:
                has_tag = False
                for tag in self.target_must_have_tag:
                    if tag in entity.tags:
                        has_tag = True
                        break
                if not has_tag:
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
        # Since this belongs to the Spell class, weird spells can overwrite it.
        # Return a list of good target tiles.
        target_tiles = []
        if self.should_target_self:
            target_tiles.append(self.caster.position)
        if self.should_target_allies:
            for entity in self.caster.world.active_entities.values:
                if entity is not None:
                    if entity.allegiance == self.caster.allegiance and self.can_cast(entity.position):
                        target_tiles.append(entity.position)
        if self.should_target_empty:
            for target in self.caster.world.active_floor.keys():
                if self.caster.world.active_entities[target] is None:
                    if self.can_cast(target):
                        target_tiles.append(target)
        if self.should_target_enemies:
            for entity in self.caster.world.active_entities.values():
                if entity is not None:
                    if entity.allegiance != self.caster.allegiance and entity.allegiance != ALLEGIANCES.NEUTRAL and self.can_cast(entity.position):
                        target_tiles.append(entity.position)
        target_tiles = self.remove_tiles_with_incompatible_tags(target_tiles)
        return target_tiles

    def remove_tiles_with_incompatible_tags(self, target_tiles):
        if len(self.target_must_have_tag) > 0:
            tiles_to_remove = []
            for tile in target_tiles:
                target = self.caster.world.total_entities[tile]
                if target is not None:
                    has_tag = False
                    for tag in self.target_must_have_tag:
                        if tag in target.tags:
                            has_tag = True
                            break
                    if not has_tag:
                        tiles_to_remove.append(tile)
            for tile in tiles_to_remove:
                target_tiles.remove(tile)
        return target_tiles


class IronNeedle(Spell):
    name = "Iron Needle"
    schools = [SCHOOLS.METAL, SCHOOLS.SORCERY]
    def __init__(self, caster):
        super().__init__(caster)

    def on_init(self):
        self.power = 5
        self.range = 6
        self.action_cost = 1
        self.max_charges = 15
        self.name = "Iron Needle"
        self.description = f"Quickly fire a needle of iron dealing {self.power} damage to a single target."
        self.level = 1
        self.schools = [SCHOOLS.METAL, SCHOOLS.SORCERY]
        self.upgrades = []
        self.recovery_time = 5

    def get_description(self):
        return f"Quickly fire a needle of iron dealing {self.power} damage to a single target."

    def get_relevant_stats(self):
        return {"power": self.power,
                "range": self.range,
                "action_cost": self.action_cost,
                "max_charges": self.max_charges,
                "recovery_time": self.recovery_time
                }

    def on_cast(self, target):
        damage_tile(self.caster.world, self, target, self.power, DAMAGE_TYPES.PIERCING)
        '''if not self.caster.world.active_entities[target] is None:
            subject = self.caster.world.active_entities[target]
            damage_entity(self, subject, self.power, DAMAGE_TYPES.PIERCING)'''
        self.caster.world.show_projectile(self.caster.position, target, "metal_projectile", 0)

class FireBreath(Spell):
    name = "Fire Breath"
    schools = [SCHOOLS.FIRE, SCHOOLS.SORCERY]
    def __init__(self, caster):
        super().__init__(caster)

    def on_init(self):
        self.power = 6
        self.range = 3
        self.action_cost = 2
        self.max_charges = 10
        self.name = "Fire Breath"
        self.description = f"Spray fire, dealing {self.power} damage in a {self.range} tile long cone."
        self.level = 1
        self.schools = [SCHOOLS.FIRE, SCHOOLS.SORCERY]
        self.upgrades = []
        self.recovery_time = 5

        self.requires_line_of_sight = False

        self.angle = 60

    def get_description(self):
        return f"Spray fire, dealing {self.power} damage in a {self.range} tile long cone, yeah."

    def on_cast(self, target):
        affected_tiles = compute_cone_tiles(self.caster.position, target, self.angle, self.range + 0.5, include_origin_tile=False)
        affected_tiles = self.caster.world.filter_line_of_effect(self.caster.position, affected_tiles, include_blocking_tile=True)
        for tile in affected_tiles:
            damage_tile(self.caster.world, self.caster, tile, self.power, DAMAGE_TYPES.FIRE)
            self.caster.world.show_effect(tile, "fire_explosion", (euclidean_distance(self.caster.position, tile)*500))

    def get_impacted_tiles(self, target):
        affected_tiles = compute_cone_tiles(self.caster.position, target, self.angle, self.range + 0.5, include_origin_tile=False)
        affected_tiles = self.caster.world.filter_line_of_effect(self.caster.position, affected_tiles, include_blocking_tile=True)
        return affected_tiles

class SeismicJolt(Spell):
    name = "Seismic Jolt"
    schools = [SCHOOLS.EARTH, SCHOOLS.SORCERY]
    def __init__(self, caster):
        super().__init__(caster)

    def on_init(self):
        self.power = 9
        self.range = 0
        self.radius = 1

        self.action_cost = 2
        self.max_charges = 7
        self.name = "Seismic Jolt"
        self.description = f"Deal {self.power} bludgeoning damage to enemies in a {self.radius} tile radius and push them back one tile."
        self.level = 2
        self.schools = [SCHOOLS.EARTH, SCHOOLS.SORCERY]
        self.upgrades = []
        self.recovery_time = 10

        self.should_target_self = False
        self.should_target_allies = False
        self.should_target_empty = False

    def get_description(self):
        return f"Deal {self.power} bludgeoning damage to enemies in a {self.radius} tile radius and push them back one tile."

    # Overwriting this makes it so much faster
    def get_targetable_tiles(self):
        return disk(self.caster.position, self.radius, include_origin_tile=False)

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



class RaiseLongdead(Spell):
    name = "Raise Longdead"
    schools = [SCHOOLS.CONJURATION, SCHOOLS.DEATH]
    def __init__(self, caster):
        super().__init__(caster)

    def on_init(self):
        self.power = 5
        self.range = 1
        self.radius = 1
        self.num_targets = 1
        self.action_cost = 2
        self.max_charges = 3
        self.current_charges = self.max_charges
        self.duration = 20
        self.name = "Raise Longdead"

        self.level = 1
        self.schools = [SCHOOLS.CONJURATION, SCHOOLS.DEATH]
        self.upgrades = []
        self.recovery_time = 10

        self.minion_damage = 2
        self.minion_health = 5
        self.minion_count = 1

        self.description = f"Within the earth rests the bones of countless generations. Long dead, these skeletal servants are not very powerful, but they are always available. The skeletons have {self.minion_health} hit points and deal {self.minion_damage} damage per attack."

        self.cannot_target_entity = True
        self.can_target_ground = True
        self.can_target_water = False
        self.can_target_void = False
        self.can_target_wall = False

        self.should_target_empty = True

    def get_description(self):
        return f"Within the earth rests the bones of countless generations. Long dead, these skeletal servants are not very powerful, but they are always available. The skeletons have {self.minion_health} hit points and deal {self.minion_damage} damage per attack."

    def on_cast(self, target):
        entity_class = self.caster.world.game.available_entities["Longdead"]
        summon_minions(self, entity_class, self.minion_count, target, duration=self.duration)




class WordOfHealing(Spell):
    name = "Word of Healing"
    schools = [SCHOOLS.HOLY, SCHOOLS.NATURE]
    def __init__(self, caster):
        super().__init__(caster)

        self.power = 10
        self.range = 6
        self.radius = 1
        self.action_cost = 2
        self.max_charges = 3
        self.name = "Word of Healing"
        self.description = f"Heal target living creature up to {self.range} tiles away by {self.power} hit points."
        self.level = 1
        self.schools = [SCHOOLS.HOLY, SCHOOLS.NATURE]
        self.upgrades = []
        self.recovery_time = 15

        self.can_target_self = False
        self.must_target_entity = False

        self.should_target_allies = True
        self.should_target_empty = False

        self.on_init()

    def get_description(self):
        return f"Heal target living creature up to {self.range} tiles away by {self.power} hit points."

    def get_impacted_tiles(self, target):
        return disk(target, self.radius, include_origin_tile=True)

    def should_cast(self):
        tiles = []
        for entity in self.caster.world.active_entities.values:
            if entity is not None:
                if entity.allegiance == self.caster.allegiance and entity.hp < entity.max_hp and ENTITY_TAGS.LIVING in entity.tags and self.can_cast(entity.position):
                    tiles.append(entity.position)
        return tiles

    def cast(self, target):
        for tile in disk(target, self.radius, include_origin_tile=True):
            entity = self.caster.world.active_entities[tile]
            if not entity is None:
                if entity.allegiance == self.caster.allegiance and ENTITY_TAGS.LIVING in entity.tags:
                    heal(self, entity, self.power)


class BluntMeleeAttack(Spell):
    name = "Bludgeoning Strike"
    def __init__(self, caster):
        super().__init__(caster)

    def on_init(self):
        self.name = "Bludgeoning Strike"
        self.description = "Striking with a club, fist or similar implement to deal bludgeoning damage."
        self.power = 2
        self.range = 1
        self.action_cost = 1
        self.max_charges = 100
        self.level = 0
        self.schools = []
        self.recovery_time = 1

    def get_description(self):
        return f"Striking with a club, fist or similar implement to deal {self.power} bludgeoning damage."


    def on_cast(self, target):
        if not self.caster.world.active_entities[target] is None:
            subject = self.caster.world.active_entities[target]
            damage_entity(self, subject, self.power, DAMAGE_TYPES.BLUDGEONING)

class SlashingMeleeAttack(Spell):
    name = "Slashing Strike"
    def on_init(self):
        self.name = "Slashing Strike"
        self.description = "Striking with a sword, claw or similar implement to deal slashing damage."
        self.power = 2
        self.range = 1
        self.action_cost = 1
        self.max_charges = 100
        self.level = 0
        self.schools = []
        self.recovery_time = 1

    def get_description(self):
        return f"Striking with a sword, claw or similar implement to deal {self.power} slashing damage."

    def on_cast(self, target):
        if not self.caster.world.active_entities[target] is None:
            subject = self.caster.world.active_entities[target]
            damage_entity(self, subject, self.power, DAMAGE_TYPES.SLASHING)

class PiercingMeleeAttack(Spell):
    name = "Piercing Strike"
    def on_init(self):
        self.name = "Piercing Strike"
        self.description = "Striking with a dagger, arrow or similar implement to deal piercing damage."
        self.power = 2
        self.range = 1
        self.action_cost = 1
        self.max_charges = 100
        self.level = 0
        self.schools = []
        self.recovery_time = 1

    def get_description(self):
        return f"Striking with a dagger, arrow or similar implement to deal {self.power} piercing damage."

    def on_cast(self, target):
        if not self.caster.world.active_entities[target] is None:
            subject = self.caster.world.active_entities[target]
            damage_entity(self, subject, self.power, DAMAGE_TYPES.PIERCING)

class FireSpit(Spell):
    name = "Fire Spit"
    def __init__(self, caster):
        super().__init__(caster)

    def on_init(self):
        self.power = 3
        self.range = range
        self.name = "Fire Spit"
        self.description = "A small spittle of fire that burns a single target at range."
        self.max_charges = 100
        self.recovery_time = 1

    def get_description(self):
        return f"A small spittle of fire that burns a single target at {self.range} range for {self.power} damage."

    def on_cast(self, target):
        subject = self.caster.world.active_entities[target]
        damage_entity(self, subject, self.power, DAMAGE_TYPES.FIRE)

class LightningBolt(Spell):
    schools = [SCHOOLS.LIGHTNING, SCHOOLS.SORCERY]
    name = "Lightning Bolt"
    def on_init(self):
        self.power = 8
        self.range = 9

        self.name = "Lightning Bolt"
        self.description = f"Fire a bolt of lightning that deals {self.power} Lightning damage to all targets it passes through."
        self.level = 1
        self.schools = [SCHOOLS.LIGHTNING, SCHOOLS.SORCERY]
        self.upgrades = []
        self.recovery_time = 8
        self.max_charges = 14

        self.requires_line_of_sight = False

    def get_description(self):
        return f"Fire a bolt of lightning that deals {self.power} Lightning damage to all targets it passes through."

    def on_cast(self, target):
        affected_tiles = bresenham(self.caster.position, target)
        affected_tiles.remove(self.caster.position)
        affected_tiles = self.caster.world.filter_line_of_effect(self.caster.position, affected_tiles, include_blocking_tile=True)
        for tile in affected_tiles:
            damage_tile(self.caster.world, self.caster, tile, self.power, DAMAGE_TYPES.LIGHTNING)

    def get_impacted_tiles(self, target):
        affected_tiles = bresenham(self.caster.position, target)
        affected_tiles.remove(self.caster.position)
        return affected_tiles


class TidalWave(Spell):
    name = "Tidal Wave"
    schools = [SCHOOLS.WATER, SCHOOLS.SORCERY]
    def on_init(self):
        self.power = 20
        self.range = 9
        self.radius = 5

        self.name = "Tidal Wave"
        self.description = f"Release a wave of crushing force that damages and pushes away enemies in a wide line."
        self.level = 3
        self.schools = [SCHOOLS.WATER, SCHOOLS.SORCERY]
        self.upgrades = []
        self.recovery_time = 10
        self.max_charges = 7

        self.requires_line_of_sight = False

    def get_description(self):
        return f"Release a wave of crushing force that deals {self.power} damage and pushes away enemies in a wide line up to {self.range} long."

    def on_cast(self, target):
        affected_tiles = wide_line(self.caster.position, target, self.radius)
        affected_tiles.remove(self.caster.position)
        affected_tiles = sorted(affected_tiles, key=lambda tile: euclidean_distance(tile, self.caster.position))
        affected_tiles = list(reversed(affected_tiles))
        for tile in affected_tiles:
            damage_tile(self.caster.world, self.caster, tile, self.power, DAMAGE_TYPES.BLUDGEONING)
            push_tile(self.caster.world, self.caster.position, tile, 3, push_walls=True)


    def get_impacted_tiles(self, target):
        affected_tiles = wide_line(self.caster.position, target, self.radius)
        affected_tiles.remove(self.caster.position)
        return affected_tiles

class PoisonMist(Spell):
    name = "Poison Mist"
    schools = [SCHOOLS.NATURE, SCHOOLS.WATER, SCHOOLS.AIR]
    def on_init(self):
        self.power = 2
        self.range = 8
        self.radius = 2
        self.duration = 10

        self.name = "Poison Mist"
        self.description = f"Create a poisonous mist in a {self.radius} tile area for {self.duration} turns, dealing {self.power} damage to creatures within each turn."
        self.level = 2
        self.schools = [SCHOOLS.NATURE, SCHOOLS.WATER, SCHOOLS.AIR]
        self.upgrades = []

        self.recovery_time = 8
        self.max_charges = 4

    def get_description(self):
        return f"Create a poisonous mist in a {self.radius} tile area for {self.duration} turns, dealing {self.power} damage to creatures within each turn."

    def on_cast(self, target):
        affected_tiles = disk(target, self.radius, include_origin_tile=True)
        for tile in affected_tiles:
            tile = (int(tile[0]), int(tile[1]))
            mist = tile_effects.PoisonMist(self.caster.world, self.caster, tile, True, self.duration)
            self.caster.world.place_tile_effect(mist, tile)

    def get_impacted_tiles(self, target):
        affected_tiles = disk(target, self.radius, include_origin_tile=True)
        return affected_tiles


class SummonMonster(Spell):
    name = "Summon Monster"
    def __init__(self, caster, monster_type, monster_count, cooldown):
        self.monster_type = monster_type
        self.monster_name = self.monster_type(caster.world).name
        self.monster_count = monster_count
        super().__init__(caster)
        self.recovery_time = cooldown

    def on_init(self):
        self.name = f"Summon {self.monster_name}"
        self.description = f"Summons a {self.monster_name}."
        self.level = 10
        #self.schools = [SCHOOLS.NATURE, SCHOOLS.WATER, SCHOOLS.AIR]
        self.max_charges = 1
        self.action_cost = 1

    def get_description(self):
        return f"Summons a {self.monster_name}."

    def on_cast(self, target):
        #print(f"Summoning {self.monster_name}. Current charges: {self.current_charges}, remaining recovery turns: {self.recovery_turns_left}, recovery time: {self.recovery_time}")
        self.caster.world.summon_entity_from_class(self.monster_type, self.monster_count, self.caster.position, self.caster.allegiance)

    def should_cast(self):
        return [self.caster.position]


class RegenerationSpell(Spell):
    name = "Regeneration"
    schools = [SCHOOLS.NATURE, SCHOOLS.HOLY]
    def on_init(self):
        self.duration = 10
        self.power = 3
        self.level = 3
        self.max_charges = 3
        self.recovery_time = 10
        self.name = "Regeneration"
        self.schools = [SCHOOLS.NATURE, SCHOOLS.HOLY]
        self.description = f"Target living creature regains {self.power} hit points at the start of each of its turns for the next {self.duration} turns."
        # Make it able to hit other things with upgrades.

        self.requires_line_of_sight = True
        self.can_target_self = False
        self.must_target_entity = True
        self.can_target_ground = True
        self.can_target_water = True
        self.can_target_void = True
        self.can_target_wall = True

        self.target_must_have_tag = [ENTITY_TAGS.LIVING]

        self.should_target_enemies = False
        self.should_target_self = False
        self.should_target_allies = True
        self.should_target_empty = False

    def get_description(self):
        return f"Target living creature regains {self.power} hit points at the start of each of its turns for the next {self.duration} turns."

    def on_cast(self, target):
        subject = self.caster.world.active_entities[target]
        if subject is not None:
            if ENTITY_TAGS.LIVING in subject.tags:
                buff = Regeneration(self.caster, subject)
                buff.duration = self.duration
                buff.power = self.power
                apply_passive(subject, buff)

    def should_cast(self):
        should_cast_tiles = []
        area = disk(self.caster.position, self.radius)
        for tile in area:
            subject = self.caster.world.total_entities[tile]
            if subject is not None:
                if subject.allegiance == self.caster.allegiance and ENTITY_TAGS.LIVING in subject.tags and not subject.has_passive("Regeneration"):
                    should_cast_tiles.append(tile)
        return should_cast_tiles



class ArcaneLessonAttack(Spell):
    name = "Arcane Bolt"
    schools = [SCHOOLS.ASTRAL]
    def on_init(self):
        self.power = 5
        self.level = 2
        self.action_cost = 2
        self.max_charges = 1
        self.recovery_time = 3
        self.range = 5
        self.schools = [SCHOOLS.ASTRAL]
        self.name = "Arcane Bolt"
        self.description = f"A rudimentary display of magic - a bolt of pure arcane energy that deals {self.power} damage."

    def get_description(self):
        return f"A rudimentary display of magic - a bolt of pure arcane energy that deals {self.power} damage."

    def on_cast(self, target):
        subject = self.caster.world.active_entities[target]
        damage_entity(self, subject, self.power, DAMAGE_TYPES.ARCANE)
        self.caster.world.show_projectile(self.caster.position, target, "arcane_projectile", 0)


class ArcaneLesson(Spell):
    name = "Arcane Lesson"
    schools = [SCHOOLS.ASTRAL, SCHOOLS.ENCHANTMENT]
    def on_init(self):
        self.duration = 22
        self.radius = 8
        self.range = 6
        self.power = 20
        self.level = 4
        self.max_charges = 3
        self.recovery_time = 12
        self.name = "Arcane Lesson"
        self.schools = [SCHOOLS.ASTRAL, SCHOOLS.ENCHANTMENT]
        self.description = f"Friendly creatures within {self.radius} tiles learn a {self.range} ranged spell dealing {self.power} Arcane damage with a 3 turn cooldown for {self.duration} turns. Like most spells, it takes 2 actions to cast."

        # Upgrade to give the attack small AoE.

        self.requires_line_of_sight = True
        self.can_target_self = True
        self.must_target_entity = True
        self.can_target_ground = True
        self.can_target_water = True
        self.can_target_void = True
        self.can_target_wall = True

        self.should_target_enemies = False
        self.should_target_self = True
        self.should_target_allies = False
        self.should_target_empty = False

    def get_description(self):
        return f"Friendly creatures within {self.radius} tiles learn a {self.range} ranged spell dealing {self.power} Arcane damage with a 3 turn cooldown for {self.duration} turns. Like most spells, it takes 2 actions to cast."

    def on_cast(self, target):
        area = disk(self.caster.position, self.radius, include_origin_tile=False)
        for tile in area:
            subject = self.caster.world.total_entities[tile]
            if subject is not None:
                if subject.allegiance == self.caster.allegiance:
                    bolt_spell = ArcaneLessonAttack(subject)
                    bolt_spell.power = self.power
                    bolt_spell.range = self.range

                    buff = GrantActive(self.caster, subject, bolt_spell)
                    buff.name = "Arcane Lesson"
                    buff.description = "This creature has learned rudimentary magic and can fire bolts of magical energy."
                    buff.duration = self.duration
                    buff.power = self.power
                    apply_passive(subject, buff)

    def should_cast(self):
        area = disk(self.caster.position, self.radius)
        for tile in area:
            subject = self.caster.world.total_entities[tile]
            if subject is not None:
                if subject.allegiance == self.caster.allegiance and not subject.has_passive("Arcane Lesson"):
                    return self.caster.position
        return []

    def get_impacted_tiles(self, target):
        affected_tiles = disk(self.caster.position, self.radius, include_origin_tile=False)
        return affected_tiles


class Flickerstep(Spell):
    name = "Flickerstep"
    schools = [SCHOOLS.ASTRAL]
    def on_init(self):
        self.range = 8
        self.action_cost = 2
        self.max_charges = 5
        self.name = "Flickerstep"
        self.description = "Step through the space between space, emerging somewhere else nearby."
        self.level = 1
        self.schools = [SCHOOLS.ASTRAL]
        self.upgrades = []
        self.recovery_time = 5

        # Upgrade for removing LoS requirement.
        # Upgrade for lowering action cost by 1.

        self.requires_line_of_sight = True
        self.can_target_self = False
        self.must_target_entity = False
        self.cannot_target_entity = True
        self.can_target_ground = True
        self.can_target_water = True
        self.can_target_void = True
        self.can_target_wall = False

        self.should_target_enemies = False
        self.should_target_self = False
        self.should_target_allies = False
        self.should_target_empty = True

    def get_description(self):
        return f"Step through the space between space, emerging up to {self.range} tiles away."

    def get_targetable_tiles(self):
        tiles = []
        for tile in disk(self.caster.position, self.range):
            if self.caster.can_move(tile) and self.caster.can_see(tile):
                tiles.append(tile)
        return tiles

    def on_cast(self, target):
        if self.caster == self.caster.world.game.pc:
            self.caster.world.move_player(target)
        else:
            self.caster.world.move_entity(self.caster, target)

    def should_cast(self):
        # This basically means the AI targets random tiles with the spell, and I think that's fine for now.
        return self.get_targetable_tiles()


class Decrepify(Spell):
    name = "Decrepify"
    schools = [SCHOOLS.DEATH, SCHOOLS.ENCHANTMENT]
    def on_init(self):
        self.range = 13
        self.action_cost = 2
        self.max_charges = 5
        self.radius = 4
        self.duration = 9
        #self.name = "Decrepify"
        self.description = f"Burden enemies with the weight of time, slowing them down for {self.duration} turns. Does not affect the undead."
        self.level = 2
        self.schools = [SCHOOLS.DEATH, SCHOOLS.ENCHANTMENT]
        self.upgrades = []
        self.recovery_time = 10

        # Upgrade for allowing affecting undead.

        self.requires_line_of_sight = True
        self.can_target_self = False
        self.must_target_entity = False
        self.cannot_target_entity = False
        self.can_target_ground = True
        self.can_target_water = True
        self.can_target_void = True
        self.can_target_wall = False

        self.should_target_enemies = True
        self.should_target_self = False
        self.should_target_allies = False
        self.should_target_empty = False

    def get_description(self):
        # Can add an if here for a future upgrade that makes it affect undead.
        return f"Burden enemies with the weight of time, slowing them down for {self.duration} turns. Does not affect the undead."

    def on_cast(self, target):
        tiles = disk(target, self.radius, True)
        for tile in tiles:
            entity = self.caster.world.total_entities[tile]
            if entity is not None:
                if ENTITY_TAGS.UNDEAD not in entity.tags:
                    debuff = Slow(self.caster, entity, duration=self.duration)
                    effects.apply_passive(entity, debuff)

    def should_cast(self):
        should_cast_tiles = []
        area = disk(self.caster.position, self.radius)
        for tile in area:
            subject = self.caster.world.total_entities[tile]
            if subject is not None:
                if subject.allegiance != self.caster.allegiance and subject.allegiance != ALLEGIANCES.NEUTRAL and ENTITY_TAGS.UNDEAD not in subject.tags and not subject.has_passive("Slow"):
                    should_cast_tiles.append(tile)
        return should_cast_tiles
