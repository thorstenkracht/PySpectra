#!/usr/bin/env python
'''
ssa() - simple scan analysis function 
        code also in 
        /home/kracht/Misc/Sardana/hasyutils/HasyUtils/ssa.py
'''
import numpy as _np
import PySpectra.dMgt.GQE as _GQE
import math as _math
import PySpectra as _pysp
import PySpectra.definitions as _defs
import sys as _sys

def ssa( xIn, yIn, flagNbs = False, stbr = 3):
    '''
    performs a simple scan analysis
    input: 
      xIn, yIn, numpy arrays
      flagNbs,  if True, no background subtraction
      stbr,     signal to background ratio
    returns: 
      dct['status']
      dct['reason']   0: ok, 1: np < 6, 2: stbr, 3: no y(i) > 0., 
                      4, 5: midpoint calc, 6: max outside x-range
                      7: not numpy array
      dct['cms']      center of mass
      dct['integral'] 
      dct['midpoint'] midpoint
      dct['fwhm'] 
      dct['peak_x'] 
      dct['peak_y']
      dct['back_int'] background integral
      dct['r_back']   right background
      dct['l_back']   left background

    '''
    status = 1
    reason = 0
    dct = {}

    dct['status'] = status
    dct['reason'] = reason
    dct['cms'] = 0
    dct['integral'] = 0
    dct['midpoint'] = 0
    dct['fwhm'] = 0
    dct['peak_x'] = 0
    dct['peak_y'] = 0
    dct['back_int'] = 0
    dct['r_back'] = 0
    dct['l_back'] = 0

    if( type( xIn).__name__ != 'ndarray' or type( yIn).__name__ != 'ndarray'): 
        dct['status'] = 0
        dct['reason'] = 7
        return dct
        
    if( xIn[-1] > xIn[0]):
        x = _np.copy( xIn)
        y = _np.copy( yIn)
    else:
        x = _np.copy( xIn)
        y = _np.copy( yIn)
        #
        # revert a numpy array
        #
        x = x[::-1]
        y = y[::-1]

    if len(x) < 6:
        dct['status'] = 0
        dct['reason'] = 1
        return dct

    b_back = 0
    a_back = 0
    n = len(x)
    y_max = y.max()
    if not flagNbs:
        n_back = len(x)/10
        if n_back < 2:
            n_back = 2
        if n_back > 20:
            n_back = 20

        x_sum  = 0.0 
        xx_sum = 0.0 
        xy_sum = 0.0   
        y_sum  = 0.0  
  
        for i in range( n_back):
            x_sum = x_sum + x[i] + x[n - 1 - i]
            xx_sum = xx_sum + x[i]*x[i] + x[n - 1 - i]*x[n - 1 - i]
            xy_sum = xy_sum + x[i]*y[i] + x[n - 1 - i]*y[n - 1 - i]
            y_sum = y_sum + y[i] + y[ n - 1 - i]      

        if (2.0*n_back*xx_sum-x_sum*x_sum) != 0.:
            b_back = (y_sum*xx_sum-xy_sum*x_sum)/(2.0*n_back*xx_sum-x_sum*x_sum)
            a_back = (2.0*n_back*xy_sum-y_sum*x_sum)/(2.0*n_back*xx_sum-x_sum*x_sum)
  
    back_int = (0.5*a_back*(x[n - 1]+x[0])+b_back)*(x[n - 1]-x[0])
    l_back = a_back*x[0]      + b_back
    r_back = a_back*x[n - 1]   + b_back  

    #
    #    the maximum has to exceed the background by a factor of stbr
    #
    if( stbr*r_back > y_max or stbr*l_back > y_max):
        dct['status'] = 0
        dct['reason'] = 2
        return dct

    #
    # BACKGROUND 
    #
    for i in range( n):
        y[i] = y[i] - a_back*x[i] - b_back

    #
    # FIND PEAK POSITION, PEAK INTENSITY AND PEAK INDEX                        
    #
  
    peak_x     = 0.0
    peak_y     = 0.0
    peak_index = 0
  
    flag = 0
    for i in range( n):
        if (y[i] > peak_y):
            peak_y = y[i]
            peak_x = x[i]
            peak_index = i
            flag = 1
  
    if flag == 0:
        dct['status'] = 0
        dct['reason'] = 3 # no y > 0
        return dct

    #
    # DETERMINE FWHM AND MIDPOINT                                                */
    #
    x_left  = 0.0
    x_right = 0.0
    
    flag    = 0
    for i in range( n):
        if (peak_index + i) >= n:
            break
        if y[peak_index+i] < 0.5*peak_y:
            temp   = (0.5*peak_y-y[peak_index+i-1])/(y[peak_index+i-1]-y[peak_index+i])
            x_right = x[peak_index+i-1]+temp*(x[peak_index+i-1]-x[peak_index+i])
            i = n - 1
            flag = 1
            break

    if flag == 0:
        dct['status'] = 0
        dct['reason'] = 4 # midpoint calc failed
        return dct
  
    flag = 0
    for i in range( n):
        if (peak_index - i) < 0:
            break
        if (y[peak_index-i] < 0.5*peak_y):
            temp   = (y[peak_index-i+1]-0.5*peak_y)/(y[peak_index-i+1]-y[peak_index-i])
            x_left = x[peak_index-i+1] - temp*(x[peak_index-i+1]-x[peak_index-i])
            i = n - 1
            flag = 1
            break

    if flag == 0:
        dct['status'] = 0
        dct['reason'] = 5  # midpoint calc failed 
        return dct

    fwhm     =  x_right-x_left
    midpoint = 0.5*(x_right+x_left)
  
    #
    # CALCULATE SCAN INTEGRAL AND CENTER OF MASS  
    #  
    scan_int = 0.0
    cms      = 0.0
  
    for i in range( n - 1):
        scan_int = scan_int + (y[i]+y[i+1])*0.5*(x[i+1]-x[i])
        cms      = cms      + (y[i]+y[i+1])*0.5*(x[i]+x[i+1])*0.5*(x[i+1]-x[i])

    cms = cms / scan_int

    #
    # b2 bug: cms was outside the x-interval
    # 
    if( cms < x[0] or cms > x[-1] or
      midpoint < x[0] or midpoint > x[-1] or
      peak_x < x[0] or peak_x > x[-1]):
        dct['status'] = 0
        dct['reason'] = 6 # max outside x-interval 
        return dct

    dct['status'] = status
    dct['reason'] = reason
    dct['cms'] = cms
    dct['integral'] = scan_int
    dct['midpoint'] = midpoint
    dct['fwhm'] = fwhm
    dct['peak_x'] = peak_x
    dct['peak_y'] = peak_y
    dct['back_int'] = back_int
    dct['r_back'] = r_back
    dct['l_back'] = l_back
    
    return dct

