import random
from walls import *
from floors import *
from util import *
import entities.entities as entities

class Biome:
    def __init__(self, world, biome_id):
        self.world = world
        self.biome_id = biome_id
        self.name = "Unnamed biome"
        self.seed = random.randint(0, 100000)
        self.monster_groups = []
        self.monster_group_weights = []
        self.monster_group_spawn_probability = 0.001
        self.poi_spawn_rate = 0.0
        self.pois = []
        self.poi_weights = []
        self.fow_colour = (255, 255, 255)

    def intensity_weight(self, coords):
        return 1

    def intensity_bias(self, coords):
        return 0

    def generate_floor_tile(self, coords):
        if random.random() < 0.9:
            return DirtFloorTile(self.world,coords)
        else:
            return WaterFloorTile(self.world, coords)

    def generate_wall_tile(self, coords):
        if random.random() < 0.9:
            return None
        else:
            return StoneWall(self.world, coords)

    def generate_entity(self, coords):
        if random.random() < 0.98:
            return None
        else:
            enemy = entities.Goblin(self.world)
            enemy.allegiance = ALLEGIANCES.ENEMY_TEAM
            return enemy

    def generate_poi(self, coords):
        if random.random() < self.poi_spawn_rate:
            # Pick one
            poi = random.choices(self.pois, self.poi_weights, k=1)[0]
            # Instance it
            poi = poi(self.world, coords)
            # Draw it onto the world
            poi.draw()

    def generate_tile_effect(self, coords):
        return None

    def generate_item(self, coords):
        return None

    def generate_monster_group(self, coords):
        if len(self.monster_groups) > 0 and random.random() < self.monster_group_spawn_probability:
            monster_group = random.choices(self.monster_groups, weights=self.monster_group_weights, k=1)[0]
            generated_monsters = []
            for monster in monster_group:
                generated_monster = monster(self.world)
                generated_monster.allegiance = ALLEGIANCES.ENEMY_TEAM
                generated_monsters.append(generated_monster)

            self.world.place_monster_group(generated_monsters, coords)

class StarterBiome(Biome):
    def __init__(self, world, biome_id):
        super().__init__(world, biome_id)
        self.name = "Starter biome"
        self.monster_group_spawn_probability = 0
        self.fow_colour = (255, 255, 255)

    def generate_floor_tile(self, coords):
        from world.world import World
        if random.random() < 0.98:
            return DirtFloorTile(self.world, coords)
        else:
            return Portal(self.world, World(self.world.game), coords)
            # home_world, home_world_coordinates, away_world_coordinates=(0, 0), paired_portal=None

    def intensity_weight(self, coords):
        return 1

    def intensity_bias(self, coords):
        return 16 - 2 * euclidean_distance((0, 0), coords)


    def generate_entity(self, coords):
        return None

    def generate_wall_tile(self, coords):
        return None

class PointOfInterest:
    def __init__(self, world, generation_coordinates):
        self.name="Unnamed Point of Interest"
        self.world = world
        self.generation_coordinates = generation_coordinates

        self.size = (3, 3)
        self.centre_tile = self.compute_centre_tile()


    def draw(self):
        pass

    def compute_centre_tile(self):
        direction_from_player = compute_direction(self.world.game.pc.position, self.generation_coordinates)
        centre_x = self.generation_coordinates[0] + (self.size[0] // 2) * direction_from_player[0]
        centre_y = self.generation_coordinates[1] + (self.size[1] // 2) * direction_from_player[1]
        centre_tile = (int(centre_x), int(centre_y))
        return centre_tile

