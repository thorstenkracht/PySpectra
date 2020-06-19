#!/usr/bin/env python
'''
'''
import numpy as np
import subprocess, signal, time, os, sys, math
#import matplotlib.pyplot as _plt
import PySpectra 
import PySpectra.definitions as definitions

def getNumberOfGqesToBeDisplayed( nameList): 
    '''
    return the number of scans to be displayed.
    Scans that are overlaid do not require extra space
    and are therefore not counted.
    '''
    if len( nameList) == 0:
        nOverlay = 0
        for gqe in PySpectra.getGqeList():
            if gqe.overlay is not None:
                nOverlay += 1
        nGqe = len( PySpectra.getGqeList()) - nOverlay
        if nGqe < 1:
            nGqe = 1
    else:
        nOverlay = 0
        for name in nameList:
            if PySpectra.getGqe( name).overlay is not None:
                nOverlay += 1
        nGqe = len( nameList) - nOverlay
        if nGqe < 1:
            nGqe = 1
    #print( "graphics.getNoOfGqesToBeDisplayed: nGqe %d" %(nGqe))
    return nGqe

def _getNumberOfOverlaid( nameList = None):
    '''
    returns the number of gqes which are overlaid to another, 
    used by e.g. graphics.display()
    '''
    count = 0
    for gqe in PySpectra.getGqeList():
        if nameList is not None: 
            if gqe.name not in nameList:
                continue
        if gqe.overlay is not None:
            count += 1

    return count

def colorSpectraToPysp( color): 
    '''
    this functions translates color numbers (a la Spectra) to strings a la Pysp
    '''
    #
    # 
    #
    if type(color) is not int: 
        return color

    if color == 1:
        color = 'black'
    elif color == 2:
        color = 'red'
    elif color == 3:
        color = 'green'
    elif color == 4:
        color = 'blue'
    elif color == 5:
        color = 'cyan'
    elif color == 6:
        color = 'yellow'
    elif color == 7:
        color = 'magenta'
    else: 
        color = 'black'

    return color

def colorPyspToSpectra( color): 
    '''
    this functions translates color names (a la PySpectra) to number (a la Spectra)
    '''
    #
    # 
    #
    if type(color) is int:
        return color

    if color == 'black':
        color = 1
    elif color == 'red':
        color = 2
    elif color == 'green':
        color = 3
    elif color == 'blue':
        color = 4
    elif color == 'cyan':
        color = 5
    elif color == 'yellow':
        color = 6
    elif color == 'magenta':
        color = 7
    else: 
        color = 1

    return color

