#!/usr/bin/env python
'''
'''
import sys
#from PyQt4 import QtGui, QtCore
from taurus.external.qt import QtGui 
from taurus.external.qt import QtCore
from taurus.qt.qtgui.application import TaurusApplication 
import taurus
import numpy as np
import HasyUtils
import PySpectra as pysp
import pyqtgraph as pg
import time
import __builtin__
import threading

app = None
win = None

TIMEOUT_REFRESH = 100

class demoSM( QtGui.QMainWindow):
    '''
    the main class of the SardanaMotorMenu application
    '''
    def __init__( self, parent = None):
        super( demoSM, self).__init__( parent)

        self.setWindowTitle( "demoSM")

        self.prepareWidgets()
        self.scanNo = -1
        __builtin__.__dict__[ 'scanNo'] = -1 
        self.statusBar = QtGui.QStatusBar()
        self.setStatusBar( self.statusBar)
        self.prepareStatusBar()

    def prepareWidgets( self):
        w = QtGui.QWidget()
        self.layout_v = QtGui.QVBoxLayout()
        w.setLayout( self.layout_v)
        self.setCentralWidget( w)
        self.layout_v.addWidget( QtGui.QLabel( "Demo"))

        #
        # the update timer, don't want to poll all devices at high speed
        #
        self.updateTimer = QtCore.QTimer(self)
        self.updateTimer.timeout.connect( self.cb_refresh)
        self.updateTimer.start( TIMEOUT_REFRESH)

    #
    # the status bar
    #
    def prepareStatusBar( self): 

        self.exit = QtGui.QPushButton(self.tr("&Exit")) 
        self.statusBar.addPermanentWidget( self.exit) # 'permanent' to shift it right
        self.exit.clicked.connect( sys.exit)
        self.exit.setShortcut( "Alt+x")

    def cb_refresh( self): 

        self.updateTimer.stop()
        
        __builtin__.__dict__[ 'mutex'].acquire()

        scanNo = __builtin__.__dict__[ 'scanNo'] 
        if scanNo != self.scanNo:
            pysp.cls()
            self.scanNo = scanNo

        pysp.display()

        self.updateTimer.start( TIMEOUT_REFRESH)

        __builtin__.__dict__[ 'mutex'].release()

def execScan( app): 
    print "main.execScan"
    (xMin, xMax, xDelta) = ( 0., 10., 0.1)
    x = np.arange( xMin, xMax, xDelta)
    t = np.tan(x)
    tan = win.addPlot( row=0, col=0)

    tan.showGrid( x = True, y = True)
    tan.enableAutoRange( x = True, y = True)
    plot = tan.plot( name = "t1", pen=( 0, 0, 255))
    for i in range( 1, len( x)):
        plot.setData( x[:i], t[:i])
        time.sleep(0.01)
        app.processEvents()
    print "main.execScan: done"

def main():
    global app, win
    app = QtGui.QApplication.instance()
    if app is None:
        print "demoSM, creating new app"
        #app = QtGui.QApplication(sys.argv)
        app = TaurusApplication( [])

    import demoDoor_v2

    __builtin__.__dict__[ 'mutex'] = threading.Lock()
        
    door = taurus.Device( HasyUtils.getLocalDoorNames()[0])

    #execScan( app)

    o = demoSM()
    o.show()

    print "main: before app.exec"


    sys.exit( app.exec_())

if __name__ == "__main__":
    main()
    
