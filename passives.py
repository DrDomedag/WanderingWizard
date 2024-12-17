import effects
from util import SCHOOL_NAMES

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
    def __init__(self, source, subject):
        super().__init__(source, subject)
        self.name = "Regeneration"
        self.nature = BLESSING
        self.power = 5
        self.description = f"This creature gradually heals all injury, and it regains {self.power} hit points at the start of each of its turns."

    def start_of_turn_effect(self):
        effects.heal(self.source, self.subject, self.power)


class TrollRegen(Passive):
    def __init__(self, source, subject):
        super().__init__(source, subject)
        self.name = "Troll Regeneration"
        self.nature = INHERENT
        self.power = 5
        self.description = f"This troll's wounds close at a terrifying rate, and it regains {self.power} hit points at the start of each of its turns."

    def start_of_turn_effect(self):
        effects.heal(self.source, self.subject, self.power)


class SpellChargeRecoveryBoost(Passive):
    def __init__(self, source, subject, school):
        super().__init__(source, subject)
        self.school = school
        self.name = f"{SCHOOL_NAMES.school} Spell Recovery Boost"
        self.nature = INHERENT
        self.power = 1
        self.description = f"You are particularly adept at quickly recovering {SCHOOL_NAMES.school} spell slots, gaining a +{self.power} bonus to their recovery speed. (This usually means recovering them twice as fast.)"

    def start_of_turn_effect(self):
        for spell in self.subject.actives:
            if self.school in spell.schools:
                spell.recovery_turns_left -= self.power


class GrantActive(Passive):
    def __init__(self, source, subject, active):
        super().__init__(source, subject)
        self.active = active
        self.name = f"Granted {self.active.name}"
        self.nature = BLESSING
        self.description = f"This passive ability has granted you the active ability f{self.active.name}."

    def on_apply_effect(self):
        self.subject.actives.append(self.active)

    def on_expire_effect(self):
        self.subject.actives.remove(self.active)

    def on_dispelled_effect(self):
        self.subject.actives.remove(self.active)

class Slow(Passive):
    def __init__(self, source, subject, duration=None):
        super().__init__(source, subject, duration)

        self.name = "Slow"
        self.nature = CURSE
        self.power = 1
        self.description = f"This entity cannot act very quickly and gains {self.power} action points fewer each turn."

    def start_of_turn_effect(self):
        self.subject.current_actions -= self.power