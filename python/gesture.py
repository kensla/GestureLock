'''
    Gesture Combination Authentication Program submodule gesture.

    @date: Feb. 02, 2011
    @author: Shao-Chuan Wang (sw2644 at columbia.edu)
'''
from constants import GAC
import motion
import im

FIST = 0
PALM = 1

class GestureState(object):
    def __init__(self):
        self.history = []
        self.maxLen = 20
        self.longThreshold = 5

    def append(self, ges):
        self.history.append(ges)
        self.history = self.history[-self.maxLen:]

    def getState(self):
        if len(self.history) > self.longThreshold:
            self.history[-self.longThreshold:]

        return 'Short '+self.history[-1]

class Gesture(object):
    def __init__(self, type_, timing=''):
        self.timing = timing
        self.type_ = type_

    def __repr__(self):
        return self.timing + ' ' + self.type_

    def __eq__(self, obj):
        return self.type_ == obj.type_ and self.timing == obj.timing

    def hasMeaning(self):
        return self.type_ != 'Not Sure'

class GestureAnalyzer(object):
    """GestureAnalyzer is responsble for recognizing gesture commands"""
    def __init__(self):
        self.motion = motion.MotionTracker()
        self.gestures_buffer = []
        self.buffer_size = 5

    def recognize(self, contours):
        max_area, contours = im.max_area(contours)
        hull = im.find_convex_hull(contours)
        mean_depth = 0
        self.motion.push(contours)
        if hull:
          cds = im.find_convex_defects(contours, hull)
          if len(cds) != 0:
              mean_depth = sum([cd[3] for cd in cds])/len(cds)

        if not self.isFist(max_area, 
                mean_depth) and not self.isPalm(max_area, mean_depth):
            if self.gestures_buffer:
              self.gestures_buffer.pop(0)
            return Gesture('Not Sure')
        if self.isFist(max_area, mean_depth):
            self.gestures_buffer.append(FIST)
        elif self.isPalm(max_area, mean_depth):
            self.gestures_buffer.append(PALM)
        self.gestures_buffer = self.gestures_buffer[-self.buffer_size:]
        avg = float(sum(self.gestures_buffer))/self.buffer_size
        if avg > 0.5:
            ges = 'Palm'
        else:
            ges = 'Fist'
        return Gesture(ges, 'Short')

    def isFist(self, area, depth):
        return GAC.FIST.DEPTH_L < depth < GAC.FIST.DEPTH_U and \
               GAC.FIST.AREA_L  < area  < GAC.FIST.AREA_U

    def isPalm(self, area, depth):
        return GAC.PALM.DEPTH_L < depth < GAC.PALM.DEPTH_U and \
               GAC.PALM.AREA_L  < area  < GAC.PALM.AREA_U

