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

class demoSM( QtGui.QMainWindow):
    '''
    the main class of the SardanaMotorMenu application
    '''
    def __init__( self, parent = None):
        super( demoSM, self).__init__( parent)

        self.setWindowTitle( "demoSM")

        self.prepareWidgets()

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
    # the status bar
    #
    def prepareStatusBar( self): 

        self.exit = QtGui.QPushButton(self.tr("&Exit")) 
        self.statusBar.addPermanentWidget( self.exit) # 'permanent' to shift it right
        self.exit.clicked.connect( sys.exit)
        self.exit.setShortcut( "Alt+x")

def execScan( app): 
    print "main.execScan"
    pg.setConfigOption( 'background', 'w')
    pg.setConfigOption( 'foreground', 'k')
    win = pg.GraphicsWindow( title="Scan the Tango Function")
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
    
    app = QtGui.QApplication.instance()
    if app is None:
        print "demoSM, creating new app"
        #app = QtGui.QApplication(sys.argv)
        app = TaurusApplication( [])
        pg.setConfigOption( 'background', 'w')
        pg.setConfigOption( 'foreground', 'k')
        win = pg.GraphicsWindow( title="Window created in main")

        __builtin__.__dict__[ 'app'] = app
        __builtin__.__dict__[ 'win'] = win


    import demoDoor

    door = taurus.Device( HasyUtils.getLocalDoorNames()[0])

    #execScan( app)

    o = demoSM()
    o.show()

    print "main: before app.exec"


    sys.exit( app.exec_())

if __name__ == "__main__":
    main()
    

