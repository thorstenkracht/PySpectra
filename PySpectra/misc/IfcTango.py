#!/bin/env python

import PySpectra as _pysp

def move( scan, target): 
    '''
    this function is invoked 
      - by a mouse click from pqtgrph/graphics.py
    '''
    import PyTango as _PyTango
    import time as _time

    print( "IfcTango.move(), motorNameList %s " % repr( scan.motorNameList))
    if _pysp.dMgt.GQE.InfoBlock.monitorGui is None and scan.motorNameList is None:
        if scan.logWidget is not None:
            scan.logWidget.append( "IfcTango.move: not called from pyspMonitor or moveMotor") 
        else:
            pass
        return 
    #
    # make sure the target is inside the x-range of the plot
    #
    if target < scan.xMin or target > scan.xMax:
        _QtGui.QMessageBox.about( None, "Info Box", 
                                  "IfcTango.Move: target %g outside %s x-axis %g %g" % 
                                  (target, scan.name, scan.xMin, scan.xMax))
        return
            
    #
    # don't use MCA data to move motors
    #
    if scan.flagMCA:
        if scan.logWidget is not None:
            scan.logWidget.append( "IfcTango.move: error, don't use MCAs to move motors") 
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
            print( "IfcTango.move: failed to create the proxy to %s" % scan.motorNameList[0])
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
        reply = _QtGui.QMessageBox.question( None, 'YesNo', msg, _QtGui.QMessageBox.Yes, _QtGui.QMessageBox.No)        

        if not reply == _QtGui.QMessageBox.Yes:
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
        scan.arrowMotorSetPoint.setPos( target, scan.getYMin())
        scan.arrowMotorSetPoint.show()
        
        return 
        
    #
    # ---
    # from the pyspMonitor application, after a scan macro has bee executed
    # ---
    #
    if _pysp.dMgt.GQE.InfoBlock.monitorGui is None or _pysp.dMgt.GQE.InfoBlock.monitorGui.scanInfo is None: 
        _QtGui.QMessageBox.about( None, "Info Box", 
                                  "GQE.Move: _pysp.dMgt.GQE.monitorGui is None or _pysp.dMgt.GQE.monitorGui.scanInfo is None")
        return

    motorArr = _pysp.dMgt.GQE.InfoBlock.monitorGui.scanInfo['motors']        
    length = len( motorArr)
    if  length == 0 or length > 3:
        _QtGui.QMessageBox.about( None, 'Info Box', "no. of motors == 0 or > 3") 
        return

    motorIndex = _pysp.dMgt.GQE.InfoBlock.monitorGui.scanInfo['motorIndex']

    if motorIndex >= length:
        _QtGui.QMessageBox.about( None, 'Info Box', "motorIndex %d >= no. of motors %d" % (motorIndex, length))
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
        reply = _QtGui.QMessageBox.question( None, 'YesNo', msg, _QtGui.QMessageBox.Yes, _QtGui.QMessageBox.No) 
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
        reply = _QtGui.QMessageBox.question( None, 'YesNo', msg, _QtGui.QMessageBox.Yes, _QtGui.QMessageBox.No)
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
        reply = _QtGui.QMessageBox.question( None, 'YesNo', msg, _QtGui.QMessageBox.Yes, _QtGui.QMessageBox.No)

    scan.infLineMouseX.hide()
    scan.infLineMouseY.hide()
    scan.arrowMotorSetPoint.setPos(  motorArr[0]['targetPos'], scan.getYMin())
    scan.arrowMotorSetPoint.show()

    if not reply == _QtGui.QMessageBox.Yes:
        _pysp.dMgt.GQE.InfoBlock.monitorGui.logWidget.append( "Move: move not confirmed")
        return

    if _pysp.dMgt.GQE.InfoBlock.monitorGui.scanInfo['title'].find( "hklscan") == 0:
        _pysp.dMgt.GQE.InfoBlock.monitorGui.logWidget.append( "br %g %g %g" % 
                                         (motorArr[0]['targetPos'],motorArr[1]['targetPos'],motorArr[2]['targetPos']))
        _pysp.dMgt.GQE.InfoBlock.monitorGui.door.RunMacro( ["br",  
                                       "%g" %  motorArr[0]['targetPos'], 
                                       "%g" %  motorArr[1]['targetPos'], 
                                       "%g" %  motorArr[2]['targetPos']])
    else:
        lst = [ "umv"]
        for hsh in motorArr:
            lst.append( "%s" % (hsh['name']))
            lst.append( "%g" % (hsh['targetPos']))
            _pysp.dMgt.GQE.InfoBlock.monitorGui.logWidget.append( "%s to %g" % (hsh['name'], hsh['targetPos']))
        _pysp.dMgt.GQE.InfoBlock.monitorGui.door.RunMacro( lst)
    return 
