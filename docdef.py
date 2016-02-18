from mongoengine import *


class Line(EmbeddedDocument):
    lineno = IntField()
    data = ListField()


class File(Document):
    user = StringField()
    revision = StringField()
    filename = StringField()
    timestamp = DateTimeField()
    content = StringField()
    lines = ListField(EmbeddedDocumentField(Line))