def createScansByColumns( hsh):
    """
    called from zmqIfc.putData()
        hsh = { 'putData': {'columns': [{'data': x, 'name': 'xaxis'},
                                        {'data': tan, 'name': 'tan'},
                                        {'data': cos, 'name': 'cos'},
                                        {'data': sin, 'name': 'sin',
                                         'showGridY': False, 'symbolColor': 'blue', 'showGridX': False, 
                                         'yLog': False, 'symbol': '+', 
                                         'xLog': False, 'symbolSize':5}]}}
    """

    if len( hsh[ 'columns']) < 2: 
        raise Exception( "PySpectra.createScansByColumns", "less than 2 columns")

    if 'title' in hsh: 
        PySpectra.setTitle( hsh[ 'title'])

    if 'comment' in hsh: 
        PySpectra.setComment( hsh[ 'comment'])

    columns = []
    xcol = hsh[ 'columns'][0]
    for elm in hsh[ 'columns'][1:]:
        if 'name' not in elm:
            raise Exception( "PySpectra.createScansByColumns", "missing 'name'")
        if 'data' not in elm:
            raise Exception( "PySpectra.createScansByColumns", "missing 'data'")
        data = elm[ 'data']
        del elm[ 'data']
        if len( data) != len( xcol[ 'data']):
            raise Exception( "PySpectra.createScansByColumns", 
                             "column length differ %s: %d, %s: %d" % ( xcol[ 'name'], len( xcol[ 'data']),
                                                                       elm[ 'name'], len( data)))

        lineColor = 'red'
        if 'lineColor' in elm:
            lineColor = elm[ 'lineColor']
            del elm[ 'lineColor'] 
            symbolColor = 'NONE'
        elif 'symbolColor' not in elm:
            lineColor = 'red'
            symbolColor = 'NONE'
        else: 
            symbolColor= 'red'
            lineColor = 'NONE'
            if 'symbolColor' in elm:
                symbolColor = elm[ 'symbolColor']
                del elm[ 'symbolColor'] 

        lineWidth = 1
        if 'lineWidth' in elm:
            lineWidth = elm[ 'lineWidth']
            del elm[ 'lineWidth'] 
        lineStyle = 'SOLID'
        if 'lineStyle' in elm:
            lineStyle = elm[ 'lineStyle']
            del elm[ 'lineStyle'] 
        showGridX = False
        if 'showGridX' in elm:
            showGridX = elm[ 'showGridX']
            del elm[ 'showGridX'] 
        showGridY = False
        if 'showGridY' in elm:
            showGridY = elm[ 'showGridY']
            del elm[ 'showGridY'] 
        xLog = False
        if 'xLog' in elm:
            xLog = elm[ 'xLog']
            del elm[ 'xLog'] 
        yLog = False
        if 'yLog' in elm:
            yLog = elm[ 'yLog']
            del elm[ 'yLog'] 
        symbol = '+'
        if 'symbol' in elm:
            symbol = elm[ 'symbol']
            del elm[ 'symbol'] 
        symbolSize= 10
        if 'symbolSize' in elm:
            symbolSize = elm[ 'symbolSize']
            del elm[ 'symbolSize'] 

        name = elm['name']
        del elm[ 'name']

        if len( list( elm.keys())) > 0: 
            raise ValueError( "PySpectra.createScansByColumns: dct not empty %s" % repr( elm))

        scan = PySpectra.Scan( name = name, 
                     xMin = data[0], xMax = data[-1], nPts = len(data),
                     xLabel = xcol[ 'name'], yLabel = name,
                     lineColor = lineColor, lineWidth = lineWidth, lineStyle = lineStyle,
                     showGridX = showGridX, showGridY = showGridY, 
                     xLog = xLog, yLog = yLog, 
                     symbol = symbol, symbolColor = symbolColor, symbolSize = symbolSize, 
                )
        for i in range(len(data)):
            scan.setX( i, xcol[ 'data'][i])
            scan.setY( i, data[i])
    PySpectra.display()

    return "done"

