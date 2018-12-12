import cv2

MATCHER = [ 'FLANN', 'BFL2', 'BFH' ]

class MatcherNotFound(Exception):
    pass

class MatcherFactory:

    def get_matcher(self, name):
        n = name.upper()
        if n == MATCHER[0]:
            return FlannMatcher()
        elif n == MATCHER[1]:
            return BFMatcherL2()
        elif n == MATCHER[2]:
            return BFMatcherHamming()
        raise MatcherNotFound('{} matcher wasn\'t found'.format(name))

class Matcher:

    MIN_MATCH_COUNT = 10

    def match(self, qdes, tdes):
        pass

class FlannMatcher(Matcher):

    def __init__(self):
        FLANN_INDEX_KDTREE = 0
        index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
        search_params = dict(checks = 100) # default 30
        self.matcher = cv2.FlannBasedMatcher(index_params, search_params)

    def match(self, qdes, tdes):
        matches = self.matcher.knnMatch(qdes, tdes, k = 2)
        good = []
        for m, n in matches:
            if m.distance < 0.7 * n.distance:
                good.append(m)
        return good

class BFMatcher(Matcher):

    BF_CROSS_CHECK = False

    def __init__(self):
        self.matcher = cv2.BFMatcher_create(crossCheck = self.BF_CROSS_CHECK)

    def match(self, qdes, tdes):
        if self.BF_CROSS_CHECK:
            return self.matcher.knnMatch(qdes, tdes, k = 2)
        matches = self.matcher.knnMatch(qdes, tdes, k = 2)
        good = []
        for m, n in matches:
            if m.distance < 0.8 * n.distance:
                good.append(m)
        return good

class BFMatcherL2(BFMatcher):

    def __init__(self):
        self.matcher = cv2.BFMatcher_create(cv2.NORM_L2, crossCheck = self.BF_CROSS_CHECK)

class BFMatcherHamming(BFMatcher):

    def __init__(self):
        self.matcher = cv2.BFMatcher_create(cv2.NORM_HAMMING, crossCheck = self.BF_CROSS_CHECK)
