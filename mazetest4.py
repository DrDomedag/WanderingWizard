import random

class ConnectedRandomWalkDungeon:
    def __init__(self, chunk_size=16, room_chance=0.5, walk_length=20, loop_chance=0.2):
        self.maze = {}  # Store tiles as {(x, y): True (path) or False (wall)}
        self.chunk_size = chunk_size
        self.room_chance = room_chance
        self.walk_length = walk_length  # Maximum steps for a random walk
        self.loop_chance = loop_chance  # Chance of creating loops
        self.generated_chunks = set()

    def generate_chunk(self, chunk_x, chunk_y):
        """Generate a chunk and connect it to the existing maze."""
        if (chunk_x, chunk_y) in self.generated_chunks:
            return  # Avoid regenerating chunks

        print(f"Generating chunk at {chunk_x}, {chunk_y}")
        self.generated_chunks.add((chunk_x, chunk_y))

        start_x = chunk_x * self.chunk_size
        start_y = chunk_y * self.chunk_size

        # Start random walk from a known path or central point
        walker_x = start_x + self.chunk_size // 2
        walker_y = start_y + self.chunk_size // 2
        self.connect_to_maze(walker_x, walker_y)

        for _ in range(random.randint(1, self.walk_length)):
            # Carve the current tile
            self.maze[(walker_x, walker_y)] = True

            # Randomly decide on the next direction (up, down, left, right)
            direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
            walker_x += direction[0]
            walker_y += direction[1]

            # Occasionally allow the walker to connect back to an existing path (loop)
            if random.random() < self.loop_chance:
                neighbors = self.get_neighbors(walker_x, walker_y)
                for nx, ny in neighbors:
                    if self.maze.get((nx, ny), False):  # Found a path
                        self.maze[(walker_x, walker_y)] = True
                        break

        # Optionally place a room in the chunk
        if random.random() < self.room_chance:
            self.place_room(start_x, start_y)

    def place_room(self, start_x, start_y):
        """Place a random-sized room within a chunk."""
        room_size = random.randint(4, self.chunk_size // 2)  # Room size
        room_x = random.randint(0, self.chunk_size - room_size)
        room_y = random.randint(0, self.chunk_size - room_size)

        # Carve out the room
        for x in range(start_x + room_x, start_x + room_x + room_size):
            for y in range(start_y + room_y, start_y + room_y + room_size):
                self.maze[(x, y)] = True

        # Ensure the room connects to the maze
        self.connect_to_maze(start_x + room_x + room_size // 2, start_y + room_y + room_size // 2)

    def connect_to_maze(self, x, y):
        """Ensure the given tile connects to an existing part of the maze."""
        if not self.maze:  # First tile in the maze
            self.maze[(x, y)] = True
            return

        # Find the nearest tile in the existing maze
        nearest = self.find_nearest_path(x, y)
        if nearest:
            self.carve_corridor(x, y, nearest[0], nearest[1])

    def find_nearest_path(self, x, y):
        """Find the nearest path tile in the maze."""
        min_distance = float('inf')
        nearest_tile = None

        for tile in self.maze.keys():
            if self.maze[tile]:  # Only consider carved tiles
                distance = abs(tile[0] - x) + abs(tile[1] - y)  # Manhattan distance
                if distance < min_distance:
                    min_distance = distance
                    nearest_tile = tile

        return nearest_tile

    def carve_corridor(self, x1, y1, x2, y2):
        """Carve a corridor from (x1, y1) to (x2, y2) using a simple straight-line algorithm."""
        # Prevent division by zero if the start and end points are the same
        if x1 == x2 and y1 == y2:
            self.maze[(x1, y1)] = True
            return

        dx, dy = x2 - x1, y2 - y1
        steps = max(abs(dx), abs(dy))

        # Prevent zero steps by ensuring the distance isn't zero
        if steps == 0:
            return

        for i in range(steps + 1):
            nx = x1 + i * dx // steps
            ny = y1 + i * dy // steps
            self.maze[(nx, ny)] = True

    def get_neighbors(self, x, y):
        """Get neighboring tiles of a given tile."""
        return [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]

    def explore(self, player_position, radius):
        """Generate chunks around the player's position."""
        px, py = player_position
        chunk_radius = (radius + self.chunk_size - 1) // self.chunk_size

        for chunk_x in range(px // self.chunk_size - chunk_radius, px // self.chunk_size + chunk_radius + 1):
            for chunk_y in range(py // self.chunk_size - chunk_radius, py // self.chunk_size + chunk_radius + 1):
                self.generate_chunk(chunk_x, chunk_y)

    def is_path(self, x, y):
        """Check if a tile is part of the maze."""
        return self.maze.get((x, y), False)




player_position = (0, 0)
radius = 40

maze = ConnectedRandomWalkDungeon(chunk_size=16, room_chance=0.7, walk_length=20, loop_chance=0.6)

# Generate the maze around the player
maze.explore(player_position, radius=radius)

# Print the maze section
for y in range(-radius, radius + 1):
    for x in range(-radius, radius + 1):
        if (x, y) == player_position:
            print("@", end=" ")  # Character position
        elif maze.is_path(x, y):
            print(".", end=" ")  # Floor
        else:
            print("#", end=" ")  # Wall
    print()