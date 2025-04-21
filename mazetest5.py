import random


def generate_maze(width, height):
    # Initialize grid with walls
    maze = [['#' for _ in range(width)] for _ in range(height)]

    # List of walls to be considered for carving
    walls = []

    # Start from a random point inside the grid
    start_x, start_y = random.randint(1, width - 2), random.randint(1, height - 2)
    maze[start_y][start_x] = ' '

    # Add all neighboring walls to the wall list
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = start_x + dx, start_y + dy
        if 1 <= nx < width - 1 and 1 <= ny < height - 1:
            walls.append((nx, ny))

    # Keep track of visited cells
    visited = set()
    visited.add((start_x, start_y))

    while walls:
        # Randomly pick a wall
        wall_x, wall_y = random.choice(walls)
        walls.remove((wall_x, wall_y))

        # Check how many neighboring open cells this wall has
        open_neighbors = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = wall_x + dx, wall_y + dy
            if (nx, ny) in visited:
                open_neighbors += 1

        # If it has exactly one neighboring open cell, carve it
        if open_neighbors == 1:
            maze[wall_y][wall_x] = ' '  # Open the wall
            visited.add((wall_x, wall_y))

            # Add its neighboring walls to the wall list
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = wall_x + dx, wall_y + dy
                if 1 <= nx < width - 1 and 1 <= ny < height - 1 and (nx, ny) not in visited:
                    walls.append((nx, ny))

    return maze


def print_maze(maze):
    for row in maze:
        print(''.join(row))


# Example usage
maze = generate_maze(60, 18)
print_maze(maze)
