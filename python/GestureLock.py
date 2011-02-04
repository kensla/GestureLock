'''
    Gesture Combination Authentication Program.
    
    @date: Jan. 29, 2011
    @author: Shao-Chuan Wang (sw2644 at columbia.edu)
'''
import cv
import im
import numpy
from constants import GAC, SDC


def handle_mouse(event, x, y, flags, param):
  pass

def handle_keyboard(key):
    ''' return 0 if normally handle the key else -1.'''
    if key == 'q':
      return -1
    elif key == 'c':
      print 'calibrate the skin detection parameters...'
      self.skin_detector.toggle_calibrate()
    return 0


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

class ImageProcessSession(object):
  """ ImageProcessSession is a high level filter manager object.
  """
  def __init__(self, skin_detector):
    self.skin_detector = skin_detector
    self.gesture = GestureAnalyzer()

  def process(self, bgrimg):
    img = self.skin_detector.detectSkin(bgrimg)
    contours = im.find_contours(img)
    max_area, contours = im.max_area(contours)
    hull = im.find_convex_hull(contours)
    img = cv.CreateImage((img.width, img.height), 8, 3)
    if not contours:
        return img
    cds = im.find_convex_defects(contours, hull)
    mean_depth = 0,0
    if len(cds) != 0:
      mean_depth = sum([cd[3] for cd in cds])/len(cds)

    print self.gesture.recognize(max_area, mean_depth)
    print (max_area, mean_depth)
    cv.DrawContours(img, contours, im.color.RED, im.color.GREEN, 1,
            thickness=3)
    return img



class SkinDetector(object):
  """A Skin Detector Class"""
  def __init__(self):
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
    cv.ShowImage("Capture from camera", img_temp)
    hsvimg = im.bgr2hsv(img_temp)
    h,s,v = im.split3(img_temp)
    skin_mask = cv.CreateImage(im.size(hsvimg), cv.IPL_DEPTH_8U, 1)
    h_mask = cv.CreateImage(im.size(hsvimg), cv.IPL_DEPTH_8U, 1)
    v_mask = cv.CreateImage(im.size(hsvimg), cv.IPL_DEPTH_8U, 1)
    
    v_mask = self.checkRange(v, self.v_low, self.v_high)
    h_mask = self.checkRange(h, self.h_low, self.h_high)    
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
  skin_detector = SkinDetector()
  skin_detector.setHueThreshold(initHueThreshold)
  skin_detector.setIntensityThreshold(initIntensityThreshold)
  cv.CreateTrackbar('hueThreshold',
                    proc_win_name,
                    initHueThreshold,
                    255,
                    skin_detector.setHueThreshold)
  cv.CreateTrackbar('intensityThreshold',
                    proc_win_name,
                    initIntensityThreshold,
                    255,
                    skin_detector.setIntensityThreshold)

  session = ImageProcessSession(skin_detector)
  while True:
    k = cv.WaitKey(msdelay)
    k = chr(k) if k > 0 else 0
    if handle_keyboard(k) < 0:
        break
    rgbimg = cv.QueryFrame(cam)
    cv.Flip(rgbimg, None, 1)
    img = session.process(rgbimg)
    cv.ShowImage(proc_win_name, img)


if __name__=='__main__':
  mainLoop()
