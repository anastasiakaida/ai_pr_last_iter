from flask.json import JSONEncoder
from bson.objectid import ObjectId

class AprJsonEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(self, obj)

