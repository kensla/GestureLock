'''
    Gesture Combination Authentication Program.

    @date: Jan. 29, 2011
    @author: Shao-Chuan Wang (sw2644 at columbia.edu)
'''
import cv
import im
import numpy
import skin, gesture

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



class ImageProcessSession(object):
  """ ImageProcessSession is a high level filter manager object.
  """
  def __init__(self, skin_detector):
    self.skin_detector = skin_detector
    self.gesture = gesture.GestureAnalyzer()

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
  skin_detector = skin.SkinDetector()
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
