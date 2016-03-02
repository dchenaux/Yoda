import bdb
import io as StringIO
import subprocess
from collections import defaultdict
from datetime import datetime

from mongoengine import *

import settings
from docdef import *



class Yoda(bdb.Bdb):
    json_results = None
    instrumented_types = (int, str)
    #instrumented_types = (dict, bytes, bool, float, int, list, object, str, tuple)


    def __init__(self, file_path):
        bdb.Bdb.__init__(self)
        if not settings.DEBUG: # If DEBUG is to FALSE connect to mongodb
            connect('yoda')
            #TODO : show some error message if it can't connect to the database
        self._clear_cache()

        self.file_path = file_path

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
        if self._wait_for_mainpyfile:
            return
        self.interaction(frame, None, 'call')

    def user_line(self, frame):
        if self._wait_for_mainpyfile:
            if (self.canonic(frame.f_code.co_filename) != "<string>" or
                frame.f_lineno <= 0):
                return
            self._wait_for_mainpyfile = 0
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

        # don't trace inside of ANY functions that aren't user-written code
        # (e.g., those from imported modules -- e.g., random, re -- or the
        # __restricted_import__ function in this file)
        #
        # empirically, it seems like the FIRST entry in self.stack is
        # the 'run' function from bdb.py, but everything else on the
        # stack is the user program's "real stack"

        # Look only at the "topmost" frame on the stack ...

        # it seems like user-written code has a filename of '<string>',
        # but maybe there are false positives too?
        if self.canonic(top_frame.f_code.co_filename) != '<string>':
          return
        # also don't trace inside of the magic "constructor" code
        if top_frame.f_code.co_name == '__new__':
          return
        # or __repr__, which is often called when running print statements
        if top_frame.f_code.co_name == '__repr__':
          return

        # if top_frame.f_globals doesn't contain the sentinel '__OPT_toplevel__',
        # then we're in another global scope altogether, so skip it!
        # (this comes up in tests/backend-tests/namedtuple.txt)
        if '__OPT_toplevel__' not in top_frame.f_globals:
          return

        if event_type == 'call':
            return

        if event_type == 'step_line':
            print(lineno, self._filter_locals(top_frame.f_locals))
            self.json_results[self.file_path][lineno].append(self._filter_locals(top_frame.f_locals))

        if event_type == 'return':
            return

        self.forget()

    def run_script(self,script_str):

        user_stdout = StringIO.StringIO()

        #sys.stdout = user_stdout

        user_globals = {"__name__"    : "__main__",
                "__user_stdout__" : user_stdout,
                # sentinel value for frames deriving from a top-level module
                "__OPT_toplevel__": True}

        self.run(script_str, user_globals, user_globals)

        if self.json_results:
            for module_file, lines in self.json_results.items():
                if settings.DEBUG:
                    for lineno, data in lines.items():
                        print(lineno)
                        print(type(data))

                else:
                    item = File(user=self._get_git_username(), revision=self._get_git_revision_short_hash(), filename=module_file, timestamp=datetime.now(), content=script_str)
                    for lineno, data in sorted(lines.items()):
                        line = Line(lineno = lineno, data = data)
                        item.lines.append(line)

                    item.save()

def exec_script(script_str,file_path):
    logger = Yoda(file_path)
    try:
        logger.run_script(script_str)
    except bdb.BdbQuit:
        pass
