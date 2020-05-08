#!/bin/env python
'''
cd /home/kracht/Misc/pySpectra
python -m unittest discover -v

python ./test/testGQE.py testGQE.testNextPrevScan
python ./test/testGQE.py testGQE.testNextPrevImage
python ./test/testGQE.py testGQE.testFillData
python ./test/testGQE.py testGQE.testCreateScansByColumns
python ./test/testGQE.py testGQE.testCreateScansByGqes
python ./test/testGQE.py testGQE.testCreateDelete
python ./test/testGQE.py testGQE.testWrite
python ./test/testGQE.py testGQE.testRead
python ./test/testGQE.py testGQE.testWriteReadImage
python ./test/testGQE.py testGQE.test_read
python ./test/testGQE.py testGQE.test_doty
python ./test/testGQE.py testGQE.testReuse
python ./test/testGQE.py testGQE.testYGreaterThanZero
python ./test/testGQE.py testGQE.testSetLimits
python ./test/testGQE.py testGQE.testSetXY
python ./test/testGQE.py testGQE.testGetXY
python ./test/testGQE.py testGQE.testExceptions
python ./test/testGQE.py testGQE.testMisc
python ./test/testGQE.py testGQE.testDoubles
python ./test/testGQE.py testGQE.test_titleAndComment
python ./test/testGQE.py testGQE.testSSA
python ./test/testGQE.py testGQE.testFsa
python ./test/testGQE.py testGQE.testGetIndex
python ./test/testGQE.py testGQE.testMotorArrowCurrentAndSetPoint
python ./test/testGQE.py testGQE.testMotorArrowMisc
python ./test/testGQE.py testGQE.testCheckTargetWithinLimits
python ./test/testGQE.py testGQE.testColorSpectraToPysp
python ./test/testGQE.py testGQE.testAddText
python ./test/testGQE.py testGQE.testTextOnlyScan
'''
import sys, time
import PyTango
import PySpectra
import PySpectra.utils as utils
import numpy as np
import unittest
import time, sys, os
import math 
import pyqtgraph as pg

#
# wrong, think of github: pySpectraPath = "/home/kracht/Misc/pySpectra"
pySpectraPath = "."

