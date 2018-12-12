import numpy as np
import cv2

from datetime import datetime

try: 
    from .tracker import TrackerBuilder, TrackerBuilderError
except (SystemError, ImportError):
    from tracker import TrackerBuilder, TrackerBuilderError

try:
    from .enviroment import EnviromentFactory, EnviromentNotFound
except (SystemError, ImportError):
    from enviroment import EnviromentFactory, EnviromentNotFound

class AgentBuilderError(Exception):
    pass

class AgentBuilder:

    def __init__(self):
        self.tb = TrackerBuilder()
        self.ef = EnviromentFactory()

    def get_agent(self,
            verbose,
            not_smart,
            detector,
            matcher,
            etype,
            esensor,
            ewidth,
            eheight,
            item
            ):

        try:
            tracker = self.tb.get_tracker(detector, matcher)
            enviroment = self.ef.get_enviroment(
                    etype, esensor, ewidth, eheight
                    )
            if verbose:
                if not_smart:
                    return VerboseAgent(tracker, enviroment, item)
                else:
                    return VerboseSmartAgent(tracker, enviroment, item)
            else:
                if not_smart:
                    return Agent(tracker, enviroment, item)
                else:
                    return SmartAgent(tracker, enviroment, item)
        except (TrackerBuilderError, EnviromentNotFound) as e:
            print(e)
            raise AgentBuilderError('Couldn\'t build agent')

class Agent:

    def __init__(self, tracker, env = None, item = None):
        self.tracker = tracker
        self.env = env
        self.item = item

    def get_name(self):
        return '{} {}'.format(
                self.tracker.get_name(),
                type(self).__name__
                )

    def run(self):
        stime = datetime.now()
        state = self.env.get_state() # color img from enviroment

        if self.item is not None:
            state_grey = cv2.cvtColor(state, cv2.COLOR_BGR2GRAY) # query grey image
            item_grey = self.item.get_img_grey() # train grey image

            qkp, qdes = self.tracker.detect_and_compute(state_grey)
            tkp, tdes = self.tracker.detect_and_compute(item_grey)

            matches = self.tracker.match(qdes, tdes)
            if len(matches) > self.tracker.matcher.MIN_MATCH_COUNT:
                dst = self.calc_dst(matches, item_grey, qkp, tkp)
                cntr = self.calc_cntr(dst)

                state = cv2.polylines(state, [np.int32(dst)], True, 255, 3, cv2.LINE_AA)
                state = cv2.circle(state, tuple(np.int32(cntr)[0]), 50, 255, -1)
                cv2.circle
                return state, cntr, stime
        
        return state, None, stime

    def calc_dst(self, gmatches, train, qkp, tkp):
        src_pts = np.float32([ tkp[m.trainIdx].pt for m in gmatches ]).reshape(-1, 1, 2)
        dst_pts = np.float32([ qkp[m.queryIdx].pt for m in gmatches ]).reshape(-1, 1, 2)

        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

        h, w = train.shape
        pts = np.float32([ [0,0], [0, h-1], [w-1, h-1], [w-1, 0] ]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, M)
        return dst

    def calc_cntr(self, dst):
        cntr = np.mean(dst, axis=0)
        cntr = cntr.round()
        return cntr

    def set_tracker(self, tracker):
        self.tracker = tracker

    def set_enviroment(self, env):
        self.env = env

    def set_item(self, item):
        self.item = item

class SmartAgent(Agent):

    def run(self):
        stime = datetime.now()
        state = self.env.get_state() # color img from enviroment

        if self.item is not None:
            state_grey = cv2.cvtColor(state, cv2.COLOR_BGR2GRAY) # query grey image
            item_grey = self.item.get_img_grey() # train grey image

            qkp, qdes = self.tracker.detect_and_compute(state_grey)
            if self.item.des is None:
                tkp, tdes = self.tracker.detect_and_compute(item_grey)
                self.item.kp = tkp
                self.item.des = tdes
            else:
                tkp = self.item.kp
                tdes = self.item.des

            matches = self.tracker.match(qdes, tdes)
            if len(matches) > self.tracker.matcher.MIN_MATCH_COUNT:
                dst = self.calc_dst(matches, item_grey, qkp, tkp)
                cntr = self.calc_cntr(dst)

                state = cv2.polylines(state, [np.int32(dst)], True, 255, 3, cv2.LINE_AA)
                state = cv2.circle(state, tuple(np.int32(cntr)[0]), 50, 255, -1)
                cv2.circle
                return state, cntr, stime
        
        return state, None, stime

