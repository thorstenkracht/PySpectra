#!/usr/bin/env python
'''
overlay 2 plots. The first plot has a log scale, the second (right axis) has not. 

problem: if we try to display major tick mark strings at the right axis, we 
         get an error. Find 'showValues'. 
'''
import pyqtgraph as pg
import numpy as np
import time, sys

plotItem = None
viewBox = None

## Handle view resizing 
def updateViews():
    ## view has resized; update auxiliary views to match
    viewBox.setGeometry( plotItem.vb.sceneBoundingRect())
    ## need to re-update linked axes since this was called
    ## incorrectly while views had different shapes.
    ## (probably this should be handled in ViewBox.resizeEvent)
    viewBox.linkedViewChanged( plotItem.vb, viewBox.XAxis)

def main(): 
    global plotItem, viewBox

    pg.setConfigOption( 'background', 'w')
    pg.setConfigOption( 'foreground', 'k')   
    app = pg.mkQApp()
    win = pg.GraphicsWindow( title="Overlay 2 plots")
    win.clear()

    win.addLabel( "First plot has log scale", 
                  row = 1, col = 1, colspan = 10)
    win.addLabel( "There are no major tick mark strings at the right axis :(", 
                  row = 2, col = 1, colspan = 10)

    (xMin, xMax, xDelta) = (-5, 5, 0.1)
    x = np.arange( xMin, xMax, xDelta)

    (mu, sigma) = (0., 1.)
    y = 1/(sigma * np.sqrt(2 * np.pi)) * np.exp( - (x - mu)**2 / (2 * sigma**2))

    (mu, sigma) = (1., 0.7)
    y2 = 1/(sigma * np.sqrt(2 * np.pi)) * np.exp( - (x - mu)**2 / (2 * sigma**2))

    y2 *= 100.

    print "maximum of 2nd plot", np.max( y2)
    plotItem = win.addPlot( row = 3, col = 1)
    plotItem.setLabels(left='axis 1')
    plotDataItem = plotItem.plot()
    plotDataItem.setData( x, y)
    plotItem.setLogMode( x = False, y = True)
    plotItem.showAxis('top')
    plotItem.showAxis('right')
    plotItem.getAxis('right').setLabel('axis2', color= '#00ffff')
    plotItem.getAxis('right').style[ 'showValues'] = False 
    
    # create a new ViewBox for the overlaid plot and make some link-magic
    viewBox = pg.ViewBox()
    plotItem.scene().addItem(viewBox)
    plotItem.getAxis('right').linkToView( viewBox)
    viewBox.setXLink( plotItem)
    
    vbDataItem = pg.PlotDataItem( x, y2, pen = '#00ffff')
    vbDataItem.setLogMode( False, False)
    viewBox.addItem( vbDataItem)

    viewBox.enableAutoRange( x = False, y = False)
    viewBox.setXRange( -5, 5)
    viewBox.setYRange( 0., 100.)

    updateViews()
    plotItem.vb.sigResized.connect(updateViews)

    app.processEvents()
    time.sleep(0.1)
    app.processEvents()

    print "Prtc ",
    sys.stdin.readline()
    
if __name__ == '__main__':
    main()

