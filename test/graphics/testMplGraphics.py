#!/bin/env python
'''
python ./test/graphics/testMplGraphics.py testMplGraphics.testDoty
python ./test/graphics/testMplGraphics.py testMplGraphics.testGrid
python ./test/graphics/testMplGraphics.py testMplGraphics.testScanning
python ./test/graphics/testMplGraphics.py testMplGraphics.testScanningWithText
python ./test/graphics/testMplGraphics.py testMplGraphics.testScanningTwoPlots
python ./test/graphics/testMplGraphics.py testMplGraphics.testScanningAutoscaleX
python ./test/graphics/testMplGraphics.py testMplGraphics.testScanningReverse
python ./test/graphics/testMplGraphics.py testMplGraphics.testScanningReverseAutoscaleX
python ./test/graphics/testMplGraphics.py testMplGraphics.testDisplaySingle
python ./test/graphics/testMplGraphics.py testMplGraphics.testFastDisplay_v1
python ./test/graphics/testMplGraphics.py testMplGraphics.testCommentTitle
python ./test/graphics/testMplGraphics.py testMplGraphics.testWsViewport
python ./test/graphics/testMplGraphics.py testMplGraphics.testLissajous
python ./test/graphics/testMplGraphics.py testMplGraphics.testWsViewport
'''
import sys, os
#pySpectraPath = "/home/kracht/Misc/pySpectra/PySpectra"
#sys.path.append( pySpectraPath)

#os.environ["PYSP_USE_MATPLOTLIB"] = "True"

import PySpectra

#from mtpltlb.graphics import *
#from pqtgrph.graphics import *

import numpy as np
import unittest
import time, sys
import math 