def createScansByGqes( hsh):
    '''
    called from zmqIfc.putData()

         { 'putData': {'gqes': [ {'x': x, 'y': tan, 'name': 'tan'},
                                 {'x': x, 'y': cos, 'name': 'cos'},
                                 {'x': x, 'y': sin, 'name': 'sin', 
                                  'showGridY': False, 'symbolColor': 'blue', 'showGridX': True, 
                                  'yLog': False, 'symbol': '+', 
                                  'xLog': False, 'symbolSize':5}],
                       'title': 'a title', 
                       'comment': 'a comment'}}
           The data are sent as a list of dictionaries containg the x- and y-data and other
           parameters describing the Scans.
    '''
    flagAtFound = False
    flagOverlayFound = False
    gqes = []
    for elm in hsh[ 'gqes']:
        if 'name' not in elm:
            raise Exception( "PySpectra.createScansByGqes", "missing 'name'")
        if 'x' not in elm:
            raise Exception( "PySpectra.createScansByGqes", "missing 'x' for %s" % elm[ 'name'])
        if 'y' not in elm:
            raise Exception( "PySpectra.createScansByGqes", "missing 'y' for %s" % elm[ 'name'])
        if len( elm[ 'x']) != len( elm[ 'y']):
            raise Exception( "PySpectra.createScansByGqes", "%s, x and y have different length %d != %d" % \
                             (elm[ 'name'], len( elm[ 'x']), len( elm[ 'y'])))
        #at = '(1,1,1)'
        #if 'at' in elm:
        #    flagAtFound = True
        #    at = elm[ 'at']
        xLabel = 'x-axis'
        if 'xlabel' in elm:
            xLabel = elm[ 'xlabel']
        yLabel = 'y-axis'
        if 'ylabel' in elm:
            yLabel = elm[ 'ylabel']
        color = 'red'
        if 'color' in elm:
            color = elm[ 'color']
            color = _colorSpectraToPysp( color)


        lineColor = 'red'
        if 'lineColor' in elm:
            lineColor = elm[ 'lineColor']
            symbolColor = 'NONE'
        elif 'symbolColor' not in elm:
            lineColor = 'red'
            symbolColor = 'NONE'
        else: 
            symbolColor= 'red'
            lineColor = 'NONE'
            if 'symbolColor' in elm:
                symbolColor = elm[ 'symbolColor']

        lineWidth = 1
        if 'lineWidth' in elm:
            lineWidth = elm[ 'lineWidth']
        lineStyle = 'SOLID'
        if 'lineStyle' in elm:
            lineStyle = elm[ 'lineStyle']
        showGridX = False
        if 'showGridX' in elm:
            showGridX = elm[ 'showGridX']
        showGridY = False
        if 'showGridY' in elm:
            showGridY = elm[ 'showGridY']
        xLog = False
        if 'xLog' in elm:
            xLog = elm[ 'xLog']
        yLog = False
        if 'yLog' in elm:
            yLog = elm[ 'yLog']
        symbol = '+'
        if 'symbol' in elm:
            symbol = elm[ 'symbol']
        symbolSize= 10
        if 'symbolSize' in elm:
            symbolSize = elm[ 'symbolSize']
        
        x = elm[ 'x']
        y = elm[ 'y']
        gqe = PySpectra.Scan( name = elm[ 'name'],
                    xMin = x[0], xMax = x[-1], nPts = len(x),
                    xLabel = xLabel, yLabel = yLabel,
                    lineColor = lineColor, lineWidth = lineWidth, lineStyle = lineStyle,
                    showGridX = showGridX, showGridY = showGridY, 
                    xLog = xLog, yLog = yLog, 
                    symbol = symbol, symbolColor = symbolColor, symbolSize = symbolSize, 
                )
        for i in range(len(x)):
            gqe.setX( i, x[i])
            gqe.setY( i, y[i])


    PySpectra.display()

    return "done"

def createGauss( name = "gauss", xMin = -5, xMax = 5., nPts = 101, 
                 lineColor = 'red', x0 = 0., sigma = 1., amplitude = 1.):

    g = PySpectra.Scan( name = name, xMin = xMin, xMax = xMax, nPts = nPts, 
                  lineColor = lineColor)
    g.y = amplitude/(sigma*np.sqrt(2.*np.pi))*np.exp( -(g.y-x0)**2/(2.*sigma**2))

    g.yMin = yMin( g)
    g.yMax = yMax( g)

    return g

_lenPlotted = -1

