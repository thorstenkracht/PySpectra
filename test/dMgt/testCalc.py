#!/bin/env python
'''
cd /home/kracht/Misc/pySpectra
python -m unittest discover -v

python ./test/dMgt/testCalc.py testCalc.testDerivative
'''
import sys
sys.path.append( "/home/kracht/Misc/pySpectra")

import PySpectra
import numpy as np
import unittest
import time, sys
import math 

class testCalc( unittest.TestCase):
        
    def testDerivative( self):

        PySpectra.cls()
        PySpectra.delete()
        scan = PySpectra.Scan( name = "t1", xMin = 0., xMax = 10.0, nPts = 201)
        scan.y = np.sin( scan.y)
        PySpectra.derivative( name = scan.name, nameNew = "t1_d")
        PySpectra.display()
        PySpectra.show()
        PySpectra.procEventsLoop()

        PySpectra.cls()
        PySpectra.delete()
        scan = PySpectra.Scan( name = "t1", xMin = 0., xMax = 10.0, nPts = 201)
        scan.y = np.cos( scan.y)
        PySpectra.derivative( name = scan.name)
        PySpectra.display()
        PySpectra.show()
        PySpectra.procEventsLoop()

        PySpectra.cls()
        PySpectra.delete()
        scan = PySpectra.Scan( name = "t1", xMin = 0., xMax = 10.0, nPts = 201)
        scan.y = np.tan( scan.y)
        PySpectra.derivative( scan.name, "t1_d")
        PySpectra.display()
        PySpectra.show()
        PySpectra.procEventsLoop()

    def testAntiDerivative( self):

        PySpectra.cls()
        PySpectra.delete()
        scan = PySpectra.Scan( name = "t1", xMin = 0., xMax = 10.0, nPts = 201)
        scan.y = np.sin( scan.y)
        PySpectra.antiderivative( name = scan.name, nameNew = "t1_ad")
        PySpectra.display()
        PySpectra.show()
        PySpectra.procEventsLoop()

    def testYToMinusY( self):

        PySpectra.cls()
        PySpectra.delete()
        scan = PySpectra.Scan( name = "t1", xMin = 0., xMax = 10.0, nPts = 201)
        scan.y = np.sin( scan.y)
        PySpectra.yToMinusY( name = scan.name, nameNew = "t1_y2MinusY")
        PySpectra.display()
        PySpectra.show()
        PySpectra.procEventsLoop()

if __name__ == "__main__":
    unittest.main()
