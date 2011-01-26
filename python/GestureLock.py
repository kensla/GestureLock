'''
    Gesture Combination Authentication Program.
    
    @author: Shao-Chuan Wang (sw2644 at columbia.edu)
'''
import cv

def handle_keyboard(key):
  ''' return 0 if normally handle the key else -1.'''
  if key == 'q':
    return -1
  return 0
  
def handle_mouse(event, x, y, flags, param):
  print x, y

def process_img(rgbimg):
  global motion_detector
  width = rgbimg.width
  height = rgbimg.height
  size = (width, height)
  depth = rgbimg.depth
  channels = rgbimg.nChannels
  hsvimg = cv.CreateImage(size, depth, channels)
  cv.CvtColor(rgbimg, hsvimg, cv.CV_BGR2HSV)
  skin_detector = SkinDetector(motion_detector)
  return skin_detector.detectSkin(hsvimg)

class SDC(object):
  ''' Skin SkinDetector Constants. '''
  GSD_HUE_LT = 3
  GSD_HUE_UT = 50
  GSD_INTENSITY_LT = 15
  GSD_INTENSITY_UT = 250
  
class HueHistogram(object):
  def __init__(self):
    self.histogramSize = SDC.GSD_HUE_UT - SDC.GSD_HUE_LT
    self.hist = cv.CreateHist([self.histogramSize], cv.CV_HIST_ARRAY,[(SDC.GSD_HUE_LT, SDC.GSD_HUE_UT)], 1)
    cv.ClearHist(self.hist)
    self.bInit = False
    
  def calHist(self, himg):
    cv.CalcArrHist([himg], self.hist)
    self.bInit = True
    
  def show(self):
    for i in xrange(self.histogramSize):
      print cv.QueryHistValue_1D(self.hist, i),
    print ''
    
  def mergeWith(self, himg, factor):
    print 'hist merging'
    pass
    
  def findCurveThresholds(self):
    pass
        
  
class MotionDetector(object):
  def __init__(self, threshold=30):
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
    cv.And(motion_frame, curr, motion_frame)
    
    # eliminate disperse pixels, which occur because of the noise of the camera 
    img_temp = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
    cv.Erode(motion_frame, img_temp)
    cv.Dilate(img_temp, motion_frame)
    
    return motion_frame
    
motion_detector = MotionDetector()

  
class SkinDetector(object):
  """A Skin Detector Class"""
  def __init__(self, motion_detector):
    self.motion_detector = motion_detector
    self.histHueMotion = HueHistogram()
    self.histHueSkin = HueHistogram()
    
  def checkRange(self, src, lowBound, highBound):
    size = (src.width, src.height)
    
    mask = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
    
    gt_low = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
    cv.CmpS(src, lowBound, gt_low, cv.CV_CMP_GT)
    lt_high = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
    cv.CmpS(src, highBound, lt_high, cv.CV_CMP_LT)
    
    cv.And(gt_low, lt_high, mask)
    return mask
    
  def detectSkin(self, hsvimg):
    size = (hsvimg.width, hsvimg.height)
    h = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
    s = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)  
    v = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
    cv.Split(hsvimg, h, s, v, None)
    
    # init skin hue histogram
    if not self.histHueSkin.bInit:
      self.histHueSkin.calHist(h)
    
    self.histHueSkin.show()
    v_low, v_high = SDC.GSD_INTENSITY_LT, SDC.GSD_INTENSITY_UT
    h_low, h_high = SDC.GSD_HUE_LT, SDC.GSD_HUE_UT
    
    skin_mask = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
    
    v_mask = self.checkRange(v, v_low, v_high)
    h_mask = self.checkRange(v, h_low, h_high)

    motion_frame = self.motion_detector.detectMotion(v)
    
    
    return motion_frame #skin_mask

def mainLoop():
  window_name = "Showing Video from Camera"
  win = cv.NamedWindow(window_name, 1)
  cam = cv.CaptureFromCAM(0)
  cv.SetMouseCallback(window_name, handle_mouse)
  msdelay = 3
  while True:
    k = cv.WaitKey(msdelay)
    k = chr(k) if k > 0 else 0
    rgbimg = cv.QueryFrame(cam)
    img = process_img(rgbimg)
    cv.ShowImage(window_name, img)
    
    if handle_keyboard(k) < 0: break
  
if __name__=='__main__':
  mainLoop()
