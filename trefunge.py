from random import choice
import termios
import sys
import tty
import argparse
import os
from functools import partial


class Stack(list):
    def pop(self, *args, **kwargs):
        try:
            return super().pop(*args, **kwargs)
        except IndexError:
            return 0


class Trefunge:

    # Uses Befunge93 instruction set, plus two new ones:
    # - zenith: go "up" a layer
    # - nadir: go "down" a layer
    # These layers are described by standard Befunge93 files (but using the extension .3f) where the ordering is
    # determined by the numerical representation of the filename, sans extension. e.g., file 0.bf would be at the bottom
    # (and first) layer, anything larger would be above, anything negative would be below.
    # Negative can be denoted by prefixing the filename with _.

    @property
    def _pc(self):
        return self.x, self.y, self.z

    def __init__(self, program_directory):
        self.x = self.y = 0  # (0, 0, 0) is top left, initial layer
        program_raw, self.z = self._read_files(program_directory)
        self.direction = (1, 0, 0)
        self.program = self._parse_program(program_raw)
        self.stack = Stack()
        self.enable_stack_history = False
        self.stack_history = []
        self.string_mode = False
        self.signal_exit = False
        self.instruction_map = {
            ' ': lambda: None,
            '+': self._addition,
            '-': self._subtraction,
            '*': self._multiplication,
            '/': self._multiplication,
            '%': self._modulo,
            '!': self._not,
            '`': self._gt,
            '>': self._right,
            '<': self._left,
            '^': self._up,
            'v': self._down,
            'z': self._zenith,
            'n': self._nadir,
            '?': self._random_direction,
            '_': self._h_if,
            '|': self._v_if,
            '"': self._toggle_string_mode,
            ':': self._duplicate,
            '\\': self._swap,
            '$': self._discard,
            '.': self._output_int,
            ',': self._output_ascii,
            '#': self._bridge,
            'g': self._get,
            'p': self._put,
            '&': self._get_int,
            '~': self._get_char,
            '@': partial(self._exit),
            '0': partial(self._num, '0'),
            '1': partial(self._num, '1'),
            '2': partial(self._num, '2'),
            '3': partial(self._num, '3'),
            '4': partial(self._num, '4'),
            '5': partial(self._num, '5'),
            '6': partial(self._num, '6'),
            '7': partial(self._num, '7'),
            '8': partial(self._num, '8'),
            '9': partial(self._num, '9'),
        }

    def _instruction_lookup(self, cmd):
        return self.instruction_map.get(cmd,
                                        partial(self._error, f'{cmd} is not a valid command. Exiting with error...'))

    def _advance_pc(self):
        self.x += self.direction[0]
        self.y += self.direction[1]
        self.z += self.direction[2]

        if self.x < 0:
            self.x += len(self.program[self.z][0])
        elif self.x == len(self.program[self.z][0]):
            self.x = 0
        if self.y < 0:
            self.y += len(self.program[self.z])
        elif self.y == len(self.program[self.z]):
            self.y = 0
        if self.z < 0:
            self.z += len(self.program)
        elif self.z == len(self.program):
            self.z = 0

    def run(self):
        while not self.signal_exit:
            if self.enable_stack_history:
                self.stack_history.append(self.stack.copy())
            cmd = self.program[self.z][self.y][self.x]
            if self.string_mode and cmd != '"':
                self.stack.append(ord(self.program[self.z][self.y][self.x]))
            else:
                self._instruction_lookup(cmd)()
            self._advance_pc()

    def _addition(self):
        a = self.stack.pop()
        b = self.stack.pop()
        self.stack.append(a + b)

    def _subtraction(self):
        a = self.stack.pop()
        b = self.stack.pop()
        self.stack.append(b - a)

    def _multiplication(self):
        a = self.stack.pop()
        b = self.stack.pop()
        self.stack.append(a * b)

    def _division(self):
        a = self.stack.pop()
        b = self.stack.pop()
        self.stack.append(b // a)

    def _modulo(self):
        a = self.stack.pop()
        b = self.stack.pop()
        self.stack.append(b % a)

    def _not(self):
        x = self.stack.pop()
        self.stack.append(1 if x == 0 else 0)

    def _gt(self):
        a = self.stack.pop()
        b = self.stack.pop()
        self.stack.append(1 if b > a else 0)

    def _right(self):
        self.direction = (1, 0, 0)

    def _left(self):
        self.direction = (-1, 0, 0)

    def _up(self):
        self.direction = (0, -1, 0)

    def _down(self):
        self.direction = (0, 1, 0)

    def _zenith(self):
        self.direction = (0, 0, 1)

    def _nadir(self):
        self.direction = (0, 0, -1)

    def _random_direction(self):
        choice([self._right, self._left, self._up, self._down, self._zenith, self._nadir])()

    def _h_if(self):
        self._right() if self.stack.pop() == 0 else self._left()

    def _v_if(self):
        self._down() if self.stack.pop() == 0 else self._up()

    def _z_if(self):
        self._nadir() if self.stack.pop() == 0 else self._zenith()

    def _toggle_string_mode(self):
        self.string_mode = not self.string_mode

    def _duplicate(self):
        val = self.stack.pop()
        self.stack.append(val)
        self.stack.append(val)

    def _swap(self):
        self.stack.append(self.stack.pop(-2))

    def _discard(self):
        self.stack.pop()

    def _output_int(self):
        print(int(self.stack.pop()), end='')

    def _output_ascii(self):
        print(chr(self.stack.pop()), end='')

    def _bridge(self):
        self._advance_pc()

    def _get(self):
        y = self.stack.pop()
        x = self.stack.pop()
        try:
            self.stack.append(ord(self.program[self.z][y][x]))
        except IndexError:
            self.stack.append(0)

    def _put(self):
        y = self.stack.pop()
        x = self.stack.pop()
        v = self.stack.pop()
        try:
            self.program[self.z][y][x] = chr(v)
        except IndexError:
            self._error(f'Put command out of bounds with coordinates ({self.x}, {self.y})')

    def _get_int(self):
        c = self._getch()
        if not c.isnumeric():
            print(f'{c} is not an integer, try again')
            self._get_int()
        else:
            self.stack.append(int(c))

    def _get_char(self):
        self.stack.append(ord(self._getch()))

    def _exit(self):
        self.signal_exit = True

    def _num(self, c):
        n = int(c)
        self.stack.append(n)

    @staticmethod
    def _error(msg=''):
        print(msg)
        exit(1)

    @staticmethod
    def _read_files(program_dir):
        # All files must have int-castable names and be of a .3f extension
        program_files = sorted([x for x in os.listdir(program_dir) if
                         x.split('.')[0].replace('_', '').isnumeric() and x.split('.')[1] == '3f'],
                               key=lambda x: int(x.split('.')[0].replace('_', '-')))

        z = program_files.index('0.3f')

        program_layers = []
        for filename in program_files:
            with open(os.path.join(program_dir, filename), 'r') as f:
                program_layers.append(f.read())

        return program_layers, z

    @staticmethod
    def _parse_program(data):
        parsed_layers = []
        for raw_layer in data:
            lines = raw_layer.split('\n')
            max_line_len = len(max(lines, key=len))
            parsed_layers.append([list(s.ljust(max_line_len)) for s in lines])
        return parsed_layers

    @staticmethod
    def _getch():
        # https://stackoverflow.com/a/28143542/7902764
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('program_dir', type=str)
    parsed_args = parser.parse_args()
    interp = Trefunge(parsed_args.program_dir)
    interp.run()
