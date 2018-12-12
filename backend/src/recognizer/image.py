import cv2
import numpy as np

class Image:

    def __init__(self, data):
        self.data = data

    def get_img(self):
        pass

    def get_img_grey(self):
        pass

class ImagePath(Image):

    def get_img(self):
        return cv2.imread(self.data)

    def get_img_grey(self):
        return cv2.imread(self.data, cv2.IMREAD_GRAYSCALE)

class ImageMongo(Image):

    def get_img(self):
        nparr = np.fromstring(self.data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img

    def get_img_grey(self):
        nparr = np.fromstring(self.data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        return img

class ImageCV2(Image):

    def get_img(self):
        return self.data

    def get_img_grey(self):
        return cv2.cvtColor(self.data, cv2.COLOR_BGR2GRAY)
