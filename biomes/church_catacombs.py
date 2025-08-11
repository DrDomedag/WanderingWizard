import random
import biomes.biome as biome
import floors
import walls
import entities.entities as entities
from util import *
from catacomb_mazegen import generate_dungeon

class ChurchCatacombs(biome.Biome):
    def __init__(self, world, biome_id):
        super().__init__(world, biome_id)
        self.name = "Catacombs"

        self.monster_groups.append([entities.Longdead] * 4)
        self.monster_group_weights.append(1)
        self.monster_groups.append([entities.Longdead] * 9)
        self.monster_group_weights.append(7)
        self.monster_group_spawn_probability = 0.002
        #self.poi_spawn_rate = 0.0005
        self.poi_spawn_rate = 0.0
        #self.pois.append(ShamanHut)
        #self.poi_weights.append(1)
        self.fow_colour = (125, 64, 125)

        self.starting_coords = self.generate_maze()


    # All non-maze tiles are stone walls on dirt floors.
    def generate_floor_tile(self, coords):
        return floors.DirtFloorTile(self.world, coords)

    def generate_wall_tile(self, coords):
        return walls.StoneWall(self.world, coords)

    def generate_entity(self, coords):
        roll = random.random()
        if roll < 0.98:
            return None
        elif roll < 0.99:
            enemy = entities.Longdead(self.world)
            enemy.allegiance = ALLEGIANCES.ENEMY_TEAM
            return enemy
        else:
            enemy = entities.Longdead(self.world)
            enemy.allegiance = ALLEGIANCES.ENEMY_TEAM
            return enemy

    def generate_poi(self, coords):
        return

    def generate_maze(self):
        dungeon, rooms, corridors, room_tiles = generate_dungeon(width=60, height=60, branching_factor=0.4, loop_chance=0.4, max_rooms=20, min_room_size=4, max_room_size=18)
        for row in range(len(dungeon)):
            for col in range(len(dungeon[0])):
                position = (col, row)
                if dungeon[row][col] == 0:
                    floor_tile = floors.StoneFloorTile(self.world, position)
                    self.world.total_floor[position] = floor_tile
                    self.world.active_floor[position] = floor_tile
                elif dungeon[row][col] == 1:
                    floor_tile = floors.DirtFloorTile(self.world, position)
                    self.world.total_floor[position] = floor_tile
                    self.world.active_floor[position] = floor_tile
                    wall_tile = walls.StoneWall(self.world, position)
                    self.world.total_walls[position] = wall_tile
                    self.world.active_walls[position] = wall_tile
                elif dungeon[row][col] == 2:
                    floor_tile = floors.DirtFloorTile(self.world, position)
                    self.world.total_floor[position] = floor_tile
                    self.world.active_floor[position] = floor_tile
                    wall_tile = walls.Door(self.world, position)
                    self.world.total_walls[position] = wall_tile
                    self.world.active_walls[position] = wall_tile
                elif dungeon[row][col] == 3:
                    floor_tile = floors.DirtFloorTile(self.world, position)
                    self.world.total_floor[position] = floor_tile
                    self.world.active_floor[position] = floor_tile
                    wall_tile = walls.Curtain(self.world, position)
                    self.world.total_walls[position] = wall_tile
                    self.world.active_walls[position] = wall_tile

        for room in rooms:
            coords = room[0]
            center = room[1]
            min_x = coords[0]
            min_y = coords[1]
            max_x = coords[2]
            max_y = coords[3]
            xsize = max_x - min_x
            ysize = max_y - min_y
            area = xsize * ysize

            # Let's leave 15% of rooms empty for suspense.
            if random.random() < 0.85:
                monster_group = random.choices(self.monster_groups, self.monster_group_weights, k=1)

                generated_monsters = []
                for monster in monster_group[0]:
                    generated_monster = monster(self.world)
                    generated_monster.allegiance = ALLEGIANCES.ENEMY_TEAM
                    generated_monsters.append(generated_monster)

                print(f"Generated monsters: {generated_monsters}")

                self.world.place_monster_group_from_instances(generated_monsters, center, away_from_player=False)

        rooms[0]


