from optparse import OptionParser

import yoda


parser = OptionParser(usage="Generate trace for yoda")
(options, args) = parser.parse_args()

fin = open(args[0])
yoda.exec_script(fin.read())