_lenPlotted = -1

def _setScanVPs( nameList, flagDisplaySingle):
    '''
    set the scan viewport, we use the at = (2,3,2) syntax
    which is (nrow, ncol, nplot)
    title and comment are ignored here. they are taken 
    care of in createPlotItem()

    if a scan has an 'at' field, like (2,2,3), these values
    have higher priority.
    '''
    global _lenPlotted

    scanList = _GQE.getScanList()

    if len( nameList) == 0:
        #
        # the number of used viewports is (len( scanList) - numberOfOverlaid) 
        #
        usedVPs = len( scanList) - _GQE._getNumberOfOverlaid()
        if usedVPs != _lenPlotted and _lenPlotted != -1: 
            _pysp.cls()
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
            ncol = int( _math.floor( _math.sqrt( usedVPs)))
            if usedVPs > _defs._MANY_SCANS: 
                ncol -= 1
            nrow = int( _math.ceil( (float(usedVPs))/float(ncol)))
        nplot = 1 
    elif len( nameList) == 1:
        if _lenPlotted != 1 and _lenPlotted != -1: 
            _pysp.cls()
        _lenPlotted = 1
        ncol = 1
        nrow = 1
        nplot = 1
    else:
        #
        # the number of used viewports is (len( nameList) - numberOfOverlaid( nameList)) 
        #
        usedVPs = len( nameList) - _GQE._getNumberOfOverlaid( nameList)
        if usedVPs != _lenPlotted and _lenPlotted != -1: 
            _pysp.cls()
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
            ncol = int( _math.floor( _math.sqrt( usedVPs)))
            if usedVPs > _defs._MANY_SCANS: 
                ncol -= 1
            nrow = int( _math.ceil( (float(usedVPs))/float(ncol)))
        nplot = 1 

    for scan in scanList:
        #
        # overlay? - don't create a viewport scan.
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

        if scan.plotItem is None:
            if scan.at is None:
                scan.ncol = ncol
                scan.nrow = nrow
                scan.nplot = nplot
            else: 
                scan.nrow = scan.at[0]
                scan.ncol = scan.at[1]
                scan.nplot = scan.at[2]
            #print "utils.setScanVPs", scan.name, \
            #    "nrow", scan.nrow, "ncol", scan.ncol, "nplot", scan.nplot
            if scan.nrow*scan.ncol < scan.nplot:
                raise ValueError( "utils.setScanVPs: nrow %d * ncol %d < nplot %d" % (scan.nrow, scan.ncol, scan.nplot))
            nplot += 1

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
        if HasyUtils.inkey() ==  32:  # space bar
            break

    Use
      HasyUtils.inkey( True) 
    to reset the terminal characteristic explicitly. This has to be
    done in particular, if you use sys.exitfunc = yourExitHandler
    which overrides the inkey() exit handler
    '''
    global _initInkey
    global _initInkeyOldTermAttr
    import atexit as _atexit
    import termios as _termios

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

    from PyQt4 import QtGui as _QtGui
    from PyQt4 import QtCore as _QtCore
    #import __builtin__
    ##__builtin__.__dict__[ 'graphicsLib'] = 'matplotlib'
    #__builtin__.__dict__[ 'graphicsLib'] = 'pyqtgraph'

    import PySpectra.pySpectraGuiClass as _gui

    app = _QtGui.QApplication.instance()
    if app is None:
        app = _QtGui.QApplication([])

    gui = _gui.pySpectraGui()
    gui.show()
    app.exec_()

    #_sys.exit( app.exec_())

