#!/bin/env python
'''
cd /home/kracht/Misc/pySpectra
python -m unittest discover -v

python ./test/graphics/testGraphics.py testGraphics.testDisplaySingle
'''
import sys
pySpectraPath = "/home/kracht/Misc/pySpectra"
sys.path.append( pySpectraPath)

import PySpectra
import numpy as np
import unittest
import time, sys
import math 

class testGraphics( unittest.TestCase):

    def testDisplaySingle( self): 

        PySpectra.cls()
        PySpectra.delete()

        sinus = PySpectra.Scan( name = 'sinus', xMin = 0., 
                                xMax = 6.0, nPts = 101, dType = np.float64,
                                at = (2,2,3), color = 'red', style = 'solidLine')
        sinus.y = np.sin( sinus.y)
        PySpectra.display( ['sinus'])
        PySpectra.show()
        PySpectra.procEventsLoop()

    def testDisplayTwo( self): 

        PySpectra.cls()
        PySpectra.delete()

        sinus = PySpectra.Scan( name = 'sinus', xMin = 0., 
                                xMax = 6.0, nPts = 101, dType = np.float64,
                                width = 5., 
                                color = 'red', style = 'dashLine')
        sinus.y = np.sin( sinus.y)

        cosinus = PySpectra.Scan( name = "cosinus", xMin = 0., 
                                  xMax = 6.0, nPts = 101, dType = np.float64,
                                  width = 3., 
                                  color = 'blue', 
                                  style = 'dotLine')
        cosinus.y = np.cos( cosinus.y)

        PySpectra.display()
        PySpectra.show()
        PySpectra.procEventsLoop()


    def testOverlay( self): 

        PySpectra.cls()
        PySpectra.delete()

        sinus = PySpectra.Scan( name = 'sinus', xMin = 0., 
                                xMax = 6.0, nPts = 101, dType = np.float64,
                                width = 5., 
                                color = 'red', style = 'dashLine')
        sinus.y = np.sin( sinus.y)

        tan = PySpectra.Scan( name = 'tangens', xMin = 0., 
                              xMax = 6.0, nPts = 101, dType = np.float64,
                              width = 2., 
                              color = 'green', style = 'dashLine')
        tan.y = np.tan( tan.y)
        #
        # cosinus has to be plotted in the same viewport as sinus
        #
        cosinus = PySpectra.Scan( name = "cosinus", xMin = 0., 
                                  xMax = 6.0, nPts = 101, dType = np.float64,
                                  width = 3., 
                                  color = 'blue', 
                                  overlay = "sinus", 
                                  style = 'dotLine')
        self.assertEqual( cosinus.overlay, 'sinus')

        cosinus.y = np.cos( cosinus.y)
        #
        # cossquare has to be plotted in the same viewport as tangens
        #
        cossquare = PySpectra.Scan( name = "cossquare", xMin = 0., 
                                    xMax = 6.0, nPts = 101, dType = np.float64,
                                    yMin = -5, yMax = 5., 
                                    width = 1., 
                                    overlay = 'tangens', 
                                    color = 'blue', 
                                    style = 'dotLine')
        self.assertEqual( cossquare.overlay, 'tangens')

        cossquare.y = np.cos( tan.x) * np.cos( tan.x)

        PySpectra.display()
        PySpectra.show()
        PySpectra.procEventsLoop()


    def testDisplayFour( self): 

        PySpectra.cls()
        PySpectra.delete()

        for i in range( 1, 5):
            s = PySpectra.Scan( name = 't%d' % i, xMin = 0., 
                                xMax = 6.0, nPts = 101, dType = np.float64,
                                xLabel = 'rad', yLabel = 'Signal', 
                                at = (2,2,3), color = 'red', style = 'solidLine',
                                width = 2.)
            s.y = np.tan( s.y)

        PySpectra.display()

        PySpectra.show()

        PySpectra.procEventsLoop()

    def testDisplayMany( self): 

        PySpectra.cls()
        PySpectra.delete()

        for i in range( 1, 20):
            s = PySpectra.Scan( name = 't%d' % i, xMin = 0., 
                                xMax = 6.0, nPts = 101, dType = np.float64,
                                xLabel = 'rad', yLabel = 'Signal', 
                                at = (2,2,3), color = 'red', style = 'solidLine',
                                width = 2.)
            s.y = np.tan( s.y)

        PySpectra.display()

        PySpectra.show()

        PySpectra.procEventsLoop()

    def testFastDisplay_v1( self):
        '''
        version 1: set the scan data and call display
        '''
        PySpectra.cls()
        PySpectra.delete()
        scan1 = PySpectra.Scan( name = 't1', nPts = 1000, yMin = -1., yMax = 1.)
        scan2 = PySpectra.Scan( name = 't2', nPts = 1000, yMin = -1., yMax = 1.)

        PySpectra.display()

        data = np.random.normal(size=(10,1000))
        x  = np.linspace( 0., 10., 1000)
        ptr = 0

        scan1.x = x
        scan2.x = x
        
        startTime = time.time()
        for i in range( 500):
            scan1.y = data[ptr%10]
            scan2.y = data[ptr%10]
            PySpectra.display()
            ptr += 1
            PySpectra.processEvents()

        diffTime = time.time() - startTime
        self.assertLess( diffTime, 5.)

    def testFastDisplay_v2( self):
        '''
        version 2: directly use the plotDataItem.setData() function
        '''
        PySpectra.cls()
        PySpectra.delete()
        scan1 = PySpectra.Scan( name = 't1', nPts = 1000, yMin = -1., yMax = 1.)
        scan2 = PySpectra.Scan( name = 't2', nPts = 1000, yMin = -1., yMax = 1.)

        data = np.random.normal(size=(10,1000))
        x  = np.linspace( 0., 10., 1000)
        ptr = 0

        scan1.x = x
        scan2.x = x
        
        scan1.y = data[0]
        scan2.y = data[0]
        PySpectra.display()

        startTime = time.time()
        for i in range( 500):
            scan1.plotDataItem.setData(x, data[ptr%10])
            scan2.plotDataItem.setData(x, data[ptr%10])
            ptr += 1
            PySpectra.processEvents()

        diffTime = time.time() - startTime
        self.assertLess( diffTime, 5.)

if __name__ == "__main__":
    unittest.main()
