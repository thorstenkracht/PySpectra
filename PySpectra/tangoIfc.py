#!/bin/env python
'''
this module contains some Tango-related functions
'''
from PyQt4 import QtCore, QtGui

import pyqtgraph as _pg
import PySpectra
import PySpectra.definitions as _definitions
import PyTango 
import HasyUtils
import time 


def moveStart( gqe, targetX, targetY = None, flagConfirm = True):
    '''
    start move and wait for completion

    this function is called from 
      - by ifc.move()
    '''

    gqe.display()

    if type( gqe) == PySpectra.Scan: 
        return moveScan( gqe, targetX, flagSync = False, flagConfirm = flagConfirm)
    elif type( gqe) == PySpectra.Image: 
        return moveImage( gqe, targetX, targetY, flagSync = False, flagConfirm = flagConfirm)
    else: 
        raise ValueError( "IfTango.move: failed to identify the gqe type" % type( gqe))


def move( gqe, targetX, targetY = None, flagConfirm = True):
    '''
    start move and wait for completion

    this function is called from 
      - ifc.move()
      - a mouse click from pqtgrph/graphics.py
    '''
    if type( gqe) == PySpectra.Scan: 
        return moveScan( gqe, targetX, flagSync = True, flagConfirm = flagConfirm)
    elif type( gqe) == PySpectra.Image: 
        return moveImage( gqe, targetX, targetY, flagSync = True, flagConfirm = flagConfirm)
    else: 
        raise ValueError( "IfTango.move: failed to identify the gqe type" % type( gqe))

