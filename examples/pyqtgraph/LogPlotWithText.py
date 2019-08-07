#!/usr/bin/env python
'''
create a plot with a log scale and add a TextItem
'''
import numpy as np
import pyqtgraph as pg
import time, sys

def display():

    pg.setConfigOption( 'background', 'w')
    pg.setConfigOption( 'foreground', 'k')
    app = pg.mkQApp()
    win = pg.GraphicsWindow( title="Log Scale Demo")

    (xMin, xMax, xDelta) = ( 0.001, 10., 0.1)
    x = np.arange( xMin, xMax, xDelta)

    plotItem1 = win.addPlot()
    plotItem1.plot( x, x)

    plotItem1.setLogMode( x = False, y = True)

    plotItem1.enableAutoRange( x = True, y = False)

    # -3 corresponds to 0.1
    plotItem1.setYRange( -3, 1)

    txt = pg.TextItem( color='k', anchor = ( 0.5, 0.5))
    txt.setHtml( '<div style="font-size:14px;">Hello</div>')
    txt.setPos( 3., 0.)
    #
    # if ignoreBounds = True is removed the x-range will
    # be from -20 to 30. 
    #
    plotItem1.addItem( txt, ignoreBounds = True)

    app.processEvents()
    time.sleep(0.1)
    app.processEvents()

    print "Prtc ",
    sys.stdin.readline()
    
if __name__ == "__main__":
    display()
