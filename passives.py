import effects
from effects import damage_entity
from util import *


INHERENT = 0
BLESSING = 1
CURSE = 2


class Passive:
    def __init__(self, source, subject, duration=None):
        self.duration = duration
        self.name = "Unnamed passive ability"
        self.description = "This passive ability defies description."
        self.nature = BLESSING
        self.source = source
        self.subject = subject
        self.status_modifiers = []
        self.power = 1
        self.range = 1
        self.radius = 1
        self.on_init()

    def on_init(self):
        pass

    def get_description(self):
        return self.description

    def increment_duration(self):
        if self.duration is None:
            pass
        elif self.duration > 0:
            self.duration -= 1
        else:
            self.on_expire_effect()
            # Remove from owner, delete self
            self.subject.passives.remove(self)

    def apply_status_modifiers(self):
        pass

    def start_of_turn_effect(self):
        pass

    def end_of_turn_effect(self):
        pass

    def on_suffer_damage_effect(self, source, amount, damage_type):
        pass

    def on_deal_hit_effect(self):
        pass

    def on_suffer_hit_effect(self):
        pass

    def on_death_effect(self):
        pass

    def on_apply_effect(self):
        pass

    def on_expire_effect(self):
        pass

    def on_dispelled_effect(self):
        pass

    def on_cause_heal_effect(self, target, amount):
        pass

    def on_healed_effect(self, source, amount):
        pass




class Regeneration(Passive):
    def on_init(self):
        self.name = "Regeneration"
        self.nature = BLESSING
        self.power = 5
        self.description = f"This creature gradually heals all injury, and it regains {self.power} hit points at the start of each of its turns."

    def get_description(self):
        return f"This creature gradually heals all injury, and it regains {self.power} hit points at the start of each of its turns."

    def start_of_turn_effect(self):
        effects.heal(self.source, self.subject, self.power)
        self.subject.world.show_effect(self.subject.position, "nature_explosion", 0)


class TrollRegen(Passive):
    def on_init(self):
        self.name = "Troll Regeneration"
        self.nature = INHERENT
        self.power = 5
        self.description = f"This troll's wounds close at a terrifying rate, and it regains {self.power} hit points at the start of each of its turns."

    def get_description(self):
        return f"This troll's wounds close at a terrifying rate, and it regains {self.power} hit points at the start of each of its turns."

    def start_of_turn_effect(self):
        effects.heal(self.source, self.subject, self.power)


class SpellChargeRecoveryBoost(Passive):
    def __init__(self, source, subject, school):
        self.school = school
        super().__init__(source, subject)

    def on_init(self):
        self.name = f"{SCHOOL_NAMES.school} Spell Recovery Boost"
        self.nature = INHERENT
        self.power = 1
        self.description = f"You are particularly adept at quickly recovering {SCHOOL_NAMES.school} spell slots, gaining a +{self.power} bonus to their recovery speed. (This usually means recovering them twice as fast.)"

    def get_description(self):
        return f"You are particularly adept at quickly recovering {SCHOOL_NAMES.school} spell slots, gaining a +{self.power} bonus to their recovery speed. (This usually means recovering them twice as fast.)"

    def start_of_turn_effect(self):
        for spell in self.subject.actives:
            if self.school in spell.schools:
                spell.recovery_turns_left -= self.power


class GrantActive(Passive):
    def __init__(self, source, subject, active):
        self.active = active
        super().__init__(source, subject)

    def on_init(self):
        self.name = f"Granted {self.active.name}"
        self.nature = BLESSING
        self.description = f"This passive ability has granted you the active ability f{self.active.name}."

    def get_description(self):
        return f"This passive ability has granted you the active ability f{self.active.name}."

    def on_apply_effect(self):
        self.subject.actives.append(self.active)

    def on_expire_effect(self):
        self.subject.actives.remove(self.active)

    def on_dispelled_effect(self):
        self.subject.actives.remove(self.active)

class Slow(Passive):
    def on_init(self):
        self.name = "Slow"
        self.nature = CURSE
        self.power = 1
        self.description = f"This entity cannot act very quickly and gains {self.power} action points fewer each turn."

    def get_description(self):
        return f"This entity cannot act very quickly and gains {self.power} action points fewer each turn."

    def start_of_turn_effect(self):
        self.subject.current_actions -= self.power

class DivineLightPassive(Passive):
    def on_init(self):
        self.name = "Divine Light"
        self.nature = BLESSING
        self.power = 3
        self.radius = 7
        self.description = f"Radiating a divine light, this creature deals {self.power} Light damage to each creature in a {self.radius} radius each turn."

    def get_description(self):
        return f"Radiating a divine light, this creature deals {self.power} Light damage to each creature in a {self.radius} radius each turn."

    def start_of_turn_effect(self):
        for tile in disk(self.subject.position, self.radius, include_origin_tile=False):
            entity = self.subject.world.total_entities[tile]
            if entity is not None:
                if entity.allegiance != self.subject.allegiance:
                    damage_entity(self.subject, entity, self.power, DAMAGE_TYPES.LIGHT)
            self.subject.world.show_effect(tile, "light_explosion", 0)