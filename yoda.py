import bdb
from collections import defaultdict
from datetime import datetime
import subprocess
import sys
import traceback
import io as StringIO

from mongoengine import *

import settings
from docdef import *


class Yoda(bdb.Bdb):
    json_results = None
    instrumented_types = (int, str)
    #instrumented_types = (dict, bytes, bool, float, int, list, object, str, tuple)


    def __init__(self):
        bdb.Bdb.__init__(self)
        if not settings.DEBUG: # If DEBUG is to FALSE connect to mongodb
            connect('yoda')
        self._clear_cache()

        self._wait_for_mainpyfile = 0

        # Key: frame object
        # Value: monotonically increasing small ID, based on call order
        self.frame_ordered_ids = {}
        self.cur_frame_id = 1

        self.breakpoints = []

    def get_frame_id(self, cur_frame):
      return self.frame_ordered_ids[cur_frame]

    def _clear_cache(self):
        self.json_results = defaultdict(lambda: defaultdict(list))

    def _filter_locals(self, local_vars):
        new_locals = []
        for name, value in list(local_vars.items()):
            if name.startswith('__'):
                continue
            if not isinstance(value, self.instrumented_types):
                continue
            new_locals.append((name, value))
        return new_locals

    def _get_git_revision_short_hash(self):
        return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'])

    def _get_git_username(self):
        return subprocess.check_output(['git', 'config', 'user.name'])

    def user_call(self, frame, args):
        # TODO: may be also flush on call
        self.interaction(frame, None, 'call')

    def user_line(self, frame):
        #lineno = frame.f_lineno-1
        #self.json_results[frame.f_globals['__file__']][lineno].append(self._filter_locals(frame.f_locals))
        #print(lineno, self._filter_locals(frame.f_locals))
        self.interaction(frame, None, 'step_line')

    def user_return(self, frame, value):
        self.interaction(frame, None, 'return')

    def user_exception(self, frame, exception):
        name = frame.f_code.co_name or "<unknown>"
        print("exception in", name, exception)
        self.set_continue()  # continue

    def forget(self):
        self.lineno = None
        self.stack = []
        self.curindex = 0
        self.curframe = None

    def setup(self, f, t):
        self.forget()
        self.stack, self.curindex = self.get_stack(f, t)
        self.curframe = self.stack[self.curindex][0]

    def interaction(self, frame, traceback, event_type):
        self.setup(frame, traceback)
        tos = self.stack[self.curindex]
        top_frame = tos[0]
        lineno = tos[1]

        # Avoid tracing imported libraries
        if  self.canonic(top_frame.f_code.co_filename).startswith(('/lib/','/usr/')):
            return
        # also don't trace inside of the magic "constructor" code
        if top_frame.f_code.co_name == '__new__':
            return
        # or __repr__, which is often called when running print statements
        if top_frame.f_code.co_name == '__repr__':
            return

        if event_type == 'call':
            return

        if event_type == 'step_line':
            print(lineno, self._filter_locals(top_frame.f_locals))

        if event_type == 'return':
            return

        # each element is a pair of (function name, ENCODED locals dict)
        encoded_stack_locals = []

    def run_script(self,script_str):
        self.executed_script = script_str
        self.executed_script_lines = self.executed_script.splitlines()

        for (i, line) in enumerate(self.executed_script_lines):
          line_no = i + 1
          if line.endswith('#break'):
            self.breakpoints.append(line_no)

        # When bdb sets tracing, a number of call and line events happens
        # BEFORE debugger even reaches user's code (and the exact sequence of
        # events depends on python version). So we take special measures to
        # avoid stopping before we reach the main script (see user_line and
        # user_call for details).
        self._wait_for_mainpyfile = 1

        user_stdout = StringIO.StringIO()

        #sys.stdout = user_stdout

        user_globals = {"__name__"    : "__main__",
                "__user_stdout__" : user_stdout,
                # sentinel value for frames deriving from a top-level module
                "__OPT_toplevel__": True}

        self.run(script_str, user_globals, user_globals)

def exec_script(script_str):
    logger = Yoda()
    try:
        logger.run_script(script_str)
    except bdb.BdbQuit:
        pass




exec_script(open("tests/sample_program.py").read())
