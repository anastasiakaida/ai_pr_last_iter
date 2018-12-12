from agent import TestAgent
from matcher import MATCHER
from detector import DETECTOR

from item import Item
from image import ImagePath, ImageCV2
from enviroment import ImageEnviroment, CameraEnviroment

import cv2

TEST_IMG_PATH = '../../img/test/'
TEST_IMG = [
        '1.jpg', '1.jpg', '1.jpg',
        '2.jpg', '2.jpg', '2.jpg',
        '3.jpg', '3.jpg', '3.jpg',
        '4.jpg', '4.jpg', '4.jpg',
        '5.jpg', '5.jpg', '5.jpg',
        '6.jpg', '6.jpg', '6.jpg',
        '7.jpg', '7.jpg', '7.jpg',
        '8.jpg', '8.jpg', '8.jpg'
        ]
TEST_RESULTS = './test_results/'

def main():
    
    test_num = 3

    item = Item(
            'TEST IMG {}'.format(test_num),
            ImagePath(TEST_IMG_PATH + TEST_IMG[test_num]),
            None,
            None
            )
    env = ImageEnviroment(ImageCV2(None))

    agents = []
    for detector in DETECTOR:
        for matcher in MATCHER:
            tracker = '{}_{}'.format(detector, matcher)
            agents.append(
                    TestAgent(tracker, env, item)
                    )

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    camera = CameraEnviroment(cap)
    for i in range(10):
        frame = camera.get_state()
        cv2.imwrite(TEST_RESULTS + 'frame_{}_{}.jpg'.format(test_num, i), frame)
        for a in agents:
            try:
                print()
                a.env.sensor.data = frame[:]
                result = a.run()
                if result['state_img'] is not None:
                    img_name = '{}_{}_{}.jpg'.format(a.name, test_num, i)
                    cv2.imwrite(TEST_RESULTS + img_name, result['state_img'])
                    tres = '{},{},{},{},{},{},{}\n'.format(
                            a.name,
                            result['item_kp_len'],
                            result['item_des_len'],
                            result['matches_len'],
                            result['item_frame_ratio'],
                            result['time'],
                            img_name
                            )
                    with open(TEST_RESULTS + 'results.txt', 'a') as f:
                        f.write(tres)
                print()
            except Exception as e:
                print(e)
                print('{} doesn\'t work'.format(a.name))

if __name__ == '__main__':
    main()
