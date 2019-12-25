use num::{self, Integer};
use num_derive::FromPrimitive;
use num_traits::FromPrimitive;
use std::fs;
use std::sync::mpsc::{channel, Receiver, Sender};
use std::thread;

type Value = i128;

/// Split number at `pos` in decimal representation.
fn split_num<T>(n: T, pos: usize) -> (T, T)
where
    T: Integer + Clone + Copy + From<i32>,
{
    let divisor = num::pow(10i32, pos).into();
    let div = n / divisor;
    let rem = n % divisor;
    (div, rem)
}

/// Split all param modes
fn split_param_modes(param_modes: Value, input_count: Value) -> (Vec<Value>, Value) {
    let mut rest = param_modes;
    let mut input_modes = Vec::with_capacity(input_count as usize);
    for _ in 0..input_count {
        let (r, mode) = split_num(rest, 1);
        input_modes.push(mode);
        rest = r;
    }
    assert!(rest <= 2);
    (input_modes, rest)
}

#[derive(FromPrimitive)]
enum OpCode {
    Add = 1,
    Mul = 2,
    Input = 3,
    Output = 4,
    JumpIfTrue = 5,
    JumpIfFalse = 6,
    LessThan = 7,
    Equals = 8,
    RelativeBaseOffset = 9,
    Halt = 99,
}

/// An implementation of the IntCode program interface from advent of code 2019.
///
/// Stdin and stdout are handled via channels.
pub struct Program {
    instruction_ptr: usize,
    relative_base: Value,
    memory: Vec<Value>,
    stdin: Receiver<Value>,
    stdout: Sender<Value>,
}

impl Program {
    pub fn new(memory: Vec<Value>, stdin: Receiver<Value>, stdout: Sender<Value>) -> Program {
        Program {
            instruction_ptr: 0,
            relative_base: 0,
            memory: memory,
            stdin: stdin,
            stdout: stdout,
        }
    }

    /// Return the Value at current instruction_ptr address while also advancing
    /// the instruction_ptr by one.
    fn next_mem(&mut self) -> Value {
        let val = self.read_mem(self.instruction_ptr);
        self.instruction_ptr += 1;
        val
    }

    /// Grow the memory to include addr and initialize all new memory addresses
    /// to zero.
    fn init_mem(&mut self, addr: usize) {
        self.memory.resize(addr + 1, 0);
    }

    /// Read from memory address `addr`, growing the memory if needed.
    /// Previously uninitialized memory is initialized to zero.
    fn read_mem(&mut self, addr: usize) -> Value {
        if addr >= self.memory.len() {
            self.init_mem(addr);
        }
        self.memory[addr]
    }

    /// Write `value` to memory address `addr`, growing the memory if needed.
    fn write_mem(&mut self, addr: usize, value: Value) {
        if addr >= self.memory.len() {
            self.init_mem(addr);
        }
        self.memory[addr] = value;
    }

    /// Read a value from memory starting at the instruction pointer for each
    /// parameter mode.
    ///
    /// Parameter modes are interpreted as follows:
    ///   * 0 (Address mode) : Interpret the value as an address and return the
    ///                        value from that address.
    ///   * 1 (Immediate mode) : Return the value directly.
    ///   * 2 (Relative mode) : Interpret the value as an address relative to
    ///                         current relative base and return the value from
    ///                         that address.
    fn read(&mut self, param_modes: Vec<Value>) -> Vec<Value> {
        let mut result = Vec::with_capacity(param_modes.len());
        for mode in param_modes {
            let val = self.next_mem();
            result.push(match mode {
                0 => {
                    assert!(val >= 0);
                    self.read_mem(val as usize)
                }
                1 => val,
                2 => {
                    assert!(self.relative_base + val >= 0);
                    self.read_mem((self.relative_base + val) as usize)
                }
                _ => panic!("Invalid input parameter mode: {}", mode),
            });
        }
        result
    }

