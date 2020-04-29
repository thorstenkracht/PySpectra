#!/bin/env python
'''
cd /home/kracht/Misc/pySpectra
python -m unittest discover -v

python ./test/testTangoIfc.py testTangoIfc.testMoveMotorStart
python ./test/testTangoIfc.py testTangoIfc.testMoveMotorNameList
python ./test/testTangoIfc.py testTangoIfc.testMoveScanInfo

'''
import sys
#pySpectraPath = "/home/kracht/Misc/pySpectra"

import PySpectra
import PySpectra.tangoIfc as tangoIfc
import PySpectra.zmqIfc as zmqIfc
import PySpectra.utils as utils
import PySpectra.GQE as GQE
import numpy as np
import unittest
import PyTango
import time, os

class testTangoIfc( unittest.TestCase):

    @classmethod
    def setUpClass( testTangoIfc):
        pass

    @classmethod
    def tearDownClass( testTangoIfc): 
        PySpectra.close()

    def testMoveMotorStart( self) : 
        import random
        print "testTangoIfc.testMoveMotorTangoIfc"

        if utils.getHostname() != 'haso107tk': 
            return 

        PySpectra.cls()
        GQE.delete()
        GQE.setTitle( "watch arrows (setPoint, current) while moving a motor forth and back")
        g = utils.createGauss( name = "gauss", xMin = -5., xMax = 5., nPts = 101, 
                               lineColor = 'red', x0 = 0., sigma = 1., amplitude = 1.)

        g.motorNameList = ["eh_mot66"]
        proxyPool = PyTango.DeviceProxy( g.motorNameList[0])
        proxy = PyTango.DeviceProxy( proxyPool.TangoDevice)
        POS = proxy.position + 1
        g.x += POS
        g.xMin += POS
        g.xMax += POS
        print( "testTangoIfc.testMoveMotorNameList: move %s to %g" % ( g.motorNameList[0], POS))
        tangoIfc.moveStart( g, POS, flagConfirm = False)
        g.display()
        g.setArrowSetPoint( POS)
        while proxy.state() != PyTango.DevState.ON:
            time.sleep( 0.5)
            g.updateArrowCurrent()

        POS -= 1
        print( "testTangoIfc.testMoveMotorNameList: move %s back to %g" % ( g.motorNameList[0], POS))
        tangoIfc.moveStart( g, POS, flagConfirm = False)
        g.setArrowSetPoint( POS)
        while proxy.state() != PyTango.DevState.ON:
            time.sleep( 0.5)
            g.updateArrowCurrent()

        return 

    def testMoveMotorNameList( self) : 
        import random
        print "testTangoIfc.testMoveMotorNameList"


        if utils.getHostname() != 'haso107tk': 
            return 

        PySpectra.cls()
        GQE.delete()
        GQE.setTitle( "watch arrows while a motor is tangoIfc.move()ed")
        g = utils.createGauss( name = "gauss", xMin = -5., xMax = 5., nPts = 101, 
                               lineColor = 'red', x0 = 0., sigma = 1., amplitude = 1.)

        g.motorNameList = ["eh_mot66"]
        proxyPool = PyTango.DeviceProxy( g.motorNameList[0])
        proxy = PyTango.DeviceProxy( proxyPool.TangoDevice)
        POS = proxy.position + 1
        g.x += POS
        g.xMin += POS
        g.xMax += POS
        print( "testTangoIfc.testMoveMotorNameList: move %s to %g" % ( g.motorNameList[0], POS))
        tangoIfc.move( g, POS, flagConfirm = False)

        POS -= 1
        print( "testTangoIfc.testMoveMotorNameList: move %s back to %g" % ( g.motorNameList[0], POS))
        tangoIfc.move( g, POS, flagConfirm = False)

        return 

    def testMoveScanInfo( self) : 

        print "testTangoIfc.testMoveScanInfo"

        PySpectra.cls()
        GQE.delete()

        #
        # see, if the pyspMonitor process exists. Otherwise launch it
        #
        ( status, wasLaunched) = zmqIfc.assertPyspMonitorRunning()
        if not status:
            print( "testTangoIfc.testMoveScanInfo: failed to launch the pyspMonitor")
            return 

        #
        # move the motors to good starting points
        #
        if not utils.runMacro( "umv eh_mot66 50 eh_mot67 12"):
            print( "testTangoIfc.testMoveScanInfo: ruNMacro failed")
            return 
        #
        # to the a2scan
        #
        if not utils.runMacro( "a2scan eh_mot66 50 51 eh_mot67 12 13 40 0.1"): 
            print( "testTangoIfc.testMoveScanInfo: ruNMacro failed")
            return 
        #
        # the pyspMonitor may still by 'scanning' although
        # we see that the scan is over. So test 'isAlive'
        #
        count = 0
        while 1: 
            ret = zmqIfc.toPyspMonitor( { 'isAlive': True})
            if ret[ 'result'] == 'done':
                break
            count += 1
            time.sleep( 0.5)
            if count > 5: 
                print( "testTangoIfc.testMoveScanInfo: isAlive failes")
                return 

        ret = zmqIfc.toPyspMonitor( { 'command': 'display sig_gen'})
        if ret[ 'result'] != 'done': 
            print( "testTangoIfc.testMoveScanInfo: 'display sig_gen' failed, %s" % repr( ret))
            return 

        GQE.setTitle( "umv; a2scan; moveStart sig_gen 50.5 False")
        if zmqIfc.toPyspMonitor( { 'command': 'moveStart sig_gen 50.5 False'})[ 'result'] != 'done':
            print( "testTangoIfc.testMoveScanInfo: moveStart failed failed")
            return 

        while 1: 
            if zmqIfc.toPyspMonitor( { 'getDoorState': True})[ 'result'] == 'ON':
                break
            time.sleep( 0.5)
        
        if wasLaunched:
            print( "testTangoIfc.testMoveScanInfo: kill pyspMonitor.py") 
            os.system( "kill_proc -f pyspMonitor.py")
        
        return 
        

if __name__ == "__main__":
    unittest.main()
