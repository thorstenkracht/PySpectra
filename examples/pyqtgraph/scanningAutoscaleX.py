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
import time
import pyqtgraph.functions as fn

win = None

def display():
    global win
    xMin = 0
    xMax = 50
    xDelta = 0.05
    x = np.arange( xMin, xMax, xDelta)
    t = np.tan(x)

    app = QtGui.QApplication.instance()
    if app is None:
        pg.setConfigOption( 'background', 'w')
        pg.setConfigOption( 'foreground', 'k')
        app = pg.mkQApp()
    
    if win is None:
        win = pg.GraphicsWindow( title="Scan the Tango Function")
    win.clear()

    #win.setBackground( QtGui.QBrush(QtGui.QColor(240,240,240)))   

    win.addLabel( "A figure containing one plot", row = 1, col = 1)
    tan = win.addPlot( row=2, col=1)
    tan.showGrid( x = True, y = True)
    tan.setTitle( title = "The tan() Function")
    tan.setLabel( 'left', 'tan')
    tan.setLabel( 'bottom', 'phase')
    tan.enableAutoRange( x = True, y = True)
    #tan.setXRange( xMin - 0.25, xMax + 0.25)
    tan.plot = tan.plot( pen = (0, 0, 255))

    #tan.clear()
    for i in range( len(x)):
        tan.plot.setData( x = x[0:i], y = t[0:i])
        app.processEvents()

if __name__ == "__main__":
    display()