    /// Write `val` to the address at instruction pointer and advance the
    /// instruction pointer by one.
    ///
    /// Parameter modes are interpreted as follows:
    ///   * 0 (Address mode) : Interpret the value as an address and write to
    ///                         that address.
    ///   * 2 (Relative mode) : Interpret the value as an address relative to
    ///                         current relative base and write to that address.
    fn write(&mut self, val: Value, param_mode: Value) {
        let addr = self.next_mem()
            + match param_mode {
                0 => 0,
                2 => self.relative_base,
                _ => panic!("Invalid output parameter mode: {}", param_mode),
            };
        assert!(addr >= 0);
        self.write_mem(addr as usize, val);
    }

    /// Start running the program, returning after reaching a halt instruction.
    pub fn run(&mut self) {
        loop {
            let (param_modes, op_code) = split_num(self.next_mem(), 2);
            match FromPrimitive::from_i128(op_code) {
                Some(OpCode::Add) => {
                    let (input_param_modes, output_param_mode) = split_param_modes(param_modes, 2);
                    let sum: Value = self.read(input_param_modes).iter().sum();
                    self.write(sum, output_param_mode);
                }
                Some(OpCode::Mul) => {
                    let (input_param_modes, output_param_mode) = split_param_modes(param_modes, 2);
                    let product: Value = self.read(input_param_modes).iter().product();
                    self.write(product, output_param_mode);
                }
                Some(OpCode::Input) => {
                    let (_, output_param_mode) = split_param_modes(param_modes, 0);
                    let val: Value = self.stdin.recv().unwrap();
                    self.write(val, output_param_mode);
                }
                Some(OpCode::Output) => {
                    let (input_param_modes, _) = split_param_modes(param_modes, 1);
                    let val = self.read(input_param_modes).pop().unwrap();
                    self.stdout.send(val).unwrap();
                }
                Some(OpCode::JumpIfTrue) => {
                    let (input_param_modes, _) = split_param_modes(param_modes, 2);
                    let mut params = self.read(input_param_modes);
                    let new_addr = params.pop().unwrap();
                    let condition = params.pop().unwrap();
                    if condition != 0 {
                        assert!(new_addr >= 0);
                        self.instruction_ptr = new_addr as usize;
                    }
                }
                Some(OpCode::JumpIfFalse) => {
                    let (input_param_modes, _) = split_param_modes(param_modes, 2);
                    let mut params = self.read(input_param_modes);
                    let new_addr = params.pop().unwrap();
                    let condition = params.pop().unwrap();
                    if condition == 0 {
                        assert!(new_addr >= 0);
                        self.instruction_ptr = new_addr as usize;
                    }
                }
                Some(OpCode::LessThan) => {
                    let (input_param_modes, output_param_mode) = split_param_modes(param_modes, 2);
                    let mut params = self.read(input_param_modes);
                    let param2 = params.pop().unwrap();
                    let param1 = params.pop().unwrap();
                    let val = (param1 < param2) as Value;
                    self.write(val, output_param_mode);
                }
                Some(OpCode::Equals) => {
                    let (input_param_modes, output_param_mode) = split_param_modes(param_modes, 2);
                    let mut params = self.read(input_param_modes);
                    let param2 = params.pop().unwrap();
                    let param1 = params.pop().unwrap();
                    let val = (param1 == param2) as Value;
                    self.write(val, output_param_mode);
                }
                Some(OpCode::RelativeBaseOffset) => {
                    let (input_param_modes, _) = split_param_modes(param_modes, 1);
                    let mut params = self.read(input_param_modes);
                    let offset = params.pop().unwrap();
                    self.relative_base += offset;
                }
                Some(OpCode::Halt) => break,
                _ => panic!("Unimplemented OpCode: {}", op_code),
            }
        }
    }
}

fn read_input_file() -> Vec<Value> {
    let input_file = "../input.txt";
    fs::read_to_string(input_file)
        .unwrap()
        .split(",")
        .map(|s| s.trim().parse().unwrap())
        .collect()
}

