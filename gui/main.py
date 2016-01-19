from mongoengine import *
from docdef import *

connect('yoda')

for file in File.objects:
    print(file.revision)
    print(file.filename)
    print(file.timestamp)
    for line in file.lines:
        print(line.lineno, line.data)