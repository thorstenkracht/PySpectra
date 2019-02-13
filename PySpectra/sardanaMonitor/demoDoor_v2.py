#!/usr/bin/env python
'''
  this is a minimal demo for a scan 
  start a spock session and execute a scan
  to see, how the data is filled
'''
import taurus
import time
#from PyQt4 import QtGui, QtCore
from taurus.external.qt import QtGui 
from taurus.external.qt import QtCore
from taurus.qt.qtgui.application import TaurusApplication 

import sardana.taurus.core.tango.sardana.macroserver as sms
import pyqtgraph as pg
import numpy as np
import PySpectra as pysp
import __builtin__

sms.registerExtensions()

class demoDoor_v2( sms.BaseDoor):

    def __init__( self, name, **kw):
        self.call__init__( sms.BaseDoor, name, **kw)
        self.initDone = True
        self.scanNo = 0
        return 

    def prepareNewScan( self, dataRecord): 
        print "prepareNewScan"
        pysp.delete()
        self.scanNo += 1
        __builtin__.__dict__[ 'mutex'].acquire()

        __builtin__.__dict__[ 'scanNo'] = self.scanNo
        scan = pysp.Scan( 's1_%d' % self.scanNo)
        scan.y = np.sin( scan.x)        
        scan.currentIndex = 0

        scan = pysp.Scan( 's2_%d' % self.scanNo)
        scan.y = np.cos( scan.x)
        scan.currentIndex = 0

        scan = pysp.Scan( 's3_%d' % self.scanNo)
        scan.y = np.tan( scan.x)
        scan.currentIndex = 0
        __builtin__.__dict__[ 'mutex'].release()

    def recordDataReceived( self, s, t, v):

        if not hasattr( self, "initDone"):
            print "recordDataRec, return"
            return

        dataRecord = sms.BaseDoor.recordDataReceived( self, s, t, v)

        if dataRecord == None:
            print "demoDoor_v2: dataRecord == None, return"
            return
        # +++
        #print ">>> recordDataReceived "
        #pp.pprint( dataRecord)
        # +++

        #
        # it may happend that no 'type' is in the record, ignore
        #
        if not dataRecord[1].has_key( 'type'):
            print "demoDoor_v2: dataRecord has not 'type', return"
            return
        #
        # a new scan 
        # 
        if dataRecord[1]['type'] == "data_desc":
            self.prepareNewScan( dataRecord)
            return

        scanList = pysp.getScanList()

        for scan in scanList:
            currentIndex = scan.currentIndex
            currentIndex += 1
            if currentIndex > len( scan.x) - 1:
                print "demoDoor_v2: currentIndex %d > len( scan.x) %d " % \
                                  (currentIndex, len( scan.x))
                #raise ValueError( "demoDoor_v2: currentIndex %d > len( scan.x) %d " % 
                #                  currentIndex, len( scan.x))
                break
            scan.currentIndex = currentIndex
        return 
# 

factory = taurus.Factory()

factory.registerDeviceClass( 'Door',  demoDoor_v2)



