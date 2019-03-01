#!/usr/bin/env python

import matplotlib
matplotlib.use( 'TkAgg')
import matplotlib.pyplot as plt
import time as _time
import os as _os
import math as _math
import numpy as _np
import PySpectra.dMgt.GQE as _GQE
import PySpectra.utils as _utils
import PySpectra.pqtgrph.graphics as _pqt_graphics
import HasyUtils as _HasyUtils
import datetime as _datetime

Fig = None
Canvas = None
def initGraphic( figureIn = None, canvasIn = None):
    '''
    haso107d1: 1920 x 1200
    spectra: 640 x 450 def., A4:  680 x 471 
    '''
    global Fig, Canvas
    if figureIn is not None:
        Fig = figureIn
        #print "+++mpl.graphics.initGraphic", dir( Fig)
        Canvas = canvasIn
        return 

    plt.ion()
    #print "graphics.initGraphic"

    if not plt.get_fignums():
        Fig = plt.figure(1, figsize=(21./2.54, 14.85/2.54))
    else:
        Fig = plt.figure(1)
        Fig.clear()

    return

def createPDF( fileName = None): 
    '''
    '''
    #flag = False
    #if Fig is None:
    #    _pqt_graphics.close()
    #    initGraphic()
    #    display()
    #    flag = True

    if fileName is None:
        fileName = "pyspOutput.pdf"
    if _os.system( "/usr/local/bin/vrsn -s -nolog %s" % fileName):
        print "graphics.createPDF: failed to save the current version of %s" % fileName
    
    try:
        Fig.savefig( fileName, bbox_inches='tight')
    except Exception, e:
        print "graphics.createPDF: failed to create", fileName
        print repr( e)
        return None

    #if flag:
    #    close()
    #    _pqt_graphics.initGraphic()
        
    return fileName
    
def _setSizeGraphicsWindow( nScan):
    '''
    '''

    if nScan > 9:
        w = 29.7
    elif nScan > 4: 
        w = 21
    else: 
        w = 14.85

    h = w/1.414
    #print "mpl_graphics.setSizeGraphicsWindow", w/2.54, h/2.54, Fig.get_figwidth(), Fig.get_figheight()

    if w/2.54 > (Fig.get_figwidth() + 0.1) or h/2.54 > (Fig.get_figheight() + 0.1): 
        if w > 29.6:
            setWsViewport( "DINA4")
        else:
            setWsViewport( "DINA5")
    return 

def setWsViewport( size = None):
    '''
    size: DINA4, DINA4P, DINA3, DINA3P
    '''
    if size is None:
        return 
    if size.upper() == "DINA4" or size.upper() == "DINA4L": 
        w = 29.7
        h = 21
    elif size.upper() == "DINA4P": 
        w = 21
        h = 29.7
    elif size.upper() == "DINA5" or size.upper() == "DINA3L": 
        w = 21
        h = 14.85
    elif size.upper() == "DINA5P": 
        w = 14.85
        h = 21.0
    elif size.upper() == "DINA6" or size.upper() == "DINA6L": 
        w = 14.85
        h = 10.5
    elif size.upper() == "DINA6P": 
        w = 10.5
        h = 14.85
    else:
        raise ValueError( "graphics.setWsViewport: no valid size, %s" % size)

    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches( w/2.54, h/2.54, forward = True)

    return 

def cls():
    '''
    clear screen: allow for a new plot
    '''
    #print "graphics.cls"
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
        #print "graphics.cls, clearing %s" % (scanList[i].name)
        scanList[i].plotItem = None
        scanList[i].plotDataItem = None
        scanList[i].lastIndex = 0


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

def listGraphicsItems(): 
    print "mtpltlb.graphics.listGraphicsItems"
    return

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
    tmp = boy + _datetime.timedelta(seconds=dotySeconds)
    #print "doty2datatime doty", doty, "to", repr( tmp)
    return tmp

