#!/usr/bin/env python
#
# file name: pg_scan.py
#
# this script can be executed, e.g., from ipython
#
# In [1]: import pg_scan
# In [2]: pg_scan.display()
#
# pg_scan simulates a measurement. Two plots, tan and dt,
# are displayed from within a loop. The length of the data 
# fields increase. The plot dt shows the time it takes to 
# display the tan data. No QtGui mainloop is involved.
#
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import time, sys
import pyqtgraph.functions as fn

win = None

def display():
    global win
    xMin = 0
    xMax = 1
    xDelta = 0.1
    x = np.arange( xMin, xMax, xDelta)
    t = np.tan(2*np.pi*x)
    s = np.sin(2*np.pi*x)

    app = QtGui.QApplication.instance()
    if app is None:
        pg.setConfigOption( 'background', 'w')
        pg.setConfigOption( 'foreground', 'k')
        app = pg.mkQApp()
    
    if win is None:
        win = pg.GraphicsWindow( title="Scan the Tango Function")
    win.clear()

    #win.setBackground( QtGui.QBrush(QtGui.QColor(240,240,240)))   
    win.addLabel( "A figure containing two plots", row = 1, col = 1)
    plotItem = win.addPlot( row=2, col=1)
    plotItem.showGrid( x = True, y = True)
    plotItem.setTitle( title = "The tan() Function")
    plotItem.setLabel( 'left', 'plotItem')
    plotItem.setLabel( 'bottom', 'phase')
    #plotItem.enableAutoRange( x = False, y = True)
    plotItem.setXRange( xMin - 0.25, xMax + 0.25)
    plotItem.setYRange( -2, 2)

    tan = plotItem.plot( x, t, pen= ( 0, 0, 255))
    sin = plotItem.plot( x, s, pen= ( 0, 255, 0))
    sin.setScale( 2.)
    app.processEvents()
    time.sleep( 0.1)
    app.processEvents()

    print "Prtc ",
    sys.stdin.readline()

if __name__ == "__main__":
    display()
