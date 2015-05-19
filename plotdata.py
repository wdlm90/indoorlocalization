# -*- coding:gb2312 -*-
from file2matrix import *
from pylab import *
from scipy import signal
import numpy as np
import math
import xlwt
import matplotlib.pyplot as plt
from sklearn.cluster import AgglomerativeClustering
from dtw import dtw
'''
fileList = getFileList("dataset",[])
for e in fileList:
    print e
'''
#feaArr,labelArr,timestampArr = file2matrix('dataset/5.13/LiuYulu/ll-ohno-20150513104228_AGONLBCW.csv')
#timestampArr = map(lambda x:float(x),timestampArr)
#print "feature length :%d" % len(feaArr)
#print feaMat[:10]
dataset = loadDataSet("dataset/5.13/LiuYulu")
def filtSensordata(feaArr):
    acce_xlist = map(lambda x:float(x),feaArr[:,0])
    acce_ylist = map(lambda x:float(x),feaArr[:,1])
    acce_zlist = map(lambda x:float(x),feaArr[:,2])
    gyros_xlist = map(lambda x:float(x),feaArr[:,3])
    gyros_ylist = map(lambda x:float(x),feaArr[:,4])
    gyros_zlist = map(lambda x:float(x),feaArr[:,5])
    b,a = signal.butter(10,0.15,'low')
    acce_xfilt = signal.filtfilt(b,a,acce_xlist)
    acce_yfilt = signal.filtfilt(b,a,acce_ylist)
    acce_zfilt = signal.filtfilt(b,a,acce_zlist)
    gyros_xfilt = signal.filtfilt(b,a,gyros_xlist)
    gyros_yfilt = signal.filtfilt(b,a,gyros_ylist)
    gyros_zfilt = signal.filtfilt(b,a,gyros_zlist)
    feaArrfilt = array([acce_xfilt,acce_yfilt,acce_zfilt,gyros_xfilt,gyros_yfilt,gyros_zfilt]).T
    return feaArrfilt

def detectEndPoint(accez,start):
    print "begin to detect end point"
    steppoint = 0
    i = start+1
    while i < len(accez)-1:
        maxpoint = 0
        minpoint = 0
        if accez[i] > accez[i-1] and accez[i] > accez[i+1] and accez[i] > 0.5:
            maxpoint = i
            print "peak:%d" % maxpoint
            j = i+1
            while j < len(accez)-1:
                if accez[j] < accez[j-1] and accez[j] < accez[j+1] and accez[j] < -0.5:
                    minpoint = j
                    if 10 < minpoint - maxpoint < 105:
                        print "valley:%d" % minpoint
                        z = i
                        while abs(accez[z]) > 0.2 and z > start:
                            z += -1
                        if z > start:
                            steppoint = z
                            return steppoint
                        else:
                            steppoint = start
                            return steppoint
                j += 1
        i += 1
    return steppoint

def detectActivity(feaArr,duration,thd1,thd2):
    print "start to detect activity"
    accexfilt = feaArr[:,0]
    acceyfilt = feaArr[:,1]
    accezfilt = feaArr[:,2]
    activities = []
    accemod = []
    for accex,accey,accez in feaArr[:,0:3]:
        acce2 = accex**2+accey**2+accez**2
        accemod.append(math.sqrt(acce2))
    #print accemod
    start = 0
    end = 1
    fealen = len(feaArr)
    print "fealen:%d"% fealen
    while start < end and start < fealen and end < fealen:
        while mean(accemod[start:end])<thd1 and max(accemod[start:end])<thd2 and end < fealen:
            end += 1
        if end - start >= duration:
            print "detect one start point %d,%d" %(start,end)
            endpoint = detectEndPoint(accezfilt,end)
            if endpoint and endpoint - start > 80:
                print "detect one endpoint:%d" % endpoint
                activities.append(feaArr[start:endpoint,:])
                start = endpoint + 1
                end = start + 10
            else:
                print "fail to detect endpoint %d,%d" %(endpoint,(endpoint-start))
                start = end + 10
                end = start + 10
        else:
            start += 10
            end = start + 10
    return activities

