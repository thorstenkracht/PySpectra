#!/usr/bin/env python
#
import matplotlib 
matplotlib.use( 'TkAgg')
import matplotlib.pyplot as plt

from PyQt4 import QtCore, QtGui

import time as _time
import os, sys
import numpy
import datetime 
import PySpectra 
import PySpectra.utils as utils
import PySpectra.definitions as definitions

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

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
        _QApp = QtGui.QApplication.instance()
        if _QApp is None:
            _QApp = QtGui.QApplication([])

    if figureIn is not None:
        Fig = figureIn
        Canvas = canvasIn
        return 

    plt.ion()

    if not plt.get_fignums():
        Fig = plt.figure(1, figsize=(21./2.54, 14.85/2.54))
        Fig.canvas.set_window_title( "pySpectra Application (MPL)")
    else:
        Fig = plt.figure(1)
        Fig.clear()

    return

def createPDF( printer = None, fileName = None, flagPrint = False, format = 'DINA4'): 
    '''
    - create a PDF file, the default name is pyspOutput.pdf
    - a version of the last output file is created
    - if flagPrint is True, the file is sent to the PRINTER 
    - returns the name of the output file
    '''

    gqeList = PySpectra.getGqeList()
    if len( gqeList) == 0:
        return None

    flag = False
    if Fig is None:
        _initGraphic()
        flag = True

    setWsViewport( format)
    
    cls()
    display()

    if fileName is None:
        fileName = "pyspOutput.pdf"

    if fileName.find( '.pdf') == -1:
        fileName += ".pdf"
 
    if os.path.exists( "/usr/local/bin/vrsn"):
        if os.system( "/usr/local/bin/vrsn -s -nolog %s" % fileName):
            print( "graphics.createPDF: failed to save the current version of %s" % fileName)
    
    try:
        # 
        # the bbox_inches='tight' does not look good,
        # if there is only one plot on the paper
        # 
        #Fig.savefig( fileName, bbox_inches='tight')
        Fig.savefig( fileName)
    except Exception as e:
        print( "graphics.createPDF: failed to create %s" % fileName)
        print( repr( e))
        return None

    if flag:
        cls()
        close()

    if flagPrint: 
        if printer is None:
            printer = os.getenv( "PRINTER")
            if printer is None: 
                raise ValueError( "mpl_graphics.createPDF: environment variable PRINTER not defined")
        if os.system( "/usr/bin/lpr -P %s %s" % (printer, fileName)):
            print( "mpl_graphics.createPDF: failed to print %s on %s" % (fileName, printer))
        else:
            pass
            # 
            # it is not clear whether we should print a message here or in the application
            # 
            # print( "createPDF: printed %s on %s" % (fileName, printer))
        
    return fileName


def configGraphics(): 
    '''
    used for pyqtgraphics
    '''
    return 
    
def _setSizeGraphicsWindow( nScan):
    '''
    '''
    if PySpectra.getWsViewportFixed(): 
        return 

    if nScan > 9:
        w = 29.7
    elif nScan > 4: 
        w = 21
    else: 
        w = 14.85

    h = w/1.414
    #print( "mpl_graphics.setSizeGraphicsWindow %g %g %s %s " % (w/2.54, h/2.54, repr( Fig.get_figwidth()), repr( Fig.get_figheight()))

    if w/2.54 > (Fig.get_figwidth() + 0.1) or h/2.54 > (Fig.get_figheight() + 0.1): 
        if w > 29.6:
            setWsViewport( "DINA4")
        else:
            setWsViewport( "DINA5")
    return 

def setWsViewport( size = None):
    '''
    size: DINA4, DINA4P, DINA4S, DINA5, DINA5P, DINA5S, DINA6, DINA6L, DINA6S
    '''

    if size is None:
        return 

    if Fig is None: 
        _initGraphic()

    if size.upper() == "DINA4" or size.upper() == "DINA4L": 
        w = 29.7
        h = 21
    elif size.upper() == "DINA4P": 
        w = 21
        h = 29.7
    elif size.upper() == "DINA4S": 
        w = 29.7
        h = 29.7
    elif size.upper() == "DINA5" or size.upper() == "DINA5L": 
        w = 21
        h = 14.85
    elif size.upper() == "DINA5P": 
        w = 14.85
        h = 21.0
    elif size.upper() == "DINA5S": 
        w = 21.0
        h = 21.0
    elif size.upper() == "DINA6" or size.upper() == "DINA6L": 
        w = 14.85
        h = 10.5
    elif size.upper() == "DINA6P": 
        w = 10.5
        h = 14.85
    elif size.upper() == "DINA6S": 
        w = 14.85
        h = 14.85
    else:
        raise ValueError( "graphics.setWsViewport: no valid size, %s" % size)

    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches( w/2.54, h/2.54, forward = True)
    PySpectra.setWsViewportFixed( True)

    return 

