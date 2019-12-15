from enum import Enum
import itertools
import operator

import numpy as np


def input_(stdin):
    return stdin


def output_(input_value):
    return input_value


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
    STDOUT = 3


# op_code: (input_param_count, stdin, output_type, func)
OP_CODES = {
    1: (2, False, Output.VAL, operator.add),
    2: (2, False, Output.VAL, operator.mul),
    3: (0, True, Output.VAL, input_),
    4: (1, False, Output.STDOUT, output_),
    5: (2, False, Output.PTR, jump_if_true),
    6: (2, False, Output.PTR, jump_if_false),
    7: (2, False, Output.VAL, less_than),
    8: (2, False, Output.VAL, equals),
    99: (0, False, Output.NONE, None),
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


def run_program(input_memory, stdin_buffer):
    stdout = []
    memory_ = input_memory.copy()
    instruction_ptr = 0
    while True:
        # Read op_code and parameters
        param_modes, op_code = divmod(memory_[instruction_ptr], 100)
        input_param_count, takes_stdin, output_type, func = OP_CODES[op_code]
        input_values = get_input_params(
            memory_,
            instruction_ptr,
            input_param_count,
            param_modes,
        )
        if takes_stdin:
            input_values.append(stdin_buffer.pop(0))

        # Run operation and handle its output
        if func is None:
            break
        output = func(*input_values)
        step_size = 1 + input_param_count
        if output_type == Output.NONE:
            pass
        elif output_type == Output.VAL:
            output_addr = memory_[instruction_ptr + input_param_count + 1]
            memory_[output_addr] = output
            step_size = 2 + input_param_count
        elif output_type == Output.PTR:
            if output is None:
                pass
            else:
                instruction_ptr = output
                step_size = None
        elif output_type == Output.STDOUT:
            stdout.append(output)

        # Step
        if step_size is not None:
            instruction_ptr += step_size

    return stdout

input_file = "../input.txt"
with open(input_file, 'r') as f:
    input_text = f.read()

# Test:
# input_text = "3,15,3,16,1002,16,10,16,1,16,15,15,4,15,99,0,0"
# input_text = "3,23,3,24,1002,24,10,24,1002,23,-1,23,101,5,23,23,1,24,23,23,4,23,99,0,0"
# input_text = "3,31,3,32,1002,32,10,32,1001,31,-2,31,1007,31,0,33,1002,33,7,33,1,33,31,31,1,32,31,31,4,31,99,0,0,0"
memory = np.array([int(i) for i in input_text.split(',')])


max_phase_settings = None
max_output = -np.inf
for phase_settings in itertools.permutations(range(5)):
    stdout = [0]
    for phase_setting in phase_settings:
        stdin = [phase_setting, stdout[0]]
        stdout = run_program(memory, stdin)
    if stdout[0] > max_output:
        max_output = stdout[0]
        max_phase_settings = phase_settings
print("Max output at (part 1):", max_phase_settings, f"(output={max_output})")
