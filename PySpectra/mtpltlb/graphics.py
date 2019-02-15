#!/usr/bin/env python

import matplotlib
matplotlib.use( 'TkAgg')
import matplotlib.pyplot as plt
import time as _time
import os as _os
import math as _math
import numpy as _np
import PySpectra.dMgt.GQE as _GQE
import HasyUtils as _HasyUtils
import datetime as _datetime

Fig = None

def initGraphic():
    '''
    haso107d1: 1920 x 1200
    spectra: 640 x 450 def., A4:  680 x 471 
    '''
    global Fig
    plt.ion()
    print "graphics.initGraphic"
    if not plt.get_fignums():
        Fig = plt.figure(1, figsize=(11.6,8.2))
    else:
        Fig = plt.figure(1)
        Fig.clear()

    return (Fig)

def _setSizeGraphicsWindow( nScan):
    # +++
    return 

def setWsViewport( size = None):
    '''
    the workstation viewport is the graphics window
    '''
    if size is None:
        return 

    if size == "DINA4" or size == "DINA4L": 
        pass
    elif size == "DINA4P": 
        pass
    else:
        raise ValueError( "graphics.setWsViewport: no valid size, %s" % size)

    return 


def procEventsLoop():
    raise ValueError( "mtpltlb.graphics.procEventsLoop: this is for pyqtgraph")

def processEvents(): 
    raise ValueError( "mtpltlb.graphics.processEvents: this is for pyqtgraph")

def cls():
    '''
    clear screen: allow for a new plot
    '''
    print "graphics.cls"
    if Fig is None:
        return 
    Fig.clear()
    #
    # clear the plotItems
    #
    scanList = _GQE.getScanList()
    for i in range( len( scanList)):
        scanList[i].plotItem = None
        scanList[i].plotDataItem = None

def _doty2datetime(doty, year = None):
    """
    Convert the fractional day-of-the-year to a datetime structure.
    The default year is the current year.

    Example: 
      a = doty2datetime( 28.12)
      m = [ 'Jan', 'Feb', 'Mar', 'Aptr', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
      print "%s %d, %02d:%02d" % (m[ a.month - 1], a.day, a.hour, a.minute)
      --> Jan 29, 02:52
    """
    if year is None:
        now = _datetime.datetime.now()
        year = now.year
    dotySeconds = doty*24.*60.*60
    boy = _datetime.datetime(year, 1, 1)
    return boy + _datetime.timedelta(seconds=dotySeconds)

def _createPlotItem( scan, nrow = 0, ncol = 0, nplot = 0):            
    '''
    create a plotItem, aka viewport (?) with title, axis descriptions and texts
    '''
    try:
        if scan.doty: 
            pass
        else:
            if nrow == 0 or ncol == 0 or nplot == 0:
                plotItem = Fig.add_subplot( scan.at[0], scan.at[1], scan.at[2])
            else:
                plotItem = Fig.add_subplot( nrow, ncol, nplot)
    except Exception, e:
        print "graphics.createPlotItem: caught exception, row", row, "col", col, "colspan", scan.colSpan
        print repr( e)
        raise ValueError( "graphics.createPlotItem, throwing exception")

    plotItem.grid( True)
    
    #
    # the length of the title has to be limited. Otherwise pg 
    # screws up. The plots will no longer fit into the workstation viewport
    # and the following display command, even with less scans, will 
    # also not fit into the graphics window
    #
    lenMax = 15
    if len( _GQE.getScanList()) > 15: 
        lenMax = 12

    if len( scan.name) > lenMax:
        tempName = "X_" + scan.name[-lenMax:]
    else: 
        tempName = scan.name

    plotItem.set_title( tempName)

    if hasattr( scan, 'xLabel'):
        plotItem.set_xlabel( scan.xLabel)
    if hasattr( scan, 'yLabel'):
        plotItem.set_ylabel( scan.yLabel)

    arX = scan.autorangeX
    arY = scan.autorangeY

    if scan.yMin is None:
        arY = True
    else:
        if not scan.autorangeY: 
            arY = False

    plotItem.set_autoscale_on( True)

    #if not arX: 
    #    plotItem.setXRange( scan.xMin, scan.xMax)

    #for elm in scan.textList:
    #    if elm.hAlign == 'left':
    #        anchorX = 0
    #    elif elm.hAlign == 'right':
    #        anchorX = 1
    #    elif elm.hAlign == 'center':
    #        anchorX = 0.5
    #    if elm.vAlign == 'top':
    #        anchorY = 0
    #    elif elm.vAlign == 'bottom':
    #        anchorY = 1
    #    elif elm.vAlign == 'center':
    #        anchorY = 0.5
    #    txt = _pg.TextItem( elm.text, color=elm.color, anchor = ( anchorX, anchorY))
    #    x = (scan.xMax - scan.xMin)*elm.x + scan.xMin
    #    y = ( _np.max( scan.y) - _np.min( scan.y))*elm.y + _np.min( scan.y)
    #    #txt.setParentItem( plotItem.getViewBox())
    #    #txt.setPos( 20, 20)
    #    plotItem.addItem( txt)
    #    txt.setPos( x, y)
    #    txt.show()

    return plotItem

