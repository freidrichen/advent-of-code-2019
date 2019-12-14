import itertools
from collections import defaultdict
from decimal import Decimal


def angle(c):
    """
    Angles are represented as a tuple of (half plane index, tan(|angle|))
    where angle is the shortest clockwise angle from (negative or positive)
    y-axis.
    """
    dx, dy = c
    if dx == 0:
        tan_angle = Decimal(0)
        index = 2*int(dy > 0)  # Indices 0 and 2 used for dx == 0
    else:
        tan_angle = Decimal(dy) / Decimal(dx)
        index = 1 + 2*int(dx < 0)  # Indices 1 and 3 used for dx != 0
    return (index, tan_angle)


def visualize(coords_by_angle_):
    coords = set().union(*coords_by_angle_.values())
    for y in range(y_len):
        for x in range(x_len):
            if x == ox and y == oy:
                print('o', end='')
            elif (x - ox, y - oy) in coords:
                print('#', end='')
            else:
                print('.', end='')
        print()


input_file = "../input.txt"
with open(input_file, 'r') as f:
    input_text = f.read()

# Test:
# input_text = """.#....#####...#..
# ##...##.#####..##
# ##...#...#.#####.
# ..#.....#...###..
# ..#.#.....#....##"""

# Test:
# input_text = (
# """.#..##.###...#######
# ##.############..##.
# .#.######.########.#
# .###.#######.####.#.
# #####.##.#.##.###.##
# ..#####..#.#########
# ####################
# #.####....###.#.#.##
# ##.#################
# #####.##.###..####..
# ..######..##.#######
# ####.##.####...##..#
# .#####..#.######.###
# ##...#.##########...
# #.##########.#######
# .####.#.###.###.#.##
# ....##.##.###..#####
# .#.#.###########.###
# #.#.#.#####.####.###
# ###.##.####.##.#..##""")

y_len = len(input_text.splitlines())
x_len = len(input_text.splitlines()[0])

asteroids = [
    (x, y)
    for y, line in enumerate(input_text.splitlines())
    for x, char in enumerate(line)
    if char == '#'
]

def shrink(x, y):
    ax, ay = abs(x), abs(y)
    gcd = max(i for i in range(1, max(ax, ay) + 1) if ax % i == ay % i == 0)
    return x / gcd, y / gcd

visible = [
    (len({
        shrink(ax - ox, ay - oy)
        for (ax, ay) in asteroids
        if ox != ax or oy != ay
    }), ox, oy) for (ox, oy) in asteroids]

print("Max visible (part 1):", max(visible))


ox, oy = max(visible)[1:]
coords = [(ax - ox, ay - oy) for (ax, ay) in asteroids]


coords_by_angle = defaultdict(list)
for c in coords:
    if c != (0, 0):
        coords_by_angle[angle(c)].append(c)
coords_by_angle = dict(coords_by_angle)

for angle in coords_by_angle.keys():
    # Sort coordinates with the same angle by sum of coordinates, i.e. distance
    # from origin.
    coords_by_angle[angle].sort(key=lambda c: abs(c[0]) + abs(c[1]))

vaporized = 0
for angle in itertools.cycle(sorted(coords_by_angle.keys())):
    # visualize(coords_by_angle)
    # input()
    try:
        c = coords_by_angle[angle].pop(0)
    except IndexError:
        pass
    else:
        vaporized += 1
        if vaporized == 200:
            print("Asteroid number 200: (part 2)", (c[0] + ox, c[1] + oy))
            break
