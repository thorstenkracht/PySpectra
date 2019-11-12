#!/usr/bin/env python
'''
ssa() - simple scan analysis function 
        code also in 
        /home/kracht/Misc/Sardana/hasyutils/HasyUtils/ssa.py
'''
import numpy as _np
import math as _math
import PySpectra as _pysp
import PySpectra.dMgt.GQE as _GQE
import sys as _sys
import os as _os
import time as _time

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

    reason2String = { '0': 'ok', 
                      '1': 'np < 6', 
                      '2': 'signal-to-background', 
                      '3': 'no y(i) > 0', 
                      '4': 'midpoint calc.', 
                      '5': 'midpoint calc.', 
                      '6': 'maximum outside x-range', 
                      '7': 'not a numpy array'}
    status = 1
    reason = 0
    dct = {}

    dct['status'] = status
    dct['reason'] = reason
    dct['reasonString'] = reason2String[ str( dct['reason'])] 
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
        dct['reasonString'] = reason2String[ str(dct['reason'])]
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
        dct['reasonString'] = reason2String[ str(dct['reason'])]
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
        dct['reasonString'] = reason2String[ str(dct['reason'])]
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
        dct['reasonString'] = reason2String[ str(dct['reason'])]
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
        dct['reasonString'] = reason2String[ str(dct['reason'])]
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
        dct['reasonString'] = reason2String[ str(dct['reason'])]
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
        dct['reasonString'] = reason2String[ str(dct['reason'])]
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

def setScanVPs( nameList, flagDisplaySingle, clsFunc):
    '''
    set the scan viewport, we use the at = (2,3,2) syntax
    which is (nrow, ncol, nplot)
    title and comment are ignored here. they are taken 
    care of in createPlotItem()

    if a scan has an 'at' field, like (2,2,3), these values
    have higher priority.

    clsFunc is specified to be able to distinguish between mpl and pqt
    '''
    global _lenPlotted

    scanList = _GQE.getScanList()

    if len( nameList) == 0:
        #
        # the number of used viewports is (len( scanList) - numberOfOverlaid) 
        #
        usedVPs = len( scanList) - _GQE._getNumberOfOverlaid()
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
            if usedVPs > _pysp.definitions.MANY_SCANS: 
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
        usedVPs = len( nameList) - _GQE._getNumberOfOverlaid( nameList)
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
            if usedVPs > _pysp.definitions.MANY_SCANS: 
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

    from PyQt4 import QtGui as _QtGui
    from PyQt4 import QtCore as _QtCore

    import PySpectra.pySpectraGuiClass as _gui

    app = _QtGui.QApplication.instance()
    if app is None:
        app = _QtGui.QApplication([])

    gui = _gui.pySpectraGui()
    gui.show()
    app.exec_()

    #_sys.exit( app.exec_())


#def waitAndProcessEvents( waitTime): 
#    '''
#    Wait for waitTime seconds to expire. During the wait time 
#    the QApp events are processed. If 'p' is pressed, the function
#    waits until another 'p' is pressed. 
#    implemented to suppress, e.g., new file reads. 
#
#    4.7.2019 taken out because it is no longer clear for what this function us useful
#
#    startTime = _time.time()
#    while (time.time() - startTime) < WAIT_TIME:
#        pysp.processEvents()
#        key = inkey()
#        if key == 32:
#            return 32
#        if key == 112: # 'p'
#            print "paused, press 'p' to resume"
#            while True:
#                pysp.processEvents()
#                if inkey() == 112:
#                    print "unpaused, press 'p' to pause"
#                    break
#                time.sleep(0.01)
#        time.sleep(0.01)
#    '''
#
#    startTime = _time.time()
#    while (_time.time() - startTime) < waitTime:
#        _pysp.processEvents()
#        key = inkey()
#        if key == 32:
#            return 32
#        if key == 112: # 'p'
#            print "paused, press 'p' to resume"
#            while True:
#                _pysp.processEvents()
#                if inkey() == 112:
#                    print "unpaused, press 'p' to pause"
#                    break
#                _time.sleep(0.01)
#        _time.sleep(0.01)
#    return True

def prtc(): 
    print "Prtc ",
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
            ret = _np.max( scan.y[:(scan.currentIndex + 1)])
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
            ret = _np.min( scan.y[:(scan.currentIndex + 1)])
    else:
        ret = scan.yMin
    return ret


def toPyspMonitor( hsh, node = None):
    """
    sends a dictionary to a PyspMonitor process, 
    returns a dictionary ...

import PySpectra
import random
MAX = 10
pos = [float(n)/MAX for n in range( MAX)]
d1 = [random.random() for n in range( MAX)]
d2 = [random.random() for n in range( MAX)]

hsh = { 'putData': 
           {'title': "Important Data", 
            'columns': 
            [ { 'name': "d1_mot01", 'data' : pos},
              { 'name': "d1_c01", 'data' : d1},
              { 'name': "d1_c02", 'data' : d2},
           ]}}
smNode = "haso107d1"
hsh = PySpectra.toPyspMonitor( hsh, node = smNode)
print hsh
if hsh[ 'result'].upper() == 'DONE':
    print "success!"
    
print PySpectra.toPyspMonitor( {'gra_decode_text': "date()"}, node = smNode)
print PySpectra.toPyspMonitor( {'gra_decode_int': "2*3"}, node = smNode)
print PySpectra.toPyspMonitor( {'gra_decode_double': "sqrt(2.)"}, node = smNode)
print PySpectra.toPyspMonitor( {'gra_command': "cls;wait 1;display 1"}, node = smNode)
hsh = PySpectra.toPyspMonitor( { 'getData': True})
print repr( hsh.keys())
print repr( hsh['getData'].keys())
print repr( hsh['getData']['D1_C01']['x'])

    """
    import zmq, json, socket

    if node is None:
        node = socket.gethostbyname( socket.getfqdn())

    context = zmq.Context()
    sckt = context.socket(zmq.REQ)
    #
    # prevent context.term() from hanging, if the message
    # is not consumed by a receiver.
    #
    sckt.setsockopt(zmq.LINGER, 1)
    try:
        sckt.connect('tcp://%s:7778' % node)
    except Exception, e:
        sckt.close()
        return { 'result': "utils.toPyspMonitor: failed to connect to %s" % node}

    hshEnc = json.dumps( hsh)
    try:
        res = sckt.send( hshEnc)
    except Exception, e:
        sckt.close()
        return { 'result': "TgUtils.toPyspMonitor: exception by send() %s" % repr(e)}
    #
    # PyspMonitor receives the Dct, processes it and then
    # returns the message. This may take some time. To pass
    # 4 arrays, each with 10000 pts takes 2.3s
    #
    if hsh.has_key( 'isAlive'):
        lst = zmq.select([sckt], [], [], 0.5)
        if sckt in lst[0]:
            hshEnc = sckt.recv() 
            sckt.close()
            context.term()
            return json.loads( hshEnc)
        else: 
            sckt.close()
            context.term()
            return { 'result': 'notAlive'}
    else:
        lst = zmq.select([sckt], [], [], 3.0)
        if sckt in lst[0]:
            hshEnc = sckt.recv() 
            sckt.close()
            context.term()
            return json.loads( hshEnc)
        else: 
            sckt.close()
            context.term()
            return { 'result': 'utils: no reply from pyspMonitor'}

def isPyspMonitorAlive( node = None):
    '''
    returns True, if there is a pyspMonitor responding to the isAlive prompt
    '''
    hsh = toPyspMonitor( { 'isAlive': True}, node = node)
    if hsh[ 'result'] == 'notAlive':
        return False
    else:
        return True
