'''
    Gesture Combination Authentication Program submodule gesture.

    @date: Feb. 02, 2011
    @author: Shao-Chuan Wang (sw2644 at columbia.edu)
'''
from constants import GAC

class GestureAnalyzer(object):
    """GestureAnalyzer is responsble for recognizing gesture commands"""
    def __init__(self):
        pass

    def recognize(self, area, depth):
        if self.isFist(area, depth):
            return 'Fist'
        elif self.isPalm(area,depth):
            return 'Palm'
        else:
            return 'Not Sure'

    def isFist(self, area, depth):
        return GAC.FIST.DEPTH_L < depth < GAC.FIST.DEPTH_U and \
               GAC.FIST.AREA_L  < area  < GAC.FIST.AREA_U

    def isPalm(self, area, depth):
        return GAC.PALM.DEPTH_L < depth < GAC.PALM.DEPTH_U and \
               GAC.PALM.AREA_L  < area  < GAC.PALM.AREA_U

