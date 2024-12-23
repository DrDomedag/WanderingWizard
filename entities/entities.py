import items
from ui import tint_sprite
from util import *
import random
from collections import defaultdict

from passives import *
import spells
from effects import *
from items import *


def get_all_entities():
    return {
        "Longdead": Longdead,
        "Goblin": Goblin,
        "Goblin Shaman": GoblinShaman,
        "Troll": Troll,
        "Kindling": Kindling,
        "Friar": Friar,
        "Knight": Knight,
        "Homunculus": Homunculus,

    }


class Entity:
    def __init__(self, world):
        self.world = world

        self.asset_name = "unknown"
        self.current_frame = 0
        self.animation_frames = 30
        self.asset_index = 0

        self.layer = "entity"

        self.name = "Nameless Entity"
        self.description = "This entity cannot be described."
        self.max_hp = 10
        self.actives = []
        self.passives = []
        self.actions_per_round = 3
        self.current_actions = 0
        self.allegiance = ALLEGIANCES.NEUTRAL
        self.resistances = defaultdict(lambda: 0)

        self.tags = []

        self.stationary = False
        self.flammable = True
        self.walking = True
        self.flying = False
        self.swimming = False
        self.intangible = False
        self.position = None
        self.owner = None

        self.opens_doors = True

        self.expires = False
        self.duration = 0

        self.items = []

        self.on_init()

        self.asset = world.game.assets[self.asset_name]
        self.idle_asset = [self.asset]
        self.acting_asset = [self.asset]
        self.greyscale_asset = desaturate_sprite(self.asset)
        self.idle_greyscale_asset = [desaturate_sprite(ia) for ia in self.idle_asset]
        self.acting_greyscale_asset = [desaturate_sprite(aa) for aa in self.acting_asset]

        self.load_assets()

        self.hp = self.max_hp

        self.post_init()

    def on_init(self):
        pass

    def post_init(self):
        pass

    def has_passive(self, name):
        for passive in self.passives:
            if passive.name == name:
                return True
        return False

    def load_assets(self):
        i = 1
        if self.world.game.assets[f"{self.asset_name}_idle_{i}"]:
            self.idle_asset = []
            self.idle_greyscale_asset = []
            while self.world.game.assets[f"{self.asset_name}_idle_{i}"]:
                self.idle_asset.append(self.world.game.assets[f"{self.asset_name}_idle_{i}"])
                self.idle_greyscale_asset.append(desaturate_sprite(self.world.game.assets[f"{self.asset_name}_idle_{i}"]))
                i += 1
        i = 1
        if self.world.game.assets[f"{self.asset_name}_acting_{i}"]:
            self.acting_asset = []
            self.acting_greyscale_asset = []
            while self.world.game.assets[f"{self.asset_name}_acting_{i}"]:
                self.acting_asset.append(self.world.game.assets[f"{self.asset_name}_acting_{i}"])
                self.acting_greyscale_asset.append(desaturate_sprite(self.world.game.assets[f"{self.asset_name}_acting_{i}"]))
                i += 1


    def update(self, greyscale=False):
        if greyscale:
            self.asset = self.idle_greyscale_asset[self.asset_index]
        else:
            self.current_frame += 1
            # If idle. Similar logic for if acted later.
            if self.current_frame >= self.animation_frames:
                self.current_frame = 0
                self.asset_index = (self.asset_index + 1) % len(self.idle_asset)
                self.asset = self.idle_asset[self.asset_index]

    def draw(self, display, screen_coords):
        # print(f"Rendering {entity.name} at game coords: {entity_coords}, self-registered coords: {entity.position} screen-centered x: {(entity_coords[0] - self.world.current_coordinates[0])}, screen x: {self.SPRITE_SIZE * (entity_coords[0] - self.world.current_coordinates[0]) + self.centre_x}, screen-centered y: {(entity_coords[1] - self.world.current_coordinates[1]) + self.centre_y}, screen y: {self.SPRITE_SIZE * (entity_coords[1] - self.world.current_coordinates[1]) + self.centre_y}")
        display.blit(self.asset, screen_coords)


    def start_of_turn(self):
        #print(f"{self.name}'s turn started.")
        self.current_actions = self.actions_per_round
        for p in self.passives:
            p.start_of_turn_effect()
            p.increment_duration()
        for active in self.actives:
            if active.current_charges < active.max_charges:
                active.recovery_turns_left -= 1
                if active.recovery_turns_left <= 0 and active.current_charges < active.max_charges:
                    active.current_charges += 1
                    active.recovery_turns_left += active.recovery_time


    def can_see(self, target):
        return self.world.can_see(self.position, target)

    def can_move(self, target):
        return self.world.check_can_move(self, target)

    def can_be_pushed(self, target):
        return self.world.check_can_be_pushed(self, target)

    def move(self, target):
        return self.world.move_entity(self, target)

    def on_suffer_damage(self, source, amount, damage_type):
        #print(f"{self.name} took {amount} damage from {source.name}.")
        for passive in self.passives:
            passive.on_suffer_damage_effect(source, amount, damage_type)
        if self.hp <= 0:
            self.die()

    def on_cause_heal(self, target, amount):
        for passive in self.passives:
            passive.on_cause_heal_effect(target, amount)

    def on_healed(self, source, amount):
        for passive in self.passives:
            passive.on_healed_effect(source, amount)


    def on_death(self):
        for passive in self.passives:
            passive.on_death_effect()
        for item in self.items:
            self.world.place_item(item, self.position)

    def die(self):
        self.world.total_entities[self.position] = None
        self.world.active_entities[self.position] = None
        self.on_death()

    def expire(self):
        self.world.total_entities[self.position] = None
        self.world.active_entities[self.position] = None
        self.on_expire()

    def act(self):
        pygame.event.pump() # Since there are a lot of "act" in a row during the enemy turn in particular, this should help keep the game from going unresponsive.
        acted = False
        actives = random.sample(self.actives, len(self.actives))
        actives.sort(key=lambda spell: spells.Spell.level)
        final_actives = []
        for active in actives:
            if not(len(active.should_cast()) <= 0 or active.current_charges <= 0):
                final_actives.append(active)
        if len(final_actives) > 0:
            self.use_active(final_actives[0])
        # If we can't meaningfully use any of our abilities, we move towards the closest enemy.
        enemies = find_and_sort_enemies_by_distance(self)

        while len(enemies) > 0 and not acted and not self.stationary:
            # Move
            target = enemies.pop()
            path = find_path(self, target.position)
            if len(path) > 0:
                self.move(path[1])
                self.current_actions -= 1
                acted = True

        if acted == False:
            # If we can't use any abilities and we can't find a path towards any enemy, we just freeze.
            self.current_actions -= 1

    def use_active(self, active):
        targets = active.should_cast()

        if len(targets) > 0:
            target = random.choice(targets)
            active.cast(target)
            return
        else:
            print(f"Found no suitable empty tile to target with {active.name}")


    def on_expire(self):
        pass

    def end_of_turn(self):
        if self.expires:
            self.duration -= 1
            if self.duration <= 0:
                self.expire()


