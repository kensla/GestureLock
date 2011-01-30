'''
    Gesture Combination Authentication Program.
    
    @date: Jan. 29, 2011
    @author: Shao-Chuan Wang (sw2644 at columbia.edu)
'''
import cv
import im
import numpy
  
def handle_mouse(event, x, y, flags, param):
  pass
  #print x, y


class SDC(object):
  ''' Skin SkinDetector Constants. '''
  GSD_HUE_LT = 3
  GSD_HUE_UT = 50
  GSD_INTENSITY_LT = 15
  GSD_INTENSITY_UT = 250
  
class ImageProcessSession(object):
  def __init__(self, skin_detector):
    self.skin_detector = skin_detector
    
  def process(self, bgrimg):
    return self.skin_detector.detectSkin(bgrimg)

  def handle_keyboard(self, key):
    ''' return 0 if normally handle the key else -1.'''
    if key == 'q':
      return -1
    elif key == 'c':
      print 'calibrate the skin detection parameters...'
      self.skin_detector.toggle_calibrate()
    return 0


class Histogram(object):
  def __init__(self):
    self.bInit = False
    self.hist = None
    self.n, self.bins = None, None
    
  def show(self):
    binc = .5*(self.bins[1:]+self.bins[:-1])
    maxn = max(self.n)
    if maxn > self.threshold:
      print maxn, binc[self.n.argmax()]
      
  def calHist(self, himg):
    self.threshold = self.threshold_ratio * himg.width * himg.height
    himg = im.cvimg2numpy(himg)
    (self.n, self.bins) = numpy.histogram(himg, 
                              bins=30, 
                              range=(self.lower_bound,self.upper_bound))
    self.bInit = True

  def peak(self):
    binc = .5*(self.bins[1:]+self.bins[:-1])
    maxn = max(self.n)
    if maxn > self.threshold:
      return binc[self.n.argmax()]
    return None

  def mergeWith(self, himg, factor):
    print 'hist merging'
    pass

  def findCurveThresholds(self):
    pass


class HueHistogram(Histogram):
  threshold_ratio = 0.01
  @property
  def lower_bound(self):
    return SDC.GSD_HUE_LT
  @property
  def upper_bound(self):
    return SDC.GSD_HUE_UT

class IntensityHistogram(Histogram):
  threshold_ratio = 0.01
  @property
  def lower_bound(self):
    return SDC.GSD_INTENSITY_LT
  @property
  def upper_bound(self):
    return SDC.GSD_INTENSITY_UT

        
  
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
    
    # eliminate disperse pixels, which occur because of the noise of the camera 
    img_temp = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
    cv.Erode(motion_frame, img_temp)
    cv.Dilate(img_temp, motion_frame)
    
    return motion_frame
    
  
