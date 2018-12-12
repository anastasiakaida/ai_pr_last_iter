from pymongo import MongoClient
import gridfs

class Handler:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.pattern_recognition
        self.fs = gridfs.GridFS(self.db)

    def find_item_one(self, param):
        return self.db.item.find_one(param)

    def find_item(self, param):
        return self.db.item.find(param)

    def insert_item(self, **kwargs):
        img_id = self.insert_image(kwargs['image'])
        return self.db.item.insert_one({
            'name' : kwargs['name'],
            'img_id' : img_id
            }).inserted_id

    def find_image(self, id):
        return self.fs.get(id)

    def insert_image(self, image):
        return self.fs.put(image, content_type = image.content_type)

