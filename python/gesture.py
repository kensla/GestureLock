'''
    Gesture Combination Authentication Program submodule gesture.

    @date: Feb. 02, 2011
    @author: Shao-Chuan Wang (sw2644 at columbia.edu)
'''
from constants import GAC
import motion
import im

class GestureAnalyzer(object):
    """GestureAnalyzer is responsble for recognizing gesture commands"""
    def __init__(self):
        self.motion = motion.MotionTracker()

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
            return 'Not Sure'
        
        if self.motion.isMoving():
            ret = 'Moving '
        else:
            ret = 'Static '
        if self.isFist(max_area, mean_depth):
            ret = ret + 'Fist'
        elif self.isPalm(max_area, mean_depth):
            ret = ret + 'Palm'
        return ret

    def isFist(self, area, depth):
        return GAC.FIST.DEPTH_L < depth < GAC.FIST.DEPTH_U and \
               GAC.FIST.AREA_L  < area  < GAC.FIST.AREA_U

    def isPalm(self, area, depth):
        return GAC.PALM.DEPTH_L < depth < GAC.PALM.DEPTH_U and \
               GAC.PALM.AREA_L  < area  < GAC.PALM.AREA_U

