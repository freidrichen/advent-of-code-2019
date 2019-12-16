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


def relative_base_offset(val):
    return val


def noop():
    pass


class Output(Enum):
    VAL = 0
    PTR = 1
    NONE = 2
    STDOUT = 3
    BASE = 4
    HALT = 5


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
    9: (1, False, Output.BASE, relative_base_offset),
    99: (0, False, Output.HALT, noop),
}


class Memory(dict):
    def __init__(self, list_data):
        for i, data in enumerate(list_data):
            self[i] = data

    def __getitem__(self, key):
        if isinstance(key, slice):
            range_ = range(key.start or 0, key.stop or len(self), key.step or 1)
            return [self[k] for k in range_]
        else:
            return super().__getitem__(key)

    def __missing__(self, key):
        if key < 0:
            raise IndexError(f"Invalid memory address: {key}")
        return 0


class Program:
    def __init__(self, memory_data, stdin, stdout):
        self._memory = Memory(memory_data)
        self._instruction_ptr = 0
        self._relative_base = 0
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
        for i, param in enumerate(input_memory):
            if i < len(param_modes):
                mode = param_modes[i]
            else:
                mode = 0
            if mode == 0:
                # Position mode: Interpret param as a memory address
                if param < 0:
                    raise RuntimeError(f"Invalid memory address: {param}")
                res.append(self._memory[param])
            elif mode == 1:
                # Immediate mode: Interpret param as a value
                res.append(param)
            elif mode == 2:
                # Relative mode: Interpret param as a memory address relative to base
                if self._relative_base + param < 0:
                    raise RuntimeError(
                        f"Invalid memory address: {self._relative_base + param}"
                    )
                res.append(self._memory[self._relative_base + param])
            else:
                raise ValueError(f"Invalid parameter mode: mode")
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
                output_param_mode = (
                    self._memory[self._instruction_ptr] // 10**(input_param_count + 2)
                )
                output_addr = self._memory[self._instruction_ptr + input_param_count + 1]
                if output_param_mode == 2:
                    output_addr += self._relative_base
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
            elif output_type == Output.BASE:
                self._relative_base += output
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
# input_text = "109,1,204,-1,1001,100,1,100,1008,100,16,101,1006,101,0,99"
# input_text = "1102,34915192,34915192,7,4,7,99,0"
# input_text = "104,1125899906842624,99"
# input_text = "109,2,203,-1,204,-1,99"
# input_text = "109,-1,4,1,99"
memory = np.array([int(i) for i in input_text.split(',')])

stdin = Queue()
stdout = Queue()
program = Program(memory, stdin, stdout)
stdin.put(1)
program.run()
assert program.halted()
output = stdout.get()
assert stdout.empty()

print("BOOST keycode (part 1):", output)


program = Program(memory, stdin, stdout)
stdin.put(2)
program.run()
assert program.halted()
output = stdout.get()
assert stdout.empty()
print("Distress beacon coordinates (part 2):", output)
