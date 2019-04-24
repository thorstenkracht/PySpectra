#!/usr/bin/env python

import matplotlib 
matplotlib.use( 'TkAgg')
import matplotlib.pyplot as plt

from PyQt4 import QtCore as _QtCore
from PyQt4 import QtGui as _QtGui

import time as _time
import os as _os
import math as _math
import numpy as _np
import PySpectra.dMgt.GQE as _GQE
import PySpectra.utils as _utils
import PySpectra.definitions as _defs
import PySpectra.pqtgrph.graphics as _pqt_graphics
import HasyUtils as _HasyUtils
import datetime as _datetime

Fig = None
Canvas = None
_QApp = None

def _initGraphic( figureIn = None, canvasIn = None):
    '''
    haso107d1: 1920 x 1200
    spectra: 640 x 450 def., A4:  680 x 471 
    '''
    global Fig, Canvas, _QApp

    if _QApp is None:
        _QApp = _QtGui.QApplication.instance()

    if figureIn is not None:
        Fig = figureIn
        Canvas = canvasIn
        return 

    plt.ion()
    #print "graphics._initGraphic"

    if not plt.get_fignums():
        Fig = plt.figure(1, figsize=(21./2.54, 14.85/2.54))
    else:
        Fig = plt.figure(1)
        Fig.clear()
    return

def createPDF( fileName = None): 
    '''
    create a PDF file, the default name is pyspOutput.pdf
    a version of the last output file is created
    '''
    flag = False
    if Fig is None:
        #_pqt_graphics.close()
        _initGraphic()
        display()
        flag = True

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

    print "mpl_graphics.createPDF: created", fileName

    if flag:
        close()
        #_pqt_graphics._initGraphic()
        
    return fileName
    
def _setSizeGraphicsWindow( nScan):
    '''
    '''
    if _GQE._getWsViewportFixed(): 
        return 

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
    _GQE._setWsViewportFixed( True)

    return 

def cls():
    '''
    clear screen: allow for a new plot
    '''
    #print "mpl_graphics.cls"

    if Fig is None: 
        _initGraphic()

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


def close(): 
    '''
    close the Figure, used by createPDF
    '''
    plt.close( 'all')
    Fig = None
    return 

def procEventsLoop():
    '''
    loops over QApp.processEvents until a <return> is entered
    '''
    print "\nPress <return> to continue ",
    while True:
        _time.sleep(0.01)
        processEvents()
        key = _HasyUtils.inkey()        
        if key == 10:
            break
    print ""

def processEvents(): 

    if Fig is None: 
        _initGraphic()

    plt.draw()
    if Canvas is not None:
        Canvas.draw()
    _QApp.processEvents()
    

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

def _setTitle( scan, nameList): 

    if scan.textOnly:
        return 
    #
    # the length of the title has to be limited. Otherwise pg 
    # screws up. The plots will no longer fit into the workstation viewport
    # and the following display command, even with less scans, will 
    # also not fit into the graphics window
    #
    lenMax = 20
    if len( _GQE.getScanList()) > 15: 
        lenMax = 17

    if len( scan.name) > lenMax:
        tempName = "X_" + scan.name[-lenMax:]
    else: 
        tempName = scan.name

    if _GQE._getNumberOfScansToBeDisplayed( nameList) < _defs._MANY_SCANS:
        scan.plotItem.set_title( tempName)
    else:
        scan.plotItem.text( 0.95, 0.8, tempName, transform = scan.plotItem.transAxes, va = 'center', ha = 'right')

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


def _addTexts( scan):
    #print "mpl_graphics.addTexts"
    for elm in scan.textList:
        #print "mpl_graphics.addTexts: %s, x %g, y %g" % (elm.text, elm.x, elm.y)
        scan.plotItem.text( elm.x, elm.y, elm.text, transform = scan.plotItem.transAxes, va = elm.vAlign, ha = elm.hAlign)

def _preparePlotParams( scan):
    '''
    this function prepares the parameters for a function call in display()
    '''
    hsh = {}
    if scan.symbolColor.upper() == "NONE":
        hsh[ 'linestyle'] = scan.lineStyle.lower()
        hsh[ 'linewidth'] = scan.lineWidth
        hsh[ 'color'] = scan.lineColor
    else: 
        if scan.lineColor.upper() == 'NONE': 
            hsh[ 'marker'] = scan.symbol
            hsh[ 'linewidth'] = 0.
            hsh[ 'markersize'] = scan.symbolSize
            hsh[ 'markeredgecolor'] = scan.symbolColor
            hsh[ 'markerfacecolor'] = scan.symbolColor
        else:
            hsh[ 'marker'] = scan.symbol
            hsh[ 'markersize'] = scan.symbolSize
            hsh[ 'markeredgecolor'] = scan.symbolColor
            hsh[ 'markerfacecolor'] = scan.symbolColor
            hsh[ 'color'] = scan.lineColor

    if scan.doty:
        hsh[ 'xdate'] = True

    return hsh

