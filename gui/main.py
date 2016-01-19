from mongoengine import *

connect('yoda')

class Line(EmbeddedDocument):
    lineno = IntField()
    data = ListField()

class File(Document):
    revision = StringField()
    filename = StringField()
    timestamp = DateTimeField()
    lines = ListField(EmbeddedDocumentField(Line))

for file in File.objects:
    print(file.revision)
    print(file.filename)
    print(file.timestamp)
    for line in file.lines:
        print(line.lineno, line.data)