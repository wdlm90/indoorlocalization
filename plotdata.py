# -*- coding:gb2312 -*-
from file2matrix import *
from pylab import *
from scipy import signal
import numpy as np
import math
import xlwt
import matplotlib.pyplot as plt
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import DBSCAN
from dtw import dtw
from hcluster import hcluster
'''
fileList = getFileList("dataset",[])
for e in fileList:
    print e
'''
#feaArr,labelArr,timestampArr = file2matrix('dataset/5.13/LiuYulu/ll-ohno-20150513104228_AGONLBCW.csv')
#timestampArr = map(lambda x:float(x),timestampArr)
#print "feature length :%d" % len(feaArr)
#print feaMat[:10]
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

def detectStep(accez,start,end):
    steppoint = 0
    i = start+1
    while i < end-1:
        maxpoint = 0
        minpoint = 0
        if accez[i] > accez[i-1] and accez[i] > accez[i+1] and accez[i]>1.0:
            maxpoint = i
            j = i+1
            while j < end-2:
                if accez[j] < accez[j-1] and accez[j] < accez[j+1] and\
                accez[j]<-1.0:
                    minpoint = j
                    if 10 < minpoint - maxpoint < 80:
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
    
def detectActivity(sensordata):
    print "start to detect activity"
    accezfilt = sensordata[:,3]
    activities = []
    start = 0
    end = 1
    fealen = len(feaArr)
    while start < end and start+200 < fealen and end < fealen:
        if (not detectStep(accezfilt,start,start+200)) and start < end:
            startpoint = start
            print "detect one activity start point %d" %(startpoint)
            steppoint = detectStep(accezfilt,start,len(accezfilt)-1)
            if steppoint and steppoint - startpoint > 50:
                endpoint = steppoint
                print "detect one activity endpoint:%d" % endpoint
                print "detect ont activity:%d,%d" %(startpoint,endpoint)
                activities.append(sensordata[startpoint:endpoint,:])
                start = endpoint
                end = start + 10
            else:
                print "fail to detect endpoint"
                print steppoint, startpoint
                break
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
#detect split point of activity and divide activity into several miniactivities
def detectSplitPoint(gyros,window_len,step):
    splitpoint = []
    for i in range(0,len(gyros)-window_len,step):
        if abs(mean(gyros[i+2*step:i+2*step+window_len,2]))>0.5 and\
        abs(mean(gyros[i:i+window_len,2]))<0.3:
            if not (i+step in splitpoint):
                splitpoint.append(i+2*step)
                print "start to turn at:%d"%(i+2*step)
        elif abs(mean(gyros[i:i+window_len,2]))>0.5 and\
        abs(mean(gyros[i+2*step:i+2*step+window_len,2]))<0.3:
            if not (i+step in splitpoint):
                splitpoint.append(i+2*step)
                print "end turning at:%d"%(i+2*step)
    return splitpoint
    
#divide activity into seveval miniactivities based on motion orientation
def divideMiniActivity(activities):
    miniActofAllAct = []
    for activity in activities:
        activity = array(activity)
        timestamp = activity[:,0]
        feaArr = activity[:,1:7]
        #rotationvecArr = getRotationArr(timestamp,feaArr)
        splitpointlist = detectSplitPoint(feaArr[:,3:6],10,5)
        miniactivities = []
        start = 0
        for point in splitpointlist:
            end = point
            miniactivities.append(activity[start:end,:])
            start = end
        miniActofAllAct.append(miniactivities)
    return miniActofAllAct

#extract features of mean and std from filter sample.
#every mini activity consist of
#[accemodavg,accexmean,accexstd,acceymean,acceystd,accezmean,accezstd,rotaionx,rotationy,rotationz]
def feaExtraction(activities):
    actlength= len(activities)
    feasOfAct = []
    for activity in activities:
        activityfea = []
        for miniactvalues in activity:
            miniactfea = []
            accemodlist = []
            for accex,accey,accez in miniactvalues[:,1:4]:
                acce2 = accex**2+accey**2+accez**2
                accemodlist.append(math.sqrt(acce2))
            accemodavg = mean(accemodlist)
            accexmean = mean(miniactvalues[:,1])
            accexstd = std(miniactvalues[:,1])
            acceymean = mean(miniactvalues[:,2])
            acceystd = std(miniactvalues[:,2])
            accezmean = mean(miniactvalues[:,3])
            accezstd = std(miniactvalues[:,3])
            timestampArr = miniactvalues[:,0]
            feaArr = miniactvalues[:,1:7]
            rotationlist = getRotationArr(timestampArr,feaArr) 
            miniactfea.append(accemodavg)
            miniactfea.append(accexmean)
            miniactfea.append(accexstd)
            miniactfea.append(acceymean)
            miniactfea.append(acceystd)
            miniactfea.append(accezmean)
            miniactfea.append(accezstd)
            miniactfea.append(rotationlist[-1,0])
            miniactfea.append(rotationlist[-1,1])
            miniactfea.append(rotationlist[-1,2])
            activityfea.append(miniactfea)
        feasOfAct.append(activityfea) 
    return feasOfAct

#get the rotation of gyrosscope of three axis
def getRotationArr(timestamp,feaArr):
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
            distance,cost,path=dtw(x[i,:],x[j,:],dist=np.linalg.norm)
            dist[i,j]=distance
    return dist


dataset = loadDataSet("dataset/5.13/LiuYulu")
print "dataset number:%d"%len(dataset)
activitiesofAll = []
#data = dataset[5]
for i in range(len(dataset)):
    feaArr = dataset[i][:,3:9]
    timestamp = dataset[i][:,0]
    filtfea = filtSensordata(feaArr)
    timestamp = map(lambda x:float(x),timestamp)
    timestampArr = np.array([timestamp]).T
    sensordata = np.append(timestampArr,filtfea,1)
    activities = detectActivity(sensordata)
    print "the %dth file contains:%d activities"%(i,len(activities))
    activitiesofAll += activities
print "activity number:%d" % len(activitiesofAll)
activitiesofMini = divideMiniActivity(activitiesofAll)
activitiesfea = feaExtraction(activitiesofMini)
n_clusters = 3
#x=array([[[1,1,1],[2,2,2],[3,3,3]],[[1,1,1],[2,2,2],[3,3,3]],[[4,4,4],[5,5,5],[6,6,6]],[[4,4,4],[5,5,5],[6,6,6]]])
k,l = hcluster(activitiesfea,4)
print l
#print len(timestampArr),len(feaArr)
'''
rotationArr = getRotationArr(timestamp,filtfea)

plt.figure(1)
ax1 = plt.subplot(311)
plt.ylabel(u'rotationx')
plt.xlabel(u'sample')
plt.plot(range(len(rotationArr)),rotationArr[:,0],color = 'red',linewidth = 1.0)
plt.xlim(0,len(rotationArr))
plt.ylim(-200,200)

ax2 = plt.subplot(312)
plt.ylabel(u'rotationy')
plt.xlabel(u'sample')
plt.plot(range(len(rotationArr)),rotationArr[:,1],color = 'green',linewidth = 1.0)
plt.xlim(0,len(rotationArr))
plt.ylim(-200,200)

ax1 = plt.subplot(313)
plt.ylabel(u'rotationz')
plt.xlabel(u'sample')
plt.plot(range(len(rotationArr)),rotationArr[:,2],color = 'blue',linewidth = 1.0)
plt.xlim(0,len(rotationArr))
plt.ylim(-200,200)

feaArrfilt = filtfea
startpoint = 0
endpoint = len(feaArrfilt)

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
'''
'''
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