def cls():
    '''
    clear screen: allow for a new plot
    '''
    #print( "mpl_graphics.cls")

    if Fig is None: 
        _initGraphic()

    Fig.clear()
    Fig.canvas.flush_events()
    #plt.draw()
    if Canvas is not None:
        try:
            Canvas.draw()
        except Exception as e:
            print( "mpl_graphics.cls: caught exception from Canvas.draw")
            print( repr( e))
    #
    # clear the plotItems
    #
    gqeList = PySpectra.getGqeList()

    for scan in gqeList:
        scan.plotItem = None
        if type( scan) == PySpectra.Scan:
            scan.plotDataItem = None
            scan.lastIndex = 0

def clear( scan): 
    '''
    the clear() is executed here to ensure that Fig is still alive
    '''
    if Fig is None: 
        return 

    scan.plotItem.clear()
    return 

def close(): 
    '''
    close the Figure, used by createPDF
    '''
    global Fig
    plt.close( 'all')
    Fig = None
    return 

def processEventsLoop( timeOut = None):
    '''
    loops over QApp.processEvents until a <return> is entered
    '''
    if timeOut is None:
        sys.stdout.write( "\nPress <return> to continue ")
        sys.stdout.flush()
    startTime = _time.time()
    while True:
        _time.sleep(0.001)
        processEvents()
        if timeOut is not None:
            if (_time.time() - startTime) > timeOut: 
                break
        #
        # :99.0 is the DISPLAY in travis
        #
        if os.getenv( "DISPLAY") == ":99.0": 
            break
        key = utils.inkey()        
        if key == 10:
            break

    if timeOut is None:
        print( "")

def processEvents(): 

    if Fig is None: 
        _initGraphic()

    Fig.canvas.flush_events()
    #plt.pause( 0.001)
    # draw()
    if Canvas is not None:
        Canvas.draw()
    _QApp.processEvents()
    

def listGraphicsItems(): 
    print( "mtpltlb.graphics.listGraphicsItems")
    return

def _doty2datetime(doty, year = None):
    """
    Convert the fractional day-of-the-year to a datetime structure.
    The default year is the current year.

    Example: 
      a = doty2datetime( 28.12)
      m = [ 'Jan', 'Feb', 'Mar', 'Aptr', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
      print( "%s %d, %02d:%02d" % (m[ a.month - 1], a.day, a.hour, a.minute))
      --> Jan 29, 02:52
    """
    if year is None:
        now = datetime.datetime.now()
        year = now.year
    dotySeconds = doty*24.*60.*60
    boy = datetime.datetime(year, 1, 1)
    tmp = boy + datetime.timedelta(seconds=dotySeconds)
    #
    # doty2datatime doty -5.0 to datetime.datetime(2018, 12, 27, 0, 0)
    # doty2datatime doty 4.8 to datetime.datetime(2019, 1, 5, 19, 12)
    # doty2datatime doty 5.0 to datetime.datetime(2019, 1, 6, 0, 0)
    #
    #print( "doty2datatime doty %g to %s " % (doty, repr( tmp)))
    return tmp

def _setTitle( gqe, nameList): 

    if type( gqe) == PySpectra.Scan and gqe.textOnly:
        return 
    #
    # the length of the title has to be limited. Otherwise pg 
    # screws up. The plots will no longer fit into the workstation viewport
    # and the following display command, even with less gqes, will 
    # also not fit into the graphics window
    #
    if len( gqe.name) > definitions.LEN_MAX_TITLE:
        tempName = "X_" + gqe.name[-definitions.LEN_MAX_TITLE:]
    else: 
        tempName = gqe.name

    #fontSize = PySpectra.getFontSize( nameList)
 
    if utils.getNumberOfGqesToBeDisplayed( nameList) < definitions.MANY_GQES:
        gqe.plotItem.set_title( tempName)
        #scan.plotItem.set_title( tempName, fontsize = fontSize)
    else:
        gqe.plotItem.text( 0.95, 0.8, tempName, 
                            transform = gqe.plotItem.transAxes, 
                            va = 'center', ha = 'right')
                            #fontsize = fontSize)
  
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

    if PySpectra.getTitle() is not None:
        top -= 0.05
    if PySpectra.getComment() is not None:
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

