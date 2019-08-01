#!/usr/bin/env python
'''
create a plot with a log scale 
'''
import numpy as np
import pyqtgraph as pg
import time, sys

def display():

    app = pg.mkQApp()
    win = pg.GraphicsWindow( title="Log Scale Demo")

    (xMin, xMax, xDelta) = (-5, 5, 0.1)

    x = np.arange( xMin, xMax, xDelta)
    mu = 0.
    sigma = 1.
    y1 = 1/(sigma * np.sqrt(2 * np.pi)) * \
          np.exp( - (x - mu)**2 / (2 * sigma**2))
    mu = 0.5
    sigma = 1.5
    y2 = 1/(sigma * np.sqrt(2 * np.pi)) * \
          np.exp( - (x - mu)**2 / (2 * sigma**2))


    plotItem1 = win.addPlot()
    plotItem2 = win.addPlot()

    #plotItem1.enableAutoRange( x = False, y = False)
    plotItem1.setXRange( xMin, xMax)
    plotItem1.setLogMode( x = False, y = True)
    #
    # -3 corresponds to 0.001, 0 to 1
    #
    plotItem1.setYRange( -3, 0)

    plotItem1.plot( x, y1)
    plotItem2.plot( x, y2)

    txt = pg.TextItem( color='w', anchor = ( 0.5, 0.5))
    txt.setHtml( '<div style="font-size:14px;">Hello</div>')
    txt.setPos( 3., -2.)
    print "text", txt.x(), txt.y()
    vb = plotItem1.getViewBox()
    vb.addItem( txt)

    app.processEvents()
    time.sleep(0.1)
    app.processEvents()

    print "Prtc ",
    sys.stdin.readline()
    
if __name__ == "__main__":
    display()