class PC(Entity):
    def __init__(self, world):
        super().__init__(world)
        self.innovation_points = 0
        self.iterations = []

    def on_init(self):

        self.name = "Wizard"
        self.max_hp = 50
        self.hp = self.max_hp
        self.allegiance = ALLEGIANCES.PLAYER_TEAM
        self.asset_name = "wizard"
        self.description = "The Wandering Wizard."
        self.tags = [ENTITY_TAGS.LIVING]
        self.load_assets()
        self.current_actions = self.actions_per_round


    def move(self, target):
        return self.world.move_player(target)

    def on_death(self):
        self.world.game.game_over()

    def add_incrementation(self, iteration):
        self.iterations.append(iteration)

    def start_of_turn(self):
        super().start_of_turn()
        is_enemy = False
        for entity in self.world.active_entities.values():
            if entity is not None:
                if entity.allegiance != ALLEGIANCES.NEUTRAL and entity.allegiance != self.allegiance:
                    is_enemy = True
                    break
        if not is_enemy:
            for active in self.actives:
                if active.current_charges < active.max_charges:
                    active.recovery_turns_left = active.recovery_time
                    active.current_charges = active.max_charges


class Spawner(Entity):
    def __init__(self, world, monster_type, monster_count, cooldown, colour):
        self.monster_type = monster_type
        super().__init__(world)

        self.actives.append(spells.SummonMonster(self, monster_type, monster_count, cooldown))
        self.asset = tint_sprite(self.asset, colour)

    def on_init(self):
        self.stationary = True
        self.max_hp = 25
        self.asset_name = "spawner"
        self.name = "Spawner"
        self.description = "A one-way portal from another realm through which pours hostile creatures."
        self.actions_per_round = 1

