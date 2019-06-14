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
    t = np.tan(2*np.pi*x)*0.

    app = QtGui.QApplication.instance()
    if app is None:
        pg.setConfigOption( 'background', 'w')
        pg.setConfigOption( 'foreground', 'k')
        app = pg.mkQApp()
    
    win = pg.GraphicsWindow( title="Display some zeros")
    win.clear()

    win.addLabel( "A figure containing a plot", row = 1, col = 1)
    zero = win.addPlot( row=2, col=1)
    zero.showGrid( x = True, y = True)
    zero.setTitle( title = "Only Zeros")
    zero.setLabel( 'left', 'zero')
    zero.setLabel( 'bottom', 'phase')
    zero.enableAutoRange( x = False, y = False)
    zero.setXRange( xMin - 0.25, xMax + 0.25)
    zero.setYRange( -1., 1.)

    zero.clear()
    zero.plot( x, t, pen=( 0, 0, 255))
    app.processEvents()
    time.sleep(0.1)
    app.processEvents()

    print "Prtc ",
    sys.stdin.readline()
    
if __name__ == "__main__":
    display()
