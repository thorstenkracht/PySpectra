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
Canvas = None
lenPlotted = -1

def initGraphic( figureIn = None, canvasIn = None):
    '''
    haso107d1: 1920 x 1200
    spectra: 640 x 450 def., A4:  680 x 471 
    '''
    global Fig, Canvas
    if figureIn is not None:
        Fig = figureIn
        Canvas = canvasIn
        return 

    plt.ion()
    print "graphics.initGraphic, Fig", id( Fig)

    if not plt.get_fignums():
        Fig = plt.figure(1, figsize=(11.6,8.2))
    else:
        Fig = plt.figure(1)
        Fig.clear()

    return

def _setSizeGraphicsWindow( nScan):

    #print "graphics.setSizeGraphicsView, nScan", nScan, "returning"
    return

    if nScan > 10:
        w = 30
    elif nScan > 4: 
        w = 25
    else: 
        w = 20
    h = w/1.414
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches( w/2.54, h/2.54, forward = True)

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

def cls():
    '''
    clear screen: allow for a new plot
    '''
    print "graphics.cls"
    if Fig is None:
        print "graphics.cls, Fig is None"
        return 
    Fig.clear()
    plt.draw()
    #
    # clear the plotItems
    #
    scanList = _GQE.getScanList()
    for i in range( len( scanList)):
        print "graphics.cls, clearing %s" % (scanList[i].name)
        scanList[i].plotItem = None
        scanList[i].plotDataItem = None
        scanList[i].lastIndex = 0

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
        if nrow == 0 or ncol == 0 or nplot == 0:
            plotItem = Fig.add_subplot( scan.at[0], scan.at[1], scan.at[2])
        else:
            plotItem = Fig.add_subplot( nrow, ncol, nplot)
    except Exception, e:
        print "graphics.createPlotItem: caught exception, nrow", nrow, "ncol", ncol, "nplot", nplot
        print repr( e)
        raise ValueError( "graphics.createPlotItem, throwing exception")

    plotItem.set_autoscale_on( True)
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

    #if not arX: 
    #    plotItem.setXRange( scan.xMin, scan.xMax)

    for elm in scan.textList:
        plotItem.text( elm.x, elm.y, elm.text, va = elm.vAlign, ha = elm.hAlign)

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

def _adjustFigure():

    left = 0.125   # the left side of the subplots of the figure
    right = 0.9    # the right side of the subplots of the figure
    bottom = 0.1   # the bottom of the subplots of the figure
    top = 0.9      # 0.9, the top of the subplots of the figure
    wspace = 0.2   # the amount of width reserved for space between subplots,
                   # expressed as a fraction of the average axis width
    hspace = 0.2   # the amount of height reserved for space between subplots,
                   # expressed as a fraction of the average axis height

    if _GQE.getTitle() is not None:
        top -= 0.05
    if _GQE.getComment() is not None:
        top -= 0.05
    #print "graphics.adjustFigure, top", top
    plt.subplots_adjust( left = left, bottom = bottom, right = right,
                         top = top, wspace = 0.2, hspace = 0.2)

    return 

