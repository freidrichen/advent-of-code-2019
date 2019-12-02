import numpy as np


input_file = "../input.txt"

with open(input_file, 'r') as f:
    input_text = f.read()

memory = np.array([int(i) for i in input_text.split(',')])
memory[1] = 12
memory[2] = 2

instruction_ptr = 0
while True:
    op_code = memory[instruction_ptr]
    if op_code == 1:
        # Add
        arg_count = 3
        input_addr1, input_addr2, output_addr = memory[instruction_ptr + 1 : instruction_ptr + arg_count]
        memory[output_addr] = memory[input_addr1] + memory[input_addr2]
        instruction_ptr += 1 + arg_count
    elif op_code == 2:
        # Multiply
        arg_count = 3
        input_addr1, input_addr2, output_addr = memory[instruction_ptr + 1 : instruction_ptr + arg_count]
        memory[output_addr] = memory[input_addr1] * memory[input_addr2]
        instruction_ptr += 1 + arg_count
    elif op_code == 99:
        # Halt
        arg_count = 0
        break

print(f"Memory[0] (part 1): {memory[0]}")

# print(f"Required fuel (part 2): {required_fuel}")
