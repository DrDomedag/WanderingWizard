from effects import *

INHERENT = 0
BLESSING = 1
CURSE = 2


class Passive:
    def __init__(self):
        self.duration = None
        self.name = "Unnamed buff"
        self.nature = BLESSING
        self.object = None
        self.subject = None
        self.status_modifiers = []

    def incrementDuration(self):
        if self.duration is None:
            pass
        elif self.duration > 0:
            self.duration -= 1
        else:
            # Remove from owner, delete self
            self.subject.passives.remove(self)

    def applyStatusModifiers(self):
        pass

    def startOfTurnEffect(self):
        pass

    def endOfTurnEffect(self):
        pass

    def onSufferHitEffect(self):
        pass

    def onSufferDamageEffect(self):
        pass

    def onDealHitEffect(self):
        pass

    def onSufferHitEffect(self):
        pass





class TrollRegen(Passive):
    def __init__(self):
        super().__init__()
        self.nature = INHERENT
        self.power = 5

    def startOfTurnEffect(self):
        healingInstance = HealingInstance()
        healingInstance.amount = self.power
        healingInstance.apply(self.subject)

