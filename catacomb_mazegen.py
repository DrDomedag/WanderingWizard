import random
from collections import deque

# Tile constants
FLOOR = 0
WALL = 1
DOOR = 2
CURTAIN = 3


def generate_dungeon(
    width=50,
    height=30,
    branching_factor=0.4,
    loop_chance=0.04,
    max_rooms=12,
    min_room_size=4,
    max_room_size=8,
    seed=None
):
    if seed is not None:
        random.seed(seed)

    # State variables
    dmap = [[WALL for _ in range(width)] for _ in range(height)]
    rooms = []           # ((x1,y1,x2,y2), (cx,cy))
    corridors = []       # ((start), (bend_or_center), (end))
    room_tiles = set()   # set of (x,y) that belong to room interiors

    # ----- utilities -----
    def in_bounds(x, y): return 0 <= x < width and 0 <= y < height
    def is_floor(x, y): return in_bounds(x, y) and dmap[y][x] == FLOOR
    def is_wall(x, y): return in_bounds(x, y) and dmap[y][x] == WALL

    def carve_room(x1, y1, x2, y2):
        for yy in range(y1, y2 + 1):
            for xx in range(x1, x2 + 1):
                dmap[yy][xx] = FLOOR
                room_tiles.add((xx, yy))

    def carve_horiz(x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            dmap[y][x] = FLOOR

    def carve_vert(y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            dmap[y][x] = FLOOR

    def carve_corridor(a, b):
        x1, y1 = a
        x2, y2 = b
        if random.random() < 0.5:
            carve_horiz(x1, x2, y1)
            carve_vert(y1, y2, x2)
            if x1 != x2 and y1 != y2:
                bend = (x2, y1)
                corridors.append((a, bend, b))
            else:
                mid = ((x1 + x2) // 2, (y1 + y2) // 2)
                corridors.append((a, mid, b))
        else:
            carve_vert(y1, y2, x1)
            carve_horiz(x1, x2, y2)
            if x1 != x2 and y1 != y2:
                bend = (x1, y2)
                corridors.append((a, bend, b))
            else:
                mid = ((x1 + x2) // 2, (y1 + y2) // 2)
                corridors.append((a, mid, b))

    def intersects(a, b):
        ax1, ay1, ax2, ay2 = a
        bx1, by1, bx2, by2 = b
        return not (ax2 < bx1 or ax1 > bx2 or ay2 < by1 or ay1 > by2)

    def place_rooms():
        attempts = 2000
        tries = 0
        while len(rooms) < max_rooms and tries < attempts:
            tries += 1
            w = random.randint(min_room_size, max_room_size)
            h = random.randint(min_room_size, max_room_size)
            x_max = width - w - 2
            y_max = height - h - 2
            if x_max < 1 or y_max < 1:
                continue
            x = random.randint(1, x_max)
            y = random.randint(1, y_max)
            new_room = (x, y, x + w - 1, y + h - 1)
            if any(intersects(new_room, r[0]) for r in rooms):
                continue
            carve_room(*new_room)
            center = ((x + x + w - 1) // 2, (y + y + h - 1) // 2)
            rooms.append((new_room, center))
        if not rooms:
            cw, ch = min_room_size, min_room_size
            cx = max(1, (width - cw) // 2)
            cy = max(1, (height - ch) // 2)
            carve_room(cx, cy, cx + cw - 1, cy + ch - 1)
            rooms.append(((cx, cy, cx + cw - 1, cy + ch - 1), (cx + cw // 2, cy + ch // 2)))

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def connect_rooms():
        if not rooms:
            return
        connected = [rooms[0]]
        unconnected = rooms[1:]
        while unconnected:
            cr = random.choice(connected)
            nr = min(unconnected, key=lambda r: dist(cr[1], r[1]))
            carve_corridor(cr[1], nr[1])
            connected.append(nr)
            unconnected.remove(nr)

    def add_branching_connections():
        for i, (_, ca) in enumerate(rooms):
            for j, (_, cb) in enumerate(rooms):
                if i >= j:
                    continue
                if dist(ca, cb) <= 15 and random.random() < branching_factor:
                    carve_corridor(ca, cb)

    def carve_corridor_loops():
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                if is_wall(x, y):
                    if is_floor(x - 1, y) and is_floor(x + 1, y) and random.random() < loop_chance:
                        dmap[y][x] = FLOOR
                    elif is_floor(x, y - 1) and is_floor(x, y + 1) and random.random() < loop_chance:
                        dmap[y][x] = FLOOR

    def bfs_accessible(start):
        visited = [[False] * width for _ in range(height)]
        sx, sy = start
        if not in_bounds(sx, sy):
            return visited
        q = deque([start])
        visited[sy][sx] = True
        while q:
            x, y = q.popleft()
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if in_bounds(nx, ny) and not visited[ny][nx]:
                    if dmap[ny][nx] in (FLOOR, DOOR, CURTAIN):
                        visited[ny][nx] = True
                        q.append((nx, ny))
        return visited

    def connect_unreachable(start=(0, 0)):
        visited = bfs_accessible(start)
        for y in range(height):
            for x in range(width):
                if dmap[y][x] in (FLOOR, DOOR, CURTAIN) and not visited[y][x]:
                    visited_cells = [(ax, ay) for ay in range(height) for ax in range(width) if visited[ay][ax]]
                    target = start if not visited_cells else min(visited_cells, key=lambda p: abs(p[0] - x) + abs(p[1] - y))
                    carve_corridor((x, y), target)
                    return True
        return False

    def place_doors_and_curtains():
        corridor_tiles = {(x, y) for y in range(height) for x in range(width) if dmap[y][x] == FLOOR and (x, y) not in room_tiles}
        def neighbors(p):
            x, y = p
            return ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))
        entrance_tiles = {c for c in corridor_tiles if any(nb in room_tiles for nb in neighbors(c))}
        visited_c = set()
        for t in list(corridor_tiles):
            if t in visited_c:
                continue
            comp = set([t])
            q = deque([t])
            visited_c.add(t)
            while q:
                cur = q.popleft()
                for nb in neighbors(cur):
                    if nb in corridor_tiles and nb not in visited_c:
                        visited_c.add(nb)
                        comp.add(nb)
                        q.append(nb)
            comp_entrances = [p for p in comp if p in entrance_tiles]
            if not comp_entrances:
                continue
            comp_set = set(comp_entrances)
            clusters = []
            while comp_set:
                s = comp_set.pop()
                cl = {s}
                q = deque([s])
                while q:
                    cur = q.popleft()
                    for nb in neighbors(cur):
                        if nb in comp_set:
                            comp_set.remove(nb)
                            cl.add(nb)
                            q.append(nb)
                clusters.append(cl)
            for cl in clusters:
                if len(cl) == 1:
                    gx, gy = next(iter(cl))
                    dmap[gy][gx] = DOOR
                else:
                    for gx, gy in cl:
                        dmap[gy][gx] = CURTAIN

    # ---- main steps ----
    place_rooms()
    connect_rooms()
    add_branching_connections()
    carve_corridor_loops()
    if dmap[0][0] == WALL:
        dmap[0][0] = FLOOR
    while connect_unreachable((0, 0)):
        pass
    place_doors_and_curtains()

    # Format for rooms:
    # ((x1,y1,x2,y2), (cx,cy))
    # where x1, y1 are the coordinates of the top left point, x2, y2 are the coordinates of the bottom right point
    # and cx, cy are the (x,y) coordinates of the centre tile.

    # Format for corridors:
    # Each corridor entry is a tuple: ((sx, sy), (mx, my), (ex, ey)).
    # If the corridor bends, (mx,my) is the bend coordinates (the turning tile).
    # If it’s straight, (mx,my) is just the center tile of the corridor segment.

    return dmap, rooms, corridors, room_tiles


def render(dmap):
    ch = {FLOOR: '.', WALL: '#', DOOR: '+', CURTAIN: '~'}
    for row in dmap:
        print(''.join(ch[t] for t in row))


# Example usage
if __name__ == "__main__":
    dungeon, rooms, corridors, room_tiles = generate_dungeon(
        width=60, height=40,
        branching_factor=0.5,
        loop_chance=0.05,
        max_rooms=15,
        min_room_size=3,
        max_room_size=10,
        seed=42
    )
    render(dungeon)
    print(f"\nRooms: {len(rooms)}")
    print(f"Corridors: {len(corridors)}")
    print(f"Room tiles: {len(room_tiles)}")
