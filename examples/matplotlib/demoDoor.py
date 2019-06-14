#!/usr/bin/env python
'''
The problem: addPlot() has to be in the constructor of the Door. 
I would like to have it in recordDataReceived() because there
the number of plots to be allocated is known. But then I get this error
  ZeroDivisionError('float division by zero',)

to demonstrate the issue:

edit demoSM.py to specifc a valid door name

./demoSM
then generate some output on the door
looks good. 

find '***' and toggle comments, then again
./demoSM
crash

'''
from taurus.external.qt import QtGui 
from taurus.external.qt import QtCore
from taurus.qt.qtgui.application import TaurusApplication 
import taurus

try:
    import sardana.taurus.core.tango.sardana.macroserver as sms
except:
    try:
        import taurus.core.tango.sardana.macroserver as sms
    except:
        print "demoDoor.py: failed to import macroserver.py"
        sys.exit(255) 

import pyqtgraph as pg
import numpy as np

sms.registerExtensions()

class demoDoor( sms.BaseDoor):

    def __init__( self, name, **kw):

        self.initDone = False

        self.app = QtGui.QApplication.instance()
        if self.app is None:
            #app = QtGui.QApplication(sys.argv)
            self.app = TaurusApplication( [])

        pg.setConfigOption( 'background', 'w')
        pg.setConfigOption( 'foreground', 'k')
        self.win = pg.GraphicsWindow( title="A Graphics Window")

        self.x = np.arange( 0., 10., 0.1)
        self.t = np.tan(self.x)
        #
        # this is not the place for calling addPlot() since
        # we don't know how many we have to allocate
        #
        self.tan = self.win.addPlot() # ***
        self.i = 2
        self.initDone = True
        self.call__init__( sms.BaseDoor, name, **kw)

        self.app.processEvents()
        return 

    def recordDataReceived( self, s, t, v):
        if not self.initDone:
            print "recordDataRec, return"
            return

        if not hasattr( self, "plot"):
            #
            # here we would like to execute addPlot()
            #
            #try:
            #    self.tan = self.win.addPlot( row=0, col=0) # ***
            #except Exception, e: 
            #    print "recordDataReceived: caught exception"
            #    print repr( e)
            #    return
            self.tan.showGrid( x = True, y = True)
            self.tan.enableAutoRange( x = True, y = True)
            self.plot = self.tan.plot( pen=( 0, 0, 255))
            return

        self.plot.setData( self.x[:self.i], self.t[:self.i])
        self.i += 1
        if self.i == len( self.x): 
            self.i = 0

factory = taurus.Factory()
factory.registerDeviceClass( 'Door',  demoDoor)