def _createPlotItem( scan):            
    '''
    create a plotItem, aka viewport (?) with title, axis descriptions and texts
    '''
    try:
        plotItem = Fig.add_subplot( scan.nrow, scan.ncol, scan.nplot)
    except Exception, e:
        print "graphics.createPlotItem: caught exception"
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
    searches the Fig.texts() to see whether textStr exists already
    '''
    argout = False
    for t in Fig.texts: 
        if textStr == t.get_text(): 
            argout = True
            break
    return argout

def _adjustFigure( nDisplay):
    '''
    configures the figure
    '''
    left = 0.125   # the left side of the subplots of the figure
    right = 0.9    # the right side of the subplots of the figure
    bottom = 0.1   # the bottom of the subplots of the figure
    top = 0.9      # 0.9, the top of the subplots of the figure
    wspace = 0.2   # the amount of width reserved for space between subplots,
                   # expressed as a fraction of the average axis width
    hspace = 0.2   # the amount of height reserved for space between subplots,
                   # expressed as a fraction of the average axis height

    if nDisplay == 3: 
        nDisplay = 4
    if nDisplay > 4: 
        nDisplay = 10

    if _GQE.getTitle() is not None:
        top -= 0.05
    if _GQE.getComment() is not None:
        top -= 0.05

    hsh = { '1':  { 'top': top,
                    'bottom': 0.10,
                    'left': 0.125,
                    'right': 0.9,
                    'hspace': 0.2,
                    'wspace': 0.2}, 
            '2':  { 'top': top,
                    'bottom': 0.10,
                    'left': 0.12,
                    'right': 0.90,
                    'hspace': 0.42,
                    'wspace': 0.20}, 
            '4':  { 'top': top + 0.02,
                    'bottom': 0.10,
                    'left': 0.10,
                    'right': 0.96,
                    'hspace': 0.44,
                    'wspace': 0.34}, 
            '10':  { 'top': top + 0.02,
                    'bottom': 0.07,
                    'left': 0.07,
                    'right': 0.97,
                    'hspace': 0.62,
                     'wspace': 0.20}
            }
    Fig.subplots_adjust( **hsh[ str(nDisplay)])

    return 

def _displayTitleComment():     
    '''
    '''
    sz = 14
    title = _GQE.getTitle()
    if title is not None:
        if not _textIsOnDisplay( title):
            t = Fig.text( 0.5, 0.95, title, va='center', ha='center')
            t.set_fontsize( sz)
    
    comment = _GQE.getComment()
    if comment is not None:
        if title is not None:
            if not _textIsOnDisplay( comment):
                t = Fig.text( 0.5, 0.90, comment, va='center', ha='center')
                t.set_fontsize( sz)
        else:
            if not _textIsOnDisplay( comment):
                t = Fig.text( 0.5, 0.95, comment, va='center', ha='center')
                t.set_fontsize( sz)
    return

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
    #print "graphics.display, nameList", nameList
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
    nDisplay = _GQE.getNumberOfScansToBeDisplayed( nameList)
    _setSizeGraphicsWindow( nDisplay)

    _adjustFigure( nDisplay)

    #
    # set scan.nrow, scan.ncol, scan.nplot
    #
    _utils._setScanVPs( nameList, flagDisplaySingle)

    _displayTitleComment()
    #
    # --- first pass: run through the scans in scanList and display 
    #     non-overlaid scans
    #
    for scan in scanList:
        #print "graphics.display", scan.name, "currentIndex", scan.currentIndex, "LastIndex", scan.lastIndex
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
                #print "graphics.display: creating plot for", scan.name, nrow, ncol, nplot
                scan.plotItem = _createPlotItem( scan)
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
                scan.plotDataItem, = scan.plotItem.plot_date( xDateMpl, 
                                                              scan.y[:(scan.currentIndex + 1)], 
                                                              xdate = True,
                                                              linestyle='solid', marker='None')
                plt.draw()
                if Canvas is not None:
                    Canvas.draw()
                scan.lastIndex = scan.currentIndex

            else:
                scan.plotDataItem, = scan.plotItem.plot( scan.x[:(scan.currentIndex + 1)], 
                                                         scan.y[:(scan.currentIndex + 1)], scan.color)
                scan.lastIndex = scan.currentIndex

        #
        # modify the scan 
        #
        scan.plotItem = scan.plotItem

        #
        # check, if there is something to display
        # 
        if scan.lastIndex == scan.currentIndex or \
           scan.currentIndex  == 0:
            continue

        if scan.doty:
            xDate = []
            for x in scan.x[:(scan.currentIndex + 1)]:
                xDate.append( _doty2datetime( x))
            xDateMpl = matplotlib.dates.date2num( xDate)
            scan.plotItem.plot_date( xDateMpl, scan.y, xdate = True, 
                                     linestyle='solid', marker='None')
        else:
            #print "graphics.display: plotting %s %d of %d" % \
            #    (scan.name, scan.currentIndex + 1, len( scan.x))
            scan.plotDataItem.set_data( scan.x[:(scan.currentIndex + 1)], 
                                        scan.y[:(scan.currentIndex + 1)])

            scan.plotItem.set_xlim( scan.x[0], scan.x[scan.currentIndex])
            scan.plotItem.set_ylim( _np.min( scan.y[:(scan.currentIndex + 1)]), 
                                _np.max( scan.y[:(scan.currentIndex + 1)]))
        #
        # keep track of what has already been displayed
        #
        scan.lastIndex = scan.currentIndex
    #
    # --- second pass: display overlaid scans
    #
    for scan in scanList:
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
        if scan.overlay is None:
            continue
        
        if len( nameList) > 0 and scan.name not in nameList:
            continue
        target = _GQE.getScan( scan.overlay)
        #
        # modify the overlaid scan 
        #
        scan.plotItem = target.plotItem.twinx()

        #print "display: overlaying %s to %s" % (scan.name, target.name)

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
    if Canvas is not None:
        Canvas.draw()
    return