def setGqeVPs( nameList, flagDisplaySingle, clsFunc):
    '''
    set the gqe viewport, we use the at = (2,3,2) syntax
    which is (nrow, ncol, nplot)
    title and comment are ignored here. they are taken 
    care of in createPlotItem()

    if a gqe has an 'at' field, like (2,2,3), these values
    have higher priority.

    clsFunc is specified to be able to distinguish between mpl and pqt
    '''
    global _lenPlotted
    debug = False

    gqeList = PySpectra.getGqeList()

    if debug:
        print( "\nutils.setGqeVPs.BEGIN: gqeList %s, nameList %s" % \
            ( repr(  [ gqe.name for gqe in gqeList]), repr(  nameList)))

    if len( nameList) == 0:
        #
        # the number of used viewports is (len( gqeList) - numberOfOverlaid) 
        #
        usedVPs = len( gqeList) - _getNumberOfOverlaid()
        if usedVPs != _lenPlotted and _lenPlotted != -1: 
            clsFunc()
        _lenPlotted = usedVPs
        if usedVPs == 0:
            return 
        if usedVPs == 1:
            ncol = 1
            nrow = 1
        elif usedVPs == 2:
            ncol = 1
            nrow = 2
        else:
            ncol = int( math.ceil( math.sqrt( usedVPs)))
            if usedVPs > definitions.MANY_GQES: 
                ncol -= 1
            nrow = int( math.ceil( (float(usedVPs))/float(ncol)))
        nplot = 1 
    elif len( nameList) == 1:
        if _lenPlotted != 1 and _lenPlotted != -1: 
            clsFunc()
        _lenPlotted = 1
        ncol = 1
        nrow = 1
        nplot = 1
    else:
        #
        # the number of used viewports is (len( nameList) - numberOfOverlaid( nameList)) 
        #
        usedVPs = len( nameList) - _getNumberOfOverlaid( nameList)
        if usedVPs != _lenPlotted and _lenPlotted != -1: 
            clsFunc()
        _lenPlotted = usedVPs
        if usedVPs == 0:
            return 
        if usedVPs == 1:
            ncol = 1
            nrow = 1
        elif usedVPs == 2:
            ncol = 1
            nrow = 2
        else:
            ncol = int( math.ceil( math.sqrt( usedVPs)))
            if usedVPs > definitions.MANY_GQES: 
                ncol -= 1
            nrow = int( math.ceil( (float(usedVPs))/float(ncol)))
        nplot = 1 

    if debug:
        print( "utils.setGqeVPs: after first pass: nrow %d, ncol %d nplot %d" % ( nrow, ncol, nplot))

    for gqe in gqeList:
        #
        # overlay? - don't create a viewport gqe.
        #
        if gqe.overlay is not None and not flagDisplaySingle:
            #
            # maybe the gqe.overlay has beed deleted
            #
            if PySpectra.getGqe( gqe.overlay) is None:
                gqe.overlay = None
            else:
                continue

        if len( nameList) > 0:
            if gqe.name not in nameList:
                continue

        if gqe.plotItem is None:
            if gqe.at is None:
                gqe.ncol = ncol
                gqe.nrow = nrow
                gqe.nplot = nplot
            else: 
                gqe.nrow = gqe.at[0]
                gqe.ncol = gqe.at[1]
                gqe.nplot = gqe.at[2]
            if gqe.nrow*gqe.ncol < gqe.nplot:
                raise ValueError( "utils.setGqeVPs: nrow %d * ncol %d < nplot %d, at %s" % \
                                  (gqe.nrow, gqe.ncol, gqe.nplot, gqe.at))
        nplot += 1
    #
    # see if 2 GQEs occupie the same cell
    #
    for first in gqeList: 
        if first.overlay:
            continue

        if len( nameList) > 0:
            if first.name not in nameList:
                continue

        for second in gqeList: 
            if second.overlay:
                continue

            if first.name == second.name: 
                continue

            if len( nameList) > 0:
                if second.name not in nameList:
                    continue
            if first.nrow == second.nrow and \
               first.ncol == second.ncol and \
               first.nplot == second.nplot:
                raise ValueError( "utils.setGqeVPs: %s and %s in the same cell row, col, nplot: %d %d %d, nameList %s" % \
                    (first.name, second.name, first.nrow, first.ncol, first.nplot, repr( nameList)))

    
    if debug:
        for gqe in gqeList: 
            if gqe.overlay is None:
                print( "utils.setGqeVPs.END: %s row, col, nplot: %d %d %d" % \
                    (gqe.name, gqe.nrow, gqe.ncol, gqe.nplot))
            else: 
                print( "utils.setGqeVPs.END: %s overlaid to %s" % \
                    (gqe.name, gqe.overlay))
    return 

