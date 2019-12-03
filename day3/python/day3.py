import numpy as np


def get_sections(line):
    return [(s[0], int(s[1:])) for s in line.split(',')]


def get_coords(sections):
    coords = set()
    current_coord = np.array([0, 0])
    for direction, length in sections:
        if direction == 'U':
            dir_unit = np.array([0, -1])
        elif direction == 'D':
            dir_unit = np.array([0, 1])
        elif direction == 'R':
            dir_unit = np.array([1, 0])
        elif direction == 'L':
            dir_unit = np.array([-1, 0])
        else:
            assert(False)
        for _ in range(length):
            current_coord += dir_unit
            coords.add(tuple(current_coord))
    return coords


input_file = "../input.txt"
with open(input_file, 'r') as f:
    input_text = f.read()
wire_sections = [
    get_sections(input_line) for input_line in input_text.splitlines()]
wire_coords = [get_coords(s) for s in wire_sections]
intersections = set.intersection(*wire_coords)
min_distance = min(sum(np.absolute(coords)) for coords in intersections)

print(f"Distance (part 1): {min_distance}")

# print(f"Inputs that produce {target} (part 2): {100*noun + verb}")
