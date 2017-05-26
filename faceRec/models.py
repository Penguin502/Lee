from django.db import models

from django.db import models

class person(models.Model):
    pId = models.CharField(max_length=20)
    pName = models.CharField(max_length=50)
    pSex = models.CharField(max_length=10)
    pStatus = models.TextField()
    eigFace = models.CharField(max_length=200)
    pFace = models.CharField(max_length=200)



    def __unicode__(self):
        return self.pName

class Log(models.Model):
    lId = models.CharField(max_length=20)
    lTime = models.TextField()
    lFlag = models.TextField()
    lMes = models.TextField()

    def __unicode__(self):
        return self.pFlag
