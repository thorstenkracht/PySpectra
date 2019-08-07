#!/usr/bin/env python
'''
create 22 plots and put the plot titles into the plot 
'''

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import time, sys
win = None,
app = None

def display( t1):
    global win, app
    xMin = 0
    xMax = 10
    xDelta = 0.1
    x = np.arange( xMin, xMax, xDelta)
    y = np.random.random_sample( (len( x), ))*10. + 100.
    win.clear()
    #procEvents()
    
    win.addLabel( "A figure containing a single plot", row = 1, col = 1, colspan = 10)
    win.addLabel( "A comment", row = 2, col = 1, colspan = 10)

    r = 3
    c = 1
    for i in range( 20): 
        plotItem = win.addPlot( row=r, col=c)
        plotItem.setTitle( title = "a function")
        plotItem.enableAutoRange( x = True, y = True)
        #
        # if you add a TextItem, see below, and you do not set the XRange
        # then the x-axis will be wrong
        #
        txt = pg.TextItem( text= t1, color='k', anchor = ( 0.0, 1.))
        txt.setPos( 5., 20.)
        #
        # if ignoreBounds is omitted, autorangeX won't work
        #
        plotItem.addItem( txt, ignoreBounds = True)

        #plotItem.setYRange( 0, 120.)
        c += 1
        if c > 4: 
            c = 1
            r += 1
        plotItem.plot( x, y, pen=( 0, 0, 255))

    procEvents()
        
    
    return

def procEvents():
    app.processEvents()
    app.processEvents()
    app.processEvents()
    return 
    
if __name__ == "__main__":

    pg.setConfigOption( 'background', 'w')
    pg.setConfigOption( 'foreground', 'k')
    app = pg.mkQApp()    
    win = pg.GraphicsWindow( title="Scan the Tango Function")

    display( "hallo")
    display( "moin")
    print "Prtc ",
    sys.stdin.readline()

