use std::cmp;
use std::collections::{HashSet, HashMap};

static COUNT: usize = 4;


fn part1() {
    let dims = 3;
    let mut pos = vec![
        -3i64, 10, -1,
        -12, -10, -5,
        -9, 0, 10,
        7, -5, -3,
    ];
    // let mut pos = vec![
    //     -1i64, 0, 2,
    //     2, -10, -7,
    //     4, -8, 8,
    //     3, 5, -1,
    // ];
    let mut vel = vec![0i64;pos.len()];

    for _ in 1..=1000 {
        // Apply gravity
        for i in 0..COUNT {
            for j in 0..COUNT {
                if i == j {
                    continue;
                }
                for d in 0..3 {
                    let idx = i*dims + d;
                    let other_idx = j*dims + d;
                    vel[idx] += (pos[other_idx] - pos[idx]).signum();
                }
            }
        }

        // Apply velocity
        for i in 0..COUNT {
            for d in 0..3 {
                let idx = i*dims + d;
                pos[idx] += vel[idx];
            }
        }
    }
    let mut total_energy = 0;
    for (p, v) in pos.chunks(dims).zip(vel.chunks(dims)) {
        let ep = p.iter().map(|x| x.abs()).sum::<i64>();
        let ek = v.iter().map(|x| x.abs()).sum::<i64>();
        // println!("pos={:?}, vel={:?}, E={}*{}", p, v, ep, ek);
        total_energy += ek*ep;
    }
    println!("Total energy (part 1): {}", total_energy);
}


fn step1d(pos: &mut [i64], vel: &mut [i64]) {
    // Apply gravity
    for i in 0..COUNT {
        for j in 0..COUNT {
            if i == j { continue }

            let idx = i;
            let other_idx = j;
            vel[idx] += (pos[other_idx] - pos[idx]).signum();
        }
    }

    // Apply velocity
    for i in 0..COUNT {
        let idx = i;
        pos[idx] += vel[idx];
    }
}


fn factorize(n: u64) -> HashMap<u64, u32> {
    let mut res = HashMap::new();
    let mut n = n;
    while n > 1 {
        for i in 2..=n {
            if n % i == 0 {
                let e = res.entry(i).or_insert(0);
                *e += 1;
                n /= i;
                break;
            }
        }
    }
    res
}


fn add_factors(factors: &mut HashMap<u64, u32>, n: u64) {
    let new_factors = factorize(n);
    for (factor, count) in new_factors {
        let e = factors.entry(factor).or_insert(0);
        *e = cmp::max(*e, count);
    }
}


fn part2() {
    let mut pos = vec![
        -3i64, -12, -9, 7,
        10, -10, 0, -5,
        -1, -5, 10, -3,
    ];
    // let mut pos = vec![
    //     -1i64, 2, 4, 3,
    //     0, -10, -8, 5,
    //     2, -7, 8, -1,
    // ];
    let mut vel = vec![0i64;pos.len()];
    let mut factors = HashMap::new();

    for (p, v) in pos.chunks_mut(COUNT).zip(vel.chunks_mut(COUNT)) {
        let mut seen_states = HashSet::<Vec<i64>>::new();
        let state = p.iter().cloned().chain(v.iter().cloned()).collect();
        seen_states.insert(state);

        loop {
            step1d(p, v);
            let state = p.iter().cloned().chain(v.iter().cloned()).collect();
            if !seen_states.insert(state) {
                break
            }
        }
        // println!("Seen states: {}", seen_states.len());
        add_factors(&mut factors, seen_states.len() as u64);
    }
    // println!("All the factors: {:?}", factors);
    let mut total_cycle = 1;
    for (factor, count) in factors {
        total_cycle *= factor.pow(count);
    }
    println!("Total cycle length (part 2): {}", total_cycle);
}


fn main() {
    part1();
    part2();
}
