import itertools


input_file = "../input.txt"
with open(input_file, 'r') as f:
    input_text = f.read()
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
    len({
        shrink(ax - ox, ay - oy)
        for (ax, ay) in asteroids
        if ox != ax or oy != ay
    }) for (ox, oy) in asteroids]

print("Max visible (part 1):", max(visible))