def _getNumberOfPlottedScans(): 
    '''
    returns the number of scans which already the plotItem - 
    the number of scans that have already at least partially plotted
    '''
    scanList = _GQE.getScanList()
    count = 0
    for scan in scanList:
        if scan.plotItem is not None:
            count += 1
    print "graphics.getNumberOfPlottedScans", count
    return count
    
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
    global lenPlotted
    #
    # don't want to check for nameList is None below
    #
    print "graphics.display, nameList", nameList
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

    if len( nameList) == 0:
        lenTemp = len( scanList) - _GQE.getNoOverlaid()
        if lenTemp != lenPlotted and lenPlotted != -1: 
            cls()
        lenPlotted = lenTemp
        if lenTemp == 0:
            return 
        ncol = int( _math.floor( _math.sqrt( lenTemp) + 0.5))
        nrow = int( _math.ceil( float(lenTemp)/float(ncol)))
        #nplot = 1 + _getNumberOfPlottedScans()
        #print "graphics.display: lenTemp %d, ncol %d, nrow %d" % (lenTemp, ncol, nrow)
        nplot = 1 
    elif len( nameList) == 1:
        if lenPlotted != 1 and lenPlotted != -1: 
            cls()
        lenPlotted = 1
        ncol = 1
        nrow = 1
        nplot = 1
    else:
        raise ValueError( "graphics.display: to be done")

    _adjustFigure()
    
    title = _GQE.getTitle()
    if title is not None:
        if not _textIsOnDisplay( title):
            Fig.text( 0.5, 0.95, title, va='center', ha='center')
    
    comment = _GQE.getComment()
    if comment is not None:
        if title is not None:
            if not _textIsOnDisplay( comment):
                Fig.text( 0.5, 0.90, comment, va='center', ha='center')
        else:
            if not _textIsOnDisplay( comment):
                Fig.text( 0.5, 0.95, comment, va='center', ha='center')

    #
    # --- first pass: run through the scans in scanList and display 
    #     non-overlaid scans
    #
    for i in range( len( scanList)):
        #
        # 'scan' is a copy
        #
        scan = scanList[i]
        print "graphics.display", scan.name, "currentIndex", scan.currentIndex, "LastIndex", scan.lastIndex
        #
        # check, if theren is something to display
        #
        #if scan.lastIndex == scan.currentIndex:
        #    continue
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
                print "graphics.display: creating plot for", scan.name, nrow, ncol, nplot
                scan.plotItem = _createPlotItem( scan, nrow, ncol, nplot)
            except ValueError, e:
                print "graphics.display: exception from createPlotItem"
                print "graphics.display: consider a 'cls'"
                print "graphics.display", repr( e)
                return 
            if scan.doty:
                xDate = []
                for x in scan.x[:(scan.currentIndex + 1)]:
                    xDate.append( _doty2datetime( x))
                xDateMpl = matplotlib.dates.date2num( xDate)
                scan.plotItem.plot_date( xDateMpl, scan.y[:(scan.currentIndex + 1)], xdate = True,
                                         linestyle='solid', marker='None')
            else:
                scan.plotDataItem, = scan.plotItem.plot( scan.x[:(scan.currentIndex + 1)], 
                                                         scan.y[:(scan.currentIndex + 1)], scan.color)

        #
        # modify the scan 
        #
        scanList[i].plotItem = scan.plotItem

        #
        # check, if there is something to display
        # 
        if scan.lastIndex == scan.currentIndex or \
           scan.currentIndex  == 0:
            nplot += 1
            continue

        if scan.doty:
            pass
            #xDate = []
            #for x in scan.x[:(scan.currentIndex + 1)]:
            #    xDate.append( _doty2datetime( x))
            #xDateMpl = matplotlib.date2num( xDate)
            #scan.plotItem.plot_date( xDateMpl, scan.y, xdate = True)
        else:
            print "graphics.display: plotting %s %d of %d" % \
                (scan.name, scan.currentIndex + 1, len( scan.x))
            scan.plotDataItem.set_data( scan.x[:(scan.currentIndex + 1)], 
                                        scan.y[:(scan.currentIndex + 1)])

        scan.plotItem.set_xlim( scan.x[0], scan.x[scan.currentIndex])
        scan.plotItem.set_ylim( _np.min( scan.y[:(scan.currentIndex + 1)]), 
                                _np.max( scan.y[:(scan.currentIndex + 1)]))
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
        if scanList[i].lastIndex == scanList[i].currentIndex:
            continue
        #
        # 'scan' is a copy
        #
        if scanList[i].overlay is None:
            continue
        
        if len( nameList) > 0 and scanList[i].name not in nameList:
            continue
        target = _GQE.getScan( scanList[i].overlay)
        scan = scanList[i]
        #
        # modify the overlaid scan 
        #
        scan.plotItem = target.plotItem.twinx()

        print "display: overlying %s to %s" % (scan.name, target.name)

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

    print "graphics.display, calling draw()"
    plt.draw()
    if Canvas is not None:
        Canvas.draw()
    return

def procEventsLoop():
    print "\nPress <return> to continue ",
    while True:
        _time.sleep(0.01)
        processEvents()
        key = _HasyUtils.inkey()        
        if key == 10:
            break
    print ""

def processEvents(): 
    #_QApp.processEvents()
    plt.draw()
    if Canvas is not None:
        Canvas.draw()