class testGQE( unittest.TestCase):

    @classmethod
    def setUpClass( testGQE):
        pass

    @classmethod
    def tearDownClass( testGQE): 
        PySpectra.close()

    def test_titleAndComment( self):

        PySpectra.cls()

        PySpectra.delete()
        PySpectra.setTitle( "a_title")
        self.assertEqual( PySpectra.getTitle(), "a_title")
        PySpectra.delete()
        self.assertEqual( PySpectra.getTitle(), None)
        PySpectra.setTitle( "a_title")
        PySpectra.setTitle( None)
        self.assertEqual( PySpectra.getTitle(), None)

        PySpectra.delete()
        PySpectra.setComment( "a_comment")
        self.assertEqual( PySpectra.getComment(), "a_comment")
        PySpectra.delete()
        self.assertEqual( PySpectra.getComment(), None)
        PySpectra.setComment( "a_comment")
        PySpectra.setComment( None)
        self.assertEqual( PySpectra.getComment(), None)

        PySpectra.delete()
        PySpectra.setTitle( "there must be this title")
        PySpectra.setComment( "and there must be this comment")
        PySpectra.Scan( "t1")
        PySpectra.display()
        PySpectra.show()
        PySpectra.processEventsLoop( 1)

        PySpectra.cls()
        PySpectra.delete()
        PySpectra.setTitle( "there is only a title, no comment")
        PySpectra.Scan( "t1")
        PySpectra.display()
        PySpectra.processEventsLoop( 1)

        PySpectra.cls()
        PySpectra.delete()
        PySpectra.setComment( "there is only a comment")
        PySpectra.Scan( "t1")
        PySpectra.display()
        PySpectra.processEventsLoop( 1)

        print "testPySpectra.test_titleAndComment DONE"
    
    def test_readMca_v1( self):

        print "testPySpectra.test_readMca_v1"

        PySpectra.cls()
        PySpectra.delete()
        PySpectra.setTitle( "the graphics window should contain 1 MCA plot")
        PySpectra.read( "%s/test/data/tst_09153_mca_s1.fio" % pySpectraPath, flagMCA = True)
        lst = PySpectra.getGqeList()
        self.assertEqual( len( lst), 1)
        self.assertEqual( lst[0].name, "d1_mca01")
        self.assertEqual( lst[0].nPts, 2048)
        
        PySpectra.display()
        #PySpectra.show()
        PySpectra.processEventsLoop( 1)

        print "testPySpectra.test_readMca_v1 DONE"

    def test_readMca_v2( self):

        print "testPySpectra.test_readMca_v2"

        PySpectra.cls()
        PySpectra.delete()
        PySpectra.setTitle( "2 MCA plots")
        PySpectra.read( "%s/test/data/tst_09154_mca_s1.fio" % pySpectraPath, flagMCA = True)
        lst = PySpectra.getGqeList()
        self.assertEqual( len( lst), 2)
        self.assertEqual( lst[0].name, "d1_mca01")
        self.assertEqual( lst[0].nPts, 8192)
        self.assertEqual( lst[1].name, "d1_mca02")
        self.assertEqual( lst[1].nPts, 8192)
        
        PySpectra.display()
        PySpectra.processEventsLoop( 1)

        print "testPySpectra.test_readMca_v2 DONE"

    def test_read( self):

        print "testPySpectra.test_read"

        PySpectra.cls()
        PySpectra.delete()
        PySpectra.setTitle( "the graphics window should contain 24 plots")
        PySpectra.read( "%s/test/data/ti_au_tio2_sio2_kat55a_0001.fio" % pySpectraPath)
        lst = PySpectra.getGqeList()
        self.assertEqual( len( lst), 24)
        self.assertEqual( lst[0].name, "TI_AU_TIO2_SIO2_KAT55A_0001")
        self.assertEqual( lst[1].name, "TI_AU_TIO2_SIO2_KAT55A_0001_RING")
        
        PySpectra.display()
        PySpectra.processEventsLoop( 1)

        PySpectra.cls()
        PySpectra.delete()
        PySpectra.setTitle( "the graphics window should contain 4 plots")
        PySpectra.read( "%s/test/data/SPLITTER_PXE_BL_22_2.dat" % pySpectraPath)
        lst = PySpectra.getGqeList()
        self.assertEqual( len( lst), 4)
        self.assertEqual( lst[0].name, "scan1")
        self.assertEqual( lst[1].name, "scan2")
        self.assertEqual( lst[2].name, "scan3")
        self.assertEqual( lst[3].name, "scan4")
        
        PySpectra.display()
        PySpectra.processEventsLoop( 1)

        print "testPySpectra.test_read DONE"

    def test_doty( self):

        print "testPySpectra.test_doty"

        PySpectra.cls()
        PySpectra.delete()
        PySpectra.setTitle( "2 plots, the seconds has doty as the x-axis")

        scan1 = PySpectra.Scan( name = "notdotyscan", xMin = 10., xMax = 30.0, 
                               nPts = 101, dType = np.float64,
                               lineColor = 'red', lineStyle = 'solidLine')
        self.assertEqual( scan1.doty, False)

        scan2 = PySpectra.Scan( name = "dotyscan", xMin = 10., xMax = 30.0, 
                               nPts = 101, dType = np.float64,
                               doty = True,lineColor = 'red', lineStyle = 'solidLine')

        self.assertEqual( scan2.doty, True)

        PySpectra.display()
        PySpectra.processEventsLoop( 1)

        print "testPySpectra.test_doty DONE"
        
    def test_createScanByLimit( self):

        print "testPySpectra.test_createScanByLimit"

        PySpectra.cls()
        PySpectra.delete()

        PySpectra.setTitle( "create scan by limits")
        scan = PySpectra.Scan( name = "test1", xMin = 0., xMax = 1.0, 
                               nPts = 101, dType = np.float64,
                               at = (2,2,3), lineColor = 'red', lineStyle = 'solidLine')
        self.assertEqual( scan.xMin, 0.)
        self.assertEqual( scan.xMax, 1.)
        self.assertEqual( scan.nPts, 101)
        self.assertEqual( scan.dType, np.float64)
        self.assertEqual( len( scan.x), 101)
        self.assertEqual( scan.x.dtype, np.float64)
        self.assertEqual( len( scan.y), 101)
        self.assertEqual( scan.y.dtype, np.float64)

        self.assertEqual( scan.lineColor, 'red')

        PySpectra.display()
        PySpectra.processEventsLoop( 1)
        print "testPySpectra.test_createScanByLimit DONE"

    def test_createScanByData( self):

        print "testPySpectra.test_createScanByData"

        PySpectra.cls()
        PySpectra.delete()
        PySpectra.setTitle( "create scan by data")
        try:
            scan = PySpectra.Scan( name = 't1', x = [0, 1, 2, 3, 4], at = "(2, 2, 4)")
        except ValueError, e:
            self.assertEqual( str( e), "GQE.Scan.__init__(): if 'x' or 'y' then both have to be supplied")
        try:
            scan = PySpectra.Scan( name = 't1', y = [0, 1, 2, 3, 4])
        except ValueError, e:
            self.assertEqual( str( e), "GQE.Scan.__init__(): if 'x' or 'y' then both have to be supplied")

        lst = PySpectra.getGqeList()
        self.assertEqual( len( lst), 0)
        
        scan = PySpectra.Scan( name = 't1', x = [0, 1, 2, 3, 4], y = [10, 12, 11, 14, 12])

        self.assertEqual( scan.name, 't1')
        self.assertEqual( scan.xMin, 0.)
        self.assertEqual( scan.xMax, 4.)
        self.assertEqual( scan.yMin, 10.)
        self.assertAlmostEqual( scan.yMax, 14.2)

        self.assertEqual( scan.nPts, 5)
        
        self.assertEqual( scan.x[0], 0)
        self.assertEqual( scan.x[4], 4)
        self.assertEqual( scan.y[0], 10)
        self.assertEqual( scan.y[4], 12)

        self.assertEqual( scan.currentIndex, 4)

        PySpectra.info( "t1")
        PySpectra.info( ["t1"])

        PySpectra.display()
        PySpectra.processEventsLoop( 1)

        print "testPySpectra.test_createScanByData, DONE"
        
    def testCreateDelete( self): 
        print "testPySpectra.testCreateDelete"
        PySpectra.delete()
        PySpectra.setTitle( "delete;create 4;display;delete")
        scanLst = PySpectra.getGqeList()
        self.assertEqual( len( scanLst), 0)
        PySpectra.Scan( name = 't1')
        PySpectra.Scan( name = 't2')
        PySpectra.Scan( name = 't3')
        PySpectra.Scan( name = 't4')
        PySpectra.display()
        scanLst = PySpectra.getGqeList()
        self.assertEqual( len( scanLst), 4)
        PySpectra.delete( [ 't1', 't2'])
        scanLst = PySpectra.getGqeList()
        self.assertEqual( len( scanLst), 2)
        self.assertEqual( scanLst[0].name, 't3')
        self.assertEqual( scanLst[1].name, 't4')
        PySpectra.delete()
        scanLst = PySpectra.getGqeList()
        self.assertEqual( len( scanLst), 0)

        print "testPySpectra.testCreateDelete, DONE"
        
    def testNextPrevScan( self):
        print "testPySpectra.testNextPrevScan"
        PySpectra.delete()
        PySpectra.Scan( name = 't1')
        PySpectra.Scan( name = 't2')
        PySpectra.Scan( name = 't3')
        PySpectra.Scan( name = 't4')
        self.assertEqual( PySpectra.nextScan().name, 't1')
        self.assertEqual( PySpectra.nextScan().name, 't2')
        self.assertEqual( PySpectra.nextScan().name, 't3')
        self.assertEqual( PySpectra.nextScan().name, 't4')
        self.assertEqual( PySpectra.nextScan().name, 't1')
        PySpectra.delete()
        PySpectra.Scan( name = 't1')
        PySpectra.Scan( name = 't2')
        PySpectra.Scan( name = 't3')
        PySpectra.Scan( name = 't4')
        self.assertEqual( PySpectra.prevScan().name, 't1')
        self.assertEqual( PySpectra.prevScan().name, 't4')
        self.assertEqual( PySpectra.prevScan().name, 't3')
        self.assertEqual( PySpectra.prevScan().name, 't2')
        self.assertEqual( PySpectra.prevScan().name, 't1')

        print "testPySpectra.testNextPrevScan, DONE"
        
    def testNextPrevImage( self):

        print "testPySpectra.testNextPrevImage"
        PySpectra.delete()
        PySpectra.Image( name = "t1", data = np.empty((100, 100)))
        PySpectra.Image( name = "t2", data = np.empty((100, 100)))
        PySpectra.Image( name = "t3", data = np.empty((100, 100)))
        PySpectra.Image( name = "t4", data = np.empty((100, 100)))
        self.assertEqual( PySpectra.nextImage().name, 't1')
        self.assertEqual( PySpectra.nextImage().name, 't2')
        self.assertEqual( PySpectra.nextImage().name, 't3')
        self.assertEqual( PySpectra.nextImage().name, 't4')
        self.assertEqual( PySpectra.nextImage().name, 't1')
        PySpectra.delete()
        PySpectra.Image( name = "t1", data = np.empty((100, 100)))
        PySpectra.Image( name = "t2", data = np.empty((100, 100)))
        PySpectra.Image( name = "t3", data = np.empty((100, 100)))
        PySpectra.Image( name = "t4", data = np.empty((100, 100)))
        self.assertEqual( PySpectra.prevImage().name, 't1')
        self.assertEqual( PySpectra.prevImage().name, 't4')
        self.assertEqual( PySpectra.prevImage().name, 't3')
        self.assertEqual( PySpectra.prevImage().name, 't2')
        self.assertEqual( PySpectra.prevImage().name, 't1')

        print "testPySpectra.testNextPrevImage, DONE"

    def testFillData( self):
        print "testPySpectra.testFillData"
        PySpectra.cls()
        PySpectra.delete()
        PySpectra.setTitle( "scan.setY()")
        scan = PySpectra.Scan( name = 't1', xLabel = "up to 200 pts", 
                               nPts = 201, yMin = -10., yMax = 10.)
        self.assertEqual( scan.currentIndex, 200)
        #scan.y = np.tan( scan.x)
        
        startTime = time.time()
        for i in range( len( scan.y)):
            scan.setY( i, math.tan( float( i)/10))
            PySpectra.display()

        diffTime = time.time() - startTime
        self.assertLess( diffTime, 12)

        PySpectra.display()
        PySpectra.processEventsLoop( 1)

        print "testPySpectra.testFillData, DONE"

    def testCreateScansByColumns( self):

        print "testPySpectra.testCreateScansByColumns"
        PySpectra.cls()
        PySpectra.delete()
        PySpectra.setTitle( "create scan putData-columns")
        x  = np.linspace( 0., 10., 100)
        tan = np.tan( x)
        sin = np.sin( x)
        cos = np.cos( x)

        hsh = { 'putData': {'columns': [{'data': x, 'name': 'xaxis'},
                                        {'data': tan, 'name': 'tan'},
                                        {'data': cos, 'name': 'cos'},
                                        {'data': sin, 'name': 'sin',
                                         'showGridY': False, 'symbolColor': 'blue', 'showGridX': False, 
                                         'yLog': False, 'symbol': '+', 
                                         'xLog': False, 'symbolSize':5}]}}

        PySpectra.toPyspLocal( hsh)

        lst = PySpectra.getGqeList()
        self.assertEqual( len( lst), 3)

        self.assertEqual( lst[0].name, 'tan')
        self.assertEqual( lst[1].name, 'cos')
        self.assertEqual( lst[2].name, 'sin')
        
        comparison = x == lst[0].x
        self.assertTrue( comparison.all())
        comparison = tan == lst[0].y
        self.assertTrue( comparison.all())
        comparison = cos == lst[1].y
        self.assertTrue( comparison.all())
        comparison = sin == lst[2].y
        self.assertTrue( comparison.all())
        PySpectra.display()

        PySpectra.processEventsLoop( 1)

        # utils.launchGui()
        print "testPySpectra.testCreateScansByColumns, DONE"

    def testCreateScansByGqes( self):

        print "testPySpectra.testCreateScansByGqes"
        PySpectra.cls()
        PySpectra.delete()
        PySpectra.setTitle( "create scan by putData-gqes")

        x  = np.linspace( 0., 10., 100)
        tan = np.tan( x)
        sin = np.sin( x)
        cos = np.cos( x)

        hsh = { 'putData': {'gqes': [ {'x': x, 'y': tan, 'name': 'tan'},
                                      {'x': x, 'y': cos, 'name': 'cos'},
                                      {'x': x, 'y': sin, 'name': 'sin', 
                                       'showGridY': False, 'symbolColor': 'blue', 'showGridX': True, 
                                       'yLog': False, 'symbol': '+', 
                                       'xLog': False, 'symbolSize':5}]}}

        PySpectra.toPyspLocal( hsh)

        lst = PySpectra.getGqeList()
        self.assertEqual( len( lst), 3)

        self.assertEqual( lst[0].name, 'tan')
        self.assertEqual( lst[1].name, 'cos')
        self.assertEqual( lst[2].name, 'sin')
        
        comparison = x == lst[0].x
        self.assertTrue( comparison.all())
        comparison = tan == lst[0].y
        self.assertTrue( comparison.all())
        comparison = cos == lst[1].y
        self.assertTrue( comparison.all())
        comparison = sin == lst[2].y
        self.assertTrue( comparison.all())
        PySpectra.display()

        PySpectra.processEventsLoop( 1)

        #utils.launchGui()
        print "testPySpectra.testCreateScansByGqes, DONE"

    def testWrite( self): 
        print "testPySpectra.testWrite"
        PySpectra.cls()
        PySpectra.delete()
        PySpectra.setTitle( "create;write;delete;read(fileName); 1 scan")
        scan = PySpectra.Scan( name = 't1', xLabel = "up to 200 pts", 
                               nPts = 201, yMin = -10., yMax = 10.)
        ret = PySpectra.write( ['t1'])

        PySpectra.delete()

        self.assertEqual( os.path.exists( ret), True)

        PySpectra.read( ret)

        scanLst = PySpectra.getGqeList()
        self.assertEqual( len( scanLst), 1)
        self.assertEqual( scanLst[0].name, "t1")
        self.assertEqual( scanLst[0].nPts, 201)

    def testRead( self): 
        print "testPySpectra.testRead"
        PySpectra.cls()
        PySpectra.delete()
        PySpectra.setTitle( "create;write;read Scan( filename=...); 1 scan")
        scan = PySpectra.Scan( name = 't1', xLabel = "up to 200 pts", 
                               nPts = 201, yMin = -10., yMax = 10.)
        ret = PySpectra.write( ['t1'])

        PySpectra.delete()

        self.assertEqual( os.path.exists( ret), True)

        scan = PySpectra.Scan( name = 't1', fileName = ret, x = 1, y = 2)

        scanLst = PySpectra.getGqeList()
        self.assertEqual( len( scanLst), 1)
        self.assertEqual( scanLst[0].name, "t1")
        self.assertEqual( scanLst[0].nPts, 201)


    def testWriteReadImage( self): 
        print "testPySpectra.testWrite"
        PySpectra.cls()
        PySpectra.delete()

        (xmin, xmax) = (-2., 1)
        (ymin, ymax) = (-1.5, 1.5)
        (width, height) = (200, 200)
        maxiter = 100
            
        m = PySpectra.Image( name = "MandelbrotSet", colorMap = 'Greys', 
                       estimatedMax = maxiter, 
                       xMin = xmin, xMax = xmax, width = width, 
                       yMin = ymin, yMax = ymax, height = height)

        m.zoomMb( flagDisplay = False)

        ret = PySpectra.write( ['MandelbrotSet'])

        PySpectra.cls()
        PySpectra.delete()
        PySpectra.setTitle( "create Mandelbrotset; write; read; display")

        self.assertEqual( os.path.exists( ret), True)

        PySpectra.read( ret)

        PySpectra.setTitle( "The Mandelbrotset")
        PySpectra.display()
        PySpectra.processEventsLoop( 2)

        lst = PySpectra.getGqeList()
        self.assertEqual( len( lst), 1)
        
        ima = lst[0]
        self.assertEqual( ima.name, "MandelbrotSet")
        self.assertEqual( type( ima), PySpectra.PySpectra.Image)
        self.assertEqual( ima.width, width)
        self.assertEqual( ima.height, height)

        self.assertEqual( ima.xMin, xmin)
        self.assertEqual( ima.xMax, xmax)
        self.assertEqual( ima.yMin, ymin)
        self.assertEqual( ima.yMax, ymax)

        ima.zoomMb( targetIX = 50, targetIY = 100, flagDisplay = False)
        PySpectra.display()
        PySpectra.processEventsLoop( 1)

        ima.zoomMb( targetIX = 50, targetIY = 100, flagDisplay = False)
        PySpectra.display()
        PySpectra.processEventsLoop( 1)

        return 

    def testReuse( self): 
        print "testPySpectra.testReuse"
        PySpectra.cls()
        PySpectra.delete()
        PySpectra.setTitle( "test re-use")

        scan = PySpectra.Scan( name = 't1', xLabel = "100 pts, going to be re-used", 
                               nPts = 100, yMin = -10., yMax = 10.)

        for i in range( 10):
            data = np.random.normal(size=(1,100))
            x1  = np.linspace( 0., 10., 100)
            PySpectra.display()
            PySpectra.processEventsLoop( 1)
            scan = PySpectra.Scan( name = 't1', reUse = True, x = x1, y = data[0])

    def testYGreaterThanZero( self): 
        print "testPySpectra.testYGreaterThanZero"
        PySpectra.cls()
        PySpectra.delete()
        PySpectra.setTitle( "test YgreaterThenZeor")
        scan = PySpectra.Scan( name = 't1', xLabel = "11 pts, going to be re-used", 
                               xMin = 0, yMin = 10, 
                               nPts = 11, )

        
        for i in range( 11):
            scan.y[i] = scan.y[i]*scan.y[i]

        scan.y[2] = 0
        scan.y[7] = 0
        #
        # remove the zeros
        #
        scan.yGreaterThanZero()

        self.assertEqual( len( scan.y), 8)
        self.assertEqual( len( scan.x), 8)
        self.assertEqual( scan.y[0], 1)
        self.assertEqual( scan.y[1], 9)
        self.assertEqual( scan.y[2], 16)
        self.assertEqual( scan.y[3], 25)
        self.assertEqual( scan.y[4], 36)
        self.assertEqual( scan.y[5], 64)
        self.assertEqual( scan.y[6], 81)
        self.assertEqual( scan.y[7], 100)

        PySpectra.display()
        PySpectra.processEventsLoop( 1)
        return 

    def testSetLimits( self): 
        print "testPySpectra.testSetLimits"
        PySpectra.cls()
        PySpectra.delete()
        PySpectra.setTitle( "test setLimits")
        scan = PySpectra.Scan( name = 't1', 
                               xMin = 0, xMax = 10, 
                               nPts = 11, )

        self.assertEqual( scan.xMin, 0.)
        self.assertEqual( scan.xMax, 10.)
        self.assertEqual( scan.yMin, 0.)
        self.assertEqual( scan.yMax, 10.)

        scan.xMin = -1.
        scan.xMax = -1.
        scan.yMin = -1.
        scan.yMax = -1.

        scan.setLimits()

        self.assertEqual( scan.xMin, 0.)
        self.assertEqual( scan.xMax, 10.)
        self.assertEqual( scan.yMin, 0.)
        self.assertEqual( scan.yMax, 10.5)

    def testSetXY( self) : 
        print "testPySpectra.testSetXY"
        PySpectra.cls()
        PySpectra.delete()
        x  = np.linspace( 0., 10., 100)
        y  = np.linspace( 0., 10., 100)
        scan = PySpectra.Scan( 't1', x = x, y = y)

        scan.setX( 0, 12)
        self.assertEqual( scan.x[0], 12)
        scan.setY( 0, 12)
        self.assertEqual( scan.y[0], 12)
        scan.setXY( 1, 11, 12)
        self.assertEqual( scan.x[1], 11)
        self.assertEqual( scan.y[1], 12)

        with self.assertRaises( ValueError) as context:
            scan.setXY( 101, 11, 12)
        #print("testSetXY: %s" %  repr( context.exception))
        self.assertTrue( "GQE.Scan.setXY: t1, index 101 out of range [0, 100]"
                         in context.exception)

        return 

    def testGetXY( self) : 
        print "testPySpectra.testSetXY"
        PySpectra.cls()
        PySpectra.delete()
        x  = np.linspace( 0., 10., 100)
        y  = np.linspace( 0., 10., 100)
        scan = PySpectra.Scan( 't1', x = x, y = y)

        scan.setX( 0, 12)
        self.assertEqual( scan.getX( 0), 12)
        scan.setY( 0, 12)
        self.assertEqual( scan.getY(0), 12)
        return 

    def testExceptions( self): 
        print "testPySpectra.testExceptions"
        PySpectra.cls()
        PySpectra.delete()

        with self.assertRaises( ValueError) as context:
            PySpectra.delete()
            scan = PySpectra.Scan()
        self.assertTrue( "GQE.Scan: 'name' is missing" in context.exception)

        with self.assertRaises( ValueError) as context:
            PySpectra.delete()
            scan = PySpectra.Scan( name = 't1')
            PySpectra.delete( 't2')
        #print repr( context.exception)
        self.assertTrue( "GQE.delete: not found t2" in context.exception)

        with self.assertRaises( ValueError) as context:
            PySpectra.delete()
            scan = PySpectra.Scan( 't1')
            scan = PySpectra.Scan( 't1')
        #print repr( context.exception)
        self.assertTrue( "GQE.Scan.__init__(): t1 exists already" in context.exception)

        with self.assertRaises( ValueError) as context:
            PySpectra.delete()
            scan = PySpectra.Scan( 't1')
            scan = PySpectra.Scan( 't1')
        #print repr( context.exception)
        self.assertTrue( "GQE.Scan.__init__(): t1 exists already" in context.exception)

        with self.assertRaises( ValueError) as context:
            PySpectra.delete()
            scan = PySpectra.Scan( 't1', y = None)
        #print repr( context.exception)
        self.assertTrue( "GQE.Scan.__init__(): if 'x' or 'y' then both have to be supplied"
                         in context.exception)

        with self.assertRaises( ValueError) as context:
            PySpectra.delete()
            scan = PySpectra.Scan( 't1', fileName = 'hallo')
        #print repr( context.exception)
        self.assertTrue( "GQE.Scan.__init__: 'fileName' but no 'x' and no 'y', hallo"
                         in context.exception)

        with self.assertRaises( ValueError) as context:
            PySpectra.delete()
            scan = PySpectra.Scan( 't1', unknown = 't1')
        #print repr( context.exception)
        self.assertTrue( "GQE.Scan.__init__(): dct not empty {'unknown': 't1'}"
                         in context.exception)

        with self.assertRaises( ValueError) as context:
            PySpectra.delete()
            x1  = np.linspace( 0., 10., 100)
            y1  = np.linspace( 0., 10., 101)
            scan = PySpectra.Scan( 't1', x = x1, y = y1)
        #print repr( context.exception)
        self.assertTrue( "GQE.Scan._createScanFromData: 'x' and 'y' differ in length 100 (x) 101 (y)"
                         in context.exception)

        with self.assertRaises( ValueError) as context:
            PySpectra.delete()
            x1  = np.linspace( 0., 10., 100)
            y1  = np.linspace( 0., 10., 100)
            scan = PySpectra.Scan( 't1', x = x1, y = y1)
            scan.setX( 100, 1.)
        #print repr( context.exception)
        self.assertTrue( "GQE.Scan.setX: t1, index 100 out of range [0, 99]"
                         in context.exception)

        with self.assertRaises( ValueError) as context:
            PySpectra.delete()
            x1  = np.linspace( 0., 10., 100)
            y1  = np.linspace( 0., 10., 100)
            scan = PySpectra.Scan( 't1', x = x1, y = y1)
            scan.setY( 100, 1.)
        #print repr( context.exception)
        self.assertTrue( "GQE.Scan.setY: t1, index 100 out of range [0, 99]"
                         in context.exception)

        with self.assertRaises( ValueError) as context:
            PySpectra.delete()
            x1  = np.linspace( 0., 10., 100)
            y1  = np.linspace( 0., 10., 100)
            scan = PySpectra.Scan( 't1', x = x1, y = y1)
            scan = PySpectra.Scan( 't1', reUse = True, x = x1[:99], y = y1[:99])
        #print repr( context.exception)
        self.assertTrue( "GQE.Scan: len( scan.x) 100 != len( kwargs[ 'x']) 99"
                         in context.exception)

        with self.assertRaises( ValueError) as context:
            PySpectra.delete()
            x1  = np.linspace( 0., 10., 100)
            y1  = np.linspace( 0., 10., 100)
            scan = PySpectra.Scan( 't1', x = x1, y = y1)
            scan = PySpectra.Scan( 't1', reUse = True, x = x1, y = y1[:99])
        #print repr( context.exception)
        self.assertTrue( "GQE.Scan: len( scan.y) 100 != len( kwargs[ 'y']) 99"
                         in context.exception)

        with self.assertRaises( ValueError) as context:
            PySpectra.delete()
            x1  = np.linspace( 0., 10., 100)
            y1  = np.linspace( 0., 10., 100)
            scan = PySpectra.Scan( 't1', x = x1, y = y1)
            scan.attrNotExist = 12
        #print repr( context.exception)
        self.assertTrue( "GQE.Scan.__setattr__: t1 unknown attribute attrNotExist"
                         in context.exception)


        with self.assertRaises( ValueError) as context:
            PySpectra.delete()
            x1  = np.linspace( 0., 10., 100)
            y1  = np.linspace( 0., 10., 100)
            scan = PySpectra.Scan( 't1', x = x1, y = y1)
            temp = scan.attrNotExist
        #print repr( context.exception)
        self.assertTrue( "GQE.Scan.__getattr__: t1 unknown attribute attrNotExist"
                         in context.exception)

    def testSSA( self) : 
        print "testPySpectra.testSSA"
        PySpectra.cls()
        PySpectra.delete()
        PySpectra.setTitle( "test SSA")

        g = utils.createGauss( name = "gauss", xMin = -5., xMax = 5., nPts = 101, 
                               lineColor = 'red', x0 = 0., sigma = 1., amplitude = 1.)
        
        g.ssa()
        self.assertEqual( len(g.textList), 5)

        # SSA results
        # midpoint: -6.84879e-06
        # peak-x:   0
        # cms:      -9.65309e-05
        # fwhm:     2.3552
        #
        self.assertTrue( g.textList[0].text == 'SSA results')

        lst = g.textList[1].text.split( ':')
        self.assertTrue( lst[0] == 'midpoint')
        self.assertTrue( abs(float(lst[1])) < 0.0001)
        
        lst = g.textList[2].text.split( ':')
        self.assertTrue( lst[0] == 'peak-x')
        self.assertTrue( abs(float(lst[1])) < 0.0001)
        
        lst = g.textList[3].text.split( ':')
        self.assertTrue( lst[0] == 'cms')
        self.assertTrue( abs(float(lst[1])) < 0.0001)
        
        lst = g.textList[4].text.split( ':')
        self.assertTrue( lst[0] == 'fwhm')
        self.assertTrue( abs(float(lst[1])) < 2.356)
        self.assertTrue( abs(float(lst[1])) > 2.350)

        PySpectra.display()
        PySpectra.processEventsLoop( 1)
        return 

    def testFsa( self): 
        print "testPySpectra.testFsa"
        PySpectra.cls()
        PySpectra.delete()
        g = utils.createGauss( name = "gauss", xMin = -5., xMax = 5., nPts = 101, 
                               lineColor = 'red', x0 = 0.12345, sigma = 1.2345, amplitude = 1.)
        
        (message, xpos, xpeak, xcms, xcen) = g.fsa()

        self.assertEqual( message, 'success')
        self.assertAlmostEqual( xpos, 0.1)
        self.assertAlmostEqual( xpeak, 0.1)
        self.assertAlmostEqual( xcms, 0.1234, 3)
        self.assertAlmostEqual( xcen, 0.1234, 3)

        self.assertTrue( g.textList[0].text == 'FSA results')

        lst = g.textList[1].text.split( ':')
        self.assertTrue( lst[0] == 'xpos')
        
        lst = g.textList[2].text.split( ':')
        self.assertTrue( lst[0] == 'xpeak')
        
        lst = g.textList[3].text.split( ':')
        self.assertTrue( lst[0] == 'xcms')
        
        lst = g.textList[4].text.split( ':')
        self.assertTrue( lst[0] == 'xcen')

        return 

    def testMisc( self) : 
        print "testPySpectra.testMisc"
        PySpectra.cls()
        PySpectra.delete()
        t1 = PySpectra.Scan( name = "t1", xMin = -5., xMax = 5., nPts = 101)
        t2 = PySpectra.Scan( name = "t2", xMin = -5., xMax = 5., nPts = 101)
        PySpectra.display()

        lst = PySpectra.getDisplayList()

        self.assertTrue( len(lst) == 2)

        self.assertTrue( PySpectra.info() == 2)

        self.assertTrue( PySpectra.getIndex( 't1') == 0)

        
    def testDoubles( self) : 

        print "testPySpectra.testDoubles"

        PySpectra.delete()

        with self.assertRaises( ValueError) as context:
            t1 = PySpectra.Scan( name = "t1", xMin = -5., xMax = 5., nPts = 101)
            t2 = PySpectra.Scan( name = "t1", xMin = -5., xMax = 5., nPts = 101)

        #print("testDoubles: caught %s" % repr( context.exception))
        self.assertTrue( "GQE.Scan.__init__(): t1 exists already"
                         in context.exception)
        PySpectra.delete()
        with self.assertRaises( ValueError) as context:
            t1 = PySpectra.Image( name = "t1", data = np.empty((100, 100)))
            t1 = PySpectra.Image( name = "t1", data = np.empty((100, 100)))

        #print repr( context.exception)
        self.assertTrue( "GQE.Image.__init__(): t1 exists already"
                         in context.exception)
        
    def testGetIndex( self) : 

        print "testPySpectra.testGetIndex"

        PySpectra.delete()
        #
        # left-right 
        #
        x1  = np.linspace( 0., 10., 11)
        y1  = np.linspace( 0., 10., 11)
        scan1 = PySpectra.Scan( 't1', x = x1, y = y1)
        self.assertEqual( scan1.getIndex( 4.2), 4)
        self.assertEqual( scan1.getIndex( 4.8), 5)

        with self.assertRaises( ValueError) as context:
            i = scan1.getIndex( -1)

        #print repr( context.exception)
        self.assertTrue( "GQE.getIndex(L2R): x -1 < x[0] 0"
                         in context.exception)

        with self.assertRaises( ValueError) as context:
            i = scan1.getIndex( 11)

        #print repr( context.exception)
        self.assertTrue( "GQE.getIndex(L2R): x 11 > x[currentIndex] 10"
                         in context.exception)
        #
        # reverse the x-axis
        #
        x2 = x1[::-1]
        scan2 = PySpectra.Scan( 't2', x = x2, y = y1)

        self.assertEqual( scan2.getIndex( 4.2), 6)
        self.assertEqual( scan2.getIndex( 4.8), 5)

        with self.assertRaises( ValueError) as context:
            i = scan2.getIndex( -1)

        #print repr( context.exception)
        self.assertTrue( "GQE.getIndex(R2L): x -1 < x[currentIndex] 0"
                         in context.exception)

        with self.assertRaises( ValueError) as context:
            i = scan2.getIndex( 11)

        print repr( context.exception)
        self.assertTrue( "GQE.getIndex(R2L): x 11 > x[0] 10"
                         in context.exception)

        return 

    def testMotorArrowCurrentAndSetPoint( self) : 

        print( "testPySpectra.testMotorArrowCurrentAndSetPoint")

        if utils.getHostname() != 'haso107tk': 
            return 

        PySpectra.cls()
        PySpectra.delete()
        PySpectra.setTitle( "test arrows, current and setpoint")

        g = utils.createGauss( name = "gauss", xMin = -5., xMax = 5., nPts = 101, 
                               lineColor = 'red', x0 = 0., sigma = 1., amplitude = 1.)
        g.x += 50

        g.motorNameList = ["eh_mot66"]
        proxy = PyTango.DeviceProxy( "eh_mot66")

        g.display()

        POSI = 50
        g.setArrowMisc( proxy.position)
        proxy.position = POSI
        print( "testPySpectra.testArrow: moving %s to %g" % (proxy.name(), POSI))
        g.setArrowSetPoint( POSI)
        while proxy.state() == PyTango.DevState.MOVING:
            g.updateArrowCurrent()
            time.sleep( 0.1)
        g.updateArrowCurrent()

        g.display()
            
        POSI = 51
        g.setArrowMisc( proxy.position)
        proxy.position = POSI
        print( "testPySpectra.testArrow: moving %s to %g" % (proxy.name(), POSI))
        g.setArrowSetPoint( POSI)
        while proxy.state() == PyTango.DevState.MOVING:
            g.setArrowCurrent( proxy.position)
            time.sleep( 0.1)
        g.setArrowCurrent( proxy.position)
        return 

    def testMotorArrowMisc( self) : 

        print( "testPySpectra.testMotorArrowMisc")

        PySpectra.cls()
        PySpectra.delete()

        g = utils.createGauss( name = "gauss", xMin = -5., xMax = 5., nPts = 101, 
                               lineColor = 'red', x0 = 0., sigma = 1., amplitude = 1.)

        g.x += 50

        g.motorNameList = ["eh_mot66"]
        PySpectra.setComment( "testPySpectra.testArrowMisc: an arrow should appear at 50.3")
        g.display()
        g.setArrowMisc( 50.3)

        g.display()
        time.sleep(3.0)
        return 

    def testCheckTargetWithinLimits( self): 

        print( "testPySpectra.testCheckTargetWithinLimits")

        if utils.getHostname() != 'haso107tk': 
            return 

        PySpectra.cls()
        PySpectra.delete()

        g = PySpectra.Scan( name = "gauss", xMin = -5., xMax = 5., nPts = 101, 
                      lineColor = 'red')
        mu = 0.
        sigma = 1.
        g.y = 1/(sigma*np.sqrt(2.*np.pi))*np.exp( -(g.y-mu)**2/(2.*sigma**2))
        g.x += 50

        g.motorNameList = ["eh_mot66"]
        proxy = PyTango.DeviceProxy( g.motorNameList[ 0])

        #
        # [ 0.0, 149.4232]
        #

        self.assertEqual( g.checkTargetWithinLimits( g.motorNameList[ 0], 51., 
                                                     proxy, flagConfirm = False), True)
        self.assertEqual( g.checkTargetWithinLimits( g.motorNameList[ 0], -1., 
                                                     proxy, flagConfirm = False), False)
        self.assertEqual( g.checkTargetWithinLimits( g.motorNameList[ 0], 151., 
                                                     proxy, flagConfirm = False), False)
        
        return 


    def testAddText( self): 

        print( "testPySpectra.testAddText")

        PySpectra.cls()
        PySpectra.delete()
        PySpectra.setTitle( "test addText")

        g = utils.createGauss()
        g.addText( name = "testText", x = 0.2, y = 0.1, color = 'magenta', 
                   fontSize = 20, text = "dies ist ein addText test text")

        self.assertEqual( len( g.textList), 1)
        txt = g.textList[0]
        self.assertEqual( txt.name, "testText")
        self.assertEqual( txt.hAlign, "left")
        self.assertEqual( txt.vAlign, "top")
        self.assertEqual( txt.color, "magenta")
        self.assertEqual( txt.fontSize, 20)
        self.assertEqual( txt.x, 0.2)
        self.assertEqual( txt.y, 0.1)
        self.assertEqual( txt.NDC, True)

        g.display()
        PySpectra.processEventsLoop( 1)
        return 

    def testTextOnlyScan( self): 

        print( "testPySpectra.testTextOnlyScan")

        PySpectra.cls()
        PySpectra.delete()
        PySpectra.setTitle( "test textOnly Scans")

        g = PySpectra.Scan( name = "textContainer", textOnly = True)

        g.addText( name = "testText", text="some text to be displayed")
        
        self.assertEqual( len( g.textList), 1)
        txt = g.textList[0]
        self.assertEqual( txt.name, "testText")
        self.assertEqual( txt.hAlign, "left")
        self.assertEqual( txt.vAlign, "top")
        self.assertEqual( txt.color, "black")
        self.assertEqual( txt.x, 0.5)
        self.assertEqual( txt.y, 0.5)
        self.assertEqual( txt.NDC, True)

        g.display()
        PySpectra.processEventsLoop( 1)
        return 
if __name__ == "__main__":
    unittest.main()