class Troll(Entity):

    def on_init(self):
        self.name = "Troll"
        self.description = "Trolls are cunning beings whose wounds regenerate."
        self.max_hp = 30
        self.tags = [ENTITY_TAGS.LIVING]
        self.passives.append(TrollRegen(self, self))
        self.asset_name = "troll"
        attack = spells.BluntMeleeAttack(self)
        attack.power = 5
        attack.name = "Fist"
        self.actives.append(attack)

class Goblin(Entity):
    def on_init(self):
        self.name = "Goblin"
        self.description = "Goblins are barely sentient - the humanoid equivalent of an amoeba."
        self.max_hp = 5
        self.tags = [ENTITY_TAGS.LIVING]
        self.asset_name = "goblin"
        attack = spells.PiercingMeleeAttack(self)
        attack.power = 1
        attack.name = "Crude Spear"
        self.actives.append(attack)

class GoblinShaman(Entity):
    def on_init(self):
        self.name = "Goblin Shaman"
        self.description = "That a creature of goblin intellect is capable of magic is a greater marvel than the wonder that is that very magic."
        self.max_hp = 10
        self.tags = [ENTITY_TAGS.LIVING]
        self.asset_name = "goblin_shaman"
        self.actives.append(spells.RaiseLongdead(self))
        melee_attack = spells.BluntMeleeAttack(self)
        melee_attack.power = 1
        melee_attack.name = "Staff"
        self.actives.append(melee_attack)
        self.items.append(items.Spellbook(self.world, 1, self.position))

class Treant(Entity):
    def on_init(self):
        self.name = "Treant"
        self.description = "A living tree, undoubtedly angered at the disturbance of its home."
        self.max_hp = 25
        self.actions_per_round = 2
        self.asset_name = "tree"
        self.resistances = RESISTANCE_SETS.SENTIENT_WOOD

        regen = Regeneration(self, self)
        regen.nature = INHERENT

        self.passives.append(regen)

        melee_attack = spells.BluntMeleeAttack(self)
        melee_attack.power = 8
        melee_attack.name = "Branch"
        self.actives.append(melee_attack)

class Longdead(Entity):
    def on_init(self):
        self.name = "Longdead"
        self.description = "This is a person who died long ago, and whose bones were swallowed by the earth, now called to serve a necromancer."
        self.max_hp = 5
        self.tags = [ENTITY_TAGS.UNDEAD]

        self.resistances[DAMAGE_TYPES.BLUDGEONING] = -100
        self.resistances[DAMAGE_TYPES.PIERCING] = 75
        self.resistances[DAMAGE_TYPES.FIRE] = 50
        self.resistances[DAMAGE_TYPES.COLD] = 100
        self.resistances[DAMAGE_TYPES.POISON] = 100
        self.resistances[DAMAGE_TYPES.DARK] = 50
        self.resistances[DAMAGE_TYPES.LIGHT] = -100
        self.resistances[DAMAGE_TYPES.PSYCHIC] = 100

        self.asset_name = "longdead"
        attack = spells.SlashingMeleeAttack(self)
        attack.name = "Rusted knife"
        attack.power = 2
        self.actives.append(attack)

