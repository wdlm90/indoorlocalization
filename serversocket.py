from socket import *
from time import ctime
from scipy import signal
from SocketServer import TCPServer,ThreadingMixIn,StreamRequestHandler
import MySQLdb
import numpy as np
import csv
import math
import traceback
class Server(ThreadingMixIn,TCPServer):pass
class Handler(StreamRequestHandler):
    def handle(self):
        while True:
            try:
                data = self.rfile.readline().strip()
                print 'receive from (%r):%r' % (self.client_address,data)
                #self.wfile.write('Thank you for connecting')
                Sensordatalist = data.split(',')
                print Sensordatalist
            except:
                traceback.print_exc()
                break

if __name__ == "__main__":
    host = ''
    port = 12345
    addr = (host,port)
    server = Server(addr,Handler)
    server.serve_forever()
'''
HOST = ''
PORT = 12345
BUFSIZE = 1024
SERVERADDR = (HOST, PORT)
sersocket = socket(AF_INET, SOCK_STREAM)
sersocket.bind(SERVERADDR)
sersocket.listen(10)
#SLM = ["location":,"walkingdirection":,"wifi":,"mag":,"pedestrains' location":]

while True:
    print 'waiting for connection'
    tcpClientSock,addr = sersocket.accept()
    print '...connected from',addr
    while True:
        try:
            tcpClientSock.settimeout(10)
            sleep(10)
            data = tcpClientSock.recv(BUFSIZE)
            #s = 'Hi, you send me :[%s] %s' % (ctime(),data.decode('utf8'))
            #print
            print data
            #value = data.split(',')
            #map(lambda x: float(x), value)
            #print value
        except:
            print addr,'time out'
            tcpClientSock.close()
            break
            '''
'''
            try:
                conn = MySQLdb.connect(host = '128.199.143.119',username = 'root',passed = 'limeng90',port = 3306,db = 'mobilesensing')
                cur = conn.cursor()
                cur.execute('insert into SensorDataTbl values(%s,%s,%s)',value)
                conn.commit()
                cur.close()
                conn.close()
            except MySQLdb.Error,e:
                print "MySQL Error %d:%s" % (e.args[0].e.args[1])
'''
       
'''
        storeindatabase(s)
        tcpClientSock.send(s.encode('utf8'))

        window = getslidingwindow(window,data,k)

        window_afterpreprocess = preprocess(window)

        location = dead_reckoning(location,window_afterpreprocess)

        recogresult,landmarktype, landmarkLocation = landmarkRecognition(window_afterpreprocess)

        if recogresult:
            updateLandmarkLib(location,win_afterprocess)
            location = landmarkLocation        
tcpClientSock.close()
sersocket.close()j
#set a sliding window to capture data
def windowdata = refreshslidingwindow(window, data, k):
    
    return window
'''
window = []
def getslidingwindow(window,sensor,k):
    if len(window)<k:
        window.append(sensor)
    else:
        window.pop(0)
        window.append(sensor)
    return window

def lowpassfilter(window):
    b,a = signal.butter(3,0.08,"low")
    sf = signal.filtfilt(b,a,[sensor.getAcce() for sensor in window])
    return [sensor.setAcce(sf) for sensor in window]
# sequence of a pedestrian's state which may be walking, standing, running, elevator... 
stateseq = []

# sequence of sensor pattern, which contains local minimum(-1), local maximum(1) and stataionary(0) 
patternseq = []
'''
# detect the sensor pattern to find out local minimum, local maximum or stationary 
def sensorPatternDetection(window,thd):
    if len(window)<=1
        return
    trend = "stable"
    i = 1;
    while(i<=length-1):
        if trend == "stable":
            if window[i].getAcce()-window[i-1].getAcce() > thd:
                trend = "up"
            elif window[i].getAcce()-window[i-1].getAcce() < -thd:
		trend = "down"
            else:
		trend = "stable"
		if window[i].getTimestamp() not in [eachpattern.getTimestamp() for eachpattern in patternseq]
                pattern = Pattern(windowp[i].getTimestamp(),0)
                patternseq.append(pattern)
	if trend == "up"
            if window[i].getAcce()-window[i-1].getAcce() > thd:
                trend = "up"
            elif window[i].getAcce()-window[i-1].getAcce() < -thd:
		trend = "down"
		if window[i].gettimestamp not in [eachpattern.getTimestamp() for eachpattern in patternseq]
                    pattern = Pattern(window[i].getTimestamp(),1)
                    patternseq.append(pattern)
            else:
		trend = "stable"
	if trend == "down":
            if window[i].getAcce()-window[i-1].getAcce() > thd:
                trend = "up"
		if window[i].gettimestamp not in [eachpattern.getTimestamp() for eachpattern in patternseq]
                    pattern = Pattern(window[i].getTimestamp(),-1)
                    patternseq.append(pattern)
            elif window[i].getAcce()-window[i-1].getAcce() < -thd:
		trend = "down"
            else:
		trend = "stable"    
 
# dectect the state of a pedestrian (1,0,...,0,-1) represents elevator down (-1,0...,0,1) represents elevatorup 
def elevatorDetection(patternseq):
    if patternseq==None
        return
    state = "standingin"
    for i in range(len(patternseq)):
        if state == "standingin":
            if patternseq[i].getAcce() == 1:
                state = "elevatordown_start"
            elif patternseq[i].getAcce() == -1:
                state = "elevatorup_start"
        elif state == "elevatordown_start"
            if patternseq[i].getAcce() == 0:
                state = "elevatordown_stable"
            else:
                state = None
        elif state == "elevatorup_start"
            if patternseq[i].getAcce() == 0:
                state = "elevatorup_stable"
            else:
                state = None
        elif state == "elevatordown_stable"
            if patternseq[i].getAcce() == -1:
                state = "elevatordown_stop"
            elif patternseq[i].getAcce() == 0:
                state = "elevatordown_stable"
            else:
                state = None
        elif state == "elevatorup_stable":
            if patternseq[i].getAcce() == 1:
                state = "elevatorup_stop"
            elif patternseq[i].getAcce() == 0:
                state = "elevatorup_stable"
            else:
                state = None
    if state == "elevatorup_stop" or "elevatordown_stop"
        print state
    return state
        
   '''     

    
    
    
