import random

class InfiniteMaze:
    def __init__(self):
        self.maze = {}  # Dictionary to store maze tiles as (x, y): True (path) or False (wall)
        self.frontier = set()  # Set of tiles that are candidates for expansion

    def initialize(self, start):
        """Initialize the maze with the starting position."""
        x, y = start
        self.maze[(x, y)] = True  # Mark start as a path
        self.add_frontier_tiles(x, y)

    def add_frontier_tiles(self, x, y):
        """Add neighbors of (x, y) to the frontier."""
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Cardinal directions (N, E, S, W)
        for dx, dy in directions:
            neighbor = (x + dx, y + dy)
            if neighbor not in self.maze:  # Only add unexplored tiles
                self.frontier.add(neighbor)

    def generate_tile(self):
        """Generate a single tile by expanding the maze."""
        if not self.frontier:
            return  # No frontier tiles to expand

        # Randomly select a frontier tile
        tile = random.choice(list(self.frontier))
        x, y = tile

        # Find neighbors in the maze
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        neighbors = [(x + dx, y + dy) for dx, dy in directions if (x + dx, y + dy) in self.maze]

        if neighbors:
            # Connect to a random neighboring maze tile
            connect_to = random.choice(neighbors)
            self.maze[(x, y)] = True  # Mark as a path
            self.carve_passage(x, y, connect_to)

            # Add its frontier tiles
            self.add_frontier_tiles(x, y)

        # Remove the tile from the frontier set
        self.frontier.remove(tile)

    def carve_passage(self, x1, y1, x2y2):
        """Carve a passage between two tiles (optional for visualization)."""
        # You can add walls or paths depending on visualization needs
        pass

    def is_path(self, x, y):
        """Check if a tile is part of the maze."""
        return self.maze.get((x, y), False)

    def explore(self, player_position, radius):
        """Ensure the maze is expanded around the player within the radius."""
        px, py = player_position
        for x in range(px - radius, px + radius + 1):
            for y in range(py - radius, py + radius + 1):
                if (x, y) not in self.maze:
                    self.generate_tile()


player_position = (0, 0)
radius = 15

maze = InfiniteMaze()
maze.initialize(player_position)
maze.explore(player_position, radius)

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
