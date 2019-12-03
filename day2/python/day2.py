import itertools

import numpy as np


def run_program(input_memory):
    memory_ = input_memory.copy()
    instruction_ptr = 0
    while True:
        op_code = memory_[instruction_ptr]
        if op_code == 1:
            # Add
            arg_count = 3
            args = memory_[instruction_ptr + 1 : instruction_ptr + arg_count + 1]
            input_addr1, input_addr2, output_addr = args
            memory_[output_addr] = memory_[input_addr1] + memory_[input_addr2]
            instruction_ptr += 1 + arg_count
        elif op_code == 2:
            # Multiply
            arg_count = 3
            args = memory_[instruction_ptr + 1 : instruction_ptr + arg_count + 1]
            input_addr1, input_addr2, output_addr = args
            memory_[output_addr] = memory_[input_addr1] * memory_[input_addr2]
            instruction_ptr += 1 + arg_count
        elif op_code == 99:
            # Halt
            arg_count = 0
            break
        else:
            raise ValueError(f"Unknown op code: {op_code}")
    return memory_[0]


input_file = "../input.txt"
with open(input_file, 'r') as f:
    input_text = f.read()
memory = np.array([int(i) for i in input_text.split(',')])

memory[1] = 12
memory[2] = 2
output = run_program(memory)

print(f"Memory[0] (part 1): {output}")

target = 19690720
for noun, verb in itertools.product(range(100), range(100)):
    memory[1] = noun
    memory[2] = verb
    output = run_program(memory)
    if output == target:
        break
else:
    raise ValueError(f"Could not find any input that produces {target}")

print(f"Inputs that produce {target} (part 2): {100*noun + verb}")
