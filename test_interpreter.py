import os
import io
import pytest
import pickle
from contextlib import redirect_stdout
from trefunge import Trefunge


PROGRAMS = [os.path.join('programs', x) for x in os.listdir('programs')]


class TestInterpreter:

    @pytest.mark.parametrize('program_dir', PROGRAMS)
    def test_program_output(self, program_dir):
        """
        Run each program in ./programs, and compare the execution output to what's in expected_output.txt
        """
        with open(os.path.join(program_dir, 'expected_output.txt'), 'r') as f:
            interpreter = Trefunge(program_dir)
            interpreter_out = io.StringIO()
            with redirect_stdout(interpreter_out):
                interpreter.run()
            assert f.read() == interpreter_out.getvalue()

    @pytest.mark.parametrize('program_dir', PROGRAMS)
    def test_stack_state(self, program_dir):
        """
        Run each program in ./programs, and compare the contents of the stack at every step of execution to what's
        expected in the pickle file stack_history.pkl
        """
        interpreter = Trefunge(program_dir)
        interpreter.enable_stack_history = True
        interpreter.run()
        with open(os.path.join(program_dir, 'stack_history.pkl'), 'rb') as f:
            assert pickle.load(f) == interpreter.stack_history