def _displayTitleComment( nameList):     
    '''
    '''
    #fontSize = PySpectra.getFontSize( nameList)

    title = PySpectra.getTitle()
    if title is not None:
        if not _textIsOnDisplay( title):
            t = Fig.text( 0.5, 0.95, title, va='center', ha='center')
            #t.set_fontsize( fontSize)
    
    comment = PySpectra.getComment()
    if comment is not None:
        if title is not None:
            if not _textIsOnDisplay( comment):
                t = Fig.text( 0.5, 0.90, comment, va='center', ha='center')
                #t.set_fontsize( fontSize)
        else:
            if not _textIsOnDisplay( comment):
                t = Fig.text( 0.5, 0.95, comment, va='center', ha='center')
                #t.set_fontsize( sz)
    return


def _addTexts( scan, nameList):
    #print( "mpl_graphics.addTexts")

    #fontSize = PySpectra.getFontSize( nameList)

    if type( scan) != PySpectra.Scan:
        return 

    for elm in scan.textList:

        #if elm.fontSize is None:
        #    sz = fontSize
        #else:
        #    sz = elm.fontSize

        scan.plotItem.text( elm.x, elm.y, elm.text, 
                            transform = scan.plotItem.transAxes, 
                            va = elm.vAlign, ha = elm.hAlign, 
                            # fontsize = sz, 
                            color = elm.color
                        )

def _preparePlotParams( scan):
    '''
    this function prepares the parameters for a function call in display()
    '''
    hsh = {}
    if scan.symbolColor.upper() == "NONE":
        hsh[ 'linestyle'] = scan.lineStyle.lower()
        hsh[ 'linewidth'] = scan.lineWidth
        hsh[ 'color'] = scan.lineColor
        hsh[ 'marker'] = None
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

    #if scan.doty:
    #    hsh[ 'xdate'] = True

    return hsh

def _createPlotItem( scan, nameList):            
    '''
    create a plotItem, aka viewport (?) with title, axis descriptions and texts
    '''

    #print( "mpl_graphics.createPlotItem: %s at nrow %d, ncol %d, nplot %d" % (scan.name, scan.nrow, scan.ncol, scan.nplot))

    try:
        scan.plotItem = Fig.add_subplot( scan.nrow, scan.ncol, scan.nplot)
        if type( scan) == PySpectra.Scan and scan.textOnly: 
            scan.plotItem.axis( 'off')
            _addTexts( scan, nameList)
            return 
    except Exception as e:
        print( "graphics.createPlotItem: caught exception")
        print( repr( e))
        raise ValueError( "graphics.createPlotItem, throwing exception")

    #print( "mpl_graphics.createPlotItem, autoscale %s %s " % ( repr( scan.autoscaleX), repr( scan.autoscaleY)))

    if type( scan) == PySpectra.Scan: 
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
        arX = scan.autoscaleX
        arY = scan.autoscaleY

        if scan.yMin is None or scan.yMax is None:
            arY = True

        if scan.doty: 
            pass
        #scan.plotItem.set_autoscalex_on( True)

        if not arX: 
            if not scan.doty: 
                scan.plotItem.set_xlim( scan.xMin, scan.xMax)
        else: 
            pass
        #scan.plotItem.set_autoscalex_on( arX)

        if not arY:
            if scan.yMin == scan.yMax:
                scan.plotItem.set_ylim( [scan.yMin - 1., scan.yMax + 1])
            else:
                scan.plotItem.set_ylim( [scan.yMin, scan.yMax])
        else:
            pass
        #scan.plotItem.set_autoscaley_on( arY)
        #
        # grid
        #
        if scan.showGridX or scan.showGridY:
            scan.plotItem.grid( True)
        else:
            scan.plotItem.grid( False)
    
    _setTitle( scan, nameList)

    if utils.getNumberOfGqesToBeDisplayed( nameList) < definitions.MANY_GQES:
        if hasattr( scan, 'xLabel') and scan.xLabel is not None:
            scan.plotItem.set_xlabel( scan.xLabel)
        if hasattr( scan, 'yLabel') and scan.yLabel is not None:
            scan.plotItem.set_ylabel( scan.yLabel)

    _addTexts( scan, nameList)

    return

