#!/bin/env python

from PyQt4 import QtCore, QtGui

import pyqtgraph as _pg
import PySpectra
import PySpectra.dMgt.GQE as GQE
import PySpectra.definitions as _definitions

def move( gqe, targetX, targetY = None):
    if type( gqe) == GQE.Scan: 
        return moveScan( gqe, targetX)
    elif type( gqe) == GQE.Image: 
        return moveImage( gqe, targetX, targetY)
    else: 
        raise ValueError( "IfTango.move: failed to identify the gqe type" % type( gqe))

def moveScan( scan, target): 
    '''
    this function is invoked 
      - by a mouse click from pqtgrph/graphics.py
    '''
    import PyTango as _PyTango
    import time as _time

    #print( "tangoIfc.move(), motorNameList %s " % repr( scan.motorNameList))
        
    if GQE.InfoBlock.monitorGui is None and scan.motorNameList is None:
        if scan.logWidget is not None:
            scan.logWidget.append( "tangoIfc.move: not called from pyspMonitor or moveMotor") 
        else:
            pass
        return 

    if GQE.InfoBlock.monitorGui.door.state() != _PyTango.DevState.ON: 
        if scan.logWidget is not None:
            scan.logWidget.append( "tangoIfc.move: door.state() != ON %s" % repr( GQE.infoBlock.monitorGui.door.state()))
        else:
            print( "tangoIfc.move: door.state() != ON %s" % repr( GQE.InfoBlock.monitorGui.door.state()))
        return 
    #
    # make sure the target is inside the x-range of the plot
    #
    if target < scan.xMin or target > scan.xMax:
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
            proxy = _PyTango.DeviceProxy( scan.motorNameList[0])
        except Exception as e: 
            print( "tangoIfc.move: failed to create the proxy to %s" % scan.motorNameList[0])
            print( "%s" % repr( e))
            return 
        #
        # stop the motor, if it is moving
        #
        if proxy.state() == _PyTango.DevState.MOVING:
            if scan.logWidget is not None:
                scan.logWidget.append( "Move: stopping %s" % proxy.name()) 
            proxy.stopMove()
        while proxy.state() == _PyTango.DevState.MOVING:
            _time.sleep(0.01)

        msg = "Move %s from %g to %g" % ( proxy.name(), 
                                          float( proxy.read_attribute( 'Position').value), 
                                          float( target))
        reply = QtGui.QMessageBox.question( None, 'YesNo', msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)        

        if not reply == QtGui.QMessageBox.Yes:
            if scan.logWidget is not None:
                scan.logWidget.append( "Move: move not confirmed") 
            else:
                print( "Move: move not confirmed")
            return
        if scan.logWidget is not None:
            scan.logWidget.append( "Moving %s from %g to %g" % ( proxy.name(), 
                                                                 float( proxy.read_attribute( 'Position').value), 
                                                                 target))
        proxy.Position = target
        #
        # the re-display removes the mouse-lines
        #
        scan.infLineMouseX.hide()
        scan.infLineMouseY.hide()

        pos = scan.plotItem.vb.mapViewToScene( _pg.Point( target, scan.getYMin())).toPoint()
        pos.setY( PySpectra.getGraphicsWindowHeight() - _definitions.ARROW_Y_OFFSET)
        #scan.arrowMotorSetPoint.setPos( target, scan.getYMin())
        scan.arrowMotorSetPoint.setPos( pos)
        scan.arrowMotorSetPoint.show()
        
        return 
        
    #
    # ---
    # from the pyspMonitor application, after a scan macro has bee executed
    # ---
    #
    if GQE.InfoBlock.monitorGui is None or GQE.InfoBlock.monitorGui.scanInfo is None: 
        QtGui.QMessageBox.about( None, "Info Box", 
                                  "GQE.Move: GQE.monitorGui is None or GQE.monitorGui.scanInfo is None")
        return

    motorArr = GQE.InfoBlock.monitorGui.scanInfo['motors']        
    length = len( motorArr)
    if  length == 0 or length > 3:
        QtGui.QMessageBox.about( None, 'Info Box', "no. of motors == 0 or > 3") 
        return

    motorIndex = GQE.InfoBlock.monitorGui.scanInfo['motorIndex']

    if motorIndex >= length:
        QtGui.QMessageBox.about( None, 'Info Box', "motorIndex %d >= no. of motors %d" % (motorIndex, length))
        return
            
    motorArr[motorIndex]['targetPos'] = target
    r = (motorArr[motorIndex]['targetPos'] - motorArr[motorIndex]['start']) / \
        (motorArr[motorIndex]['stop'] - motorArr[motorIndex]['start']) 

    if length == 1:
        p0 = _PyTango.DeviceProxy( motorArr[0]['name'])
        if not scan._checkTargetWithinLimits( motorArr[0]['name'], float( motorArr[0]['targetPos']), p0): 
            return 
                
        msg = "Move %s from %g to %g" % (motorArr[0]['name'], 
                                         float(p0.read_attribute( 'Position').value), 
                                         float( motorArr[0]['targetPos']))
        reply = QtGui.QMessageBox.question( None, 'YesNo', msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No) 
    #
    # for hklscan: a h-move may move the same motors as a k-move, etc. 
    #
    elif length == 2:
        motorArr[0]['targetPos'] = (motorArr[0]['stop'] - motorArr[0]['start'])*r + motorArr[0]['start']
        motorArr[1]['targetPos'] = (motorArr[1]['stop'] - motorArr[1]['start'])*r + motorArr[1]['start']
        p0 = _PyTango.DeviceProxy( motorArr[0]['name'])
        p1 = _PyTango.DeviceProxy( motorArr[1]['name'])
        if not scan._checkTargetWithinLimits( motorArr[0]['name'], float( motorArr[0]['targetPos']), p0): 
            return 
        if not scan._checkTargetWithinLimits( motorArr[1]['name'], float( motorArr[1]['targetPos']), p1): 
            return 
        msg = "Move\n  %s from %g to %g\n  %s from %g to %g " % \
              (motorArr[0]['name'], p0.read_attribute( 'Position').value, motorArr[0]['targetPos'],
               motorArr[1]['name'], p1.read_attribute( 'Position').value, motorArr[1]['targetPos'])
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
        p0 = _PyTango.DeviceProxy( motorArr[0]['name'])
        p1 = _PyTango.DeviceProxy( motorArr[1]['name'])
        p2 = _PyTango.DeviceProxy( motorArr[2]['name'])
        if not scan._checkTargetWithinLimits( motorArr[0]['name'], float( motorArr[0]['targetPos']), p0): 
            return 
        if not scan._checkTargetWithinLimits( motorArr[1]['name'], float( motorArr[1]['targetPos']), p1): 
            return 
        if not scan._checkTargetWithinLimits( motorArr[2]['name'], float( motorArr[2]['targetPos']), p2): 
            return 
        msg = "Move\n  %s from %g to %g\n  %s from %g to %g\n  %s from %g to %g " % \
              (motorArr[0]['name'], p0.read_attribute( 'Position').value, motorArr[0]['targetPos'],
               motorArr[1]['name'], p1.read_attribute( 'Position').value, motorArr[1]['targetPos'],
               motorArr[2]['name'], p2.read_attribute( 'Position').value, motorArr[2]['targetPos'])
        reply = QtGui.QMessageBox.question( None, 'YesNo', msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

    scan.infLineMouseX.hide()
    scan.infLineMouseY.hide()

    pos = scan.plotItem.vb.mapViewToScene( _pg.Point( motorArr[0]['targetPos'], scan.getYMin())).toPoint()
    #scan.arrowMotorSetPoint.setPos(  motorArr[0]['targetPos'], scan.getYMin())
    scan.arrowMotorSetPoint.setPos(  pos)
    scan.arrowMotorSetPoint.show()

    if not reply == QtGui.QMessageBox.Yes:
        GQE.InfoBlock.monitorGui.logWidget.append( "Move: move not confirmed")
        return

    if GQE.InfoBlock.monitorGui.scanInfo['title'].find( "hklscan") == 0:
        GQE.InfoBlock.monitorGui.logWidget.append( "br %g %g %g" % 
                                         (motorArr[0]['targetPos'],motorArr[1]['targetPos'],motorArr[2]['targetPos']))
        GQE.InfoBlock.monitorGui.door.RunMacro( ["br",  
                                       "%g" %  motorArr[0]['targetPos'], 
                                       "%g" %  motorArr[1]['targetPos'], 
                                       "%g" %  motorArr[2]['targetPos']])
    else:
        lst = [ "umv"]
        for hsh in motorArr:
            lst.append( "%s" % (hsh['name']))
            lst.append( "%g" % (hsh['targetPos']))
            GQE.InfoBlock.monitorGui.logWidget.append( "%s to %g" % (hsh['name'], hsh['targetPos']))
        GQE.InfoBlock.monitorGui.door.RunMacro( lst)

    return 

    #
    # why do we need a class function for move()
    #
def moveImage( image, targetIX, targetIY): 
    '''
    this function is invoked by a mouse click from pqtgrph/graphics.py
    '''
    import PyTango as _PyTango
    import time as _time

    if str(image.name).upper().find( "MANDELBROT") != -1:
        return image.zoom( targetIX, targetIY)

    if not hasattr( image, 'xMin'):
        print( "Gqe.Image.move: %s no attribute xMin" % image.name)
        return 

    if type( image) != Image:
        print( "Gqe.Image.move: %s is not a Image" % image.name)
        return 
            
    targetX = float( targetIX)/float( image.width)*( image.xMax - image.xMin) + image.xMin
    targetY = float( targetIY)/float( image.height)*( image.yMax - image.yMin) + image.yMin
    print( "GQE.Image.move x %g, y %g" % (targetX, targetY))

    if GQE.InfoBlock.monitorGui is None:
        if image.logWidget is not None:
            image.logWidget.append( "GQE.Image.move: not called from pyspMonitor") 
        else:
            print( "GQE.Image.move: not called from pyspMonitor")
        return 

    try: 
        proxyX = _PyTango.DeviceProxy( image.xLabel)
    except Exception as e:
        print( "Image.move: no proxy to %s" % image.xLabel)
        print( repr( e))
        return 

    try: 
        proxyY = _PyTango.DeviceProxy( image.yLabel)
    except Exception as e:
        print( "Image.move: no proxy to %s" % image.yLabel)
        print( repr( e))
        return 

    #
    # stop the motors, if they is moving
    #
    if proxyX.state() == _PyTango.DevState.MOVING:
        if image.logWidget is not None:
            image.logWidget.append( "Image.Move: stopping %s" % proxyX.name()) 
        proxyX.stopMove()
    while proxyX.state() == _PyTango.DevState.MOVING:
        _time.sleep(0.01)
    if proxyY.state() == _PyTango.DevState.MOVING:
        if image.logWidget is not None:
            image.logWidget.append( "Image.Move: stopping %s" % proxyY.name()) 
        proxyY.stopMove()
    while proxyY.state() == _PyTango.DevState.MOVING:
        _time.sleep(0.01)

    msg = "Move\n  %s from %g to %g\n  %s from %g to %g " % \
          (proxyX.name(), proxyX.read_attribute( 'Position').value, targetX,
           proxyY.name(), proxyY.read_attribute( 'Position').value, targetY)
    reply = QtGui.QMessageBox.question( None, 'YesNo', msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        
    if not reply == QtGui.QMessageBox.Yes:
        if image.logWidget is not None:
            GQE.InfoBlock.monitorGui.logWidget.append( "Image.Move: move not confirmed")
        return

    lst = [ "umv %s %g %s %g" % (proxyX.name(), targetX, proxyY.name(), targetY)]
        
    if image.logWidget is not None:
        GQE.InfoBlock.monitorGui.logWidget.append( "%s" % (lst[0]))

    GQE.InfoBlock.monitorGui.door.RunMacro( lst)
    return 
