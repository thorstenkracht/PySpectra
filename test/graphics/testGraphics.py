#!/bin/env python
'''
cd /home/kracht/Misc/pySpectra
python -m unittest discover -v

python ./test/graphics/testGraphics.py testGraphics.testDisplayScan
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

    def testDoty( self): 
        '''
        using showGridX, showGridY
        '''
        print "testGrphics.testDoty"

        PySpectra.cls()
        PySpectra.delete()
        PySpectra.setTitle( "check x-axis doty")

        sinus = PySpectra.Scan( name = 'sinus', 
                                xMin = 0., xMax = 6.0, nPts = 101, lineColor = 'red', doty = True)
        sinus.y = np.sin( sinus.y)

        PySpectra.display()
        PySpectra.show()
        PySpectra.procEventsLoop()

        print "testGrphics.testDoty, DONE"

    def testGrid( self): 
        '''
        using showGridX, showGridY
        '''
        print "testGrphics.testGrid"
        PySpectra.cls()
        PySpectra.delete()
        PySpectra.setTitle( "check grids")

        sinus = PySpectra.Scan( name = 'sinus', 
                                xMin = 0., showGridX = True, xMax = 6.0, nPts = 101, lineColor = 'red')
        cos = PySpectra.Scan( name = 'cos', 
                                xMin = 0., showGridY = True, xMax = 6.0, nPts = 101, lineColor = 'red')
        tan = PySpectra.Scan( name = 'tan', 
                                xMin = 0., showGridY = True, showGridX = True, xMax = 6.0, nPts = 101, lineColor = 'red')
        sinus.y = np.sin( sinus.y)
        cos.y = np.cos( cos.y)
        tan.y = np.tan( tan.y)

        PySpectra.display()
        PySpectra.show()
        PySpectra.procEventsLoop()

        print "testGrphics.testGrid, DONE"

    def testDisplayScan_v1( self): 
        '''
        using setX and setY
        '''
        print "testGrphics.testDisplayScan_v1"
        PySpectra.cls()
        PySpectra.delete()

        sinus = PySpectra.Scan( name = 'sinus', xMin = 0., xMax = 6.0, nPts = 101, lineColor = 'red')
        for i in range( sinus.nPts): 
            sinus.setX( i, i/10.)
            sinus.setY( i, math.sin( i/10.))
            PySpectra.display( ['sinus'])
            time.sleep( 0.01)
        print "testGrphics.testDisplayScan_v1, DONE"

    def testDisplayScan_v2( self): 
        '''
        using setY only
        '''
        print "testGrphics.testDisplayScan_v2"
        PySpectra.cls()
        PySpectra.delete() 
        cosinus = PySpectra.Scan( name = 'cosinus', xMin = 0., 
                                xMax = 6.0, nPts = 101, lineColor = 'blue')
        for i in range( cosinus.nPts): 
            cosinus.setY( i, math.cos( cosinus.x[i]))
            PySpectra.display( ['cosinus'])
            time.sleep( 0.01)
        print "testGrphics.testDisplayScan_v2, DONE"

    def testDisplayScan_v3( self): 
        '''
        using setX and setY
        '''
        print "testGrphics.testDisplayScan_v3"
        PySpectra.cls()
        PySpectra.delete()

        sinus = PySpectra.Scan( name = 'sinus', xMin = 0., xMax = 6.0, nPts = 101, lineColor = 'red')
        cosinus = PySpectra.Scan( name = 'cosinus', xMin = 0., xMax = 6.0, nPts = 101, lineColor = 'blue')
        for i in range( sinus.nPts): 
            sinus.setX( i, i/10.)
            sinus.setY( i, math.sin( i/10.))
            cosinus.setX( i, i/10.)
            cosinus.setY( i, math.cos( i/10.))
            PySpectra.display( ['sinus', 'cosinus'])
            time.sleep( 0.01)

        print "testGrphics.testDisplayScan_v3, DONE"

    def testDisplayScan_v4( self): 
        '''
        using setX and setY, autorangeX
        '''
        print "testGrphics.testDisplayScan_v4"
        PySpectra.cls()
        PySpectra.delete()

        sinus = PySpectra.Scan( name = 'sinus', xMin = 0., xMax = 100.0, nPts = 101, lineColor = 'red',
                                autorangeX = True)
        for i in range( sinus.nPts): 
            sinus.setX( i, i/10.)
            sinus.setY( i, math.sin( i/10.))
            PySpectra.display( ['sinus'])
            time.sleep( 0.01)
        print "testGrphics.testDisplayScan_v4, DONE"

    def testDisplaySingle( self): 

        print "testGrphics.testDisplaySingle"
        PySpectra.cls()
        PySpectra.delete()

        sinus = PySpectra.Scan( name = 'sinus', xMin = 0., 
                                xMax = 6.0, nPts = 101, dType = np.float64,
                                at = (2,2,3), lineColor = 'red', lineStyle = 'solidLine')

        sinus.y = np.sin( sinus.y)
        PySpectra.display( ['sinus'])
        PySpectra.show()
        PySpectra.procEventsLoop()

        print "testGrphics.testDisplaySingle"

    def testDisplaySymbol( self): 

        print "testGrphics.testDisplaySymbol"

        PySpectra.cls()
        PySpectra.delete()

        sinus = PySpectra.Scan( name = 'sinus', xMin = 0., 
                                xMax = 6.0, nPts = 101, dType = np.float64,
                                at = (2,2,3), symbolColor = 'red', symbol = 'o', symbolSize = 10)

        sinus.y = np.sin( sinus.y)
        PySpectra.display( ['sinus'])
        PySpectra.show()
        PySpectra.procEventsLoop()

        print "testGrphics.testDisplaySymbol. DONE"

    def testDisplayTwo( self): 

        print "testGrphics.testDisplayTwo"

        PySpectra.cls()
        PySpectra.delete()

        sinus = PySpectra.Scan( name = 'sinus', xMin = 0., 
                                xMax = 6.0, nPts = 101, dType = np.float64,
                                lineWidth = 5., 
                                lineColor = 'red', lineStyle = 'dashLine')
        sinus.y = np.sin( sinus.y)

        cosinus = PySpectra.Scan( name = "cosinus", xMin = 0., 
                                  xMax = 6.0, nPts = 101, dType = np.float64,
                                  lineWidth = 3., 
                                  lineColor = 'blue', 
                                  lineStyle = 'dotLine')
        cosinus.y = np.cos( cosinus.y)

        PySpectra.display()
        PySpectra.show()
        PySpectra.procEventsLoop()

        print "testGrphics.testDisplayTwo, DONE"

    def testOverlay( self): 

        print "testGrphics.testOverlay"

        PySpectra.cls()
        PySpectra.delete()

        sinus = PySpectra.Scan( name = 'sinus', xMin = 0., 
                                xMax = 6.0, nPts = 101, dType = np.float64,
                                lineWidth = 5., 
                                lineColor = 'red', lineStyle = 'dashLine')
        sinus.y = np.sin( sinus.y)

        tan = PySpectra.Scan( name = 'tangens', xMin = 0., 
                              xMax = 6.0, nPts = 101, dType = np.float64,
                              lineWidth = 2., 
                              lineColor = 'green', lineStyle = 'dashLine')
        tan.y = np.tan( tan.y)
        #
        # cosinus has to be plotted in the same viewport as sinus
        #
        cosinus = PySpectra.Scan( name = "cosinus", xMin = 0., 
                                  xMax = 6.0, nPts = 101, dType = np.float64,
                                  lineWidth = 3., 
                                  lineColor = 'blue', 
                                  overlay = "sinus", 
                                  lineStyle = 'dotLine')
        self.assertEqual( cosinus.overlay, 'sinus')

        cosinus.y = np.cos( cosinus.y)
        #
        # cossquare has to be plotted in the same viewport as tangens
        #
        cossquare = PySpectra.Scan( name = "cossquare", xMin = 0., 
                                    xMax = 6.0, nPts = 101, dType = np.float64,
                                    yMin = -5, yMax = 5., 
                                    lineWidth = 1., 
                                    overlay = 'tangens', 
                                    lineColor = 'blue', 
                                    lineStyle = 'dotLine')
        self.assertEqual( cossquare.overlay, 'tangens')

        cossquare.y = np.cos( tan.x) * np.cos( tan.x)

        PySpectra.display()
        PySpectra.show()
        PySpectra.procEventsLoop()

        print "testGrphics.testOverlay, DONE"

    def testDisplayFour( self): 

        print "testGrphics.testDisplayFour"

        PySpectra.cls()
        PySpectra.delete()

        for i in range( 1, 5):
            s = PySpectra.Scan( name = 't%d' % i, xMin = 0., 
                                xMax = 6.0, nPts = 101, dType = np.float64,
                                xLabel = 'rad', yLabel = 'Signal', 
                                at = (2,2,i), lineColor = 'red', lineStyle = 'solidLine',
                                lineWidth = 2.)
            s.y = np.tan( s.y)

        PySpectra.display()

        PySpectra.show()

        PySpectra.procEventsLoop()

        print "testGrphics.testDisplayFour, DONE"

    def testDisplayMany( self): 

        print "testGrphics.testDisplayMany"

        PySpectra.cls()
        PySpectra.delete()

        for i in range( 1, 20):
            s = PySpectra.Scan( name = 't%d' % i, xMin = 0., 
                                xMax = 6.0, nPts = 101, dType = np.float64,
                                xLabel = 'rad', yLabel = 'Signal', 
                                at = (5,4,i), lineColor = 'red', lineStyle = 'solidLine',
                                lineWidth = 2.)
            s.y = np.tan( s.y)

        PySpectra.display()

        PySpectra.show()

        PySpectra.procEventsLoop()

        print "testGrphics.testDisplayMany, DONE"

    def testFastDisplay_v1( self):
        '''
        version 1: set the scan data and call display
        '''

        print "testGrphics.testDisplay_v1"

        PySpectra.cls()
        PySpectra.delete()
        scan1 = PySpectra.Scan( name = 't1', nPts = 1000, yMin = -1., yMax = 1.)
        scan2 = PySpectra.Scan( name = 't2', nPts = 1000, yMin = -1., yMax = 1.)

        PySpectra.display()

        data = np.random.normal(size=(10,100))
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

        print "testGrphics.testDisplay_v1, DONE"

    def testFastDisplay_v2( self):
        '''
        version 2: directly use the plotDataItem.setData() function
        '''
        print "testGrphics.testDisplay_v2"

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
        self.assertLess( diffTime, 7.)
        print "testGrphics.testDisplay_v2, DONE"

if __name__ == "__main__":
    unittest.main()
