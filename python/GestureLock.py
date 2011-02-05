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


class Grammar(object):
    def __init__(self):
        self.grammar = []
        self.n_grammar = 10
        self.repeat_count = 0
        self.not_sure_count = 0
        self.long_threshold = 8
        self.last_ges = gesture.Gesture('Not Sure')
        self.start_ges = gesture.Gesture('Palm', 'Long')

    def __repr__(self):
        return repr(self.grammar)


    def instantGes(self, ges):
        if ges.hasMeaning():
            self.not_sure_count = 0
            last = self.last_ges
            if last.type_ == ges.type_:
                self.repeat_count += 1
            else:
                self.repeat_count = 0

            if self.repeat_count >= self.long_threshold:
                ges.timing = 'Long'

            if self.grammar:
                if last.type_ == ges.type_:
                    self.grammar[-1] = ges
                else:
                    self.grammar.append(ges)
            else:  # empty grammar needs 'Long Palm' to start to record
                if ges == self.start_ges:
                    self.grammar.append(ges)
            self.last_ges = ges
        else:
            self.not_sure_count += 1
            if self.not_sure_count >= self.long_threshold:
                self.grammar = []
                self.repeat_count = 0

        print self.grammar

class ImageProcessSession(object):
  """ ImageProcessSession is a high level filter manager object.
  """
  def __init__(self, skin_detector):
    self.skin_detector = skin_detector
    self.gesture = gesture.GestureAnalyzer()
    self.grammar = Grammar()

  def process(self, bgrimg):
    img = self.skin_detector.detectSkin(bgrimg)
    contours = im.find_contours(img)
    img = cv.CreateImage((img.width, img.height), 8, 3)
    if not contours:
        return img

    ges = self.gesture.recognize(contours)
    print ges
    self.grammar.instantGes(ges)
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
