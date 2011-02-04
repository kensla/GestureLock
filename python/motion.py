'''
    Gesture Combination Authentication Program submodule motion.

    @date: Jan. 29, 2011
    @author: Shao-Chuan Wang (sw2644 at columbia.edu)
'''
import cv

class MotionDetector(object):
  ''' A motioni detector class. '''
  def __init__(self, threshold=30):
    ''' threshold: pixel threshold for detecting motion between two frames. '''
    self.threshold = threshold
    self.nHistory = 1
    self.history_frames = []
    
  def detectMotion(self, curr):
    assert(curr.nChannels==1)
    if len(self.history_frames) < self.nHistory:
      self.history_frames.append(curr)
      return curr
    else:
      oldest_frame = self.history_frames.pop(0)
      self.history_frames.append(curr)
    size = (curr.width, curr.height)
    motion_frame = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
    cv.AbsDiff(oldest_frame, curr, motion_frame)
    cv.CmpS(motion_frame, self.threshold, motion_frame, cv.CV_CMP_GT)
    
    # Eliminate disperse pixels, which occur because of 
    # the noise of the camera 
    img_temp = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
    cv.Erode(motion_frame, img_temp)
    cv.Dilate(img_temp, motion_frame)
    
    return motion_frame
