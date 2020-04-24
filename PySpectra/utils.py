#!/usr/bin/env python
'''
'''
import numpy as np
import math as _math
import sys as _sys
import os as _os
import time as _time
#import matplotlib.pyplot as _plt
import PySpectra 
import PySpectra.definitions as _definitions


def createGauss( name = "gauss", xMin = -5, xMax = 5., nPts = 101, 
                 lineColor = 'red', x0 = 0., sigma = 1., amplitude = 1.):
    import PySpectra.GQE as GQE

    g = GQE.Scan( name = name, xMin = xMin, xMax = xMax, nPts = nPts, 
                  lineColor = lineColor)
    g.y = amplitude/(sigma*np.sqrt(2.*np.pi))*np.exp( -(g.y-x0)**2/(2.*sigma**2))

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
    import PySpectra.GQE as _gqe
    global _lenPlotted
    debug = False

    gqeList = _gqe.getGqeList()

    if debug:
        print( "utils.setGqeVPs.BEGIN: gqeList %s, nameList %s" % \
            ( repr(  [ gqe.name for gqe in gqeList]), repr(  nameList)))

    if len( nameList) == 0:
        #
        # the number of used viewports is (len( gqeList) - numberOfOverlaid) 
        #
        usedVPs = len( gqeList) - _gqe._getNumberOfOverlaid()
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
            ncol = int( _math.ceil( _math.sqrt( usedVPs)))
            if usedVPs > _definitions.MANY_GQES: 
                ncol -= 1
            nrow = int( _math.ceil( (float(usedVPs))/float(ncol)))
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
        usedVPs = len( nameList) - _gqe._getNumberOfOverlaid( nameList)
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
            ncol = int( _math.ceil( _math.sqrt( usedVPs)))
            if usedVPs > _definitions.MANY_GQES: 
                ncol -= 1
            nrow = int( _math.ceil( (float(usedVPs))/float(ncol)))
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
            if _gqe.getGqe( gqe.overlay) is None:
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
                raise ValueError( "utils.setGqeVPs: nrow %d * ncol %d < nplot %d, atr %s" % \
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

    if not _os.path.isfile( processName):
        print( "OtherUtils.assertProcessRunning: %s does not exist" % processName)
        return (False, False)
        
    if _os.system( "%s &" % processName):
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
            _time.sleep( 3) 
            return (True, True)
        _time.sleep( 0.1)
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

    door = GQE.InfoBlock.getDoorProxy()
    if door is None:
        print( "utils.runMacro: no door")
        return False
    #
    # move the motors to good starting points
    #
    door.RunMacro( line.split( ' '))
    while door.state() == PyTango.DevState.RUNNING: 
        time.sleep( 0.1)

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
    _termios.tcsetattr( _sys.stdin.fileno(), _termios.TCSADRAIN, _initInkeyOldTermAttr)
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

    if _os.isatty( 1) == 0:
        return -1

    if resetTerminal and _initInkey:
        _initInkey = False
        _termios.tcsetattr( _sys.stdin.fileno(), _termios.TCSADRAIN, _initInkeyOldTermAttr)
        return -1

    #
    # changing the terminal attributes takes quite some time,
    # therefore we cannot change them for every inkey() call
    #
    if not _initInkey:
        _initInkey = True
        _initInkeyOldTermAttr = _termios.tcgetattr( _sys.stdin.fileno())
        new = _termios.tcgetattr( _sys.stdin.fileno())
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
        _termios.tcsetattr( _sys.stdin.fileno(), _termios.TCSADRAIN, new)
        _atexit.register( _inkeyExitHandler)
	    
    key = _sys.stdin.read(1)
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

    #_sys.exit( app.exec_())

def prtc(): 
    _sys.stdout.write( "Prtc ")
    _sys.stdout.flush()
    _sys.stdin.readline()

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