class Kindling(Entity):
    def on_init(self):
        self.name = "Kindling"
        self.description = "Curious goblinoid creatures touched by the element of fire, the Kindling live in small packs and often worship flames at crude stone shrines."
        self.max_hp = 5
        self.tags = [ENTITY_TAGS.LIVING, ENTITY_TAGS.ELEMENTAL]

        self.resistances[DAMAGE_TYPES.FIRE] = 100
        self.resistances[DAMAGE_TYPES.COLD] = -100
        self.resistances[DAMAGE_TYPES.POISON] = 50

        self.asset_name = "kindling"

        melee_attack = spells.BluntMeleeAttack(self)
        melee_attack.power = 2
        melee_attack.name = "Fist"
        self.actives.append(melee_attack)

        fire_spit = spells.FireSpit(self)
        fire_spit.power = 3
        fire_spit.range = 4
        self.actives.append(fire_spit)

class Friar(Entity):
    def on_init(self):
        self.name = "Friar"
        self.description = "Faithful keeper of the flock, humble spellcaster, and eyes and ears of the church in the provinces. A good life - at least until the gods went mad."

        self.opens_doors = False

        self.max_hp = 15
        self.tags = [ENTITY_TAGS.LIVING]
        self.resistances[DAMAGE_TYPES.LIGHT] = 50

        self.asset_name = "friar"

        melee_attack = spells.BluntMeleeAttack(self)
        melee_attack.power = 2
        melee_attack.name = "Fist"
        self.actives.append(melee_attack)

        fire_spit = spells.FireSpit(self)
        fire_spit.power = 5
        fire_spit.range = 4
        fire_spit.max_charges = 1
        fire_spit.recovery_time = 2
        fire_spit.description = "A small bolt of holy energy."
        fire_spit.get_description = lambda: f"A small bolt of holy energy."
        fire_spit.name = "Holy Bolt"
        self.actives.append(fire_spit)

        self.actives.append(spells.WordOfHealing(self))

        self.items.append(items.Spellbook(self.world, 2, self.position, schools=[SCHOOLS.LIGHT]))



class Knight(Entity):
    def on_init(self):
        self.name = "Knight"
        self.description = "Protector of the realm, keeper of the law and guardian of the innocent. An honourable life - at least until the gods went mad."

        self.opens_doors = False

        self.max_hp = 20
        self.tags = [ENTITY_TAGS.LIVING]
        self.resistances[DAMAGE_TYPES.LIGHT] = 50
        self.resistances[DAMAGE_TYPES.BLUDGEONING] = 25
        self.resistances[DAMAGE_TYPES.SLASHING] = 50
        self.resistances[DAMAGE_TYPES.PIERCING] = 50

        self.asset_name = "knight"

        melee_attack = spells.SlashingMeleeAttack(self)
        melee_attack.power = 5
        melee_attack.name = "Broadsword"
        self.actives.append(melee_attack)

        self.actives.append(spells.KnightSmite(self))




class Homunculus(Entity):
    def on_init(self):
        self.name = "Homunculus"
        self.description = "A small mage's assistant made of its master's flesh."
        self.max_hp = 15
        self.tags = [ENTITY_TAGS.LIVING, ENTITY_TAGS.CONSTRUCT]

        self.asset_name = "homunculus"

        melee_attack = spells.BluntMeleeAttack(self)
        melee_attack.power = 2
        melee_attack.name = "Fist"
        self.actives.append(melee_attack)

        regen = Regeneration(self, self)
        regen.power = 1
        regen.nature = INHERENT
        self.passives.append(regen)