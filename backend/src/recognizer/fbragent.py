import numpy as np
import cv2

from datetime import datetime

class Agent:
    
    MIN_MATCH_COUNT = 10

    def __init__(self, env, item = None, debug = False):
        self.env = env
        self.item = item
        self.debug = debug

    def set_item(self, item):
        self.item = item

    def run(self):
        if self.debug:
            print('Agent: recognition started')
            tstart = datetime.now()
        
        state = self.env.get_state()
        cntr = None
        if self.item is not None:
            state_grey = cv2.cvtColor(state, cv2.COLOR_BGR2GRAY) # query image
            item_grey = self.item.get_img_grey() # train image
            dst, cntr = self.detect(item_grey, state_grey)
            if dst is None or cntr is None:
                pass
                #self.env.save_state(state)
            else:
                state = cv2.polylines(state, [np.int32(dst)], True, 255, 3, cv2.LINE_AA)
                state = cv2.circle(state, tuple(np.int32(cntr)[0]), 50, 255, -1)
                #self.env.save_state(state)
        else:
            if self.debug:
                print('Agent has no Item')
        
        if self.debug:
            tend = datetime.now()
            dtime = tend - tstart
            if cntr is not None:
                print('Object center: {}'.format(cntr))
            print('Recognition took {} ms'.format(dtime.total_seconds() * 1000))
        
        return state, cntr

    def detect(self, train, query):
        sift = cv2.xfeatures2d.SIFT_create()

        kp1, des1 = sift.detectAndCompute(query, None)
        kp2, des2 = sift.detectAndCompute(train, None)

        if kp1 is None:
            if self.debug:
                print('Can\'t calculate key points of query image')
            return None, None
        if kp2 is None:
            if self.debug:
                print('Can\'t calculate key points of train image')
            return None, None
        if des1 is None:
            if self.debug:
                print('Can\'t calculate descriptor of query image')
            return None, None
        if des2 is None:
            if self.debug:
                print('Can\'t calculate descriptor of train image')
            return None, None

        FLANN_INDEX_KDTREE = 0
        
        index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
        search_params = dict(checks = 100)

        flann = cv2.FlannBasedMatcher(index_params, search_params)

        matches = flann.knnMatch(des1, des2, k = 2)

        good = []
        for m, n in matches:
            if m.distance < 0.7 * n.distance:
                good.append(m)

        if len(good) > Agent.MIN_MATCH_COUNT:
            try:
                src_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1, 1, 2)
                dst_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1, 1, 2)

                M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

                h, w = train.shape
                pts = np.float32([ [0,0], [0, h-1], [w-1, h-1], [w-1, 0] ]).reshape(-1, 1, 2)
                dst = cv2.perspectiveTransform(pts, M)
                
                cntr = np.mean(dst, axis=0)
                cntr = cntr.round()

                print("Matches found - %d/%d" % (len(good), Agent.MIN_MATCH_COUNT))
                return dst, cntr
            except Exception as e:
                print(e)
                return None, None
        else:
            print("Not enough matches are found - %d/%d" % (len(good), Agent.MIN_MATCH_COUNT))
            return None, None
