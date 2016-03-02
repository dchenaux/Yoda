#!/usr/bin/env python

from optparse import OptionParser
import os

import yoda


parser = OptionParser(usage="Generate trace for Yoda")
(options, args) = parser.parse_args()

file_path = os.path.abspath(args[0])
yoda.exec_script(open(file_path).read(), file_path)


