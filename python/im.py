'''
    Image Utility
    
    @date: Jan. 29, 2011
    @author: Shao-Chuan Wang (sw2644 at columbia.edu)
'''
import numpy
import cv
import matplotlib.pyplot as pyplot

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
  
if __name__=='__main__':
  im = cv.LoadImage('me.jpg')
  im = bgr2hsv(im)
  h,s,v = split3(im)
  h = cvimg2numpy(h)
  s = cvimg2numpy(s)
  v = cvimg2numpy(v)
  
  print h.shape

  exit()
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
  
  raw_input()
