#encoding=utf8
from django.shortcuts import render
from django.http import HttpResponse
import os
import models
import cv2
import numpy as np
import lib
import base64
import time
import cPickle as pickle

class info():
    pass

#index Page
def index(request):
    return render(request, './faceRec/index.html')


def recAction(request):
    if request.method=='POST':
        infoList = []
        numList = []
        count=1
        try:
            # 从表单中获取文件
            myfile1 = request.FILES.get('file1', None)
            myfile2 = request.FILES.get('file2', None)

            # 如果上传的是视频
            if myfile2:

                myfile = myfile2
                #打开文件 向video 写东西
                dest = open(os.path.join('./faceRec/static/video', myfile.name), 'wb')
                for chunk in myfile.chunks():
                    dest.write(chunk)
                dest.close()
                profileID = int(time.time())
                # 写完了
                t = time.strftime('%Y-%m-%d/%H:%M:%S',time.localtime())

                pid = os.fork()
                if pid==0:
                    print pid
                    L = models.Log(lId=str(profileID), lTime=t, lFlag=u'否')
                    L.save()
                    inf = info()
                    inf.mes = "文件上传完成，请您在3-5分钟后查看检测结果。页面将在5秒之后跳转回首页..."
                    inf.sec=5000
                    return render(request, './faceRec/Error.html', {'info':inf})
                else:
                    # 获取视频路径
                    videoPath = os.path.join('./faceRec/static/video', myfile.name)
                    # 列出所有的数据库数据项
                    allInfos = models.person.objects.all()
                    print videoPath

                    # 打开视频
                    cap = cv2.VideoCapture(videoPath)
                    flag = 0
                    a = 0

                    while True:
                        cv2.waitKey(1)
                        ret, frame = cap.read()
                        if ret == False:
                            break
                        # 跳帧操作
                        if a % 20 == 0:
                            a += 1
                            # flag表示处理了几帧
                            flag += 1

                            # 将读到的帧写到temp文件中
                            cv2.imwrite(os.path.join('./faceRec/static/temp', 'temp' + str(flag) + '.png'), frame)

                            # 将当前帧加密为b64
                            img1 = base64.b64encode(
                                open(os.path.join('./faceRec/static/temp', 'temp' + str(flag) + '.png'), 'rb').read())

                            for i in allInfos:
                                # 打开数据库中的人脸并编码
                                img2 = base64.b64encode(open("./faceRec" + i.pFace, 'rb').read())
                                # img1 与img2 都是base64
                                try:
                                    if lib.Rec(img1, img2):
                                        # 建立一个空对象
                                        inf = info()
                                        # 检测到的人
                                        inf.mainMessage = i
                                        # 上传的图片信息
                                        inf.img = '/static/temp/' + 'temp' + str(flag) + '.png'
                                        # 把识别到的信息入栈
                                        infoList.append(inf)
                                        # 序号自增
                                        numList.append(count)
                                        count += 1
                                        print i.pName
                                except:
                                    pass
                        else:
                            a += 1
                    # 释放摄像头 或者 Cap
                    cap.release()

                    fp = open('./faceRec/static/log/'+str(profileID)+'.log','wb')
                    decObj = [infoList, numList]
                    dec = pickle.dump(decObj, fp)
                    fp.close()

                    L = models.Log.objects.get(lId=profileID)
                    L.lFlag=u'是'
                    L.lMes='./faceRec/static/log/'+str(profileID)+'.log'
                    L.save()


                    return  HttpResponse('Success')


            elif myfile1:
                myfile = myfile1
                #把图片写到本地
                dest = open(os.path.join('./faceRec/static/temp', myfile.name), 'wb')
                for chunk in myfile.chunks():
                    dest.write(chunk)
                dest.close()

                allInfos = models.person.objects.all()

                imgPath = os.path.join('./faceRec/static/temp', myfile.name)
                img1 = base64.b64encode(open(imgPath, 'rb').read())
                for i in allInfos:
                    img2 = base64.b64encode(open('./faceRec' + i.pFace, 'rb').read())
                    try:
                        if lib.Rec(img1, img2):
                            inf = info()
                            # Python 特殊机制，对数据进行封装
                            inf.mainMessage = i
                            inf.img = '/static/temp/' + myfile.name
                            infoList.append(inf)
                            numList.append(count)
                            count += 1
                            # infoList.append(infoDict)
                    except:
                        pass
                if len(infoList) == 0:
                    inf = info()
                    inf.mes='          系统中未检测到此人，页面将在5秒之后跳转回首页...'
                    inf.sec=5000
                    return render(request, './faceRec/Error.html', {'info':inf})
                return render(request, './faceRec/result.html', {'infos': infoList, 'nums': numList})



        except:

            pass

    return HttpResponse("UNKnown Error")



#upload Page
def upload(request):
    return render(request, './faceRec/upload.html')


def uploadAction(request):
    if request.method=='POST':
        try:
            id = int(time.time())
            # 获取
            myfile = request.FILES.get('head', None)
            dest = open(os.path.join('./faceRec/static/image', myfile.name), 'wb')
            # dest = open('/home/edsger/workspace/Lee/Lee/faceRec/static/image/' + myfile.name)
            for chunk in myfile.chunks():
                dest.write(chunk)
            dest.close()
            imgPath = '/static/image/' + myfile.name
            pName = request.POST['username']
            pSex = request.POST['sex']
            pStatus = request.POST['info']
            tempPerson = models.person(id=id,pName=pName, pSex=pSex, pStatus=pStatus, pFace=imgPath)
            tempPerson.save()
            return render(request, 'faceRec/index.html')

        except:
            pass

    return HttpResponse("Error")


def admin(request):
    # 查询出所有的人物信息
    persons = models.person.objects.all()
    return  render(request, 'faceRec/admin.html', {'persons':persons})

def personPage(request, personId):
    person = models.person.objects.get(id=personId)
    return render(request, 'faceRec/personPage.html', {'person':person})

def result(request):
    return render(request, 'faceRec/result.html')




def logMes(request):
    logs = models.Log.objects.all()
    return render(request, './faceRec/log.html', {'logs':logs})


def videoLog(request, logId):
    try:
        fp = open('./faceRec/static/log/'+str(logId)+'.log')
        infoList, numList = pickle.load(fp)
        fp.close()
        return render(request, './faceRec/result.html', {'infos': infoList, 'nums': numList})
    except:
        inf = info()
        inf.mes="任务不存在或者未完成，请您稍后再试。将在5秒后跳转至首页..."
        inf.sec=5000
        return render(request, 'faceRec/Error.html', {'info':inf})

