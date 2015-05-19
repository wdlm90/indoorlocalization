#coding=utf-8
import sys

from socket import *
from time import ctime
from scipy import signal
from SocketServer import TCPServer,ThreadingMixIn,StreamRequestHandler
import MySQLdb
import json
import numpy as np
import csv
import math
import traceback

class Server(ThreadingMixIn,TCPServer):pass
class Handler(StreamRequestHandler):
    def handle(self):
        try:
            conn = MySQLdb.connect(host = '127.0.0.1',user = 'root',passwd = 'limeng90',port = 3306,db = 'mobilesensing')
            cur = conn.cursor()
            conn.set_character_set('utf8')
            cur.execute('SET NAMES utf8;')
            cur.execute('SET CHARACTER SET utf8;')
            cur.execute('SET character_set_connection=utf8;')
            print 'successfully connect to MySQL'
        except:
            print 'fail to connect to MySQL'
        while True:
            try:
                print "begin to receive sensing data"
                data = self.rfile.readline().strip()
                print self.client_address,repr(data)
                #self.wfile.write('Thank you for connecting')
                sensordata = json.loads(data)
                #print "pythonobject:",type(sensordata)
                values = (sensordata.get('projectname'),sensordata.get('username'),sensordata.get('timestamp'),\
                          sensordata.get('label'),sensordata.get('datatype'),sensordata.get('acceX'),\
                          sensordata.get('acceY'),sensordata.get('acceZ'),sensordata.get('gyrosX'),\
                          sensordata.get('gyrosY'),sensordata.get('gyrosZ'),sensordata.get('orientX'),\
                          sensordata.get('orientY'),sensordata.get('orientZ'),sensordata.get('magnetX'),\
                          sensordata.get('magnetY'),sensordata.get('magnetZ'),sensordata.get('light'),\
                          sensordata.get('barometer'),sensordata.get('soundlevel'),sensordata.get('cellid'),\
                          sensordata.get('gpsLat'),sensordata.get('gpsLong'),sensordata.get('gpsAlt'),\
                          sensordata.get('gpsSpeed'),sensordata.get('gpsBearing'),sensordata.get('wifiSSID1'),\
                          sensordata.get('wifiBSSID1'),sensordata.get('wifiRSS1'),sensordata.get('wifiSSID2'),\
                          sensordata.get('wifiBSSID2'),sensordata.get('wifiRSS2'),sensordata.get('wifiSSID3'),\
                          sensordata.get('wifiBSSID3'),sensordata.get('wifiRSS3'),sensordata.get('wifiSSID4'),\
                          sensordata.get('wifiBSSID4'),sensordata.get('wifiRSS4'),sensordata.get('wifiSSID5'),\
                          sensordata.get('wifiBSSID5'),sensordata.get('wifiRSS5'),sensordata.get('wifiSSID6'),\
                          sensordata.get('wifiBSSID6'),sensordata.get('wifiRSS6'),sensordata.get('wifiSSID7'),\
                          sensordata.get('wifiBSSID7'),sensordata.get('wifiRSS7'),sensordata.get('wifiSSID8'),\
                          sensordata.get('wifiBSSID8'),sensordata.get('wifiRSS8'),sensordata.get('wifiSSID9'),\
                          sensordata.get('wifiBSSID9'),sensordata.get('wifiRSS9'),sensordata.get('wifiSSID10'),\
                          sensordata.get('wifiBSSID10'),sensordata.get('wifiRSS10'))
                query = "insert into SensorDataTbl values ('%s','%s',%d,'%s',%d,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%d,%f,%f,%f,%f,%f,'%s','%s',%d,'%s','%s',%d,'%s','%s',%d,'%s','%s',%d,'%s','%s',%d,'%s','%s',%d,'%s','%s',%d,'%s','%s',%d,'%s','%s',%d,'%s','%s',%d)" % values

                #query = "insert into SensorDataTbl values('%(projectname)s','%(username)s',%(timestamp)d,'%(label)s',%(datatype)d,%(acceX)f,%(acceY)f,%(acceZ)f,%(gyrosX)f,%(gyrosY)f,%(gyrosZ)f，%(orientX)f，%(orientY)f，%(orientZ)f,%(magnetX)f,%(magnetY)f,%(magnetZ)f,%(light)f,%(barometer)f,%(soundlevel)f,%(cellid)d,%(gpsLat)f,%(gpsLong)f,%(gpsAlt)f,%(gpsSpeed)f,%(gpsBearing)f,'%(wifiSSID1)s','%(wifiBSSID1)s',%(wifiRSS1)d,'%(wifiSSID2)s','%(wifiBSSID2)s',%(wifiRSS2)d,'%(wifiSSID3)s','%(wifiBSSID3)s',%(wifiRSS3)d,'%(wifiSSID4)s','%(wifiBSSID4)s',%(wifiRSS4)d,'%(wifiSSID5)s','%(wifiBSSID5)s',%(wifiRSS5)d,'%(wifiSSID6)s','%(wifiBSSID6)s',%(wifiRSS6)d,'%(wifiSSID7)s','%(wifiBSSID7)s',%(wifiRSS7)d,'%(wifiSSID8)s','%(wifiBSSID8)s',%(wifiRSS8)d,'%(wifiSSID9)s','%(wifiBSSID9)s',%(wifiRSS9)d,'%(wifiSSID10)s','%(wifiBSSID10)s',%(wifiRSS10)d)"  % sensordata

                print query
                #testvalues = ('1','limeng','NULL')
                #testquery = "insert into test values ('%s','%s',%d)" % testvalues
                #print testquery
                cur.execute(query)
                conn.commit()
                print "insert successfully"
            except:
                traceback.print_exc()
                break
        cur.close()
        conn.close()

if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf8')
    host = ''
    port = 12345
    addr = (host,port)
    server = Server(addr,Handler)
    server.serve_forever()