import random
from biomes.biome import Biome
from floors import DirtFloorTile
from walls import Tree
import entities.entities as entities
from util import *

class Forest(Biome):
    def __init__(self, world, biome_id):
        super().__init__(world, biome_id)
        self.name = "Forest"

        self.monster_groups = []
        self.monster_group_weights = []
        self.monster_groups.append([entities.Troll, entities.Troll, entities.Goblin, entities.Goblin])
        self.monster_group_weights.append(1)
        self.monster_groups.append([entities.Goblin] * 9)
        self.monster_group_weights.append(3)


    def generate_floor_tile(self, coords):
        return DirtFloorTile(self.world)

    def generate_wall_tile(self, coords):
        if random.random() < 0.8:
            return None
        else:
            return Tree(self.world)

    def generate_entity(self, coords):
        roll = random.random()
        if roll < 0.98:
            return None
        elif roll < 0.99:
            enemy = entities.Goblin(self.world)
            enemy.allegiance = ALLEGIANCES.ENEMY_TEAM
            return enemy
        else:
            enemy = entities.Troll(self.world)
            enemy.allegiance = ALLEGIANCES.ENEMY_TEAM
            return enemy


    def generate_monster_group(self, coords):
        monster_group = random.choice(self.monster_groups)
        generated_monsters = []
        for monster in monster_group:
            generated_monster = monster(self.world)
            generated_monster.allegiance = ALLEGIANCES.ENEMY_TEAM
            generated_monsters.append(generated_monster)

        self.world.place_monster_group(generated_monsters, coords)