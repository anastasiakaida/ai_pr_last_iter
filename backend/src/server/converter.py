from werkzeug.routing import BaseConverter
from bson.objectid import ObjectId
from bson.errors import InvalidId
from flask import abort

class ObjectIdConverter(BaseConverter):

    def to_python(self, value):
        try:
            return ObjectId(value)
        except InvalidId:
            raise abort(404)

    def to_url(self, value):
        return str(value)
