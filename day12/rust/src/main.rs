fn main() {
    let dims = 3;
    let count = 4;
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
        for i in 0..count {
            for j in 0..count {
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
        for i in 0..count {
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
