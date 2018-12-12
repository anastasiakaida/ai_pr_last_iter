import cv2

ENVIROMENT = [ 'CAMERA', 'IMAGE' ]

class EnviromentNotFound(Exception):
    pass

from image import ImagePath

class EnviromentFactory:

    def get_enviroment(self, enviroment, sensor, width = None, height = None):
        env = enviroment.upper()
        if env == ENVIROMENT[0]:
            if width is None and height is None:
                return CameraEnviroment(sensor)
            return CameraEnviroment(sensor, width, height)
        elif env == ENVIROMENT[1]:
            return ImageEnviroment(ImagePath(sensor))
        raise EnviromentNotFound('{} enviroment wasn\'t found'.format(enviroment))

class Enviroment:

    def __init__(self, sensor):
        self.sensor = sensor
    
    def get_state(self):
        return self.sensor

    def get_state_grey(self):
        pass

class CameraEnviroment(Enviroment):

    def __init__(self, camera_id, width = 1280, height = 720):
        cap = cv2.VideoCapture(camera_id)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        super().__init__(cap)

    def get_state(self):
        buffer_size = self.sensor.get(cv2.CAP_PROP_BUFFERSIZE)
        while buffer_size >= 0:
            ret, frame = self.sensor.read()
            buffer_size -= 1
        return frame.copy()

    def get_state_grey(self):
        return cv2.cvtColor(self.get_state(), cv2.COLOR_BGR2GRAY).copy()

    def set_resolution(self, width, height):
        self.sensor.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.sensor.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

class ImageEnviroment(Enviroment):

    def get_state(self):
        return self.sensor.get_img().copy()

    def get_state_grey(self):
        return self.sensor.get_img_grey().copy()
