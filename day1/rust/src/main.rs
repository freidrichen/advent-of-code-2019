use std::fs;

fn get_input_numbers() -> Vec<u64> {
    let input_file = "../input.txt";
    fs::read_to_string(input_file)
        .unwrap()
        .lines()
        .map(|s| s.parse().unwrap())
        .collect()
}

fn get_required_fuel(mass: u64) -> u64 {
    (mass / 3).checked_sub(2).unwrap_or(0)
}

fn get_total_required_fuel(mass: u64) -> u64 {
    let mut required_fuel: u64 = get_required_fuel(mass);
    let mut unaccounted_fuel = required_fuel;
    while unaccounted_fuel > 0 {
        let additional_fuel = get_required_fuel(unaccounted_fuel);
        required_fuel += additional_fuel;
        unaccounted_fuel = additional_fuel;
    }
    required_fuel
}

fn main() {
    let module_masses = get_input_numbers();
    let required_fuel: u64 = module_masses
        .iter()
        .map(|&mass| get_required_fuel(mass))
        .sum();
    println!("Required fuel (part 1): {}", required_fuel);

    let required_fuel: u64 = module_masses
        .iter()
        .map(|&mass| get_total_required_fuel(mass))
        .sum();
    println!("Required fuel (part 2): {}", required_fuel);
}
