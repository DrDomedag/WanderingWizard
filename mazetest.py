import random


class InfiniteMaze:
    def __init__(self):
        self.maze = {}  # Store maze tiles: True for floor, False for wall
        self.frontier = []  # List of frontier tiles

        # Start the maze at the origin
        self.start_x, self.start_y = 0, 0
        self.maze[(self.start_x, self.start_y)] = True
        self.add_frontier(self.start_x, self.start_y)

    def add_frontier(self, x, y):
        """
        Add neighboring tiles to the frontier if they are not already in the maze.
        """
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Cardinal directions
            neighbor = (x + dx, y + dy)
            if neighbor not in self.maze:
                self.frontier.append(neighbor)

    def is_floor(self, x, y):
        """
        Determine if the tile (x, y) is a floor. Generates the maze dynamically if needed.
        """
        if (x, y) in self.maze:
            return self.maze[(x, y)]  # Return already determined value

        # If tile is not in the maze, decide based on maze generation rules
        if (x, y) in self.frontier:
            # Decide whether to carve this tile
            neighbors = self.get_neighbors(x, y)
            floor_neighbors = sum(1 for n in neighbors if self.maze.get(n, False))

            # Carve only if this tile maintains a maze-like structure
            if floor_neighbors == 1:  # Ensure connectivity
                if random.random() < 0.9:
                    self.maze[(x, y)] = True
                    self.add_frontier(x, y)  # Add its neighbors to the frontier
                    return True


        # Default to wall, but not always
        if random.random() < 0.1:
            self.maze[(x, y)] = True
            self.add_frontier(x, y)  # Add its neighbors to the frontier

        self.maze[(x, y)] = False
        return False

    def get_neighbors(self, x, y):
        """
        Get the coordinates of neighboring tiles.
        """
        return [(x + dx, y + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]]

    def get_visible_tiles(self, char_x, char_y, radius):
        """
        Get all tiles within line of sight, expanding the maze as needed.
        """
        visible_tiles = {}
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                x, y = char_x + dx, char_y + dy
                if abs(dx) + abs(dy) <= radius:  # Example LOS shape: Manhattan distance
                    visible_tiles[(x, y)] = self.is_floor(x, y)
        return visible_tiles


# Example Usage
maze = InfiniteMaze()
character_position = (0, 0)

# Get visible tiles within a radius of 5
visible = maze.get_visible_tiles(character_position[0], character_position[1], radius=5)

# Print the maze section
for y in range(-5, 6):
    for x in range(-5, 6):
        if (x, y) == character_position:
            print("@", end=" ")  # Character position
        elif visible.get((x, y), False):
            print(".", end=" ")  # Floor
        else:
            print("#", end=" ")  # Wall
    print()