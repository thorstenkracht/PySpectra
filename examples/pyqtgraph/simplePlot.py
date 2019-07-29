#!/usr/bin/env python
#

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import time, sys


def display():
    global win
    xMin = 0
    xMax = 50
    xDelta = 0.1
    x = np.arange( xMin, xMax, xDelta)
    t = np.tan(2*np.pi*x)

    app = QtGui.QApplication.instance()
    if app is None:
        pg.setConfigOption( 'background', 'w')
        pg.setConfigOption( 'foreground', 'k')
        app = pg.mkQApp()
    
    win = pg.GraphicsWindow( title="Scan the Tango Function")
    win.clear()

    win.addLabel( "A figure containing a plots", row = 1, col = 1)
    tan = win.addPlot( row=2, col=1)
    tan.showGrid( x = True, y = True)
    tan.setTitle( title = "The tan() Function")
    tan.setLabel( 'left', 'tan')
    tan.setLabel( 'bottom', 'phase')
    tan.enableAutoRange( x = False, y = True)
    tan.setXRange( xMin - 0.25, xMax + 0.25)

    tan.clear()
    t = tan.plot( x, t, pen=( 0, 0, 255))
    app.processEvents()
    time.sleep(0.1)
    app.processEvents()

    print "plotDataItem, viewPos", repr(t.dataBounds( 0))
    print "Prtc ",
    sys.stdin.readline()
    
if __name__ == "__main__":
    display()