#
# this function is copied from 
#  /home/kracht/Misc/Sardana/hasyutils/HasyUtils/OtherUtils.py
#
def assertProcessRunning(processName): 
    """
    returns ( True, False), if processName is running
    returns ( False, False), if the processName (the file) does not exist
    returns ( True, True), if processName was launched successfully
    returns ( False, False), if the launch failed

    example: 
      (status, wasLaunched) = HasyUtils.assertProcessRunning( '/usr/bin/pyspMonitor.py')

  """
    #
    # see, if the pyspMonitor process exists. Otherwise launch it
    #
    if findProcessByName( processName): 
        return (True, False)

    if not os.path.isfile( processName):
        print( "OtherUtils.assertProcessRunning: %s does not exist" % processName)
        return (False, False)
        
    if os.system( "%s &" % processName):
        print( "OtherUtils.assertProcessRunning: failed to launch %s" % processName)
        return (False, False)

    count = 0
    while 1: 
        count += 1
        if findProcessByName( processName): 
            #
            # we need some extra time. The process appears in
            # the process list but is not active
            #
            time.sleep( 3) 
            return (True, True)
        time.sleep( 0.1)
        if count > 15:
            print( "OtherUtils.assertProcessRunning: %s does not start in time " % processName)
            return ( False, False)

    return (True, True)
#
# I don't know whether the following function is really needed - 
# syntactical sugar perhaps
#
def assertPyspMonitorRunning(): 
    """
    returns (status, wasLaunched)
    """
    return assertProcessRunning( "/usr/bin/pyspMonitor.py")

#
# this function is copied from 
#  /home/kracht/Misc/Sardana/hasyutils/HasyUtils/OtherUtils.py
#
def findProcessByName( cmdLinePattern):
    """
    returns True, if the process list contains a command line
    containing the pattern specified

    cmdLinePattern, e.g.: 'pyspMonitor.py' 
      which matches ['python', '/usr/bin/pyspMonitor.py']

    """
    import psutil

    for p in psutil.process_iter():
        lst = p.cmdline()
        if len( lst) == 0:
            continue
        for elm in lst: 
            if elm.find( cmdLinePattern) != -1:
                return True
    return False


def killProcess( processName):
    p = subprocess.Popen(['ps', '-Af'], stdout=subprocess.PIPE)
    out, err = p.communicate()
    for line in out.splitlines():
        if processName in line:
            pid = int(line.split(None)[1])
            os.kill(pid, signal.SIGKILL)
    return 

def getHostname():
    '''Return the hostname, short form, e.g.: haspp08 '''
    import socket 
    return socket.gethostname()


def getHostnameLong():
    '''return the hostname, long form, e.g.: haspp08.desy.de '''
    # ('haso107tk.desy.de', ['haso107tk'], ['131.169.221.161'])
    import socket 
    return socket.gethostbyname_ex( socket.gethostname())[0]

def runMacro( line): 
    """
    send a command to the door and wait for completion
    """
    import PyTango
    import PySpectra.GQE as GQE
    import time

    print( "utils.runMacro: %s" % line)

    door = PySpectra.InfoBlock.getDoorProxy()
    if door is None:
        print( "utils.runMacro: no door")
        return False
    #
    # move the motors to good starting points
    #
    door.RunMacro( line.split( ' '))
    while door.state() == PyTango.DevState.RUNNING: 
        time.sleep( 0.1)

    if door.state() != PyTango.DevState.ON: 
        raise ValueError( "utils.runMacro: door state not ON, instead %s" % repr( door.state()))

    print( "utils.runMacro: %s, DONE" % line)

    return True

