from effects import *

INHERENT = 0
BLESSING = 1
CURSE = 2


class Passive:
    def __init__(self, source, subject):
        self.duration = None
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
            # Remove from owner, delete self
            self.subject.passives.remove(self)

    def apply_status_modifiers(self):
        pass

    def start_of_turn_effect(self):
        pass

    def end_of_turn_effect(self):
        pass

    def on_suffer_damage_effect(self):
        pass

    def on_deal_hit_effect(self):
        pass

    def on_suffer_hit_effect(self):
        pass

    def on_death_effect(self):
        pass





class TrollRegen(Passive):
    def __init__(self, source, subject):
        super().__init__(source, subject)
        self.name = "Troll Regeneration"
        self.nature = INHERENT
        self.power = 5
        self.description = f"This troll's wounds close at a terrifying rate, and it regains {self.power} hit points at the start of each of its turns."

    def start_of_turn_effect(self):
        heal(self.source, self.subject, self.power)


