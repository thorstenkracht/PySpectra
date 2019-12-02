#!/bin/env python
'''
cd /home/kracht/Misc/pySpectra
python -m unittest discover -v

python ./test/graphics/testGraphics.py testGraphics.testClose
python ./test/graphics/testGraphics.py testGraphics.testDoty
python ./test/graphics/testGraphics.py testGraphics.testGrid
python ./test/graphics/testGraphics.py testGraphics.testScanning
python ./test/graphics/testGraphics.py testGraphics.testScanningWithText
python ./test/graphics/testGraphics.py testGraphics.testScanningTwoPlots
python ./test/graphics/testGraphics.py testGraphics.testScanningAutoscaleX
python ./test/graphics/testGraphics.py testGraphics.testScanningReverse
python ./test/graphics/testGraphics.py testGraphics.testScanningReverseAutoscaleX
python ./test/graphics/testGraphics.py testGraphics.testDisplaySingleWithText
python ./test/graphics/testGraphics.py testGraphics.testDisplaySymbol
python ./test/graphics/testGraphics.py testGraphics.testDisplayTwo
python ./test/graphics/testGraphics.py testGraphics.testOverlay
python ./test/graphics/testGraphics.py testGraphics.testDisplayFour
python ./test/graphics/testGraphics.py testGraphics.testDisplayMany
python ./test/graphics/testGraphics.py testGraphics.testDisplayVeryMany
python ./test/graphics/testGraphics.py testGraphics.testFastDisplay_v1
python ./test/graphics/testGraphics.py testGraphics.testFastDisplay_v2
python ./test/graphics/testGraphics.py testGraphics.testWsViewport
python ./test/graphics/testGraphics.py testGraphics.testLissajous
python ./test/graphics/testGraphics.py testGraphics.testOverlay2BothLog
python ./test/graphics/testGraphics.py testGraphics.testOverlay2FirstLog
python ./test/graphics/testGraphics.py testGraphics.testOverlay2SecondLog
python ./test/graphics/testGraphics.py testGraphics.testImageMB1
python ./test/graphics/testGraphics.py testGraphics.testImageMB2
python ./test/graphics/testGraphics.py testGraphics.testToPysp1
'''
import sys
pySpectraPath = "/home/kracht/Misc/pySpectra"
sys.path.append( pySpectraPath)

import PySpectra
import pyqtgraph as pg
import numpy as np
import unittest
import time, sys
import math 

