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
        '''
        This test case produces this error, maybe it is related to the fact
        that the derivative is from 0.025 to 9.975 and one point less.

        Traceback (most recent call last):
        File "/usr/lib/python2.7/dist-packages/pyqtgraph/graphicsItems/AxisItem.py", line 412, in paint
        specs = self.generateDrawSpecs(painter)
        File "/usr/lib/python2.7/dist-packages/pyqtgraph/graphicsItems/AxisItem.py", line 819, in generateDrawSpecs
        textSize2 = np.max([r.height() for r in textRects])
        File "/usr/lib/python2.7/dist-packages/numpy/core/fromnumeric.py", line 2125, in amax
        out=out, keepdims=keepdims)
        File "/usr/lib/python2.7/dist-packages/numpy/core/_methods.py", line 17, in _amax
        out=out, keepdims=keepdims)
        ValueError: zero-size array to reduction operation maximum which has no identity
        '''

        print "testCalc.testDerivative"

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

        print "testCalc.testDerivative, DONE"
        
    def testAntiDerivative( self):

        print "testCalc.testAntiDerivative"

        PySpectra.cls()
        PySpectra.delete()
        scan = PySpectra.Scan( name = "t1", xMin = 0., xMax = 10.0, nPts = 201)
        scan.y = np.sin( scan.y)
        PySpectra.antiderivative( name = scan.name, nameNew = "t1_ad")
        PySpectra.display()
        PySpectra.show()
        PySpectra.procEventsLoop()

        print "testCalc.testAntiDerivative, DONE"

    def testYToMinusY( self):

        print "testCalc.testYToMinusY"

        PySpectra.cls()
        PySpectra.delete()
        scan = PySpectra.Scan( name = "t1", xMin = 0., xMax = 10.0, nPts = 201)
        scan.y = np.sin( scan.y)
        PySpectra.yToMinusY( name = scan.name, nameNew = "t1_y2MinusY")
        PySpectra.display()
        PySpectra.show()
        PySpectra.procEventsLoop()

        print "testCalc.testYToMinusY, DONE"

if __name__ == "__main__":
    unittest.main()