class testMplGraphics( unittest.TestCase):

    def testDoty( self): 
        '''
        using showGridX, showGridY
        '''
        print "testMplGraphics.testDoty"

        PySpectra.mtpltlb.graphics.cls()
        PySpectra.delete()
        PySpectra.setTitle( "check x-axis doty")

        sinus = PySpectra.Scan( name = 'sinus', 
                                xMin = 0., xMax = 6.0, nPts = 101, lineColor = 'red', doty = True)
        sinus.y = np.sin( sinus.y)

        PySpectra.mtpltlb.graphics.display()

        #PySpectra.show()
        PySpectra.mtpltlb.graphics.procEventsLoop( 1)

        print "testMplGraphics.testDoty, DONE"


    def testGrid( self): 
        '''
        using showGridX, showGridY
        '''
        print "testMplGraphics.testGrid"
        PySpectra.mtpltlb.graphics.cls()
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

        PySpectra.mtpltlb.graphics.display()
        PySpectra.mtpltlb.graphics.display()
        #PySpectra.show()
        PySpectra.mtpltlb.graphics.procEventsLoop( 1)

        print "testMplGraphics.testGrid, DONE"

    def testScanning( self): 
        '''
        using setX and setY
        '''
        print "testMplGraphics.testScanning"
        PySpectra.mtpltlb.graphics.cls()
        PySpectra.delete()

        PySpectra.setTitle( "x-axis not re-scaled")
        sinus = PySpectra.Scan( name = 'sinus', xMin = 0., xMax = 6.0, nPts = 101, lineColor = 'red')
        for i in range( sinus.nPts): 
            sinus.setX( i, i/10.)
            sinus.setY( i, math.sin( i/10.))
            PySpectra.mtpltlb.graphics.display( ['sinus'])
            time.sleep( 0.01)
        print "testMplGraphics.testScanning, DONE"

    def testScanningWithText( self): 
        '''
        using setX and setY
        '''
        print "testGrphics.testScanningWithText"
        PySpectra.mtpltlb.graphics.cls()
        PySpectra.delete()

        PySpectra.setTitle( "x-axis is not re-scaled, watch text")

        scan = PySpectra.Scan( name = 'tangens', xMin = 0., xMax = 6.0, nPts = 101, autoscaleY = True, lineColor = 'red')
        scan.addText( text = "a test text", x = 0.95, y = 0.9, hAlign = 'right', 
                       vAlign = 'center', fontSize = 14, color = 'black', NDC = True)
        for i in range( scan.nPts): 
            scan.setX( i, i/10.)
            scan.setY( i, math.tan( i/10.))
            PySpectra.mtpltlb.graphics.display( ['tangens'])
            time.sleep( 0.02)
        print "testGrphics.testScanningWithText, DONE"

    def testScanningTwoPlots( self): 
        '''
        using setX and setY
        '''
        print "testMplGraphics.testScanningTwoPlots"
        PySpectra.mtpltlb.graphics.cls()
        PySpectra.delete()

        PySpectra.setTitle( "two plots, x-axis not re-scaled")

        sinus = PySpectra.Scan( name = 'sinus', xMin = 0., xMax = 6.0, nPts = 101, lineColor = 'red')
        cosinus = PySpectra.Scan( name = 'cosinus', xMin = 0., xMax = 6.0, nPts = 101, lineColor = 'blue')
        for i in range( sinus.nPts): 
            sinus.setX( i, i/10.)
            sinus.setY( i, math.sin( i/10.))
            cosinus.setX( i, i/10.)
            cosinus.setY( i, math.cos( i/10.))
            PySpectra.mtpltlb.graphics.display( ['sinus', 'cosinus'])
            time.sleep( 0.01)

        print "testMplGraphics.testScanningTwoPlots, DONE"

    def testScanningAutoscaleX( self): 
        '''
        using setX and setY
        '''
        print "testGrphics.testScanningAutoscaleX_v1"
        PySpectra.mtpltlb.graphics.cls()
        PySpectra.delete()

        PySpectra.setTitle( "x-axis is re-scaled")
        sinus = PySpectra.Scan( name = 'sinus', 
                                xMin = 0., xMax = 6.0, nPts = 101, 
                                autoscaleX = True, 
                                lineColor = 'red')
        for i in range( sinus.nPts): 
            sinus.setX( i, i/10.)
            sinus.setY( i, math.sin( i/10.))
            PySpectra.mtpltlb.graphics.display( ['sinus'])
            time.sleep( 0.01)
        print "testGrphics.testScanningAutoscaleX_v1, DONE"

    def testScanningReverse( self): 
        '''
        scanning in reverse direction
        '''
        print "testGrphics.testScanningReverse"
        PySpectra.mtpltlb.graphics.cls()
        PySpectra.delete()

        PySpectra.setTitle( "reverse scannning, no re-scale")
        sinus = PySpectra.Scan( name = 'sinus', xMin = 0., xMax = 6.0, nPts = 101, lineColor = 'red')
        sinus.xMax = 10.
        for i in range( sinus.nPts): 
            x = 10. - i/10.
            sinus.setX( i, x)
            sinus.setY( i, math.sin( i/10.))
            PySpectra.mtpltlb.graphics.display( ['sinus'])
            time.sleep( 0.01)
        print "testGrphics.testScanningReverse_v1, DONE"

    def testScanningReverseAutoscaleX( self): 
        '''
        scanning in reverse direction
        '''
        print "testGrphics.testScanningReverseAutoscaleX"
        PySpectra.mtpltlb.graphics.cls()
        PySpectra.delete()

        PySpectra.setTitle( "reverse scannning, re-scale")
        sinus = PySpectra.Scan( name = 'sinus', 
                                xMin = 0., xMax = 6.0, nPts = 101, 
                                autoscaleX = True, 
                                lineColor = 'red')
        sinus.xMax = 10.
        for i in range( sinus.nPts): 
            x = 10. - i/10.
            sinus.setX( i, x)
            sinus.setY( i, math.sin( i/10.))
            PySpectra.mtpltlb.graphics.display( ['sinus'])
            time.sleep( 0.01)
        print "testGrphics.testScanningReverseAutoscaleX, DONE"

    def testDisplaySingle( self): 

        print "testMplGraphics.testDisplaySingle"
        PySpectra.mtpltlb.graphics.cls()
        PySpectra.delete()

        sinus = PySpectra.Scan( name = 'sinus', xMin = 0., 
                                xMax = 6.0, nPts = 101, dType = np.float64,
                                at = (2,2,3), lineColor = 'red', lineStyle = 'solid')

        sinus.y = np.sin( sinus.y)
        PySpectra.mtpltlb.graphics.display( ['sinus'])
        #PySpectra.show()
        PySpectra.mtpltlb.graphics.procEventsLoop( 1)

        print "testMplGraphics.testDisplaySingle, DONE"

    def testDisplaySymbol( self): 

        print "testMplGraphics.testDisplaySymbol"

        PySpectra.mtpltlb.graphics.cls()
        PySpectra.delete()

        sinus = PySpectra.Scan( name = 'sinus', xMin = 0., 
                                xMax = 6.0, nPts = 101, dType = np.float64,
                                at = (2,2,3), symbolColor = 'red', symbol = 'o', symbolSize = 10)

        sinus.y = np.sin( sinus.y)
        PySpectra.mtpltlb.graphics.display( ['sinus'])
        #PySpectra.show()


        PySpectra.mtpltlb.graphics.procEventsLoop( 1)
        print "testMplGraphics.testDisplaySymbol. DONE"

    def testDisplayTwo( self): 

        print "testMplGraphics.testDisplayTwo"

        PySpectra.mtpltlb.graphics.cls()
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

        PySpectra.mtpltlb.graphics.display()
        #PySpectra.show()
        PySpectra.mtpltlb.graphics.procEventsLoop( 1)

        print "testMplGraphics.testDisplayTwo, DONE"

    def testOverlay( self): 

        print "testMplGraphics.testOverlay"

        PySpectra.mtpltlb.graphics.cls()
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

        PySpectra.mtpltlb.graphics.display()
        #PySpectra.show()
        PySpectra.mtpltlb.graphics.procEventsLoop( 1)

        print "testMplGraphics.testOverlay, DONE"

    def testDisplayFour( self): 

        print "testMplGraphics.testDisplayFour"

        PySpectra.mtpltlb.graphics.cls()
        PySpectra.delete()

        for i in range( 1, 5):
            s = PySpectra.Scan( name = 't%d' % i, xMin = 0., 
                                xMax = 6.0, nPts = 101, dType = np.float64,
                                xLabel = 'rad', yLabel = 'Signal', 
                                at = (2,2,i), lineColor = 'red', lineStyle = 'solid',
                                lineWidth = 2.)
            s.y = np.tan( s.y)

        PySpectra.mtpltlb.graphics.display()

        #PySpectra.show()

        PySpectra.mtpltlb.graphics.procEventsLoop( 1)

        print "testMplGraphics.testDisplayFour, DONE"

    def testDisplayMany( self): 

        print "testMplGraphics.testDisplayMany"

        PySpectra.mtpltlb.graphics.cls()
        PySpectra.delete()

        for i in range( 1, 20):
            s = PySpectra.Scan( name = 't%d' % i, xMin = 0., 
                                xMax = 6.0, nPts = 101, dType = np.float64,
                                xLabel = 'rad', yLabel = 'Signal', 
                                at = (5,4,i), lineColor = 'red', lineStyle = 'solid',
                                lineWidth = 2.)
            s.y = np.tan( s.y)

        PySpectra.mtpltlb.graphics.display()

        #PySpectra.show()

        PySpectra.mtpltlb.graphics.procEventsLoop( 1)

        print "testMplGraphics.testDisplayMany, DONE"

    def testFastDisplay_v1( self):
        '''
        version 1: set the scan data and call display
        '''

        print "testMplGraphics.testDisplay_v1"

        PySpectra.mtpltlb.graphics.cls()
        PySpectra.delete()
        scan1 = PySpectra.Scan( name = 't1', nPts = 100, yMin = -1., yMax = 1.)
        scan2 = PySpectra.Scan( name = 't2', nPts = 100, yMin = -1., yMax = 1.)

        PySpectra.mtpltlb.graphics.display()

        data = np.random.normal(size=(10,100))
        x  = np.linspace( 0., 10., 100)
        ptr = 0

        scan1.x = x
        scan2.x = x
        
        startTime = time.time()
        for i in range( 20):
            PySpectra.mtpltlb.graphics.cls()
            scan1.y = data[ptr%10]
            scan2.y = data[ptr%10]
            PySpectra.mtpltlb.graphics.display()
            ptr += 1
            PySpectra.mtpltlb.graphics.processEvents()

        diffTime = time.time() - startTime
        self.assertLess( diffTime, 11.)

        print "testMplGraphics.testDisplay_v1, DONE"


    def testCommentTitle( self):
        '''
        '''
        print "testMplGraphics.testCommentTitel"

        PySpectra.mtpltlb.graphics.cls()
        PySpectra.delete()
        PySpectra.setComment( "this is a comment")
        PySpectra.setTitle( "check comment and title")

        sinus = PySpectra.Scan( name = 'sinus', 
                                xMin = 0., xMax = 6.0, nPts = 101, lineColor = 'red')
        sinus.y = np.sin( sinus.y)

        PySpectra.mtpltlb.graphics.display()

        #PySpectra.show()
        PySpectra.mtpltlb.graphics.procEventsLoop( 1)

        print "testMplGraphics.testCommentTitle, DONE"


    def testWsViewport( self):
        '''
        '''
        print "testMplGrphics.testWsViewport"

        PySpectra.cls()
        PySpectra.delete()
        PySpectra.setTitle( "go through the viewports")

        sinus = PySpectra.Scan( name = 'sinus', 
                                xMin = 0., xMax = 6.0, nPts = 101, lineColor = 'red', doty = True)
        sinus.y = np.sin( sinus.y)

        for elm in [ 'DINA4', 'DINA4P', 'DINA4S', 'DINA5', 'DINA5P', 'DINA5S', 
                     'DINA6', 'DINA6P', 'DINA6S']: 
            PySpectra.mtpltlb.graphics.setWsViewport( elm)
            PySpectra.mtpltlb.graphics.display()
            PySpectra.mtpltlb.graphics.procEventsLoop( 1)

        print "testMplGrphics.testWsViewport, DONE"


    def testLissajous( self):
        '''

        '''
        print "testMplGrphics.testLissayous"

        PySpectra.mtpltlb.graphics.cls()
        PySpectra.mtpltlb.graphics.setWsViewport( "dinA6s")
        PySpectra.delete()
        scan = PySpectra.Scan( name = 'Lissajous', nPts = 1000, xMin = -1., xMax = 1.)

        x  = np.linspace( 0., 6.5, 1000)
        y  = np.linspace( 0., 6.5, 1000)

        scan.x = np.cos( x)
        scan.y = np.sin( y)

        PySpectra.mtpltlb.graphics.display()

        startTime = time.time()
        for i in range( 150):
            x = x + 0.005
            scan.plotDataItem.setData(np.cos( x), np.sin( y))
            PySpectra.mtpltlb.graphics.processEvents()

        diffTime = time.time() - startTime

        self.assertLess( diffTime, 6.)
        print "testMplGrphics.testLissajous, DONE"
        
    def testWsViewport( self):
        '''
        '''
        print "testGrphics.testWsViewport"

        PySpectra.mtpltlb.graphics.cls()
        PySpectra.delete()
        PySpectra.setTitle( "go through the viewports")

        sinus = PySpectra.Scan( name = 'sinus', 
                                xMin = 0., xMax = 6.0, nPts = 101, lineColor = 'red', doty = True)
        sinus.y = np.sin( sinus.y)

        for elm in [ 'DINA4', 'DINA4P', 'DINA5', 'DINA5P', 'DINA6', 'DINA6P']: 
            PySpectra.mtpltlb.graphics.setWsViewport( elm)
            PySpectra.mtpltlb.graphics.display()
            PySpectra.mtpltlb.graphics.procEventsLoop( 1)

        print "testGrphics.testWsViewport, DONE"

if __name__ == "__main__":
    unittest.main()
