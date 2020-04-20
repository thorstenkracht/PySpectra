#!/bin/env python
'''
cd /home/kracht/Misc/pySpectra
python -m unittest discover -v

python ./test/testSpock.py testSpock.testMoveMotor

'''
import sys
#pySpectraPath = "/home/kracht/Misc/pySpectra"

import PySpectra
import PySpectra.misc.tangoIfc as tangoIfc
import PySpectra.dMgt.GQE as GQE
import numpy as np
import unittest
import PyTango
import HasyUtils
import time, os

class testSpock( unittest.TestCase):

    @classmethod
    def setUpClass( testSpock):
        pass

    @classmethod
    def tearDownClass( testSpock): 
        PySpectra.close()

    def testMoveMotor( self) : 
        print "testSpock.testMoveMotor"

        PySpectra.cls()
        GQE.delete()
        g = GQE.Scan( name = "gauss", xMin = -5., xMax = 5., nPts = 101)
        mu = 0.
        sigma = 1.
        g.y = 1/(sigma*np.sqrt(2.*np.pi))*np.exp( -(g.y-mu)**2/(2*sigma**2))

        g.motorNameList = ["eh_mot66"]
        proxyPool = PyTango.DeviceProxy( g.motorNameList[0])
        proxy = PyTango.DeviceProxy( proxyPool.TangoDevice)
        POS = proxy.position + 1
        g.x += POS
        g.xMin += POS
        g.xMax += POS
        print( "testSpock.testMoveMotorNameList: move %s to %g" % ( g.motorNameList[0], POS))
        tangoIfc.move( g, POS)

        POS -= 1
        print( "testSpock.testMoveMotorNameList: move %s back to %g" % ( g.motorNameList[0], POS))
        tangoIfc.move( g, POS)

        PySpectra.processEventsLoop( 1)

        return 

if __name__ == "__main__":
    unittest.main()