_initInkey = False
_initInkeyOldTermAttr = None

def _inkeyExitHandler(): 
    global _initInkey
    global _initInkeyOldTermAttr
    import termios as _termios

    if not _initInkey:
        return
    _initInkey = False
    _termios.tcsetattr( sys.stdin.fileno(), _termios.TCSADRAIN, _initInkeyOldTermAttr)
    return

def inkey( resetTerminal = None):
    '''
    Return the pressed key, nonblocking. Returns -1, if no key was pressed.

    while 1:
        ....
        if inkey() ==  32:  # space bar
            break

    Use
      inkey( True) 
    to reset the terminal characteristic explicitly. This has to be
    done in particular, if you use sys.exitfunc = yourExitHandler
    which overrides the inkey() exit handler
    '''
    global _initInkey
    global _initInkeyOldTermAttr
    import atexit as _atexit
    import termios as _termios

    if os.isatty( 1) == 0:
        return -1

    if resetTerminal and _initInkey:
        _initInkey = False
        _termios.tcsetattr( sys.stdin.fileno(), _termios.TCSADRAIN, _initInkeyOldTermAttr)
        return -1

    #
    # changing the terminal attributes takes quite some time,
    # therefore we cannot change them for every inkey() call
    #
    if not _initInkey:
        _initInkey = True
        _initInkeyOldTermAttr = _termios.tcgetattr( sys.stdin.fileno())
        new = _termios.tcgetattr( sys.stdin.fileno())
        new[3] = new[3] & ~_termios.ICANON & ~_termios.ECHO
        #
        # VMIN specifies the minimum number of characters to be read
        #
        new[6] [_termios.VMIN] = 0
        #
        # VTIME specifies how long the driver waits for VMIN characters.
        # the unit of VTIME is 0.1 s. 
        #
        new[6] [_termios.VTIME] = 1
        _termios.tcsetattr( sys.stdin.fileno(), _termios.TCSADRAIN, new)
        _atexit.register( _inkeyExitHandler)
	    
    key = sys.stdin.read(1)
    if( len( key) == 0):
        key = -1
    else:
        key = ord( key)

    return key

def launchGui(): 
    '''
    launches the Gui
    '''

    from PyQt4 import QtGui, QtCore

    import PySpectra.pySpectraGuiClass as _gui

    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication([])

    gui = _gui.pySpectraGui()
    gui.show()
    app.exec_()

    #sys.exit( app.exec_())

def prtc(): 
    sys.stdout.write( "Prtc ")
    sys.stdout.flush()
    sys.stdin.readline()

def xMax( scan):
    '''    
    return the maximum x-value of a scan, used to place text on the screen, 
    NDC coordinates
    '''
    if scan.autoscaleX:
        ret = max( scan.x[0], scan.x[ scan.currentIndex])
    else:
        ret = max( scan.xMin, scan.xMax)
    return ret

def xMin( scan):
    '''    
    return the minimum x-value of a scan, used to place text on the screen,
    NDC coordinates
    '''
    if scan.autoscaleX:
        ret = min( scan.x[0], scan.x[ scan.currentIndex])
    else:
        ret = min( scan.xMin, scan.xMax)
    return ret

def yMax( scan):
    '''    
    return the maximum y-value of a scan, used to place text on the screen, 
    NDC coordinates
    '''
    if scan.autoscaleY:
        if scan.currentIndex == 0:
            ret = scan.y[0]
        else:
            ret = np.max( scan.y[:scan.currentIndex + 1])
    else:
        ret = scan.yMax
    return ret

def yMin( scan):
    '''    
    return the minimum y-value of a scan, used to place text on the screen,
    NDC coordinates
    '''
    if scan.autoscaleY: 
        if scan.currentIndex == 0:
            ret = scan.y[0]
        else:
            ret = np.min( scan.y[:scan.currentIndex + 1])
    else:
        ret = scan.yMin
    return ret

