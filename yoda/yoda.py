import bdb
from collections import defaultdict
from datetime import datetime
import subprocess
import sys
import traceback
import inspect
import types
import timeit

from mongoengine import *

import settings
from docdef import *


class Yoda(bdb.Bdb):
    run = 0
    json_results = None
    instrumented_types = (int, float)
    #instrumented_types = (dict, bytes, bool, float, int, list, object, str, tuple)

    prev_lineno = 0

    def __init__(self):
        bdb.Bdb.__init__(self)
        if not settings.DEBUG: # If DEBUG is to FALSE connect to mongodb
            connect('yoda')
        self._clear_cache()

    def _clear_cache(self):
        self.json_results = defaultdict(defaultdict)

    def _filter_locals(self, local_vars):
        new_locals = {}
        for name, value in list(local_vars.items()):
            if name.startswith('__'):
                continue
            if not isinstance(value, self.instrumented_types):
                continue
            new_locals[name] = [value]

        return new_locals

    def _get_git_revision_short_hash(self):
        return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'])

    def _get_git_username(self):
        return subprocess.check_output(['git', 'config', 'user.name'])

    def user_call(self, frame, args):
        self.set_step() # continue

    def user_line(self, frame):
        #print(inspect.getframeinfo(frame))
        lineno = frame.f_lineno
        #print(self.prev_lineno, lineno)

        locals = self._filter_locals(frame.f_locals)
        filename = frame.f_globals['__file__']

        if not self.json_results:
            self.json_results[filename][self.prev_lineno] = locals
        else :
            for module_file, lines in self.json_results.items():
                keylist = []
                for k in lines.keys():
                    keylist.append(k)
            if self.prev_lineno not in keylist:
                self.json_results[filename][self.prev_lineno] = locals
            else:
                for k in locals:
                    for v in locals[k]:
                        if k in self.json_results[filename][self.prev_lineno]:
                            self.json_results[frame.f_globals['__file__']][self.prev_lineno][k].append(v)
                        else:
                            self.json_results[frame.f_globals['__file__']][self.prev_lineno][k] = [v]

        print('>>', lineno, self.prev_lineno, self.json_results[frame.f_globals['__file__']][self.prev_lineno])

        self.prev_lineno = lineno

        self.set_step()

    def user_return(self, frame, value):
        self.set_step()  # continue

    def user_exception(self, frame, exception):
        name = frame.f_code.co_name or "<unknown>"
        print("exception in", name, exception)
        self.set_continue()  # continue

    def set_quit(self):
        self.stopframe = self.botframe
        self.returnframe = None
        self.quitting = True
        sys.settrace(None)

        if self.json_results:

            if settings.DEBUG:
                pass
            else:
                for module_file, lines in self.json_results.items():
                    if 'yoda.py' not in module_file:
                        file = open(module_file, 'r')
                        file_content = file.read()
                        file.close()

                        if file_content:
                            item = File(user=self._get_git_username(), revision=self._get_git_revision_short_hash(), filename=module_file, timestamp=datetime.now(), content=file_content)
                            for lineno, data in sorted(lines.items()):
                                line = Line(lineno = lineno, data = data)
                                item.lines.append(line)

                            item.save()
                self._clear_cache()
        print(timeit.timeit('"-".join(str(n) for n in range(100))', number=10000))

db = Yoda()
