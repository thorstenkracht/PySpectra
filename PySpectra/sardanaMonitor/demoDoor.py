#!/usr/bin/env python
'''
  this is a minimal demo for a scan 
  start a spock session and execute a scan
  to see, how the data is filled

  Problem: find '***'
'''
import time
#from PyQt4 import QtGui, QtCore
from taurus.external.qt import QtGui 
from taurus.external.qt import QtCore
from taurus.qt.qtgui.application import TaurusApplication 

try:
    import sardana.taurus.core.tango.sardana.macroserver as sms
except:
    try:
        import taurus.core.tango.sardana.macroserver as sms
    except:
        print "demoDoor.py: failed to import macroserver.py"
        sys.exit(255) 

#import sardana.taurus.core.tango.sardana.macroserver as sms
import pyqtgraph as pg
import numpy as np

sms.registerExtensions()

class demoDoor( sms.BaseDoor):

    def __init__( self, name, **kw):

        self.initDone = False
        print "demoDoor.__init__()"
        self.app = QtGui.QApplication.instance()
        pg.setConfigOption( 'background', 'w')
        pg.setConfigOption( 'foreground', 'k')
        self.win = pg.GraphicsWindow( title="A Graphics Window")

        self.x = np.arange( 0., 10., 0.1)
        self.t = np.tan(self.x)
        #
        # *** this is not the place for calling addPlot() since
        # *** we don't know how many we have to allocate
        #
        #self.tan = self.win.addPlot()
        #self.app.processEvents()
        self.i = 2
        self.initDone = True
        self.call__init__( sms.BaseDoor, name, **kw)
        return 

    def recordDataReceived( self, s, t, v):
        if not self.initDone:
            print "recordDataRec, return"
            return

        print "recordDataRec"

        if not hasattr( self, "plot"):
            #
            # *** here we would like to execute addPlot()
            #
            try:
                self.tan = self.win.addPlot( row=0, col=0)
            except Exception, e: 
                print "recordDataReceived: caught exception"
                print repr( e)
                return

            self.tan.showGrid( x = True, y = True)
            self.tan.enableAutoRange( x = True, y = True)
            self.plot = self.tan.plot( name = "t1", pen=( 0, 0, 255))
            self.plot.setData( self.x, self.t)
        self.plot.setData( self.x[:self.i], self.t[:self.i])
        self.app.processEvents()
        self.i += 1

import taurus

factory = taurus.Factory()
factory.registerDeviceClass( 'Door',  demoDoor)



