input_file = "../input.txt"
with open(input_file, 'r') as f:
    input_text = f.read()
orbits = [orbit.split(')') for orbit in input_text.splitlines()]

distances = {'COM': 0}
orbit_count = 0

for center, satelite in orbits:
    if center in distances:
        distances[satelite] = distances[center] + 1
        orbit_count += distances[satelite]
    else:
        orbits.append((center, satelite))

print(f"Number of orbits (part 1): {orbit_count}")


orbits = {satelite: center for center, satelite in orbits}

def get_orbit_chain(start, stop):
    """Trace a node's orbits back to COM."""
    current = start
    res = []
    while current != stop:
        current = orbits[current]
        res.append(current)
    return list(reversed(res))


you_chain = get_orbit_chain('YOU', 'COM')
santa_chain = get_orbit_chain('SAN', 'COM')

for i, (y, s) in enumerate(zip(you_chain, santa_chain)):
    if y != s:
        break
# i is now the index of the first nodes that differ, which is also the number
# of nodes that are the same in both chains

distance = (
    len(you_chain) - i  # Number of unique nodes in this chain
    + len(santa_chain) - i  # Number of unique nodes in this chain
    + 1  # Have to pass one common node
    - 1  # Converting from number of nodes to number of steps
)
print(f"Distance (part2): {distance}")
