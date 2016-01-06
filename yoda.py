import bdb
from collections import defaultdict
#import types
#import os.path
from pymongo import MongoClient
from datetime import datetime
import settings
import inspect
import sys

class Yoda(bdb.Bdb):
    run = 0
    json_results = None
    instrumented_types = (int)
    #instrumented_types = (dict, bytes, bool, float, int, list, object, str, tuple)


    def __init__(self):
        bdb.Bdb.__init__(self)
        if not settings.DEBUG: # If DEBUG is to FALSE connect to mongodb
            self.client = MongoClient(settings.MONGODB_URI)
            self.db = self.client['yoda']
        self._clear_cache()

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

    def user_call(self, frame, args):
        # TODO: may be also flush on call
        self.set_step() # continue

    def user_line(self, frame):
        # str line number because mongo do not accept int keys
        lineno = str(frame.f_lineno-1)
        self.json_results[frame.f_globals['__file__']][lineno].append(self._filter_locals(frame.f_locals))
        self.set_step()

    def user_return(self, frame, value):
        if self.json_results:
            for module_file, lines in self.json_results.items():
                if settings.DEBUG:
                    print (module_file)
                    print (lines)
                    
                else:
                    #collection_name, _ = os.path.splitext(os.path.basename(module_file))
                    collection = self.db['file']
                    item = {'revision': 1,
                            'filename': module_file,
                            'timestamp': datetime.utcnow(),
                            'lines': [{'lineno': lineno, 'data': data} for lineno, data in lines.items()]}
                    collection.insert(item)
            self._clear_cache()
        self.set_step()  # continue

    def user_exception(self, frame, exception):
        name = frame.f_code.co_name or "<unknown>"
        print("exception in", name, exception)
        self.set_continue()  # continue

db = Yoda()
