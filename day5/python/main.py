from enum import Enum
import itertools
import operator

import numpy as np


def input_():
    return int(input("Please supply a number: "))


def output_(input_value):
    print(input_value)


def jump_if_true(condition, target):
    if condition != 0:
        return target
    else:
        return None


def jump_if_false(condition, target):
    if condition == 0:
        return target
    else:
        return None


def less_than(x, y):
    return int(x < y)


def equals(x, y):
    return int(x == y)


class Output(Enum):
    VAL = 0
    PTR = 1
    NONE = 2


OP_CODES = {
    1: (2, Output.VAL, operator.add),
    2: (2, Output.VAL, operator.mul),
    3: (0, Output.VAL, input_),
    4: (1, Output.NONE, output_),
    5: (2, Output.PTR, jump_if_true),
    6: (2, Output.PTR, jump_if_false),
    7: (2, Output.VAL, less_than),
    8: (2, Output.VAL, equals),
    99: (0, Output.NONE, None),
}


def get_input_params(memory, instruction_ptr, input_param_count, param_modes):
    if not input_param_count:
        return []

    input_ptr = instruction_ptr + 1
    input_memory = memory[input_ptr:input_ptr + input_param_count]
    param_modes = list(reversed([int(mode) for mode in str(param_modes)]))

    res = []
    for param, mode in itertools.zip_longest(input_memory, param_modes, fillvalue=0):
        if mode == 0:
            # Position mode: Interpret param as a memory address
            res.append(memory[param])
        elif mode == 1:
            # Position mode: Interpret param as a value
            res.append(param)
        else:
            raise ValueError(f"Invalid parameter mode: {mode}")
    return res


def run_program(input_memory):
    memory_ = input_memory.copy()
    instruction_ptr = 0
    while True:
        # Read op_code and parameters
        param_modes, op_code = divmod(memory_[instruction_ptr], 100)
        input_param_count, output_type, func = OP_CODES[op_code]
        input_values = get_input_params(
            memory_,
            instruction_ptr,
            input_param_count,
            param_modes,
        )

        # Run operation and handle its output
        if func is None:
            break
        output = func(*input_values)
        step_size = None
        if output_type == Output.NONE:
            step_size = 1 + input_param_count
        elif output_type == Output.VAL:
            output_addr = memory_[instruction_ptr + input_param_count + 1]
            memory_[output_addr] = output
            step_size = 2 + input_param_count
        elif output_type == Output.PTR:
            if output is None:
                step_size = 1 + input_param_count
            else:
                instruction_ptr = output
                continue

        # Step
        if step_size is not None:
            instruction_ptr += step_size


input_file = "../input.txt"
with open(input_file, 'r') as f:
    input_text = f.read()
memory = np.array([int(i) for i in input_text.split(',')])


print("Part 1:")
# Input 1!
run_program(memory)


print("Part 2:")
# Input 5!
run_program(memory)


# Tests:

# memory = [3,9,8,9,10,9,4,9,99,-1,8]
# run_program(memory)

# memory = [3,9,7,9,10,9,4,9,99,-1,8]
# run_program(memory)

# memory = [3,3,1108,-1,8,3,4,3,99]
# run_program(memory)

# memory = [3,3,1107,-1,8,3,4,3,99]
# run_program(memory)

# memory = [3,12,6,12,15,1,13,14,13,4,13,99,-1,0,1,9]
# run_program(memory)

# memory = [3,3,1105,-1,9,1101,0,0,12,4,12,99,1]
# run_program(memory)

# memory = [
#     3,21,1008,21,8,20,1005,20,22,107,8,21,20,1006,20,31,
#     1106,0,36,98,0,0,1002,21,125,20,4,20,1105,1,46,104,
#     999,1105,1,46,1101,1000,1,20,4,20,1105,1,46,98,99,
# ]
# run_program(memory)
