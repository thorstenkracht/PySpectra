#!/bin/env python
'''
cd /home/kracht/Misc/pySpectra
python -m unittest discover -v

python ./test/dMgt/testCalc.py testCalc.testYToMinusY
python ./test/dMgt/testCalc.py testCalc.testDerivative
python ./test/dMgt/testCalc.py testCalc.testDerivativeAntiDerivative
'''
import sys
sys.path.append( "/home/kracht/Misc/pySpectra")

import PySpectra
import numpy as np
import unittest
import time, sys
import math 

class testCalc( unittest.TestCase):

    @classmethod
    def setUpClass( testCalc):
        pass

    @classmethod
    def tearDownClass( testCalc): 
        PySpectra.close()

    def testYToMinusY( self):

        print "testCalc.testYToMinusY"

        PySpectra.cls()
        PySpectra.dMgt.GQE.delete()
        scan = PySpectra.dMgt.GQE.Scan( name = "t1", xMin = 2., xMax = 10.0, nPts = 201)
        scan.y = np.sin( scan.y)
        scanMY = PySpectra.dMgt.calc.yToMinusY( name = scan.name, nameNew = "t1_y2MinusY")

        self.assertEqual( len( scan.y), len( scanMY.y))
        self.assertEqual( len( scan.x), len( scanMY.x))
        
        for i in range( len( scan.y)):
            self.assertEqual( scan.y[i], - scanMY.y[i])
            self.assertEqual( scan.x[i], scanMY.x[i])
        
        PySpectra.display()
        #PySpectra.show()
        PySpectra.procEventsLoop( 1)

        print "testCalc.testYToMinusY, DONE"
        
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
        PySpectra.dMgt.GQE.delete()
        scan = PySpectra.dMgt.GQE.Scan( name = "t1", xMin = 0., xMax = 10.0, nPts = 201)
        scan.y = np.sin( scan.y)
        PySpectra.dMgt.calc.derivative( name = scan.name, nameNew = "t1_d")
        PySpectra.display()
        #PySpectra.show()
        PySpectra.procEventsLoop( 1)

        PySpectra.cls()
        PySpectra.dMgt.GQE.delete()
        scan = PySpectra.dMgt.GQE.Scan( name = "t1", xMin = 0., xMax = 10.0, nPts = 201)
        scan.y = np.cos( scan.y)
        PySpectra.dMgt.calc.derivative( name = scan.name)
        PySpectra.display()
        #PySpectra.show()
        PySpectra.procEventsLoop( 1)

        PySpectra.cls()
        PySpectra.dMgt.GQE.delete()
        scan = PySpectra.dMgt.GQE.Scan( name = "t1", xMin = 0., xMax = 10.0, nPts = 201)
        scan.y = np.tan( scan.y)
        PySpectra.dMgt.calc.derivative( scan.name, "t1_d")
        PySpectra.display()
        #PySpectra.show()
        PySpectra.procEventsLoop( 1)

        print "testCalc.testDerivative, DONE"
        
    def testAntiDerivative( self):

        print "testCalc.testAntiDerivative"

        PySpectra.cls()
        PySpectra.dMgt.GQE.delete()
        scan = PySpectra.dMgt.GQE.Scan( name = "t1", xMin = 0., xMax = 10.0, nPts = 201)
        scan.y = np.sin( scan.y)
        PySpectra.dMgt.calc.antiderivative( name = scan.name, nameNew = "t1_ad")
        PySpectra.display()
        #PySpectra.show()
        PySpectra.procEventsLoop( 1)

        print "testCalc.testAntiDerivative, DONE"
        
    def testDerivativeAntiDerivative( self):

        print "testCalc.testDerivativeAntiDerivative"

        PySpectra.cls()
        PySpectra.dMgt.GQE.delete()
        scan = PySpectra.dMgt.GQE.Scan( name = "t1", xMin = 0., xMax = 10.0, nPts = 201)
        scan.y = np.sin( scan.y)
        derivative = PySpectra.dMgt.calc.derivative( name = scan.name, nameNew = "t1_d")
        stamm = PySpectra.dMgt.calc.antiderivative( name = derivative.name, nameNew = "t1_ad")

        self.assertEqual( len( scan.y), len( stamm.y))
        self.assertEqual( len( scan.x), len( stamm.x))
        
        for i in range( len( scan.y)):
            self.assertEqual( scan.x[i], stamm.x[i])
        
        diff = 0.
        for i in range( len( scan.y) - 1):
            diff = diff + math.fabs( scan.y[i] - stamm.y[i])

        self.assertLess( diff, 0.08)

        stamm.lineColor = 'blue'
        PySpectra.dMgt.GQE.delete( "t1_d")

        PySpectra.dMgt.GQE.overlay( "t1_ad", "t1") 

        PySpectra.cls()
        PySpectra.display()

        #PySpectra.launchGui()
        PySpectra.procEventsLoop( 3)

        print "testCalc.testDerivativeAntiDerivative, DONE"

if __name__ == "__main__":
    unittest.main()
