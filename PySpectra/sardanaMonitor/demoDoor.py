#!/usr/bin/env python
'''
  this is a minimal demo for a scan 
  start a spock session and execute a scan
  to see, how the data is filled

  Problem: find '***'
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
import __builtin__

sms.registerExtensions()

class demoDoor( sms.BaseDoor):

    def __init__( self, name, **kw):
        self.call__init__( sms.BaseDoor, name, **kw)

        print "demoDoor.__init__()", id( self)
        self.app = QtGui.QApplication.instance()
        self.win = __builtin__.__dict__[ 'win']

        self.x = np.arange( 0., 10., 0.1)
        self.t = np.tan(self.x)
        #
        # *** this is not the place for calling addPlot() since
        # *** we don't know how many we have to allocate
        #
        self.tan = self.win.addPlot()
        self.app.processEvents()
        return 

    def recordDataReceived( self, s, t, v):
        print "recordDataRec"
        if not hasattr( self, "app"):
            print "recordDataRec, return"
            return

        if not hasattr( self, 'i'):
            self.i = 2
        if not hasattr( self, "plot"):
            #
            # *** here we would like to execute addPlot()
            #
            #self.tan = self.win.addPlot( row=0, col=0)
            self.tan.showGrid( x = True, y = True)
            self.tan.enableAutoRange( x = True, y = True)
            self.plot = self.tan.plot( name = "t1", pen=( 0, 0, 255))
            self.plot.setData( self.x, self.t)
        self.plot.setData( self.x[:self.i], self.t[:self.i])
        self.app.processEvents()
        self.i += 1

factory = taurus.Factory()

factory.registerDeviceClass( 'Door',  demoDoor)