fn main() {
    let memory = read_input_file();
    let (stdin_sender, stdin_receiver) = channel();
    let (stdout_sender, stdout_receiver) = channel();
    let mut program = Program::new(memory, stdin_receiver, stdout_sender);
    // stdin_sender.send(1).unwrap();
    stdin_sender.send(2).unwrap();
    thread::spawn(move || program.run());

    for output in stdout_receiver {
        println!("{}", output)
    }

    // println!("Total cycle length (part 2): {}", total_cycle);
}

#[cfg(test)]
mod tests {
    use super::*;

    fn create_program(mem: Vec<Value>) -> Program {
        let (_stdin_sender, stdin_receiver) = channel();
        let (stdout_sender, _stdout_receiver) = channel();
        Program::new(mem, stdin_receiver, stdout_sender)
    }

    #[test]
    fn test_split_num() {
        assert_eq!(split_num(1, 0), (1, 0));
        assert_eq!(split_num(12, 0), (12, 0));
        assert_eq!(split_num(12, 1), (1, 2));
        assert_eq!(split_num(12, 2), (0, 12));
        assert_eq!(split_num(12, 3), (0, 12));
    }

    #[test]
    fn test_split_param_modes() {
        assert_eq!(split_param_modes(0, 0), (vec![], 0));
        assert_eq!(split_param_modes(0, 1), (vec![0], 0));
        assert_eq!(split_param_modes(0, 3), (vec![0, 0, 0], 0));
        assert_eq!(split_param_modes(210, 2), (vec![0, 1], 2));
    }

    #[test]
    fn test_read_mem_mode0() {
        let mut program = create_program(vec![-1, 0]);
        program.instruction_ptr = 1;
        assert_eq!(program.read(vec![0]), vec![-1]);
    }

    #[test]
    fn test_read_mem_mode1() {
        let mut program = create_program(vec![-1, 0]);
        program.instruction_ptr = 1;
        assert_eq!(program.read(vec![1]), vec![0]);
    }

    #[test]
    fn test_read_mem_mode2() {
        let mut program = create_program(vec![-1, 0, 1]);
        program.instruction_ptr = 1;
        program.relative_base = 2;
        assert_eq!(program.read(vec![2]), vec![1]);
    }

    #[test]
    fn test_read_mem_multiple() {
        let mut program = create_program(vec![-1, 1, 2, 3, 5]);
        program.instruction_ptr = 1;
        program.relative_base = -1;
        assert_eq!(program.read(vec![2, 1, 0]), vec![-1, 2, 3]);
    }

    #[test]
    fn test_read_outside_mem() {
        let mut program = create_program(vec![-1, 2]);
        program.instruction_ptr = 3;
        program.read(vec![0]);
        assert_eq!(program.memory, vec![-1, 2, 0, 0]);
    }

    #[test]
    fn test_write_mem_mode0() {
        let mut program = create_program(vec![-1, 0]);
        program.instruction_ptr = 1;
        program.write(1, 0);
        assert_eq!(program.memory, vec![1, 0]);
    }

    #[test]
    fn test_write_mem_mode2() {
        let mut program = create_program(vec![-1, 0, 0]);
        program.instruction_ptr = 1;
        program.relative_base = 1;
        program.write(1, 2);
        assert_eq!(program.memory, vec![-1, 1, 0]);
    }

    #[test]
    fn test_write_outside_mem() {
        let mut program = create_program(vec![-1, 2]);
        program.instruction_ptr = 3;
        program.write(1, 0);
        assert_eq!(program.memory, vec![1, 2, 0, 0]);
    }

    #[test]
    fn test_op1_add_mode0() {
        let mut program = create_program(vec![1, 0, 4, 5, 99, -1]);
        program.run();
        assert_eq!(program.memory, vec![1, 0, 4, 5, 99, 100]);
    }

    #[test]
    fn test_op1_add_mode1() {
        let mut program = create_program(vec![1101, 50, 50, 5, 99, -1]);
        program.run();
        assert_eq!(program.memory, vec![1101, 50, 50, 5, 99, 100]);
    }

    #[test]
    fn test_op1_add_mode2() {
        let mut program = create_program(vec![22201, 2, 3, 3, 99, -1]);
        program.relative_base = 2;
        program.run();
        assert_eq!(program.memory, vec![22201, 2, 3, 3, 99, 98]);
    }