#get the type of miniactivity
def miniActivityType(accex,accey):
    type = ""
    if accex>0 and accey>0:
        type = '1'
    elif accex<0 and accey>0:
        type = '2'
    elif accex<0 and accey<0:
        type = '3'
    elif accex>0 and accey<0:
        type = '4'
    return type

#divide activity into seveval miniactivities based on motion orientation
def divideMiniActivity(activities):
    miniActofAllAct = []
    for activity in activities:
        miniActofOneAct = []
        accex = activity[0][0]
        accey = activity[0][1]
        preminitype = miniActivityType(accex,accey)
        miniactvalue = []
        miniactvalue.append(activity[0])
        for i in range(1,len(activity)):
            curminitype = miniActivityType(activity[i,0],activity[i,1])
            if curminitype == preminitype:
                miniactvalue.append(activity[i,:])
            else:
                miniActofOneAct.append({"value":miniactvalue,"type":preminitype})
                miniactvalue = []
                miniactvalue.append(activity[i,:])
                preminitype = miniActivityType(activity[i,0],activity[i,1])
        miniActofOneAct.append({"value":miniactvalue,"type":preminitype})
        miniActofAllAct.append(miniActofOneAct)
    return miniActofAllAct

#extract features of mean and std from filter sample.
def feaExtraction(activities):
    actlength= len(activities)
    feasOfAct = []
    for activity in activities:
        activityfea = []
        for miniact in activity:
            miniactfea = []
            miniacttype = miniact["type"]
            miniactvalues = array(miniact["value"])
            accemod = []
            for accex,accey,accez in miniactvalues[:,0:3]:
                acce2 = accex**2+accey**2+accez**2
                accemod.append(math.sqrt(acce2))
            accexmean = mean(miniactvalues[:,0])
            accexstd = std(miniactvalues[:,0])
            acceymean = mean(miniactvalues[:,1])
            acceystd = std(miniactvalues[:,1])
            accezmean = mean(miniactvalues[:,2])
            accezstd = std(miniactvalues[:,2])
            rotationlist = getRotationList(timestampArr,feaArrfilt) 
            miniactfea.append(miniacttype)
            miniactfea.append(accexmean)
            miniactfea.append(accexstd)
            miniactfea.append(acceymean)
            miniactfea.append(acceystd)
            miniactfea.append(accezmean)
            miniactfea.append(accezstd)
            miniactfea.append(ratationlist[-1,0])
            miniactfea.append(ratationlist[-1,1])
            miniactfea.append(ratationlist[-1,2])
            activityfea.append(miniactfea)
        feasOfAct.append(activityfea)
    return feasOfAct

#get the rotation of gyrosscope of three axis
def getRotationlist(timestamp,feaArr):
    if len(timestamp) != len(feaArr):
        print "timestamp is not as long as feaArr" 
    rotationx = 0.0
    rotationy = 0.0
    rotationz = 0.0
    rotationveclist = []
    for i in xrange(1,len(feaArr)):
        dT = (timestamp[i] - timestamp[i-1])/1000.0
        rotationx += (feaArr[i-1,3] * dT * 180.0)/math.pi
        rotationy += (feaArr[i-1,4] * dT * 180.0)/math.pi
        rotationz += (feaArr[i-1,5] * dT * 180.0)/math.pi
        rotationvect = []
        rotationvect.append(rotationx)
        rotationvect.append(rotationy)
        rotationvect.append(rotationz)
        rotationveclist.append(rotationvect)
    return array(rotationveclist)
#return the distance matrix computed with dtw
def dtwDist(x):
    x = array(x)
    length = len(x)
    dist = zeros((length,length))
    for i in range(length):
        for j in range(length):
            distance,cost,path=dtw(x[i,:],x[j,:])
            dist[i,j]=distance
    return dist
