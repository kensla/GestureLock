'''
    Image Utility
    
    @date: Jan. 29, 2011
    @author: Shao-Chuan Wang (sw2644 at columbia.edu)
'''
import numpy
import cv
import matplotlib.pyplot as pyplot

class Color(object):
    pass

color=Color()
color.RED=(0,0,255,0)
color.GREEN=(0,255,0,0)
color.BLUE=(255,0,0,0)

def cvimg2numpy(cvimg):
  return numpy.asarray(cv.GetMat(cvimg))
  
def bgr2hsv(cvimg):
  size = (cvimg.width, cvimg.height)
  depth = cvimg.depth
  channels = cvimg.nChannels
  hsvimg = cv.CreateImage(size, depth, channels)
  cv.CvtColor(cvimg, hsvimg, cv.CV_BGR2HSV)
  return hsvimg
  
def bgr2gray(cvimg):
  size = (cvimg.width, cvimg.height)
  depth = cvimg.depth
  channels = cvimg.nChannels
  grayimg = cv.CreateImage(size, depth, 1)
  cv.CvtColor(cvimg, grayimg, cv.CV_BGR2GRAY)
  return grayimg
  
def bgr2rgb(cvimg):
  size = (cvimg.width, cvimg.height)
  depth = cvimg.depth
  channels = cvimg.nChannels
  rgbimg = cv.CreateImage(size, depth, channels)
  cv.CvtColor(cvimg, rgbimg, cv.CV_BGR2RGB)
  return rgbimg

def split3(cvimg):
  size = (cvimg.width, cvimg.height)
  c1 = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
  c2 = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)  
  c3 = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
  cv.Split(cvimg, c1, c2, c3, None)
  return c1,c2,c3
  
def size(cvimg):
  return (cvimg.width, cvimg.height)

def test_funcs():

  im = cv.LoadImage('me.jpg')
  im = bgr2hsv(im)
  h,s,v = split3(im)
  h = cvimg2numpy(h)
  s = cvimg2numpy(s)
  v = cvimg2numpy(v)
  
  print h.shape

  pyplot.figure(1)
  pyplot.imshow(h, cmap=pyplot.cm.gray)
  
  pyplot.figure(2)
  pyplot.imshow(s, cmap=pyplot.cm.gray)
  
  pyplot.figure(3)
  pyplot.imshow(v, cmap=pyplot.cm.gray)
  
  pyplot.figure(4)
  (n, bins) = numpy.histogram(h.flatten(), bins=30)
  binc = .5*(bins[1:]+bins[:-1])
  print binc[n.argmax()]


def visit(im, i=0, j=0):
    h, w = im.shape
    visited = numpy.zeros(im.shape, dtype=numpy.uint8)
    def near(x, y):
        if (x,y) in ret:
            for c in xrange(max(y-1,0), min(y+2,h)):
                for r in xrange(max(x-1,0), min(x+2,w)):
                    if not im[c,r]:
                      yield c,r
        else:
            for c in xrange(max(y-1,0), min(y+2,h)):
                for r in xrange(max(x-1,0), min(x+2,w)):
                    if (c,r)!=(x,y):
                      yield c, r
    def all_points(im):
        for c in xrange(h):
            for r in xrange(w):
                yield c,r
    q = [(i,j)]
    ret = set([])
    while q:
        u = q.pop(0)
        for v in near(*u):
            if not visited[v]:
                visited[v] = 1
                q.append(v)
                if im[v]:
                    ret.add(v)
    return ret

def find_contours(im):
    storage = cv.CreateMemStorage(0)
    try:
      contours = cv.FindContours(im, 
                               storage,
                               cv.CV_RETR_TREE,
                               cv.CV_CHAIN_APPROX_SIMPLE)
      contours = cv.ApproxPoly(contours,
                             storage,
                             cv.CV_POLY_APPROX_DP, 3, 1)
    except cv.error, e:
      print e
      return None
    return contours

def find_convex_hull(cvseq):
    storage = cv.CreateMemStorage(0)
    try:
      hull = cv.ConvexHull2(cvseq, storage, cv.CV_CLOCKWISE, 0)
    except TypeError, e:
      return None
    return hull

def find_convex_defects(contour, hull):
    storage = cv.CreateMemStorage(0)
    return cv.ConvexityDefects(contour, hull, storage)


def max_area(contours):
    ''' returns the contour with maximal area. 
        @return: (max_area, max_contour)
    '''
    max_area = 0
    max_contours = contours
    try:
      while True:
          area = cv.ContourArea(contours)
          if area > max_area:
              max_area = area
              max_contours = contours
          contours = contours.h_next()
    except TypeError, e:
      return max_area, max_contours
    return max_area, max_contours

def plot_contours(contours, shape):
    img = cv.CreateImage(shape, 8, 3)
    cv.NamedWindow('show', 1)
    cv.SetZero(img)
    cv.DrawContours(img, contours, color.RED, color.GREEN, 1)
    cv.ShowImage('show', img)


if __name__=='__main__':
  im = cv.LoadImage('mask.png')
  im = bgr2gray(im)
  contours = find_contours(im)
  area = cv.ContourArea(contours)
  print area
  hull = find_convex_hull(contours)
  defects = find_convex_defects(contours, hull)
  print defects
  plot_contours(contours, (im.width, im.height))
  raw_input()
