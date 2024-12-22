import random
from random import shuffle

import spells
from util import *


class Item:
    def __init__(self, world, position):
        self.world = world
        self.position = position
        self.layer = "item"
        self.name = "Nameless Item"
        self.asset_name = "unknown"
        self.on_init()
        self.asset = world.game.assets[self.asset_name]

    def on_init(self):
        pass

    def on_pickup(self):
        pass

class Spellbook(Item):
    def __init__(self, world, level, position, schools=None, spell_list=None):
        super().__init__(world, position)
        self.level = level
        self.schools = schools
        self.spell_list = spell_list

    def on_init(self):
        self.name = "Spellbook"
        self.asset_name = "spellbook"

    def on_pickup(self):
        target_level = self.level
        while target_level > 0:
            if self.spell_list is not None:
                final_candidate_list = []
                for candidate_spell in self.spell_list:
                    known = False
                    for known_spell in self.world.game.pc.actives:
                        if candidate_spell.name == known_spell.name:
                            known = True
                            break
                    if not known and candidate_spell.level == target_level:
                        final_candidate_list.append(candidate_spell)
                shuffle(final_candidate_list)
            else:
                # Since get_random_spells_of_tier handles the schools=None scenario, this deals with both schools being
                # specified and schools not being specified.
                final_candidate_list = self.world.game.pc_available_spell_list.get_random_spells_of_tier(target_level, 1, schools=self.schools)
            if len(final_candidate_list) > 0:
                spell = final_candidate_list[0]
                self.world.game.pc.actives.append(spell(self.world.game.pc))
                self.world.active_items[self.position] = None
                self.world.total_items[self.position] = None
                self.world.game.pc_available_spell_list.remove(spell)
            else:
                print(f"No unlearned spells at tier {target_level}")
            target_level -= 1

class InnovationPoint(Item):

    def on_init(self):
        self.name = "Rune of Innovation"
        self.asset_name = "innovation_point"

    def on_pickup(self):
        self.world.game.pc.innovation_points += 1

class Iteration(Item):
    def __init__(self, world, position, school=None, stat=None, value=None):
        super().__init__(world, position)
        if school is None:
            self.school = SCHOOLS.get_random_value()
        else:
            self.school = school

        incrementable_stats = ["damage", "range", "radius", "duration", "minion_damage", "minion_health", "minion_count"]

        if stat is None or stat not in incrementable_stats:
            self.stat = random.choice
        else:
            self.stat = stat

        if value is None:
            self.value = 1
        else:
            self.value = value

        self.name = f"{SCHOOL_NAMES[self.school]} {stat} Incrementation"

    def on_pickup(self):
        self.world.game.pc.add_iteration(self)
        self.position = None





'''
class SchoolSpellbook(Spellbook):
    def __init__(self, world, level, position, schools):
        super().__init__(world, level, position)
        self.schools = schools

    def on_pickup(self):
        target_level = self.level
        while target_level > 0:
            spell = self.world.game.pc_available_spell_list.get_random_spells_of_tier(target_level, 1)
            if len(spell) > 0:
                spell = spell[0]
                self.world.game.pc.actives.append(spell(self.world.game.pc))
                self.world.active_items[self.position] = None
                self.world.total_items[self.position] = None
                self.world.game.pc_available_spell_list.remove(spell)
                del (self)
            else:
                print(f"No unlearned spells at tier {self.level}")
            target_level -= 1
'''


