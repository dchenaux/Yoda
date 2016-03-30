from mongoengine import *


class Line(EmbeddedDocument):
    lineno = IntField()
    data = DictField()

class Frame(EmbeddedDocument):
    name = StringField()
    lines = ListField(EmbeddedDocumentField(Line))


class File(Document):
    user = StringField()
    revision = StringField()
    filename = StringField()
    timestamp = DateTimeField()
    content = StringField()
    frames = ListField()