def _textIsOnDisplay( textStr):
    '''
    searches the list of Items to see whether textStr exists already
    '''
    return False # +++
    for item in _win.items():
        if type( item) is _pg.graphicsItems.LabelItem.LabelItem: 
            if textStr == item.text:
                return True

    return False

def display( nameList = None):
    '''
    display one or more or all scans

    Parameters
    ----------
    None: 
          display all scans
    Name: string
          a list of scans to be displayed

    Example
    -------
    PySpectra.display( [ 's1', 's2'])
      display scans s1 and s2
    PySpectra.display()
      display all scans

    Module: PySpectra.graphics.<graphLib>.graphics.py
    '''
    #
    # don't want to check for nameList is None below
    #
    print "graphics.display"
    if nameList is None:
        nameList = []

    if Fig is None: 
        initGraphic()

    #
    # Do not put a cls() here because it takes a lot of time, especially when
    # fast displays are done. 
    # Try /home/kracht/Misc/pySpectra/test/dMgt/testGQE.py testFillData

    #
    # see if the members of nameList arr in the scanList
    #
    for nm in nameList:
        if _GQE.getScan( nm) is None:
            raise ValueError( "graphics.display: %s is not in the scanList" % nm)

    scanList = _GQE.getScanList()
    #
    # if there is only one scan to be displayed, there is no overlay
    #
    flagDisplaySingle = False
    if len( nameList) == 1 or len( scanList) == 1:
        flagDisplaySingle = True

    #
    # adjust the graphics window to the number of displayed scans
    #
    _setSizeGraphicsWindow( _GQE.getNumberOfScansToBeDisplayed( nameList))
    
    lenTemp = len( scanList)
    ncol = _math.floor( _math.sqrt( lenTemp) + 0.5)
    nrow = _math.ceil( float(lenTemp)/float(ncol))
    nplot = 1
    #title = _GQE.getTitle()
    #if title is not None:
    #    if not _textIsOnDisplay( title):
    #        _win.addLabel( title, row = row, col = 0, rowspan = 1, 
    #                       colspan = int( ncol))
    #    row += 1
    
    #comment = _GQE.getComment()
    #if comment is not None:
    #    if not _textIsOnDisplay( comment):
    #        _win.addLabel( comment, row = row, col = 0, 
    #                       rowspan = 1, colspan = int( ncol))
    #    row += 1
    #
    # --- first pass: run through the scans in scanList and display 
    #     non-overlaid scans
    #
    for i in range( len( scanList)):
        #
        # 'scan' is a copy
        #
        scan = scanList[i]
        #
        # check, if theren is something to display
        #
        if scan.lastIndex == scan.currentIndex:
            continue
        #
        # overlay? - don't create a plot for this scan. Plot it
        # in the second pass. But it is displayed, if it is the only 
        # scan or if it is the only scan mentioned in nameList
        #
        if scan.overlay is not None and not flagDisplaySingle:
            continue

        if len( nameList) > 0: 
            if scan.name not in nameList:
                continue
        #
        # if we re-use the  plotItem ( aka viewport ?),
        # we can use setData(), see below. That makes things much faster.
        #
        if scan.plotItem is None:
            try:
                scan.plotItem = _createPlotItem( scan, nrow, ncol, nplot)
            except ValueError, e:
                print "graphics.display: exception from createPlotItem"
                print "graphics.display: consider a 'cls'"
                print "graphics.display", repr( e)
                return 
            scan.plotDataItem, = scan.plotItem.plot( scan.x[:(scan.currentIndex + 1)], 
                                                     scan.y[:(scan.currentIndex + 1)], scan.color)

        #
        # modify the scan 
        #
        scanList[i].plotItem = scan.plotItem

        scan.plotDataItem.set_data( scan.x[:(scan.currentIndex + 1)], 
                                    scan.y[:(scan.currentIndex + 1)])
        scan.plotItem.relim()
        scan.plotItem.autoscale_view( True, False, True)
        #
        # keep track of what has already been displayed
        #
        scan.lastIndex = scan.currentIndex

        nplot += 1
    #
    # --- second pass: display overlaid scans
    #
    for i in range( len( scanList)):
        #
        # if only one scan is displayed, there is no overlay
        #
        if len( nameList) == 1:
            break
        #
        # check, if theren is something to display
        #
        if scan.lastIndex == scan.currentIndex:
            continue
        #
        # 'scan' is a copy
        #
        scan = scanList[i]
        if scan.overlay is None:
            continue
        
        if len( nameList) > 0 and scan.name not in nameList:
            continue
        target = _GQE.getScan( scan.overlay)
        scan.plotItem = target.plotItem
        #
        # modify the overlaid scan 
        #
        scanList[i].plot = scan.plotItem

        scan.plotDataItem, = scan.plotItem.plot( scan.x[:(scan.currentIndex + 1)], 
                                                 scan.y[:(scan.currentIndex + 1)], scan.color)

        scan.plotItem.relim()
        scan.plotItem.autoscale_view( True, False, True)

        target.plotItem.set_title( "%s and %s" % (target.name, scan.name))

        scan.lastIndex = scan.currentIndex
        if scan.yMin is None:
            scan.plotItem.set_autoscale_on( True)
        else:
            scan.plotItem.set_ylim( scan.yMin, scan.yMax)
        scan.plotItem.set_xlim( scan.xMin, scan.xMax)

    plt.draw()
    return