class SkinDetector(object):
  """A Skin Detector Class"""
  def __init__(self, motion_detector):
    self.motion_detector = motion_detector
    self.histHueMotion = HueHistogram()
    self.histIntensityMotion = IntensityHistogram()
    self.histHueSkin = HueHistogram()
    self.calibrating = False
    self.storage=cv.CreateMemStorage(0)
    
    
    self.v_low = SDC.GSD_INTENSITY_LT
    self.v_high = SDC.GSD_INTENSITY_UT
    self.h_low = SDC.GSD_HUE_LT
    self.h_high = SDC.GSD_HUE_UT
    
  def checkRange(self, src, lowBound, highBound):
    size = im.size(src)
    
    mask = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
    
    gt_low = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
    cv.CmpS(src, lowBound, gt_low, cv.CV_CMP_GT)
    lt_high = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
    cv.CmpS(src, highBound, lt_high, cv.CV_CMP_LT)
    
    cv.And(gt_low, lt_high, mask)
    return mask
    
  def toggle_calibrate(self):
    self.calibrating = self.calibrating ^ True
    
  def segment(self, bgrimg):
    segmented = cv.CreateImage(im.size(bgrimg), bgrimg.depth, bgrimg.nChannels)
    cv.PyrSegmentation(bgrimg, segmented, self.storage, 3, 188, 60)
    #cv.PyrMeanShiftFiltering(bgrimg, segmented, 100, 50)
    return segmented
    
  def setHueThreshold(self, hueThreshold):
    self.h_low, self.h_high = max(hueThreshold-55,0), min(hueThreshold+55,255)
    print self.h_low, self.h_high

  def setIntensityThreshold(self, intensityThreshold):
    self.v_low, self.v_high = max(intensityThreshold-40,0), min(intensityThreshold+40,255)
    print self.v_low, self.v_high

    
  def detectSkin(self, bgrimg):
    img_temp = cv.CreateImage(im.size(bgrimg), bgrimg.depth, bgrimg.nChannels)
    cv.Smooth(bgrimg, img_temp, cv.CV_MEDIAN, 15)#, 0, 20, 20)
    #img_temp = self.segment(img_temp)
    cv.ShowImage("Capture from camera", img_temp)
    
    hsvimg = im.bgr2hsv(img_temp)
    h,s,v = im.split3(img_temp)
    
    #cv.Circle(img_temp, (img_temp.width/2, img_temp.height/2), 5, color=(255,0,0,0), thickness=2 )
    
    
    # init skin hue histogram
    if not self.histHueSkin.bInit:
      self.histHueSkin.calHist(h)
    
    skin_mask = cv.CreateImage(im.size(hsvimg), cv.IPL_DEPTH_8U, 1)
    
    h_mask = cv.CreateImage(im.size(hsvimg), cv.IPL_DEPTH_8U, 1)
    v_mask = cv.CreateImage(im.size(hsvimg), cv.IPL_DEPTH_8U, 1)
    
    motion_frame = self.motion_detector.detectMotion(v)
    
    cv.And(motion_frame, h, h_mask)
    cv.And(motion_frame, v, v_mask)
        
    if self.calibrating:
      # cetner calibration: currently not working..:(
      #hmat = im.cvimg2numpy(h)
      #h_value = hmat[h.height/2,h.width/2]
      #vmat = im.cvimg2numpy(v)
      #v_value = vmat[v.height/2,v.width/2]
      
      # histogram peak thresholding
      self.histHueMotion.calHist(h_mask)
      self.histIntensityMotion.calHist(v_mask)
      h_peak = self.histHueMotion.peak()
      if h_peak:
        self.h_low, self.h_high = h_peak-15,  h_peak+15
        print 'h_peak:', h_peak
      v_peak = self.histIntensityMotion.peak()
      if v_peak:
        self.v_low, self.v_high = v_peak-30, v_peak+30
        print 'v_peak:', v_peak
        
      # user specified thresholding
      # here we can try new UI and let the user adjust the threshold.
        
    #self.h_low, self.h_high = 19.45-7, 19.45+7
    #self.v_low, self.v_high = 159.92-35, 159.92+35
    
    v_mask = self.checkRange(v, self.v_low, self.v_high)
    #v_mask = self.checkRange(v, 0,255)
    h_mask = self.checkRange(h, self.h_low, self.h_high)    
    #h_mask = self.checkRange(h, 0,255)
    cv.And(h_mask, v_mask, skin_mask)
    
    
    return skin_mask

def mainLoop():
  proc_win_name = "Processing window"
  cam_win_name = "Capture from camera"
  proc_win = cv.NamedWindow(proc_win_name, 1)
  cam_win = cv.NamedWindow(cam_win_name, 1)
  
  cam = cv.CaptureFromCAM(0)
  
  cv.SetMouseCallback(proc_win_name, handle_mouse)
  cv.SetMouseCallback(cam_win_name, handle_mouse)
  
  msdelay = 3
  initHueThreshold = 42
  initIntensityThreshold = 191
  skin_detector = SkinDetector(MotionDetector())
  skin_detector.setHueThreshold(initHueThreshold)
  skin_detector.setIntensityThreshold(initIntensityThreshold)
  cv.CreateTrackbar('hueThreshold', proc_win_name, initHueThreshold, 255, skin_detector.setHueThreshold)
  cv.CreateTrackbar('intensityThreshold', proc_win_name, initIntensityThreshold, 255, skin_detector.setIntensityThreshold) 
  
  session = ImageProcessSession(skin_detector)
  while True:
    k = cv.WaitKey(msdelay)
    k = chr(k) if k > 0 else 0
    if session.handle_keyboard(k) < 0:
      break
    
    rgbimg = cv.QueryFrame(cam)
    cv.Flip(rgbimg, None, 1)
    img = session.process(rgbimg)
    cv.ShowImage(proc_win_name, img)
    
    
if __name__=='__main__':
  mainLoop()