class testGraphics( unittest.TestCase):

    @classmethod
    def setUpClass( testGraphics):
        pass

    @classmethod
    def tearDownClass( testGraphics): 
        PySpectra.close()

    def testClose( self): 
        '''
        '''
        print "testGraphics.testClose"

        PySpectra.cls()
        PySpectra.delete()
        PySpectra.setTitle( "testing close()")

        sinus = PySpectra.Scan( name = 'sinus', 
                                xMin = 0., xMax = 6.0, nPts = 101, lineColor = 'red', doty = True)
        sinus.y = np.sin( sinus.y)

        PySpectra.display()
        PySpectra.procEventsLoop( 1)

        PySpectra.close()

        PySpectra.cls()
        PySpectra.delete()
        PySpectra.setTitle( "testing close(), again")

        sinus = PySpectra.Scan( name = 'sinus', 
                                xMin = 0., xMax = 6.0, nPts = 101, lineColor = 'red', doty = True)
        sinus.y = np.sin( sinus.y)

        PySpectra.display()
        PySpectra.procEventsLoop( 1)

        print "testGraphics.testClose, DONE"

    def testDoty( self): 
        '''
        using showGridX, showGridY
        '''
        print "testGraphics.testDoty"

        PySpectra.cls()
        PySpectra.delete()
        PySpectra.setTitle( "check x-axis doty")

        sinus = PySpectra.Scan( name = 'sinus', 
                                xMin = 0., xMax = 6.0, nPts = 101, lineColor = 'red', doty = True)
        sinus.y = np.sin( sinus.y)

        PySpectra.display()
        #PySpectra.show()
        PySpectra.procEventsLoop( 1)

        print "testGraphics.testDoty, DONE"

    def testGrid( self): 
        '''
        using showGridX, showGridY
        '''
        print "testGraphics.testGrid"
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
        #PySpectra.show()
        PySpectra.procEventsLoop( 1)

        print "testGraphics.testGrid, DONE"

    def testScanning( self): 
        '''
        using setX and setY
        '''
        print "testGraphics.testScanning"
        PySpectra.cls()
        PySpectra.delete()

        PySpectra.setTitle( "x-axis is not re-scaled")

        sinus = PySpectra.Scan( name = 'sinus', 
                                xMin = 0., xMax = 6.0, nPts = 101, autoscaleX = False, 
                                lineColor = 'red')
        for i in range( sinus.nPts): 
            sinus.setX( i, i/10.)
            sinus.setY( i, math.sin( i/10.))
            PySpectra.display( ['sinus'])
            time.sleep( 0.01)
        print "testGraphics.testScanning, DONE"

    def testScanningWithText( self): 
        '''
        using setX and setY
        '''
        print "testGraphics.testScanningWithText"
        PySpectra.cls()
        PySpectra.delete()

        PySpectra.setTitle( "x-axis is not re-scaled, watch text")

        scan = PySpectra.Scan( name = 'tangens', 
                               xMin = 0., xMax = 6.0, nPts = 101, 
                               autoscaleX = False, autoscaleY = True, 
                               lineColor = 'red')
        scan.addText( text = "a test text", x = 0.95, y = 0.9, hAlign = 'right', 
                       vAlign = 'center', fontSize = 18, color = 'red', NDC = True)
        for i in range( scan.nPts): 
            scan.setX( i, i/10.)
            scan.setY( i, math.tan( i/10.))
            PySpectra.display( ['tangens'])
            time.sleep( 0.02)
        print "testGraphics.testScanningWithText, DONE"

    def testScanningTwoPlots( self): 
        '''
        using setX and setY
        '''
        print "testGraphics.testScanningTwoPlots"
        PySpectra.cls()
        PySpectra.delete()

        PySpectra.setTitle( "two plot, x-axis is not re-scaled")

        sinus = PySpectra.Scan( name = 'sinus', xMin = 0., xMax = 6.0, nPts = 101, 
                                autoscaleX = False, 
                                lineColor = 'red')
        cosinus = PySpectra.Scan( name = 'cosinus', 
                                  xMin = 0., xMax = 6.0, nPts = 101, 
                                  autoscaleX = False, 
                                  lineColor = 'blue')
        for i in range( sinus.nPts): 
            sinus.setX( i, i/10.)
            sinus.setY( i, math.sin( i/10.))
            cosinus.setX( i, i/10.)
            cosinus.setY( i, math.cos( i/10.))
            PySpectra.display( ['sinus', 'cosinus'])
            time.sleep( 0.01)

        print "testGraphics.testScanningTwoPlots, DONE"

    def testScanningAutoscaleX( self): 
        '''
        using setX and setY
        '''
        print "testGraphics.testScanningAutoscaleX"
        PySpectra.cls()
        PySpectra.delete()

        PySpectra.setTitle( "autoscale of the x-axis")

        sinus = PySpectra.Scan( name = 'sinus', 
                                xMin = 0., xMax = 6.0, nPts = 101, 
                                autoscaleX = True, 
                                lineColor = 'red')
        for i in range( sinus.nPts): 
            sinus.setX( i, i/10.)
            sinus.setY( i, math.sin( i/10.))
            PySpectra.display( ['sinus'])
            time.sleep( 0.01)
        print "testGraphics.testScanningAutoscaleX, DONE"

    def testScanningReverse( self): 
        '''
        scanning in reverse direction
        '''
        print "testGraphics.testScanningReverse"
        PySpectra.cls()
        PySpectra.delete()

        PySpectra.setTitle( "reverse scan, no re-scale")

        sinus = PySpectra.Scan( name = 'sinus', 
                                xMin = 0., xMax = 6.0, nPts = 101, 
                                autoscaleX = False, 
                                lineColor = 'red')
        sinus.xMax = 10.
        for i in range( sinus.nPts): 
            x = 10. - i/10.
            sinus.setX( i, x)
            sinus.setY( i, math.sin( i/10.))
            PySpectra.display( ['sinus'])
            time.sleep( 0.01)
        print "testGraphics.testScanningReverse, DONE"

    def testScanningReverseAutoscaleX( self): 
        '''
        scanning in reverse direction
        '''
        print "testGraphics.testScanningReverseAutoscaleX"
        PySpectra.cls()
        PySpectra.delete()

        PySpectra.setTitle( "reverse scan, re-scale")

        sinus = PySpectra.Scan( name = 'sinus', 
                                xMin = 0., xMax = 6.0, nPts = 101, 
                                autoscaleX = True, 
                                lineColor = 'red')
        sinus.xMax = 10.
        for i in range( sinus.nPts): 
            x = 10. - i/10.
            sinus.setX( i, x)
            sinus.setY( i, math.sin( i/10.))
            PySpectra.display( ['sinus'])
            time.sleep( 0.01)
        print "testGraphics.testScanningReverseAutoscalX, DONE"

    def testDisplaySingleWithText( self): 
        '''
        spectra: 
          create/text/string=Text/x=0.95/y=0.95/v_align=1/h_align=3 1
        '''
        print "testGraphics.testDisplaySingleWithText"
        PySpectra.cls()
        PySpectra.delete()

        #PySpectra.setTitle( "this is the title text")
        #PySpectra.setComment( "this is a comment")
        sinus = PySpectra.Scan( name = 'sinus', xMin = -3., 
                                xMax = 3., nPts = 101, dType = np.float64,
                                xLabel = "x-Label", yLabel = "y-Label",
                                at = (2,2,3), lineColor = 'red', lineStyle = 'solid')
        sinus.addText( text = "a test text", x = 0.95, y = 0.9, hAlign = 'right', 
                       vAlign = 'center', fontSize = 18, color = 'red', NDC = True)
        sinus.y = np.sin( sinus.x)
        PySpectra.display( ['sinus'])
        #PySpectra.show()
        PySpectra.procEventsLoop( 1)

        print "testGraphics.testDisplaySingleWidhtText, DONE"

    def testDisplaySymbol( self): 

        print "testGraphics.testDisplaySymbol"

        PySpectra.cls()
        PySpectra.delete()

        sinus = PySpectra.Scan( name = 'sinus', xMin = 0., 
                                xMax = 6.0, nPts = 101, dType = np.float64,
                                at = (2,2,3), symbolColor = 'red', symbol = 'o', symbolSize = 10)

        sinus.y = np.sin( sinus.y)
        PySpectra.display( ['sinus'])
        #PySpectra.show()
        PySpectra.procEventsLoop( 1)

        print "testGraphics.testDisplaySymbol. DONE"

    def testDisplayTwo( self): 

        print "testGraphics.testDisplayTwo"

        PySpectra.cls()
        PySpectra.delete()

        sinus = PySpectra.Scan( name = 'sinus', xMin = 0., 
                                xMax = 6.0, nPts = 101, dType = np.float64,
                                lineWidth = 5., 
                                lineColor = 'red', lineStyle = 'dashed')
        sinus.y = np.sin( sinus.y)

        cosinus = PySpectra.Scan( name = "cosinus", xMin = 0., 
                                  xMax = 6.0, nPts = 101, dType = np.float64,
                                  lineWidth = 3., 
                                  lineColor = 'blue', 
                                  lineStyle = 'dotted')
        cosinus.y = np.cos( cosinus.y)

        PySpectra.display()
        #PySpectra.show()
        PySpectra.procEventsLoop( 1)

        print "testGraphics.testDisplayTwo, DONE"

    def testOverlay( self): 

        print "testGraphics.testOverlay"

        PySpectra.cls()
        PySpectra.delete()

        sinus = PySpectra.Scan( name = 'sinus', xMin = 0., 
                                xMax = 6.0, nPts = 101, dType = np.float64,
                                lineWidth = 5., 
                                lineColor = 'red', lineStyle = 'dashed')
        sinus.y = np.sin( sinus.y)

        tan = PySpectra.Scan( name = 'tangens', xMin = 0., 
                              xMax = 6.0, nPts = 101, dType = np.float64,
                              lineWidth = 2., 
                              lineColor = 'green', lineStyle = 'dashed')
        tan.y = np.tan( tan.y)
        #
        # cosinus has to be plotted in the same viewport as sinus
        #
        cosinus = PySpectra.Scan( name = "cosinus", xMin = 0., 
                                  xMax = 6.0, nPts = 101, dType = np.float64,
                                  lineWidth = 3., 
                                  lineColor = 'blue', 
                                  overlay = "sinus", 
                                  lineStyle = 'dotted')
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
                                    lineStyle = 'dotted')
        self.assertEqual( cossquare.overlay, 'tangens')

        cossquare.y = np.cos( tan.x) * np.cos( tan.x)

        PySpectra.display()
        #PySpectra.show()
        PySpectra.procEventsLoop( 1)

        print "testGraphics.testOverlay, DONE"

    def testDisplayFour( self): 

        print "testGraphics.testDisplayFour"

        PySpectra.cls()
        PySpectra.delete()

        for i in range( 1, 5):
            s = PySpectra.Scan( name = 't%d' % i, xMin = 0., 
                                xMax = 6.0, nPts = 101, dType = np.float64,
                                xLabel = 'rad', yLabel = 'Signal', 
                                at = (2,2,i), lineColor = 'red', lineStyle = 'solid',
                                lineWidth = 2.)
            s.y = np.tan( s.y)

        PySpectra.display()

        #PySpectra.show()

        PySpectra.procEventsLoop( 1)

        print "testGraphics.testDisplayFour, DONE"

    def testDisplayMany( self): 

        print "testGraphics.testDisplayMany"

        PySpectra.cls()
        PySpectra.delete()

        for i in range( 1, 20):
            s = PySpectra.Scan( name = 't%d' % i, xMin = 0., 
                                xMax = 6.0, nPts = 101, dType = np.float64,
                                xLabel = 'rad', yLabel = 'Signal', 
                                at = (5,4,i), lineColor = 'red', lineStyle = 'solid',
                                lineWidth = 2.)
            s.y = np.tan( s.y)

        PySpectra.display()

        #PySpectra.show()

        PySpectra.procEventsLoop( 1)

        print "testGraphics.testDisplayMany, DONE"

    def testDisplayVeryMany( self): 

        print "testGraphics.testDisplayMany"

        PySpectra.cls()
        PySpectra.delete()

        for i in range( 1, 50):
            s = PySpectra.Scan( name = 't%d' % i, xMin = 0., 
                                xMax = 6.0, nPts = 101, dType = np.float64,
                                xLabel = 'rad', yLabel = 'Signal', 
                                lineColor = 'red', lineStyle = 'solid',
                                lineWidth = 2.)
            s.y = np.tan( s.y)

        PySpectra.display()

        PySpectra.procEventsLoop( 1)

        print "testGraphics.testDisplayMany, DONE"

    def testFastDisplay_v1( self):
        '''
        version 1: set the scan data and call display
        '''

        print "testGraphics.testDisplay_v1"

        PySpectra.cls()
        PySpectra.delete()
        scan1 = PySpectra.Scan( name = 't1', nPts = 100, yMin = -1., yMax = 1.)
        scan2 = PySpectra.Scan( name = 't2', nPts = 100, yMin = -1., yMax = 1.)

        PySpectra.display()

        data = np.random.normal(size=(10,100))
        x  = np.linspace( 0., 10., 100)
        ptr = 0

        scan1.x = x
        scan2.x = x
        
        startTime = time.time()
        for i in range( 100):
            PySpectra.cls()
            scan1.y = data[ptr%10]
            scan2.y = data[ptr%10]
            PySpectra.display()
            ptr += 1
            PySpectra.processEvents()

        diffTime = time.time() - startTime
        self.assertLess( diffTime, 8.)
        self.assertGreater( diffTime, 3.)

        print "testGraphics.testDisplay_v1, DONE"

    def testFastDisplay_v2( self):
        '''
        version 2: directly use the plotDataItem.setData() function
        '''
        print "testGraphics.testDisplay_v2"

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
        for i in range( 200):
            scan1.plotDataItem.setData(x, data[ptr%10])
            scan2.plotDataItem.setData(x, data[ptr%10])
            ptr += 1
            PySpectra.processEvents()

        diffTime = time.time() - startTime

        self.assertLess( diffTime, 7.)
        self.assertGreater( diffTime, 2.0)
        print "testGraphics.testDisplay_v2, DONE"

    def testWsViewport( self):
        '''
        '''
        print "testGraphics.testWsViewport"

        PySpectra.cls()
        PySpectra.delete()
        PySpectra.setTitle( "go through the viewports")

        sinus = PySpectra.Scan( name = 'sinus', 
                                xMin = 0., xMax = 6.0, nPts = 101, lineColor = 'red', doty = True)
        sinus.y = np.sin( sinus.y)

        for elm in [ 'DINA4', 'DINA4P', 'DINA4S', 'DINA5', 'DINA5P', 'DINA5S', 
                     'DINA6', 'DINA6P', 'DINA6S']: 
            PySpectra.setWsViewport( elm)
            PySpectra.display()
            PySpectra.procEventsLoop( 1)

        print "testGraphics.testWsViewport, DONE"


    def testLissajous( self):
        '''

        '''
        print "testGraphics.testLissayous"

        PySpectra.cls()
        PySpectra.delete()
        scan = PySpectra.Scan( name = 'Lissajous', nPts = 1000, xMin = -1., xMax = 1.)

        x  = np.linspace( 0., 6.5, 1000)
        y  = np.linspace( 0., 6.5, 1000)

        scan.x = np.cos( x)
        scan.y = np.sin( y)

        PySpectra.display()

        startTime = time.time()
        for i in range( 500):
            x = x + 0.005
            scan.plotDataItem.setData(np.cos( x), np.sin( y))
            PySpectra.processEvents()

        diffTime = time.time() - startTime

        self.assertLess( diffTime, 12.)
        print "testGraphics.testLissajous, DONE"

    def testOverlay2BothLog( self):
        '''

        '''
        print "testGraphics.testOverly2BothLog"

        PySpectra.cls()
        PySpectra.delete()
        PySpectra.setTitle( "2 Overlay Scans, with log scale")
        g1 = PySpectra.Scan( name = "gauss", xMin = -5., xMax = 5., yLog = True, nPts = 101, lineColor = 'red')
        mu = 0.
        sigma = 1.
        g1.y = 1/(sigma*np.sqrt(2.*np.pi))*np.exp( -(g1.y-mu)**2/(2.*sigma**2))
        g2 = PySpectra.Scan( name = "gauss2", xMin = -5., xMax = 5., yMin = 0.001, yLog = True, 
                             yMax = 1., nPts = 101, lineColor = 'green')
        mu = 0.5
        sigma = 1.2
        g2.y = 1/(sigma*np.sqrt(2.*np.pi))*np.exp( -(g2.y-mu)**2/(2.*sigma**2))
        
        PySpectra.overlay( "gauss2", "gauss")
        PySpectra.display()
        PySpectra.procEventsLoop( 1)

    def testOverlay2FirstLog( self):
        '''

        '''
        print "testGraphics.testOverly2FirstLog"

        PySpectra.cls()
        PySpectra.delete()
        PySpectra.setTitle( "2 Overlay Scans, with log scale")
        g1 = PySpectra.Scan( name = "gauss", xMin = -5., xMax = 5., yLog = True, nPts = 101, lineColor = 'red')
        mu = 0.
        sigma = 1.
        g1.y = 1/(sigma*np.sqrt(2.*np.pi))*np.exp( -(g1.y-mu)**2/(2.*sigma**2))
        g2 = PySpectra.Scan( name = "gauss2", xMin = -5., xMax = 5., yMin = 0.001, yLog = False,
                             nPts = 101, lineColor = 'green')
        mu = 0.5
        sigma = 1.2
        g2.y = 1/(sigma*np.sqrt(2.*np.pi))*np.exp( -(g2.y-mu)**2/(2.*sigma**2))
        
        PySpectra.overlay( "gauss2", "gauss")
        PySpectra.display()
        PySpectra.procEventsLoop( 1)

        print "testGraphics.testOverly2FirstLog DONE"

    def testOverlay2SecondLog( self):
        '''

        '''
        print "testGraphics.testOverly2SecondLog"

        PySpectra.cls()
        PySpectra.delete()
        PySpectra.setTitle( "2 Overlay Scans, with log scale")
        g1 = PySpectra.Scan( name = "gauss", xMin = -5., xMax = 5., yLog = False, nPts = 101, lineColor = 'red')
        mu = 0.
        sigma = 1.
        g1.y = 1/(sigma*np.sqrt(2.*np.pi))*np.exp( -(g1.y-mu)**2/(2.*sigma**2))
        g2 = PySpectra.Scan( name = "gauss2", xMin = -5., xMax = 5., yMin = 0.001, yLog = True, 
                             yMax = 1., nPts = 101, lineColor = 'green')
        mu = 0.5
        sigma = 1.2
        g2.y = 1/(sigma*np.sqrt(2.*np.pi))*np.exp( -(g2.y-mu)**2/(2.*sigma**2))
        
        PySpectra.overlay( "gauss2", "gauss")
        PySpectra.display()
        PySpectra.procEventsLoop( 1)

        print "testGraphics.testOverly2SecondLog"

    def mandelbrot( self, c,maxiter):
        z = c
        for n in range(maxiter):
            if abs(z) > 2:
                return n
            z = z*z + c
        return 0

    def testImageMB1( self): 
        print "testGQE.testImageMB1"

        PySpectra.setWsViewport( 'DINA5S')

        PySpectra.cls()
        PySpectra.delete()

        (xmin, xmax) = (-2., 1)
        (ymin, ymax) = (-1.5, 1.5)
        (width, height) = (500, 500)
        maxiter = 20

        r1 = np.linspace(xmin, xmax, width + 1)
        r2 = np.linspace(ymin, ymax, height + 1)
        n3 = np.empty((width + 1,height + 1))
        for i in range(width):
            for j in range(height):
                n3[i,j] = self.mandelbrot(r1[i] + 1j*r2[j],maxiter)
            
        m = PySpectra.Image( name = "MandelbrotSet1", data = n3,
                            xMin = xmin, xMax = xmax, width = width,  
                            yMin = ymin, yMax = ymax, height = height, 
                            xLabel = "eh_mot01", yLabel = "eh_mot02")

        PySpectra.display()

        self.assertEqual( m.xMin, xmin)
        self.assertEqual( m.xMax, xmax)
        self.assertEqual( m.yMin, ymin)
        self.assertEqual( m.yMax, ymax)
        self.assertEqual( m.height, height)
        self.assertEqual( m.width, width)
        #
        # to understand '+ 1'consider : x [-2, 1], width 100
        #  if x == 1 -> ix == 100, so we need '+ 1'
        #
        self.assertEqual( m.data.shape[0], width + 1)
        self.assertEqual( m.data.shape[1], height + 1)

        PySpectra.procEventsLoop( 2)

    def testImageMB2( self): 
        print "testGQE.testImageMB2"

        PySpectra.setWsViewport( 'DINA5S')

        PySpectra.cls()
        PySpectra.delete()

        (xmin, xmax) = (-2., 1)
        (ymin, ymax) = (-1.5, 1.5)
        (width, height) = (300, 300)
        maxiter = 20

        m = PySpectra.Image( name = "MandelbrotSet2", xMin = xmin, xMax = xmax, width = width,  
                            yMin = ymin, yMax = ymax, height = height, 
                            xLabel = "eh_mot01", yLabel = "eh_mot02")

        r1 = np.linspace(xmin, xmax, width)
        r2 = np.linspace(ymin, ymax, height)
        for i in range(width):
            for j in range(height):
                res = self.mandelbrot(r1[i] + 1j*r2[j],maxiter)
                m.setPixel( x = r1[i], y = r2[j], value = res)

            PySpectra.cls()
            PySpectra.display()
        PySpectra.procEventsLoop(1)

        self.assertEqual( m.xMin, xmin)
        self.assertEqual( m.xMax, xmax)
        self.assertEqual( m.yMin, ymin)
        self.assertEqual( m.yMax, ymax)
        self.assertEqual( m.height, height)
        self.assertEqual( m.width, width)
        #
        # to understand '+ 1'consider : x [-2, 1], width 100
        #  if x == 1 -> ix == 100, so we need '+ 1'
        #
        self.assertEqual( m.data.shape[0], width + 1)
        self.assertEqual( m.data.shape[1], height + 1)


    def mandelbrot( self,  c, maxiter):
        z = c
        for n in range(maxiter):
            if abs(z) > 2:
                return n
            z = z*z + c
        return 0

    def testToPysp1( self): 
        print "testGQE.testToPysp1"

        PySpectra.cls()
        PySpectra.delete()
        (xmin, xmax) = (-2.,-0.5)
        (ymin, ymax) = (0, 1.5)
        (width, height) = (100, 100)
        maxiter = 25
        #
        # do the clean-up before we start
        #
        hsh = PySpectra.toPysp( { 'command': ['delete', 'setWsViewport DINA5S', 'cls']})
        if hsh[ 'result'] != "done":
            print "error from ['delete', 'setWsViewport DINA5S', 'cls']"
            return 
        
        hsh = { 'putData': 
                { 'name': "MandelBrot",
                  'type': 'image', 
                  'xMin': xmin, 'xMax': xmax, 'width': width, 
                  'yMin': ymin, 'yMax': ymax, 'height': height}}
        hsh = PySpectra.toPysp( hsh)
        if hsh[ 'result'] != "done":
            print "error from putData"
            return 
        
        r1 = np.linspace(xmin, xmax, width)
        r2 = np.linspace(ymin, ymax, height)
        for i in range(width):
            for j in range(height):
                res = self.mandelbrot(r1[i] + 1j*r2[j],maxiter)
                hsh = { 'putData': 
                        { 'name': "MandelBrot",
                          'noDisplay': True, 
                          'setPixel': ( r1[i], r2[j], res)}}
                hsh = PySpectra.toPysp( hsh)
                if hsh[ 'result'] != "done":
                    print "error from setPixel"
                    return
            PySpectra.cls()
            PySpectra.display()

        return 
        
if __name__ == "__main__":
    unittest.main()
