import random
from walls import *
from floors import *
from util import *
import entities.entities as entities

class Biome():
    def __init__(self, world, biome_id):
        self.world = world
        self.biome_id = biome_id
        self.name = "Unnamed biome"
        self.seed = random.randint(0, 100000)

    def intensity_weight(self, coords):
        return 1

    def intensity_bias(self, coords):
        return 0

    def generate_floor_tile(self, coords):
        if random.random() < 0.9:
            return DirtFloorTile()
        else:
            return WaterFloorTile()

    def generate_wall_tile(self, coords):
        if random.random() < 0.9:
            return None
        else:
            return StoneWall(self.world)

    def generate_entity(self, coords):
        if random.random() < 0.98:
            return None
        else:
            enemy = entities.Goblin(self.world)
            enemy.allegiance = ALLEGIANCES.ENEMY_TEAM
            return enemy

    def generate_tile_effect(self, coords):
        return None

    def generate_item(self, coords):
        return None


class StarterBiome(Biome):
    def __init__(self, world, biome_id):
        super().__init__(world, biome_id)
        self.name = "Starter biome"

    def generate_floor_tile(self, coords):
        return DirtFloorTile()

    def intensity_weight(self, coords):
        return 1

    def intensity_bias(self, coords):
        return 10 - 2 * euclidean_distance((0, 0), coords)


    def generate_entity(self, coords):
        return None

    def generate_wall_tile(self, coords):
        return None

class PointOfInterest():
    def __init__(self, world, generation_coordinates):
        self.name="Unnamed Point of Interest"
        self.world = world
        self.generation_coordinates = generation_coordinates

        self.size = (3, 3)
        self.centre_tile = self.compute_centre_tile()


    def draw(self, world):
        pass


    def compute_centre_tile(self):
        direction_from_player = compute_direction(self.world.game.pc.position, self.generation_coordinates)
        centre_x = self.generation_coordinates[0] + (self.size[0] // 2) * direction_from_player[0]
        centre_y = self.generation_coordinates[1] + (self.size[1] // 2) * direction_from_player[1]
        centre_tile = (int(centre_x), int(centre_y))
        return centre_tile

