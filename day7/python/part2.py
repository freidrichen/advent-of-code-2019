from enum import Enum
from queue import Queue, Empty
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


def noop():
    pass


class Output(Enum):
    VAL = 0
    PTR = 1
    NONE = 2
    STDOUT = 3
    HALT = 4


# op_code: (input_param_count, takes_stdin, output_type, func)
OP_CODES = {
    1: (2, False, Output.VAL, operator.add),
    2: (2, False, Output.VAL, operator.mul),
    3: (0, True, Output.VAL, input_),
    4: (1, False, Output.STDOUT, output_),
    5: (2, False, Output.PTR, jump_if_true),
    6: (2, False, Output.PTR, jump_if_false),
    7: (2, False, Output.VAL, less_than),
    8: (2, False, Output.VAL, equals),
    99: (0, False, Output.HALT, noop),
}



class Program:
    def __init__(self, memory, stdin, stdout):
        self._memory = memory.copy()
        self._instruction_ptr = 0
        self._stdin = stdin
        self._stdout = stdout
        self._halted = False

    def halted(self):
        return self._halted

    def _get_input_params(self, input_param_count, param_modes):
        if not input_param_count:
            return []

        input_ptr = self._instruction_ptr + 1
        input_memory = self._memory[input_ptr:input_ptr + input_param_count]
        param_modes = list(reversed([int(mode) for mode in str(param_modes)]))

        res = []
        for param, mode in itertools.zip_longest(input_memory, param_modes, fillvalue=0):
            if mode == 0:
                # Position mode: Interpret param as a memory address
                res.append(self._memory[param])
            elif mode == 1:
                # Immediate mode: Interpret param as a value
                res.append(param)
            else:
                raise ValueError(f"Invalid parameter mode: {mode}")
        return res

    def run(self):
        while True:
            # Read op_code, parameters and stdin
            param_modes, op_code = divmod(self._memory[self._instruction_ptr], 100)
            input_param_count, takes_stdin, output_type, func = OP_CODES[op_code]
            input_values = self._get_input_params(input_param_count, param_modes)
            if takes_stdin:
                try:
                    input_values.append(self._stdin.get_nowait())
                except Empty:
                    break

            # Run operation and handle its output
            output = func(*input_values)
            step_size = 1 + input_param_count
            if output_type == Output.NONE:
                pass
            elif output_type == Output.VAL:
                output_addr = self._memory[self._instruction_ptr + input_param_count + 1]
                self._memory[output_addr] = output
                step_size = 2 + input_param_count
            elif output_type == Output.PTR:
                if output is None:
                    pass
                else:
                    self._instruction_ptr = output
                    step_size = None
            elif output_type == Output.STDOUT:
                self._stdout.put_nowait(output)
            elif output_type == Output.HALT:
                self._halted = True
                break

            # Step instruction pointer
            if step_size is not None:
                self._instruction_ptr += step_size


input_file = "../input.txt"
with open(input_file, 'r') as f:
    input_text = f.read()

# Test:
# input_text = "3,26,1001,26,-4,26,3,27,1002,27,2,27,1,27,26,27,4,27,1001,28,-1,28,1005,28,6,99,0,0,5"
# input_text = "3,52,1001,52,-5,52,3,53,1,52,56,54,1007,54,5,55,1005,55,26,1001,54,-5,54,1105,1,12,1,53,54,53,1008,54,0,55,1001,55,1,55,2,53,55,53,4,53,1001,56,-1,56,1005,56,6,99,0,0,0,0,10"
memory = np.array([int(i) for i in input_text.split(',')])

max_phase_settings = None
max_output = -np.inf
for phase_settings in itertools.permutations(range(5, 10)):
    stdin = [Queue() for _ in range(5)]
    stdout = stdin[1:] + [stdin[0]]
    programs = []
    for i, phase_setting in enumerate(phase_settings):
        stdin[i].put(phase_setting)
        programs.append(Program(memory, stdin[i], stdout[i]))
    stdin[0].put(0)
    while True:
        running_programs = 0
        for prog in programs:
            if not prog.halted():
                running_programs += 1
                prog.run()
        if not running_programs:
            break
    output = stdout[4].get()
    if output > max_output:
        max_output = output
        max_phase_settings = phase_settings
print("Max output at (part 2):", max_phase_settings, f"(output={max_output})")
