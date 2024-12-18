import random

class InfiniteMazeWithRooms:
    def __init__(self, chunk_size=16, room_chance=0.7):
        self.maze = {}  # Store the maze as {(x, y): True (path) or False (wall)}
        self.chunk_size = chunk_size  # Size of each modular chunk
        self.room_chance = room_chance  # Probability of generating a room in a chunk
        self.generated_chunks = set()  # Track which chunks are generated
        self.corridors_to_carve = []  # Queue of corridors to carve

    def generate_chunk(self, chunk_x, chunk_y):
        """Generate a chunk of the maze, including rooms."""
        if (chunk_x, chunk_y) in self.generated_chunks:
            return  # Chunk already generated

        print(f"Generating chunk at {chunk_x}, {chunk_y}")
        self.generated_chunks.add((chunk_x, chunk_y))

        # Chunk origin
        start_x = chunk_x * self.chunk_size
        start_y = chunk_y * self.chunk_size

        # 1. Place rooms
        if random.random() < self.room_chance:
            self.generate_room(start_x, start_y)

        # 2. Queue corridors to neighboring chunks (but do not generate them yet)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # West, East, North, South
        for dx, dy in directions:
            neighbor_chunk = (chunk_x + dx, chunk_y + dy)
            if neighbor_chunk not in self.generated_chunks:
                self.corridors_to_carve.append((chunk_x, chunk_y, neighbor_chunk))

    def generate_room(self, start_x, start_y):
        """Generate a square room in the chunk."""
        print(f"Generating room at chunk origin {start_x}, {start_y}")
        room_size = random.randint(4, self.chunk_size - 4)  # Room size, must fit in chunk
        room_x = random.randint(0, self.chunk_size - room_size)
        room_y = random.randint(0, self.chunk_size - room_size)

        for x in range(start_x + room_x, start_x + room_x + room_size):
            for y in range(start_y + room_y, start_y + room_y + room_size):
                self.maze[(x, y)] = True  # Mark as path

    def carve_corridors(self):
        """Process queued corridors without generating new chunks."""
        processed = set()  # Track processed corridors
        print(f"Carving {len(self.corridors_to_carve)} corridors.")

        while self.corridors_to_carve:
            chunk_x1, chunk_y1, (chunk_x2, chunk_y2) = self.corridors_to_carve.pop(0)

            # Skip already-processed corridors
            if ((chunk_x1, chunk_y1), (chunk_x2, chunk_y2)) in processed:
                continue

            # Ensure both chunks are already generated
            if (chunk_x1, chunk_y1) in self.generated_chunks and (chunk_x2, chunk_y2) in self.generated_chunks:
                # Carve a corridor between the chunks
                self.carve_corridor_between_chunks(chunk_x1, chunk_y1, chunk_x2, chunk_y2)

            # Mark this corridor as processed
            processed.add(((chunk_x1, chunk_y1), (chunk_x2, chunk_y2)))
            processed.add(((chunk_x2, chunk_y2), (chunk_x1, chunk_y1)))

    def carve_corridor_between_chunks(self, chunk_x1, chunk_y1, chunk_x2, chunk_y2):
        """Carve a corridor between two chunks."""
        print(f"Carving corridor between chunks ({chunk_x1}, {chunk_y1}) and ({chunk_x2}, {chunk_y2})")
        start_x = chunk_x1 * self.chunk_size + self.chunk_size // 2
        start_y = chunk_y1 * self.chunk_size + self.chunk_size // 2
        end_x = chunk_x2 * self.chunk_size + self.chunk_size // 2
        end_y = chunk_y2 * self.chunk_size + self.chunk_size // 2

        # Bresenham's line algorithm to carve a straight corridor
        dx = abs(end_x - start_x)
        dy = abs(end_y - start_y)
        sx = 1 if start_x < end_x else -1
        sy = 1 if start_y < end_y else -1
        err = dx - dy

        x, y = start_x, start_y
        while (x, y) != (end_x, end_y):
            self.maze[(x, y)] = True  # Mark as path
            e2 = err * 2
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def is_path(self, x, y):
        """Check if a tile is part of the maze."""
        return self.maze.get((x, y), False)

    def explore(self, player_position, radius):
        """Expand the maze around the player within a given radius."""
        px, py = player_position
        chunk_radius = (radius + self.chunk_size - 1) // self.chunk_size  # Number of chunks to generate

        # Generate all chunks within the radius
        for chunk_x in range(px // self.chunk_size - chunk_radius, px // self.chunk_size + chunk_radius + 1):
            for chunk_y in range(py // self.chunk_size - chunk_radius, py // self.chunk_size + chunk_radius + 1):
                self.generate_chunk(chunk_x, chunk_y)

        # After generating chunks, carve the queued corridors
        self.carve_corridors()



player_position = (0, 0)
radius = 20

maze = InfiniteMazeWithRooms(chunk_size=16, room_chance=0.6)

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