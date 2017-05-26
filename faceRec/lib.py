#encoding=utf-8
import cv2
import sys
import numpy as np
from numpy import *
import urllib
import urllib2
import base64
import json
def init(img1, img2):
    url = 'https://api-cn.faceplusplus.com/facepp/v3/compare'
    data = {}
    data['api_key'] = 'RZTnpvFJ8YTyWxxE2Zlus8LLRJ9nR8kg'
    data['api_secret'] = 'ArqCf4GSWYKpY8kQOsz5zy5fupV9xh0h'
    data['image_base64_1'] = img1
    data['image_base64_2'] = img2

    postdata = urllib.urlencode(data)

    js = urllib2.urlopen(url, postdata).read()
    returnJs = json.loads(js)
    try:
        #print returnJs['confidence']
        if returnJs['confidence'] > 60:
            return True
        else:
            return False
    except:
        return False
def Rec(img1='', img2=''):


    result = init(img1, img2)
    return result

def getFace(img):
    #cascPath = '/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml'
    cascPath = '/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_alt2.xml'
    faceCascade = cv2.CascadeClassifier(cascPath)
    kernel = np.ones((5,5), np.uint8)
    erosion = cv2.erode(img, kernel, iterations=1)

    #转化成灰度值方便进行人脸识别
    gray = cv2.cvtColor(erosion, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=5,minSize=(30, 30))

    faceArr = []
    for face in faces:
        if face!=np.array([]):
            x, y, a, b = face[0], face[1], face[2], face[3]
            temp = cv2.resize(gray[x:x+a, y:y+b], (92,112), cv2.INTER_LINEAR)
            faceArr.append(temp)
    return  faceArr


def getEig():
    s = ''
    with open('upload/static/file/eig_vect.dat') as fp:
        s = fp.read()
    with open('upload/static/file/imageMu.dat') as fp:
        b = fp.read()
    return np.fromstring(s), np.fromstring(b)


def distEclud(vecA, vecB):  # 欧氏距离
    eps = 1.0e-16
    return linalg.norm(vecA-vecB)+eps


def cosSim(vecA, vecB):	 # 夹角余弦
    eps = 1.0e-16
    return (dot(vecA,vecB.T)/((linalg.norm(vecA)*linalg.norm(vecB))+eps))[0,0]


def eigFace(img):
    faces = getFace(img)
    faceList = []
    for face  in faces:
        eigvect, mu = getEig()
        eig = np.dot(face.reshape(1, -1) - mu, eigvect.reshape(10304, 5))
        faceList.append(eig)
    return faceList[0]


def rec(img1='', img2=''):
    im1 = base64.decode(img1)
    im2 = base64.decode(img2)
    try:
        i1 = getFace(cv2.imread(im1))
        i2 = getFace(cv2.imread(im2))
        eig1 = eigFace(i1)  ## 1*5 向量
        eig2 = eigFace(i2)
        dist = distEclud(eig1, eig2)
        if dict < 2000:
            return True
        else:
            return False
    except:
        return False

    pass