def _displayImages( nameList): 
    '''
    '''
    gqeList = PySpectra.getGqeList()
    for image in gqeList:
        if type( image) != PySpectra.Image: 
            continue
        if len( nameList) > 0: 
            if image.name not in nameList:
                continue
        _createPlotItem( image, nameList)
        if image.log: 
            try: 
                image.img = image.plotItem.imshow( numpy.rot90( numpy.flipud( numpy.log( image.data)), k = 3), 
                                                   origin = 'lower',
                                                   cmap=plt.get_cmap( image.colorMap))
            except Exception as e: 
                image.log = False
                print( "mpl_graphics: log failed")
                print( repr( e))
                return 
            
        else:
            if image.modulo != -1:
                image.img = image.plotItem.imshow( numpy.rot90( numpy.flipud( image.data % image.modulo), k = 3), 
                                                   origin = 'lower',
                                                   cmap=plt.get_cmap( image.colorMap))
            else: 
                image.img = image.plotItem.imshow( numpy.rot90( numpy.flipud( image.data), k = 3), 
                                                   origin = 'lower',
                                                   cmap=plt.get_cmap( image.colorMap))
        
        axes = image.plotItem.axes
        Fig.canvas.draw()
        labels = [item.get_text() for item in axes.get_xticklabels()]
        labelsNew = []
        for l in labels: 
            if len( l) == 0:
                labelsNew.append( '')
                continue
            x = float( l)/float( image.width)*( image.xMax - image.xMin) + image.xMin
            labelsNew.append( '%g' % x)
        axes.set_xticklabels( labelsNew)
        labels = [item.get_text() for item in axes.get_yticklabels()]
        labelsNew = []
        for l in labels: 
            if len( l) == 0:
                labelsNew.append( '')
                continue
            #
            # 14.1.2020
            #   int( l) replaces by float( l)
            #   problem was int( '0.0') caused an error
            #
            y = float( l)/float( image.height)*( image.yMax - image.yMin) + image.yMin
            labelsNew.append( '%g' % y)
        axes.set_yticklabels( labelsNew)
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
    #print( "mpl_graphics.display, nameList %s" % repr( nameList))
    if nameList is None:
        nameList = []

    if Fig is None: 
        _initGraphic()

    #
    # Do not put a cls() here because it takes a lot of time, especially when
    # fast displays are done. 
    # Try /home/kracht/Misc/pySpectra/test/testGQE.py testFillData

    #
    # see if the members of nameList arr in the gqeList
    #
    for nm in nameList:
        if PySpectra.getGqe( nm) is None:
            raise ValueError( "graphics.display: %s is not in the gqeList" % nm)

    gqeList = PySpectra.getGqeList()
    #
    # if there is only one scan to be displayed, there is no overlay
    #
    flagDisplaySingle = False
    if len( nameList) == 1 or len( gqeList) == 1:
        flagDisplaySingle = True

    #
    # adjust the graphics window to the number of displayed scans
    #
    nDisplay = utils.getNumberOfGqesToBeDisplayed( nameList)
    _setSizeGraphicsWindow( nDisplay)

    _adjustFigure( nDisplay)

    #
    # set scan.nrow, scan.ncol, scan.nplot
    #
    utils.setGqeVPs( nameList, flagDisplaySingle, cls)

    _displayTitleComment( nameList)

    _displayImages( nameList)
    #
    # --- first pass: run through the scans in gqeList and display 
    #     non-overlaid scans
    #
    for scan in gqeList:
        
        if type(scan) != PySpectra.Scan:
            continue

        #
        # overlay? - don't create a plot for this scan. Plot it
        # in the second pass. But it is displayed, if it is the only 
        # scan or if it is the only scan mentioned in nameList
        #
        if scan.overlay is not None and not flagDisplaySingle:
            #
            # maybe the scan.overlay has beed deleted
            #
            if PySpectra.getGqe( scan.overlay) is None:
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
                #print( "graphics.display: creating plot for %s" % scan.name)
                _createPlotItem( scan, nameList)
            except ValueError as e:
                print( "graphics.display: exception from createPlotItem")
                print( "graphics.display: consider a 'cls'")
                print( "graphics.display %s" % repr( e))
                return 

            if type( scan) == PySpectra.Scan and scan.textOnly: 
                continue

            if scan.doty:
                xDate = []
                #
                # [  0.01 ,   1.009,   2.008,   3.007,   4.006,   5.005,   6.004,
                #    7.003,   8.002,   9.001,  10.   ]
                # -> 
                #  [ 737060.01 ,  737061.009,  737062.008,  737063.007,  737064.006,
                # 737065.005,  737066.004,  737067.003,  737068.002,  737069.001, 737070.]
                #
                for x in scan.x[:(scan.currentIndex + 1)]:
                    xDate.append( _doty2datetime( x))
                xDateMpl = matplotlib.dates.date2num( xDate)
                scan.xDateMpl = xDateMpl[:]
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
            #
            # setData is the function name in pyqtgraph
            #
            scan.plotDataItem.setData = scan.plotDataItem.set_data
            scan.lastIndex = scan.currentIndex

        if type( scan) == PySpectra.Scan and scan.textOnly: 
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
            #print( "mpl_display, currentIndex %s, lastIndex %s, continue" % (scan.currentIndex, scan.lastIndex))
            continue

        if scan.doty:
            pass
            #xDate = []
            #for x in scan.x[:(scan.currentIndex + 1)]:
            #    xDate.append( _doty2datetime( x))
            #xDateMpl = matplotlib.dates.date2num( xDate)
            #scan.plotItem.plot_date( xDateMpl, scan.y)
        else:
            scan.plotDataItem.set_data( scan.x[:(scan.currentIndex + 1)], 
                                        scan.y[:(scan.currentIndex + 1)])
            #
            #  9.7.2019: setting x-limits of the scan
            #    - for aligning motors the x-axis should be auto-ranged, 
            #      in both directions
            #    - for scans the x-axis should be fully visible from the beginning
            #
            if scan.autoscaleX:
                scan.plotItem.set_xlim( min( scan.x[0], scan.x[scan.currentIndex]), 
                                        max( scan.x[0], scan.x[scan.currentIndex]))
            scan.plotItem.set_ylim( numpy.min( scan.y[:(scan.currentIndex + 1)]), 
                                    numpy.max( scan.y[:(scan.currentIndex + 1)]))
        #
        # keep track of what has already been displayed
        #
        scan.lastIndex = scan.currentIndex

    #
    # --- 
    # --- second pass: display overlaid scans
    # --- 
    #
    for scan in gqeList:
        
        if type(scan) != PySpectra.Scan:
            continue
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
        target = PySpectra.getGqe( scan.overlay)
        if target is None or target.plotItem is None:
            raise ValueError( "mpl_graphics.display: %s tries to overlay to %s" %
                              (scan.name, scan.overlay))
        #
        # instantiate a second axes that shares the same x-axis 
        #
        scan.plotItem = target.plotItem.twinx()

        if scan.xLog: 
            scan.plotItem.set_xscale( "log")
        if scan.yLog: 
            scan.plotItem.set_yscale( "log")
        
        if len( PySpectra.getGqeList()) >= definitions.MANY_GQES or \
           scan.yTicksVisible == False: 
            plt.setp( scan.plotItem.get_yticklabels(), visible=False)

        hsh = _preparePlotParams( scan)

        #
        # follow the target scan as far as the axes are concerned
        #
        if target.doty:
            scan.plotItem.plot_date( target.xDateMpl, scan.y, **hsh)
        else:
            scan.plotItem.plot( scan.x[:(scan.currentIndex + 1)], 
                                scan.y[:(scan.currentIndex + 1)], 
                                **hsh)

        scan.lastIndex = scan.currentIndex
        if scan.autoscaleY:
            scan.plotItem.set_autoscaley_on( True)
        else:
            scan.plotItem.set_ylim( scan.yMin, scan.yMax)

        if scan.useTargetWindow:
            if target.autoscaleY:
                (mi, ma) = target.plotItem.get_ylim()
                scan.plotItem.set_ylim( mi, ma)
            else: 
                scan.plotItem.set_ylim( target.yMin, target.yMax)

        if not scan.doty:
            if scan.autoscaleX:
                scan.plotItem.set_autoscalex_on( True)
            else:
                scan.plotItem.set_xlim( scan.xMin, scan.xMax)

    #
    # draw() is non-blocking
    #
    #plt.draw()
    Fig.canvas.flush_events()
    #plt.pause( 0.001)
    if Canvas is not None:
        try:
            Canvas.draw()
        except Exception as e:
            print( "mpl_graphics.display: caught exception from Canvas.draw")
            print( repr( e))
    return