dist = dtwDist([[1,2],[1,1]])
print dist
activitiesofAll = []
for data in dataset:
    feaArr = data[:,3:9]
    timestampArr = data[:,0]
    filtfea = filtSensordata(feaArr)
    timestampArr = map(lambda x:float(x),timestampArr)
    activities = detectActivity(filtfea)
    activitiesofAll.append(activities)
print len(activitiesofAll)
activitiesofMini = divideMiniActivity(activities)
activitiesfea = feaExtraction(activitiesofMini)
model = AgglomerativeClustering(n_clusters=n_clusters,linkage="average",affinity=dtwDist)
model.fit(activitiesfea)
print model.label_

'''




print len(timestampArr),len(feaArr)
rotationArr = getRotationlist(timestampArr,feaArrfilt)

plt.figure(1)
ax1 = plt.subplot(311)
plt.ylabel(u'rotationx')
plt.xlabel(u'sample')
plt.plot(range(len(rotationArr)),rotationArr[:,0],color = 'red',linewidth = 1.0)
plt.xlim(0,len(rotationArr))
plt.ylim(-180,180)

ax2 = plt.subplot(312)
plt.ylabel(u'rotationy')
plt.xlabel(u'sample')
plt.plot(range(len(rotationArr)),rotationArr[:,1],color = 'green',linewidth = 1.0)
plt.xlim(0,len(rotationArr))
plt.ylim(-180,180)

ax1 = plt.subplot(313)
plt.ylabel(u'rotationz')
plt.xlabel(u'sample')
plt.plot(range(len(rotationArr)),rotationArr[:,2],color = 'blue',linewidth = 1.0)
plt.xlim(0,len(rotationArr))
plt.ylim(-180,180)


startpoint = 0
endpoint = len(feaArr)

plt.figure(2)
ax1 = plt.subplot(311)
plt.ylabel(u'acceleration_x')
plt.xlabel(u'sample')
plt.plot(range(startpoint,endpoint),feaArrfilt[:,0],color = 'green',linewidth = 1.0)
plt.xlim(startpoint,endpoint)
plt.ylim(-5.0,5.0)
#savefig('figure/dong ting/acce_x_4.png',dpi = 80)

ax2 = plt.subplot(312)
plt.ylabel(u'acceleration_y')
plt.xlabel(u'sample')
plt.plot(range(startpoint,endpoint),feaArrfilt[startpoint:endpoint,1],color = 'blue',linewidth = 1.0)
plt.xlim(startpoint,endpoint)
plt.ylim(-5.0,5.0)
#savefig('figure/dong ting/acce_y_4.png',dpi = 80)

ax3 = plt.subplot(313)
plt.ylabel(u'acceleration_z')
plt.xlabel(u'sample')
plt.plot(range(startpoint,endpoint),feaArrfilt[startpoint:endpoint,2],color = 'red',linewidth = 1.0)
plt.xlim(startpoint,endpoint)
plt.ylim(-5.0,5.0)
#savefig('figure/dong ting/acce_z_4.png',dpi = 80)

plt.figure(3)
ax1 = plt.subplot(311)
plt.ylabel(u'gyroscope_x')
plt.xlabel(u'sample')
plt.plot(range(startpoint,endpoint),feaArrfilt[startpoint:endpoint,3],color = 'green',linewidth = 1.0)
plt.xlim(startpoint,endpoint)
plt.ylim(-5.0,5.0)
#savefig('figure/dong ting/gyros_x_4.png',dpi = 80)

ax2 = plt.subplot(312)
plt.ylabel(u'gyroscope_y')
plt.xlabel(u'sample')
plt.plot(range(startpoint,endpoint),feaArrfilt[startpoint:endpoint,4],color = 'blue',linewidth = 1.0)
plt.xlim(startpoint,endpoint)
plt.ylim(-5.0,5.0)
#savefig('figure/dong ting/gyros_y_4.png',dpi = 80)

ax3 = plt.subplot(313)
plt.ylabel(u'gyroscope_z')
plt.xlabel(u'sample')
plt.plot(range(startpoint,endpoint),feaArrfilt[startpoint:endpoint,5],color = 'red',linewidth = 1.0)
plt.xlim(startpoint,endpoint)
plt.ylim(-5.0,5.0)
plt.show()

#savefig('figure/dong ting/gyros_z_4.png',dpi = 80)
#activities = [feaArr]


activities = detectActivity(feaArr,50,1.2,1.5)
actnum = len(activities)
print "activity number : %d" % actnum
if len(activities) > 0:
    dividedact = divideMiniActivity(activities)
    #print len(dividedact[0])
    for act in dividedact:
        for miniact in act:
            print miniact["type"]
        print "\n"
#feature = feaExtraction(dividedact)


def splitActivity(acce):
    miniactivities = []
    miniactivity = []
    angles = []
    miniactivity.append(acce[0,:])
    for i in range(0,len(acce)):
        tan_angle = acce[i,1]/acce[i,0]
        angle = np.arctan(tan_angle)*360/(2*np.pi)
        if acce[i,0] < 0:
            angle += 180
        if angle < 0:
            angle += 360
            angles.append(angle)
    for i in range(1,len(acce)):
        #print angle
        xaxis = acce[i,0]
        yaxis = acce[i,1]
        prexaxis = acce[i-1,0]
        preyaxis = acce[i-1,1]
        if xaxis * prexaxis > 0 and yaxis * preyaxis > 0:
            miniactivity.append(acce[i,:])
        else:
            miniactivities.append(miniactivity)
            miniactivity = []
            miniactivity.append(acce[i,:])
    miniactivities.append(miniactivity)
    return miniactivities,angles
#miniactivities,angles = splitActivity(acce)
#print acce,angles


accemod = []
for accex,accey,accez in feaArr[:,0:3]:
    acce2 = accex**2+accey**2+accez**2
    accemod.append(math.sqrt(acce2))
figure(figsize = (10,5),dpi = 80)
ylabel(u'accemod')
xlabel(u'sample')
plot(range(startpoint,endpoint),accemod[startpoint:endpoint],color = 'red',linewidth = 1.0)
xlim(startpoint,endpoint)
ylim(0,10.0)

show()
sensornum = 6
#extract features of mean and std from filter sample.
def featureExtraction(sample,interval):
    winlen = shape(sample)[1]
    feanum = 2
    intervalnum = winlen/interval
    fea = []
    for i in range(6):
        for start in range(0,winlen,interval):
            if start+interval-1 < winlen:
                end = start + interval - 1
            else:
                end = winlen - 1
            meanvalue = mean(window_sample[i,start:end+1])
            stdvalue = std(window_sample[i,start:end+1])
            fea.append(meanvalue)
            fea.append(stdvalue)
    return fea
#print fea
#wirte feature to file
def writeFeaToFile(feature,filename):
    wb = xlwt.Workbook()
    ws = wb.add_sheet('Sheet 1')
    for i in range(len(feature)):
        fealine = feature[i]
        for j in range(len(fealine)):
            ws.write(i,j,feature[i][j])
    wb.save(filename)
#get samples within windowsize
stepsize = 70
windowsize = 350
featotal = []
for startpoint in range(0,len(acce_xfilt),stepsize):
    if startpoint + windowsize -1 < len(acce_xfilt):
        endpoint = startpoint + windowsize-1
    else:
        endpoint = len(acce_xfilt)-1
    window_accex = acce_xfilt[startpoint:endpoint+1]
    window_accey = acce_yfilt[startpoint:endpoint+1]
    window_accez = acce_zfilt[startpoint:endpoint+1]
    window_gyrosx = gyros_xfilt[startpoint:endpoint+1]
    window_gyrosy = gyros_yfilt[startpoint:endpoint+1]
    window_gyrosz = gyros_zfilt[startpoint:endpoint+1]
    window_sample = array([window_accex,window_accey,window_accez,window_gyrosx,window_gyrosy,window_gyrosz])
    #print shape(window_sample)
    interval = 70
    fea = featureExtraction(window_sample,70)
    featotal.append(fea)
writeFeaToFile(featotal,'feature/Zheng Qunhua_4.xls')
# window_sample
'''
