SORCERY = 0
ENCHANTMENT = 1
CONJURATION = 2


# Theme ideas:
'''
Blood
Illusion
Demonic
Draconic
Arcane-ish, aether
Astral
Storm
Metal (summon dancing swords, walls of swords, robots, armour etc.)
Crystal
Ice
Fire
Water
Lightning/Storm
Nature
Holy
Light
Unholy
Necromantic (Summon Longdead)
Earth/Stone
Psionic
Spirit
Rune
Entropy
Emotion

Combos:
Fungus (nature + earth)
Steam (fire + water)
'''



class Spell:
    def __init__(self):
        self.power = 5
        self.range = 1
        self.radius = 1
        self.num_targets = 1
        self.tags = []
        self.action_cost = 2
        self.name = "Unnamed Spell"

    def onCast(self, target):
        pass


class MeleeAttack(Spell):
    def __init__(self):
        super().__init__()
        self.name = "Strike"