def moveScan( scan, target, flagSync = None, flagConfirm = True): 
    '''
    start move and wait for completion

    to execute the move information provided by a Scan GQE is used.
    '''

    #print( "tangoIfc.move(), motorNameList %s " % repr( scan.motorNameList))
        
    if PySpectra.InfoBlock.monitorGui is None and scan.motorNameList is None:
        if scan.logWidget is not None:
            scan.logWidget.append( "tangoIfc.move: not called from pyspMonitor or moveMotor") 
        else:
            pass
        return 
    
    door = PySpectra.InfoBlock.getDoorProxy()
            
    if door.state() != PyTango.DevState.ON: 
        if scan.logWidget is not None:
            scan.logWidget.append( "tangoIfc.move: door.state() != ON %s" % 
                                   repr( door.state()))
        else:
            print( "tangoIfc.move: door.state() != ON %s" % repr( door.state()))
        return 
    #
    # make sure the target is inside the x-range of the plot
    #
    if target < scan.xMin or target > scan.xMax:
        if PySpectra.InfoBlock.monitorGui is None: 
            print( "tangoIfc.Move: target %g outside %s x-axis %g %g" % 
                   (target, scan.name, scan.xMin, scan.xMax))
        else: 
            QtGui.QMessageBox.about( None, "Info Box", 
                                     "tangoIfc.Move: target %g outside %s x-axis %g %g" % 
                                     (target, scan.name, scan.xMin, scan.xMax))
        return
            
    #
    # don't use MCA data to move motors
    #
    if scan.flagMCA:
        if scan.logWidget is not None:
            scan.logWidget.append( "tangoIfc.move: error, don't use MCAs to move motors") 
        return 

    #
    # ---
    # from moveMotor widget
    # - one motor only
    # ---
    #
    if scan.motorNameList is not None and len( scan.motorNameList) == 1: 

        try: 
            proxyPool = PyTango.DeviceProxy( scan.motorNameList[0])
            proxy = PyTango.DeviceProxy( proxyPool.TangoDevice)
        except Exception as e: 
            print( "tangoIfc.move: failed to create the proxy to %s" % scan.motorNameList[0])
            print( "%s" % repr( e))
            return 
        #
        # stop the motor, if it is moving
        #
        if proxy.state() == PyTango.DevState.MOVING:
            if scan.logWidget is not None:
                scan.logWidget.append( "Move: stopping %s" % proxy.name()) 
            proxy.stopMove()
        while proxy.state() == PyTango.DevState.MOVING:
            time.sleep(0.01)

        msg = "Move %s from %g to %g" % ( proxy.name(), 
                                          float( proxy.read_attribute( 'Position').value), 
                                          float( target))
        #
        # when executing 'moveStart' we don't want to wait here. 
        # otherwise the client receives a time-out
        #
        if flagConfirm:
            if PySpectra.InfoBlock.monitorGui is None: 
                if not HasyUtils.yesno( msg + " y/[n]: "):
                    print( "Move: move not confirmed")
                    return
            else: 
                reply = QtGui.QMessageBox.question( None, 'YesNo', 
                                                    msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)        

                if reply != QtGui.QMessageBox.Yes:
                    if scan.logWidget is not None:
                        scan.logWidget.append( "Move: move not confirmed") 
                    else:
                        print( "Move: move not confirmed")
                    return

        if scan.logWidget is not None:
            scan.logWidget.append( "Moving %s from %g to %g" % ( proxy.name(), 
                                                                 float( proxy.read_attribute( 'Position').value), 
                                                                 target))
        scan.display()
        #
        # before we hide the mouse lines, make sure that they are there
        # mouse lines and arrows are created, when a single scan is displayed
        #
        if scan.infLineMouseX is not None: 
            scan.infLineMouseX.hide()
            scan.infLineMouseY.hide()
            scan.setArrowSetPoint( target)

        #
        # wait for move completion
        #
        proxy.Position = target

        if flagSync: 
            while proxy.state() == PyTango.DevState.MOVING:
                if scan.arrowCurrent is not None: 
                    scan.updateArrowCurrent()
                time.sleep( 0.1)
                PySpectra.processEvents()
        #
        # to make sure that the arrows are really on top of each other
        #
        if scan.arrowCurrent is not None: 
            scan.updateArrowCurrent()
            scan.arrowSetPoint.hide()
        
        return 
        
    #
    # ---
    # from the pyspMonitor application, after a scan macro has bee executed
    # ---
    #
    if PySpectra.InfoBlock.monitorGui is None or PySpectra.InfoBlock.monitorGui.scanInfo is None: 
        QtGui.QMessageBox.about( None, "Info Box", 
                                  "PySpectra.Move: PySpectra.monitorGui is None or PySpectra.monitorGui.scanInfo is None")
        return

    motorArr = PySpectra.InfoBlock.monitorGui.scanInfo['motors']        
    length = len( motorArr)
    if  length == 0 or length > 3:
        QtGui.QMessageBox.about( None, 'Info Box', "no. of motors == 0 or > 3") 
        return

    motorIndex = PySpectra.InfoBlock.monitorGui.scanInfo['motorIndex']

    if motorIndex >= length:
        QtGui.QMessageBox.about( None, 'Info Box', "motorIndex %d >= no. of motors %d" % (motorIndex, length))
        return
            
    motorArr[motorIndex]['targetPos'] = target
    r = (motorArr[motorIndex]['targetPos'] - motorArr[motorIndex]['start']) / \
        (motorArr[motorIndex]['stop'] - motorArr[motorIndex]['start']) 

    if length == 1:
        p0Pool = PyTango.DeviceProxy( motorArr[0]['name'])
        p0 = PyTango.DeviceProxy( p0Pool.TangoDevice)
        if not scan.checkTargetWithinLimits( motorArr[0]['name'], float( motorArr[0]['targetPos']), p0, 
                                             flagConfirm = True): 
            return 
                
        msg = "Move %s from %g to %g" % (motorArr[0]['name'], 
                                         float(p0.read_attribute( 'Position').value), 
                                         float( motorArr[0]['targetPos']))
        if flagConfirm: 
            reply = QtGui.QMessageBox.question( None, 'YesNo', msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No) 
    #
    # for hklscan: a h-move may move the same motors as a k-move, etc. 
    #
    elif length == 2:
        motorArr[0]['targetPos'] = (motorArr[0]['stop'] - motorArr[0]['start'])*r + motorArr[0]['start']
        motorArr[1]['targetPos'] = (motorArr[1]['stop'] - motorArr[1]['start'])*r + motorArr[1]['start']
        p0Pool = PyTango.DeviceProxy( motorArr[0]['name'])
        p0 = PyTango.DeviceProxy( p0Pool.TangoDevice)
        p1Pool = PyTango.DeviceProxy( motorArr[1]['name'])
        p1 = PyTango.DeviceProxy( p1Pool.TangoDevice)
        if not scan.checkTargetWithinLimits( motorArr[0]['name'], float( motorArr[0]['targetPos']), p0, 
                                             flagConfirm = True): 
            return 
        if not scan.checkTargetWithinLimits( motorArr[1]['name'], float( motorArr[1]['targetPos']), p1, 
                                             flagConfirm = True): 
            return 
        msg = "Move\n  %s from %g to %g\n  %s from %g to %g " % \
              (motorArr[0]['name'], p0.read_attribute( 'Position').value, motorArr[0]['targetPos'],
               motorArr[1]['name'], p1.read_attribute( 'Position').value, motorArr[1]['targetPos'])

        if flagConfirm: 
            reply = QtGui.QMessageBox.question( None, 'YesNo', msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
    #
    # for hklscan: a h-move may move the same motors as a k-move, etc. 
    #   - therefore we may have to repeat the Move2Cursor
    #   - and we have to check whether a motor is already in-target
    #
    elif length == 3:
        motorArr[0]['targetPos'] = (motorArr[0]['stop'] - motorArr[0]['start'])*r + motorArr[0]['start']
        motorArr[1]['targetPos'] = (motorArr[1]['stop'] - motorArr[1]['start'])*r + motorArr[1]['start']
        motorArr[2]['targetPos'] = (motorArr[2]['stop'] - motorArr[2]['start'])*r + motorArr[2]['start']
        p0Pool = PyTango.DeviceProxy( motorArr[0]['name'])
        p0 = PyTango.DeviceProxy( p0Pool.TangoDevice)
        p1Pool = PyTango.DeviceProxy( motorArr[1]['name'])
        p1 = PyTango.DeviceProxy( p1Pool.TangoDevice)
        p2Pool = PyTango.DeviceProxy( motorArr[2]['name'])
        p2 = PyTango.DeviceProxy( p2Pool.TangoDevice)
        if not scan.checkTargetWithinLimits( motorArr[0]['name'], float( motorArr[0]['targetPos']), p0, 
                                             flagConfirm = True): 
            return 
        if not scan.checkTargetWithinLimits( motorArr[1]['name'], float( motorArr[1]['targetPos']), p1, 
                                             flagConfirm = True): 
            return 
        if not scan.checkTargetWithinLimits( motorArr[2]['name'], float( motorArr[2]['targetPos']), p2, 
                                             flagConfirm = True): 
            return 
        msg = "Move\n  %s from %g to %g\n  %s from %g to %g\n  %s from %g to %g " % \
              (motorArr[0]['name'], p0.read_attribute( 'Position').value, motorArr[0]['targetPos'],
               motorArr[1]['name'], p1.read_attribute( 'Position').value, motorArr[1]['targetPos'],
               motorArr[2]['name'], p2.read_attribute( 'Position').value, motorArr[2]['targetPos'])

        if flagConfirm: 
            reply = QtGui.QMessageBox.question( None, 'YesNo', msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
    #
    # when executing moveStart or unit tests we don't want to wait
    #
    if not flagConfirm: 
        reply = QtGui.QMessageBox.Yes

    if scan.infLineMouseX is not None: 
        scan.infLineMouseX.hide()
        scan.infLineMouseY.hide()

        scan.setArrowSetPoint(  motorArr[0]['targetPos'])
        scan.arrowSetPoint.show()

    if not reply == QtGui.QMessageBox.Yes:
        PySpectra.InfoBlock.monitorGui.logWidget.append( "Move: move not confirmed")
        return

    if PySpectra.InfoBlock.monitorGui.scanInfo['title'].find( "hklscan") == 0:
        PySpectra.InfoBlock.monitorGui.logWidget.append( "br %g %g %g" % 
                                         (motorArr[0]['targetPos'],
                                          motorArr[1]['targetPos'],
                                          motorArr[2]['targetPos']))
        door.RunMacro( ["br",  
                        "%g" %  motorArr[0]['targetPos'], 
                        "%g" %  motorArr[1]['targetPos'], 
                        "%g" %  motorArr[2]['targetPos']])
    else:
        lst = [ "umv"]
        for hsh in motorArr:
            lst.append( "%s" % (hsh['name']))
            lst.append( "%g" % (hsh['targetPos']))
            PySpectra.InfoBlock.monitorGui.logWidget.append( "%s to %g" % (hsh['name'], hsh['targetPos']))
        door.RunMacro( lst)

    if flagSync:
        while door.state() == PyTango.DevState.RUNNING: 
            time.sleep( 0.1)
            PySpectra.processEvents()
        
    return 

    #
    # why do we need a class function for move()
    #
def moveImage( image, targetIX, targetIY, flagSync, flagConfirm = True): 
    '''
    this function is invoked by a mouse click from pqtgrph/graphics.py
    '''
    import PyTango as PyTango
    import time as _time

    if str(image.name).upper().find( "MANDELBROT") != -1:
        return image.zoomMb( targetIX, targetIY)

    if not hasattr( image, 'xMin'):
        print( "Gqe.Image.move: %s no attribute xMin" % image.name)
        return 

    if type( image) != Image:
        print( "Gqe.Image.move: %s is not a Image" % image.name)
        return 
            
    targetX = float( targetIX)/float( image.width)*( image.xMax - image.xMin) + image.xMin
    targetY = float( targetIY)/float( image.height)*( image.yMax - image.yMin) + image.yMin
    print( "PySpectra.Image.move x %g, y %g" % (targetX, targetY))

    if PySpectra.InfoBlock.monitorGui is None:
        if image.logWidget is not None:
            image.logWidget.append( "PySpectra.Image.move: not called from pyspMonitor") 
        else:
            print( "PySpectra.Image.move: not called from pyspMonitor")
        return 

    try: 
        proxyXPool = PyTango.DeviceProxy( image.xLabel)
        proxyX = PyTango.DeviceProxy( proxyXPool.TangoDevice)
    except Exception as e:
        print( "Image.move: no proxy to %s" % image.xLabel)
        print( repr( e))
        return 

    try: 
        proxyYPool = PyTango.DeviceProxy( image.yLabel)
        proxyY = PyTango.DeviceProxy( proxyYPool.TangoDevice)
    except Exception as e:
        print( "Image.move: no proxy to %s" % image.yLabel)
        print( repr( e))
        return 

    #
    # stop the motors, if they is moving
    #
    if proxyX.state() == PyTango.DevState.MOVING:
        if image.logWidget is not None:
            image.logWidget.append( "Image.Move: stopping %s" % proxyX.name()) 
        proxyX.stopMove()
    while proxyX.state() == PyTango.DevState.MOVING:
        time.sleep(0.01)
    if proxyY.state() == PyTango.DevState.MOVING:
        if image.logWidget is not None:
            image.logWidget.append( "Image.Move: stopping %s" % proxyY.name()) 
        proxyY.stopMove()
    while proxyY.state() == PyTango.DevState.MOVING:
        time.sleep(0.01)

    if flagConfirm: 
        msg = "Move\n  %s from %g to %g\n  %s from %g to %g " % \
              (proxyX.name(), proxyX.read_attribute( 'Position').value, targetX,
               proxyY.name(), proxyY.read_attribute( 'Position').value, targetY)
        reply = QtGui.QMessageBox.question( None, 'YesNo', msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        
        if not reply == QtGui.QMessageBox.Yes:
            if image.logWidget is not None:
                PySpectra.InfoBlock.monitorGui.logWidget.append( "Image.Move: move not confirmed")
            return

    lst = [ "umv %s %g %s %g" % (proxyX.name(), targetX, proxyY.name(), targetY)]
        
    if image.logWidget is not None:
        PySpectra.InfoBlock.monitorGui.logWidget.append( "%s" % (lst[0]))

    door = PySpectra.InfoBlock.getDoorProxy()

    if door is None: 
        return 

    door.RunMacro( lst)

    if flagSync:
        while door.state() == PyTango.DevState.RUNNING: 
            time.sleep( 0.1)
            PySpectra.processEvents()

    return 