class VerboseAgent(Agent):

    def __init__(self, tracker, env = None, item = None):
        print('Creating {} agent'.format(tracker.get_name()))
        super().__init__(tracker, env, item)
        print('{} agent created'.format(tracker.get_name()))

    def run(self):
        print('{} start run'.format(self.get_name()))
        stime = datetime.now()
        state = self.env.get_state() # color img from enviroment

        if self.item is not None:
            print('{} recognizing {}'.format(self.get_name(), self.item.get_name()))
            state_grey = cv2.cvtColor(state, cv2.COLOR_BGR2GRAY) # query grey image
            item_grey = self.item.get_img_grey() # train grey image

            qkp, qdes = self.tracker.detect_and_compute(state_grey)
            tkp, tdes = self.tracker.detect_and_compute(item_grey)

            matches = self.tracker.match(qdes, tdes)
            if len(matches) > self.tracker.matcher.MIN_MATCH_COUNT:
                print('Matches found - {}/{}'.format(
                    len(matches), self.tracker.matcher.MIN_MATCH_COUNT)
                    )
                dst = self.calc_dst(matches, item_grey, qkp, tkp)
                cntr = self.calc_cntr(dst)

                state = cv2.polylines(state, [np.int32(dst)], True, 255, 3, cv2.LINE_AA)
                state = cv2.circle(state, tuple(np.int32(cntr)[0]), 50, 255, -1)

                etime = datetime.now()
                dtime = etime - stime
                t = dtime.total_seconds() * 1000
                print('Recognition took {} ms'.format(t))

                print('{} end run'.format(self.get_name()))
                return state, cntr, stime
            else:
                print('Not enough matches are found - {}/{}'.format(
                    len(matches), self.tracker.matcher.MIN_MATCH_COUNT)
                    )
        else: 
            print('Agent does\'t have item to recognize')

        etime = datetime.now()
        dtime = etime - stime
        t = dtime.total_seconds() * 1000

        print('Recognition took {} ms'.format(t))

        print('{} end run'.format(self.get_name()))
        return state, None, stime

class VerboseSmartAgent(SmartAgent):

    def __init__(self, tracker, env = None, item = None):
        print('Creating {} agent'.format(tracker.get_name()))
        super().__init__(tracker, env, item)
        print('{} agent created'.format(tracker.get_name()))

    def run(self):
        print('{} start run'.format(self.get_name()))
        stime = datetime.now()
        state = self.env.get_state() # color img from enviroment

        if self.item is not None:
            print('{} recognizing {}'.format(self.get_name(), self.item.get_name()))
            state_grey = cv2.cvtColor(state, cv2.COLOR_BGR2GRAY) # query grey image
            item_grey = self.item.get_img_grey() # train grey image

            qkp, qdes = self.tracker.detect_and_compute(state_grey)
            if self.item.des is None:
                tkp, tdes = self.tracker.detect_and_compute(item_grey)
                self.item.kp = tkp
                self.item.des = tdes
            else:
                tkp = self.item.kp
                tdes = self.item.des

            matches = self.tracker.match(qdes, tdes)
            if len(matches) > self.tracker.matcher.MIN_MATCH_COUNT:
                print('Matches found - {}/{}'.format(
                    len(matches), self.tracker.matcher.MIN_MATCH_COUNT)
                    )
                dst = self.calc_dst(matches, item_grey, qkp, tkp)
                cntr = self.calc_cntr(dst)

                state = cv2.polylines(state, [np.int32(dst)], True, 255, 3, cv2.LINE_AA)
                state = cv2.circle(state, tuple(np.int32(cntr)[0]), 50, 255, -1)

                etime = datetime.now()
                dtime = etime - stime
                t = dtime.total_seconds() * 1000
                print('Recognition took {} ms'.format(t))

                print('{} end run'.format(self.get_name()))
                return state, cntr, stime
            else:
                print('Not enough matches are found - {}/{}'.format(
                    len(matches), self.tracker.matcher.MIN_MATCH_COUNT)
                    )
        else: 
            print('Agent does\'t have item to recognize')

        etime = datetime.now()
        dtime = etime - stime
        t = dtime.total_seconds() * 1000

        print('Recognition took {} ms'.format(t))

        print('{} end run'.format(self.get_name()))
        return state, None, stime

