#!/usr/bin/env python
'''
create a plot with a log scale - the setYRange() call is ignored
'''
import numpy as np
import pyqtgraph as pg
import time, sys

def display():

    (xMin, xMax, xDelta) = (-5, 5, 0.1)

    x = np.arange( xMin, xMax, xDelta)

    mu = 0.
    sigma = 1.
    y = 1/(sigma * np.sqrt(2 * np.pi)) * \
          np.exp( - (x - mu)**2 / (2 * sigma**2))

    app = pg.mkQApp()
    win = pg.GraphicsWindow( title="Log Scale Demo")

    plotItem = win.addPlot()

    #plotItem.enableAutoRange( x = False, y = False)
    plotItem.setXRange( xMin, xMax)
    plotItem.setLogMode( x = False, y = True)
    plotItem.setYRange( -3, 0)

    plotItem.plot( x, y)

    txt = pg.TextItem( color='w', anchor = ( 0.5, 0.5))
    txt.setHtml( '<div style="font-size:14px;">Hello</div>')
    txt.setPos( 3., -2.)
    print "text", txt.x(), txt.y()
    vb = plotItem.getViewBox()
    vb.addItem( txt)

    app.processEvents()
    time.sleep(0.1)
    app.processEvents()

    print "Prtc ",
    sys.stdin.readline()
    
if __name__ == "__main__":
    display()