    #[test]
    fn test_op2_mul() {
        let mut program = create_program(vec![1102, 5, 3, 5, 99, -1]);
        program.run();
        assert_eq!(program.memory, vec![1102, 5, 3, 5, 99, 15]);
    }

    #[test]
    fn test_op3_input() {
        let (stdin_sender, stdin_receiver) = channel();
        let (stdout_sender, _stdout_receiver) = channel();
        let mut program = Program::new(vec![3, 3, 99, -1], stdin_receiver, stdout_sender);
        stdin_sender.send(5).unwrap();
        program.run();
        assert_eq!(program.memory, vec![3, 3, 99, 5]);
    }

    #[test]
    fn test_op4_output() {
        let (_stdin_sender, stdin_receiver) = channel();
        let (stdout_sender, stdout_receiver) = channel();
        let mut program = Program::new(vec![4, 2, 99], stdin_receiver, stdout_sender);
        program.run();
        assert_eq!(stdout_receiver.recv().unwrap(), 99);
        assert_eq!(program.memory, vec![4, 2, 99]);
    }

    #[test]
    fn test_op5_jump_if_true_1() {
        let mut program = create_program(vec![1105, 1, 4, -1, 99]);
        program.run();
    }

    #[test]
    fn test_op5_jump_if_true_2() {
        let mut program = create_program(vec![1105, 0, 4, 99, -1]);
        program.run();
    }

    #[test]
    fn test_op5_jump_if_true_3() {
        let mut program = create_program(vec![1105, -1, 4, -1, 99]);
        program.run();
    }

    #[test]
    fn test_op6_jump_if_false_1() {
        let mut program = create_program(vec![1106, 0, 4, -1, 99]);
        program.run();
    }

    #[test]
    fn test_op6_jump_if_false_2() {
        let mut program = create_program(vec![1106, 1, 4, 99, -1]);
        program.run();
    }

    #[test]
    fn test_op6_jump_if_false_3() {
        let mut program = create_program(vec![1106, -1, 4, 99, -1]);
        program.run();
    }

    #[test]
    fn test_op7_less_than_1() {
        let mut program = create_program(vec![1107, -1, 3, 5, 99, -1]);
        program.run();
        assert_eq!(program.memory, vec![1107, -1, 3, 5, 99, 1]);
    }

    #[test]
    fn test_op7_less_than_2() {
        let mut program = create_program(vec![1107, 1, -3, 5, 99, -1]);
        program.run();
        assert_eq!(program.memory, vec![1107, 1, -3, 5, 99, 0]);
    }

    #[test]
    fn test_op8_equals_1() {
        let mut program = create_program(vec![1108, 3, 3, 5, 99, -1]);
        program.run();
        assert_eq!(program.memory, vec![1108, 3, 3, 5, 99, 1]);
    }

    #[test]
    fn test_op8_equals_2() {
        let mut program = create_program(vec![1108, 2, 3, 5, 99, -1]);
        program.run();
        assert_eq!(program.memory, vec![1108, 2, 3, 5, 99, 0]);
    }

    #[test]
    fn test_op9_relative_base_offset() {
        let mut program = create_program(vec![109, 2, 99]);
        program.run();
        assert_eq!(program.relative_base, 2);
    }

    #[test]
    fn test_op99_halt() {
        let mut program = create_program(vec![99, -1]);
        program.run();
    }

    #[test]
    fn test_input_output_program1() {
        // Test program from day 5
        let mem = vec![3, 9, 8, 9, 10, 9, 4, 9, 99, -1, 8];
        let (stdin_sender, stdin_receiver) = channel();
        let (stdout_sender, stdout_receiver) = channel();
        {
            let mut program = Program::new(mem.clone(), stdin_receiver, stdout_sender);
            stdin_sender.send(8).unwrap();
            program.run();
        }
        assert_eq!(stdout_receiver.into_iter().collect::<Vec<_>>(), vec![1]);
    }

    // #[test]
    // fn test_
    // 3,9,7,9,10,9,4,9,99,-1,8
}