class TestAgent(VerboseAgent):

    def run(self):
        stime = datetime.now()
        result = {
                'item_kp_len': None,
                'item_des_len': None,
                'matches_len': None,
                'item_frame_ratio': None,
                'time': None,
                'state_img': None
                }
        print('{} agent start run'.format(self.get_name()))
        state = self.env.get_state() # color img from enviroment

        if self.item is not None:
            print('Agent recognizing {}'.format(self.item.get_name()))
            state_grey = cv2.cvtColor(state, cv2.COLOR_BGR2GRAY) # query grey image
            item_grey = self.item.get_img_grey() # train grey image

            qkp, qdes = self.tracker.detect_and_compute(state_grey)
            tkp, tdes = self.tracker.detect_and_compute(item_grey)

            result['item_kp_len'] = len(tkp)
            result['item_des_len'] = len(tdes)

            matches = self.tracker.match(qdes, tdes)

            result['matches_len'] = len(matches)

            if len(matches) > self.tracker.matcher.MIN_MATCH_COUNT:
                print('Matches found - {}/{}'.format(
                    len(matches), self.tracker.matcher.MIN_MATCH_COUNT)
                    )
                dst = self.calc_dst(matches, item_grey, qkp, tkp)
                cntr = self.calc_cntr(dst)

                state = cv2.polylines(state, [np.int32(dst)], True, 255, 3, cv2.LINE_AA)
                state = cv2.circle(state, tuple(np.int32(cntr)[0]), 50, 255, -1)

                result['state_img'] = state

                frame_area = self.frame_area(state_grey)
                item_area = self.item_area(dst)
                item_frame_ratio = item_area/frame_area

                result['item_frame_ratio'] = item_frame_ratio

                print('Ratio: {}'.format(item_frame_ratio))
                print('Agent end run')
                
                etime = datetime.now()
                dtime = etime - stime
                t = dtime.total_seconds() * 1000
                result['time'] = t
                print('Recognition took {} ms'.format(t))
                return result
            else:
                print('Not enough matches are found - {}/{}'.format(
                    len(matches), self.tracker.matcher.MIN_MATCH_COUNT)
                    )
        else:
            print('Agent does\'t have item to recognize')

        etime = datetime.now()
        dtime = etime - stime
        t = dtime.total_seconds() * 1000
        result['time'] = t
        result['state_img'] = state

        print('Recognition took {} ms'.format(t))

        print('Agent end run')
        return result

    def item_area(self, dst):
        print('Calculating item area')

        top_right = dst[0]
        top_left = dst[1]
        down_left = dst[2]
        down_right = dst[3]

        print('top right {}'.format(top_right))
        print('top left {}'.format(top_left))
        print('down left {}'.format(down_left))
        print('down right {}'.format(down_right))

        d1 = np.subtract(top_right, down_left)
        d2 = np.subtract(top_left, down_right)

        print('d1 {}'.format(d1))
        print('d2 {}'.format(d2))

        d1 = np.sqrt(np.sum(np.square(d1)))
        d2 = np.sqrt(np.sum(np.square(d2)))
        area = d1 * d2  / 2
        
        print('Item area is {}'.format(area))
        return area

    def frame_area(self, state):
        print('Calculating frame area')
        area = np.prod(state.shape[:2])
        print('Frame area is {}'.format(area))
        return area
