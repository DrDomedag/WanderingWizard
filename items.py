import spells


class Item:
    def __init__(self, world, position):
        self.world = world
        self.position = position
        self.asset_name = "unknown"
        self.asset = world.assets[self.asset_name]
        self.layer = "item"
        self.name = "Nameless Item"

    def on_pickup(self):
        pass

class Spellbook(Item):
    def __init__(self, world, level, position):
        super().__init__(world, position)
        self.level = level
        self.asset = "spellbook"

    def on_pickup(self):
        target_level = self.level
        while target_level > 0:
            spell = self.world.game.pc_available_spell_list.get_random_spells_of_tier(target_level, 1)
            if len(spell) > 0:
                spell = spell[0]
                self.world.pc.actives.append(spell(self.world.pc))
                self.world.active_items[self.position] = None
                self.world.total_items[self.position] = None
                self.world.game.pc_available_spell_list.remove(spell)
                del (self)
            else:
                print(f"No unlearned spells at tier {self.level}")
            target_level -= 1

