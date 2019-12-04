import numpy as np


def get_required_fuel(masses):
    return np.maximum(masses // 3 - 2, 0)


input_file = "../input.txt"

with open(input_file, 'r') as f:
    input_text = f.read()

module_masses = np.array([int(line) for line in input_text.splitlines()])
required_fuel = np.sum(get_required_fuel(module_masses))

print(f"Required fuel (part 1): {required_fuel}")


required_fuel = 0
for module_mass in module_masses:
    required_module_fuel = get_required_fuel(module_mass)
    unaccounted_fuel = required_module_fuel
    while unaccounted_fuel > 0:
        additional_fuel = get_required_fuel(unaccounted_fuel)
        required_module_fuel += additional_fuel
        unaccounted_fuel = additional_fuel
    required_fuel += required_module_fuel

print(f"Required fuel (part 2): {required_fuel}")