def _createPlotItem( scan, nameList):            
    '''
    create a plotItem, aka viewport (?) with title, axis descriptions and texts
    '''

    #print "mpl_graphics.createPlotItem: %s at nrow %d, ncol %d, nplot %d" % (scan.name, scan.nrow, scan.ncol, scan.nplot)

    try:
        scan.plotItem = Fig.add_subplot( scan.nrow, scan.ncol, scan.nplot)
        if scan.textOnly: 
            scan.plotItem.axis( 'off')
            scan.plotItem.set_xlim( [0., 1.])
            scan.plotItem.set_ylim( [0., 1.])
            _addTexts( scan)
            return 
            
    except Exception, e:
        print "graphics.createPlotItem: caught exception"
        print repr( e)
        raise ValueError( "graphics.createPlotItem, throwing exception")

    #print "mpl_graphics.createPlotItem, autorange", scan.autorangeX, scan.autorangeY

    #
    # log scale
    #
    if scan.xLog: 
        scan.plotItem.set_xscale( "log")
    if scan.yLog: 
        scan.plotItem.set_yscale( "log")

    #
    # autoscale
    #
    arX = scan.autorangeX
    arY = scan.autorangeY

    if scan.yMin is None or scan.yMax is None:
        arY = True

    scan.plotItem.set_autoscalex_on( arX)
    scan.plotItem.set_autoscaley_on( arY)

    if not arX:
        scan.plotItem.set_xlim( [scan.xMin, scan.xMax])
    if not arY:
        scan.plotItem.set_ylim( [scan.yMin, scan.yMax])

    if scan.showGridX or scan.showGridY:
        scan.plotItem.grid( True)
    else:
        scan.plotItem.grid( False)
    
    _setTitle( scan, nameList)

    if _GQE._getNumberOfScansToBeDisplayed( nameList) < _defs._MANY_SCANS:
        if hasattr( scan, 'xLabel'):
            scan.plotItem.set_xlabel( scan.xLabel)
        if hasattr( scan, 'yLabel'):
            scan.plotItem.set_ylabel( scan.yLabel)

    _addTexts( scan)

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
    #print "mpl_graphics.display, nameList", nameList
    if nameList is None:
        nameList = []

    if Fig is None: 
        _initGraphic()

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
    nDisplay = _GQE._getNumberOfScansToBeDisplayed( nameList)
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
        #
        # overlay? - don't create a plot for this scan. Plot it
        # in the second pass. But it is displayed, if it is the only 
        # scan or if it is the only scan mentioned in nameList
        #
        if scan.overlay is not None and not flagDisplaySingle:
            #
            # maybe the scan.overlay has beed deleted
            #
            if _GQE.getScan( scan.overlay) is None:
                scan.overlay = None
            else:
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
                _createPlotItem( scan, nameList)
            except ValueError, e:
                print "graphics.display: exception from createPlotItem"
                print "graphics.display: consider a 'cls'"
                print "graphics.display", repr( e)
                return 

            if scan.textOnly: 
                continue

            if scan.doty:
                xDate = []
                for x in scan.x[:(scan.currentIndex + 1)]:
                    xDate.append( _doty2datetime( x))
                xDateMpl = matplotlib.dates.date2num( xDate)
                hsh = _preparePlotParams( scan)
                scan.plotDataItem, = scan.plotItem.plot_date( xDateMpl, 
                                                              scan.y[:(scan.currentIndex + 1)], 
                                                              **hsh)
            #
            # not doty
            #
            else:
                hsh = _preparePlotParams( scan)
                scan.plotDataItem, = scan.plotItem.plot( scan.x[:(scan.currentIndex + 1)], 
                                                         scan.y[:(scan.currentIndex + 1)], 
                                                         **hsh) 
            scan.lastIndex = scan.currentIndex

        if scan.textOnly: 
            continue
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
            scan.plotItem.plot_date( xDateMpl, scan.y)
        else:
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

        if scan.overlay is None:
            continue
        #
        # check, if theren is something to display
        #
        if scan.lastIndex == scan.currentIndex:
            continue
        
        if len( nameList) > 0 and scan.name not in nameList:
            continue
        target = _GQE.getScan( scan.overlay)
        if target is None or target.plotItem is None:
            raise ValueError( "mpl_graphics.display: %s tries to overlay to %s" %
                              (scan.name, scan.overlay))
        #
        # instantiate a second axes that shares the same x-axis 
        #
        scan.plotItem = target.plotItem.twinx()
        
        if len( _GQE._scanList) >= _defs._MANY_SCANS:
            plt.setp( scan.plotItem.get_yticklabels(), visible=False)

        hsh = _preparePlotParams( scan)
        scan.plotDataItem, = scan.plotItem.plot( scan.x[:(scan.currentIndex + 1)], 
                                                 scan.y[:(scan.currentIndex + 1)], 
                                                 **hsh)

        scan.plotItem.relim()
        scan.plotItem.autoscale_view( True, True, True)

        scan.lastIndex = scan.currentIndex
        #if scan.yMin is None:
        #    scan.plotItem.set_autoscale_on( True)
        #else:
        #    scan.plotItem.set_ylim( scan.yMin, scan.yMax)
        scan.plotItem.set_xlim( scan.xMin, scan.xMax)

    plt.draw()
    if Canvas is not None:
        Canvas.draw()
    return
