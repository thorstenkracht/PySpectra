#!/bin/env python
'''
cd /home/kracht/Misc/pySpectra
python -m unittest discover -v

python ./test/dMgt/testGQE.py testGQE.testNextPrevScan
python ./test/dMgt/testGQE.py testGQE.testNextPrevImage
python ./test/dMgt/testGQE.py testGQE.testFillData
python ./test/dMgt/testGQE.py testGQE.testFillDataByColumns
python ./test/dMgt/testGQE.py testGQE.testFillDataByGqes
python ./test/dMgt/testGQE.py testGQE.testCreateDelete
python ./test/dMgt/testGQE.py testGQE.testWrite
python ./test/dMgt/testGQE.py testGQE.testRead
python ./test/dMgt/testGQE.py testGQE.testWriteReadImage
python ./test/dMgt/testGQE.py testGQE.test_read
python ./test/dMgt/testGQE.py testGQE.testReuse
python ./test/dMgt/testGQE.py testGQE.testYGreaterThanZero
python ./test/dMgt/testGQE.py testGQE.testSetLimits
python ./test/dMgt/testGQE.py testGQE.testSetXY
python ./test/dMgt/testGQE.py testGQE.testGetXY
python ./test/dMgt/testGQE.py testGQE.testExceptions
python ./test/dMgt/testGQE.py testGQE.testMisc
python ./test/dMgt/testGQE.py testGQE.testDoubles
python ./test/dMgt/testGQE.py testGQE.test_titleAndComment
python ./test/dMgt/testGQE.py testGQE.testSSA
python ./test/dMgt/testGQE.py testGQE.testFsa
python ./test/dMgt/testGQE.py testGQE.testGetIndex
python ./test/dMgt/testGQE.py testGQE.testMotorArrowCurrentAndSetPoint
python ./test/dMgt/testGQE.py testGQE.testMotorArrowMisc
python ./test/dMgt/testGQE.py testGQE.testCheckTargetWithinLimits
'''
import sys, time
import PyTango
import PySpectra
import PySpectra.dMgt.GQE as GQE
import PySpectra.misc.zmqIfc as zmqIfc
import PySpectra.misc.utils as utils
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

        GQE.delete()
        GQE.setTitle( "a_title")
        self.assertEqual( GQE.getTitle(), "a_title")
        GQE.delete()
        self.assertEqual( GQE.getTitle(), None)
        GQE.setTitle( "a_title")
        GQE.setTitle( None)
        self.assertEqual( GQE.getTitle(), None)

        GQE.delete()
        GQE.setComment( "a_comment")
        self.assertEqual( GQE.getComment(), "a_comment")
        GQE.delete()
        self.assertEqual( GQE.getComment(), None)
        GQE.setComment( "a_comment")
        GQE.setComment( None)
        self.assertEqual( GQE.getComment(), None)

        GQE.delete()
        GQE.setTitle( "there must be this title")
        GQE.setComment( "and there must be this comment")
        GQE.Scan( "t1")
        PySpectra.display()
        GQE.show()
        PySpectra.processEventsLoop( 1)

        PySpectra.cls()
        GQE.delete()
        GQE.setTitle( "there is only a title, no comment")
        GQE.Scan( "t1")
        PySpectra.display()
        PySpectra.processEventsLoop( 1)

        PySpectra.cls()
        GQE.delete()
        GQE.setComment( "there is only a comment")
        GQE.Scan( "t1")
        PySpectra.display()
        PySpectra.processEventsLoop( 1)

        print "testGQE.test_titleAndComment DONE"
    
    def test_readMca_v1( self):

        print "testGQE.test_readMca_v1"

        PySpectra.cls()
        GQE.delete()
        GQE.read( "%s/test/data/tst_09153_mca_s1.fio" % pySpectraPath, flagMCA = True)
        lst = GQE.getGqeList()
        self.assertEqual( len( lst), 1)
        self.assertEqual( lst[0].name, "d1_mca01")
        self.assertEqual( lst[0].nPts, 2048)
        
        PySpectra.display()
        #GQE.show()
        print "the graphics window should contain 1 MCA plot now"
        PySpectra.processEventsLoop( 1)

        print "testGQE.test_readMca_v1 DONE"

    def test_readMca_v2( self):

        print "testGQE.test_readMca_v2"

        PySpectra.cls()
        GQE.delete()
        GQE.read( "%s/test/data/tst_09154_mca_s1.fio" % pySpectraPath, flagMCA = True)
        lst = GQE.getGqeList()
        self.assertEqual( len( lst), 2)
        self.assertEqual( lst[0].name, "d1_mca01")
        self.assertEqual( lst[0].nPts, 8192)
        self.assertEqual( lst[1].name, "d1_mca02")
        self.assertEqual( lst[1].nPts, 8192)
        
        PySpectra.display()
        #GQE.show()
        print "the graphics window should contain 2 MCA plots now"
        PySpectra.processEventsLoop( 1)

        print "testGQE.test_readMca_v2 DONE"

    def test_read( self):

        print "testGQE.test_read"

        PySpectra.cls()
        GQE.delete()
        GQE.read( "%s/test/data/ti_au_tio2_sio2_kat55a_0001.fio" % pySpectraPath)
        lst = GQE.getGqeList()
        self.assertEqual( len( lst), 24)
        self.assertEqual( lst[0].name, "TI_AU_TIO2_SIO2_KAT55A_0001")
        self.assertEqual( lst[1].name, "TI_AU_TIO2_SIO2_KAT55A_0001_RING")
        
        PySpectra.display()
        #GQE.show()
        print "the graphics window should contain 24 plots now"
        PySpectra.processEventsLoop( 1)

        PySpectra.cls()
        GQE.delete()
        GQE.read( "%s/test/data/SPLITTER_PXE_BL_22_2.dat" % pySpectraPath)
        lst = GQE.getGqeList()
        self.assertEqual( len( lst), 4)
        self.assertEqual( lst[0].name, "scan1")
        self.assertEqual( lst[1].name, "scan2")
        self.assertEqual( lst[2].name, "scan3")
        self.assertEqual( lst[3].name, "scan4")
        
        PySpectra.display()
        #GQE.show()
        PySpectra.processEventsLoop( 1)

        print "testGQE.test_read DONE"

    def test_doty( self):

        print "testGQE.test_doty"

        PySpectra.cls()
        GQE.delete()

        scan1 = GQE.Scan( name = "notdotyscan", xMin = 10., xMax = 30.0, 
                               nPts = 101, dType = np.float64,
                               lineColor = 'red', lineStyle = 'solidLine')
        self.assertEqual( scan1.doty, False)

        scan2 = GQE.Scan( name = "dotyscan", xMin = 10., xMax = 30.0, 
                               nPts = 101, dType = np.float64,
                               doty = True,lineColor = 'red', lineStyle = 'solidLine')

        self.assertEqual( scan2.doty, True)

        PySpectra.display()
        #PySpectra.show()
        PySpectra.processEventsLoop( 1)

        print "testGQE.test_doty DONE"
        
    def test_createScanByLimit( self):

        print "testGQE.test_createScanByLimit"

        PySpectra.cls()
        GQE.delete()

        scan = GQE.Scan( name = "test1", xMin = 0., xMax = 1.0, 
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

        print "testGQE.test_createScanByLimit DONE"

    def test_createScanByData( self):

        print "testGQE.test_createScanByData"

        PySpectra.cls()
        GQE.delete()
        try:
            scan = GQE.Scan( name = 't1', x = [0, 1, 2, 3, 4])
        except ValueError, e:
            self.assertEqual( str( e), "GQE.Scan.__init__(): if 'x' or 'y' then both have to be supplied")
        try:
            scan = GQE.Scan( name = 't1', y = [0, 1, 2, 3, 4])
        except ValueError, e:
            self.assertEqual( str( e), "GQE.Scan.__init__(): if 'x' or 'y' then both have to be supplied")

        lst = GQE.getGqeList()
        self.assertEqual( len( lst), 0)
        
        scan = GQE.Scan( name = 't1', x = [0, 1, 2, 3, 4], y = [10, 12, 11, 14, 12])

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

        print "testGQE.test_createScanByData, DONE"
        
    def testCreateDelete( self): 
        print "testGQE.testCreateDelete"
        GQE.delete()
        scanLst = GQE.getGqeList()
        self.assertEqual( len( scanLst), 0)
        GQE.Scan( name = 't1')
        GQE.Scan( name = 't2')
        GQE.Scan( name = 't3')
        GQE.Scan( name = 't4')
        PySpectra.display()
        scanLst = GQE.getGqeList()
        self.assertEqual( len( scanLst), 4)
        GQE.delete( [ 't1', 't2'])
        scanLst = GQE.getGqeList()
        self.assertEqual( len( scanLst), 2)
        self.assertEqual( scanLst[0].name, 't3')
        self.assertEqual( scanLst[1].name, 't4')
        GQE.delete()
        scanLst = GQE.getGqeList()
        self.assertEqual( len( scanLst), 0)

        print "testGQE.testCreateDelete, DONE"
        
    def testNextPrevScan( self):
        print "testGQE.testNextPrevScan"
        GQE.delete()
        GQE.Scan( name = 't1')
        GQE.Scan( name = 't2')
        GQE.Scan( name = 't3')
        GQE.Scan( name = 't4')
        self.assertEqual( GQE.nextScan().name, 't1')
        self.assertEqual( GQE.nextScan().name, 't2')
        self.assertEqual( GQE.nextScan().name, 't3')
        self.assertEqual( GQE.nextScan().name, 't4')
        self.assertEqual( GQE.nextScan().name, 't1')
        GQE.delete()
        GQE.Scan( name = 't1')
        GQE.Scan( name = 't2')
        GQE.Scan( name = 't3')
        GQE.Scan( name = 't4')
        self.assertEqual( GQE.prevScan().name, 't1')
        self.assertEqual( GQE.prevScan().name, 't4')
        self.assertEqual( GQE.prevScan().name, 't3')
        self.assertEqual( GQE.prevScan().name, 't2')
        self.assertEqual( GQE.prevScan().name, 't1')

        print "testGQE.testNextPrevScan, DONE"
        
    def testNextPrevImage( self):

        print "testGQE.testNextPrevImage"
        GQE.delete()
        GQE.Image( name = "t1", data = np.empty((100, 100)))
        GQE.Image( name = "t2", data = np.empty((100, 100)))
        GQE.Image( name = "t3", data = np.empty((100, 100)))
        GQE.Image( name = "t4", data = np.empty((100, 100)))
        self.assertEqual( GQE.nextImage().name, 't1')
        self.assertEqual( GQE.nextImage().name, 't2')
        self.assertEqual( GQE.nextImage().name, 't3')
        self.assertEqual( GQE.nextImage().name, 't4')
        self.assertEqual( GQE.nextImage().name, 't1')
        GQE.delete()
        GQE.Image( name = "t1", data = np.empty((100, 100)))
        GQE.Image( name = "t2", data = np.empty((100, 100)))
        GQE.Image( name = "t3", data = np.empty((100, 100)))
        GQE.Image( name = "t4", data = np.empty((100, 100)))
        self.assertEqual( GQE.prevImage().name, 't1')
        self.assertEqual( GQE.prevImage().name, 't4')
        self.assertEqual( GQE.prevImage().name, 't3')
        self.assertEqual( GQE.prevImage().name, 't2')
        self.assertEqual( GQE.prevImage().name, 't1')

        print "testGQE.testNextPrevImage, DONE"

    def testFillData( self):
        print "testGQE.testFillData"
        PySpectra.cls()
        GQE.delete()
        scan = GQE.Scan( name = 't1', xLabel = "up to 200 pts", 
                               nPts = 201, yMin = -10., yMax = 10.)
        self.assertEqual( scan.currentIndex, 200)
        #scan.y = np.tan( scan.x)
        
        startTime = time.time()
        for i in range( len( scan.y)):
            scan.setY( i, math.tan( float( i)/10))
            PySpectra.display()

        diffTime = time.time() - startTime
        self.assertLess( diffTime, 12)

        print "testGQE.testFillData, DONE"

    def testFillDataByColumns( self):

        print "testGQE.testFillDataByColumns"
        PySpectra.cls()
        GQE.delete()
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

        zmqIfc.execHsh( hsh)

        lst = GQE.getGqeList()
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
        print "testGQE.testFillDataByColumns, DONE"

    def testFillDataByGqes( self):

        print "testGQE.testFillDataByGqes"
        PySpectra.cls()
        GQE.delete()
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

        zmqIfc.execHsh( hsh)

        lst = GQE.getGqeList()
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
        print "testGQE.testFillDataByGqes, DONE"

    def testWrite( self): 
        print "testGQE.testWrite"
        PySpectra.cls()
        GQE.delete()
        scan = GQE.Scan( name = 't1', xLabel = "up to 200 pts", 
                               nPts = 201, yMin = -10., yMax = 10.)
        ret = GQE.write( ['t1'])

        GQE.delete()

        self.assertEqual( os.path.exists( ret), True)

        GQE.read( ret)

        scanLst = GQE.getGqeList()
        self.assertEqual( len( scanLst), 1)
        self.assertEqual( scanLst[0].name, "t1")
        self.assertEqual( scanLst[0].nPts, 201)

    def testRead( self): 
        print "testGQE.testRead"
        PySpectra.cls()
        GQE.delete()
        scan = GQE.Scan( name = 't1', xLabel = "up to 200 pts", 
                               nPts = 201, yMin = -10., yMax = 10.)
        ret = GQE.write( ['t1'])

        GQE.delete()

        self.assertEqual( os.path.exists( ret), True)

        scan = GQE.Scan( name = 't1', fileName = ret, x = 1, y = 2)

        scanLst = GQE.getGqeList()
        self.assertEqual( len( scanLst), 1)
        self.assertEqual( scanLst[0].name, "t1")
        self.assertEqual( scanLst[0].nPts, 201)


    def testWriteReadImage( self): 
        print "testGQE.testWrite"
        PySpectra.cls()
        GQE.delete()

        (xmin, xmax) = (-2., 1)
        (ymin, ymax) = (-1.5, 1.5)
        (width, height) = (200, 200)
        maxiter = 100
            
        m = GQE.Image( name = "MandelbrotSet", colorMap = 'Greys', 
                       estimatedMax = maxiter, 
                       xMin = xmin, xMax = xmax, width = width, 
                       yMin = ymin, yMax = ymax, height = height)

        m.zoomMb( flagDisplay = False)

        ret = GQE.write( ['MandelbrotSet'])

        PySpectra.cls()
        GQE.delete()

        self.assertEqual( os.path.exists( ret), True)

        GQE.read( ret)

        GQE.setTitle( "The Mandelbrotset")
        PySpectra.display()
        PySpectra.processEventsLoop( 2)

        lst = GQE.getGqeList()
        self.assertEqual( len( lst), 1)
        
        ima = lst[0]
        self.assertEqual( ima.name, "MandelbrotSet")
        self.assertEqual( type( ima), PySpectra.dMgt.GQE.Image)
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
        print "testGQE.testReuse"
        PySpectra.cls()
        GQE.delete()
        scan = GQE.Scan( name = 't1', xLabel = "100 pts, going to be re-used", 
                               nPts = 100, yMin = -10., yMax = 10.)

        for i in range( 10):
            data = np.random.normal(size=(1,100))
            x1  = np.linspace( 0., 10., 100)
            PySpectra.display()
            PySpectra.processEventsLoop( 1)
            scan = GQE.Scan( name = 't1', reUse = True, x = x1, y = data[0])

    def testYGreaterThanZero( self): 
        print "testGQE.testYGreaterThanZero"
        PySpectra.cls()
        GQE.delete()
        scan = GQE.Scan( name = 't1', xLabel = "11 pts, going to be re-used", 
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

    def testSetLimits( self): 
        print "testGQE.testSetLimits"
        PySpectra.cls()
        GQE.delete()
        scan = GQE.Scan( name = 't1', 
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
        print "testGQE.testSetXY"
        PySpectra.cls()
        GQE.delete()
        x  = np.linspace( 0., 10., 100)
        y  = np.linspace( 0., 10., 100)
        scan = GQE.Scan( 't1', x = x, y = y)

        scan.setX( 0, 12)
        self.assertEqual( scan.x[0], 12)
        scan.setY( 0, 12)
        self.assertEqual( scan.y[0], 12)
        scan.setXY( 1, 11, 12)
        self.assertEqual( scan.x[1], 11)
        self.assertEqual( scan.y[1], 12)


        with self.assertRaises( ValueError) as context:
            scan.setXY( 101, 11, 12)
        print repr( context.exception)
        self.assertTrue( "GQE.Scan.setXY: t1, index 101 out of range [0, 100]"
                         in context.exception)

    def testGetXY( self) : 
        print "testGQE.testSetXY"
        PySpectra.cls()
        GQE.delete()
        x  = np.linspace( 0., 10., 100)
        y  = np.linspace( 0., 10., 100)
        scan = GQE.Scan( 't1', x = x, y = y)

        scan.setX( 0, 12)
        self.assertEqual( scan.getX( 0), 12)
        scan.setY( 0, 12)
        self.assertEqual( scan.getY(0), 12)
        
    def testExceptions( self): 
        print "testGQE.testExceptions"
        PySpectra.cls()
        GQE.delete()

        with self.assertRaises( ValueError) as context:
            GQE.delete()
            scan = GQE.Scan()
        self.assertTrue( "GQE.Scan: 'name' is missing" in context.exception)

        with self.assertRaises( ValueError) as context:
            GQE.delete()
            scan = GQE.Scan( name = 't1')
            GQE.delete( 't2')
        #print repr( context.exception)
        self.assertTrue( "GQE.delete: not found t2" in context.exception)

        with self.assertRaises( ValueError) as context:
            GQE.delete()
            scan = GQE.Scan( 't1')
            scan = GQE.Scan( 't1')
        #print repr( context.exception)
        self.assertTrue( "GQE.Scan.__init__(): t1 exists already" in context.exception)

        with self.assertRaises( ValueError) as context:
            GQE.delete()
            scan = GQE.Scan( 't1')
            scan = GQE.Scan( 't1')
        #print repr( context.exception)
        self.assertTrue( "GQE.Scan.__init__(): t1 exists already" in context.exception)

        with self.assertRaises( ValueError) as context:
            GQE.delete()
            scan = GQE.Scan( 't1', y = None)
        #print repr( context.exception)
        self.assertTrue( "GQE.Scan.__init__(): if 'x' or 'y' then both have to be supplied"
                         in context.exception)

        with self.assertRaises( ValueError) as context:
            GQE.delete()
            scan = GQE.Scan( 't1', fileName = 'hallo')
        #print repr( context.exception)
        self.assertTrue( "GQE.Scan.__init__: 'fileName' but no 'x' and no 'y', hallo"
                         in context.exception)

        with self.assertRaises( ValueError) as context:
            GQE.delete()
            scan = GQE.Scan( 't1', unknown = 't1')
        #print repr( context.exception)
        self.assertTrue( "GQE.Scan.__init__(): dct not empty {'unknown': 't1'}"
                         in context.exception)

        with self.assertRaises( ValueError) as context:
            GQE.delete()
            x1  = np.linspace( 0., 10., 100)
            y1  = np.linspace( 0., 10., 101)
            scan = GQE.Scan( 't1', x = x1, y = y1)
        #print repr( context.exception)
        self.assertTrue( "GQE.Scan._createScanFromData: 'x' and 'y' differ in length 100 (x) 101 (y)"
                         in context.exception)

        with self.assertRaises( ValueError) as context:
            GQE.delete()
            x1  = np.linspace( 0., 10., 100)
            y1  = np.linspace( 0., 10., 100)
            scan = GQE.Scan( 't1', x = x1, y = y1)
            scan.setX( 100, 1.)
        #print repr( context.exception)
        self.assertTrue( "GQE.Scan.setX: t1, index 100 out of range [0, 99]"
                         in context.exception)

        with self.assertRaises( ValueError) as context:
            GQE.delete()
            x1  = np.linspace( 0., 10., 100)
            y1  = np.linspace( 0., 10., 100)
            scan = GQE.Scan( 't1', x = x1, y = y1)
            scan.setY( 100, 1.)
        #print repr( context.exception)
        self.assertTrue( "GQE.Scan.setY: t1, index 100 out of range [0, 99]"
                         in context.exception)

        with self.assertRaises( ValueError) as context:
            GQE.delete()
            x1  = np.linspace( 0., 10., 100)
            y1  = np.linspace( 0., 10., 100)
            scan = GQE.Scan( 't1', x = x1, y = y1)
            scan = GQE.Scan( 't1', reUse = True, x = x1[:99], y = y1[:99])
        #print repr( context.exception)
        self.assertTrue( "GQE.Scan: len( scan.x) 100 != len( kwargs[ 'x']) 99"
                         in context.exception)

        with self.assertRaises( ValueError) as context:
            GQE.delete()
            x1  = np.linspace( 0., 10., 100)
            y1  = np.linspace( 0., 10., 100)
            scan = GQE.Scan( 't1', x = x1, y = y1)
            scan = GQE.Scan( 't1', reUse = True, x = x1, y = y1[:99])
        #print repr( context.exception)
        self.assertTrue( "GQE.Scan: len( scan.y) 100 != len( kwargs[ 'y']) 99"
                         in context.exception)

        with self.assertRaises( ValueError) as context:
            GQE.delete()
            x1  = np.linspace( 0., 10., 100)
            y1  = np.linspace( 0., 10., 100)
            scan = GQE.Scan( 't1', x = x1, y = y1)
            scan.attrNotExist = 12
        #print repr( context.exception)
        self.assertTrue( "GQE.Scan.__setattr__: t1 unknown attribute attrNotExist"
                         in context.exception)


        with self.assertRaises( ValueError) as context:
            GQE.delete()
            x1  = np.linspace( 0., 10., 100)
            y1  = np.linspace( 0., 10., 100)
            scan = GQE.Scan( 't1', x = x1, y = y1)
            temp = scan.attrNotExist
        #print repr( context.exception)
        self.assertTrue( "GQE.Scan.__getattr__: t1 unknown attribute attrNotExist"
                         in context.exception)

    def testSSA( self) : 
        print "testGQE.testSSA"
        PySpectra.cls()
        GQE.delete()
        g = GQE.Scan( name = "gauss", xMin = -5., xMax = 5., nPts = 101)
        mu = 0.
        sigma = 1.
        g.y = 1/(sigma*np.sqrt(2.*np.pi))*np.exp( -(g.y-mu)**2/(2*sigma**2))
        
        g.ssa()
        self.assertEqual( len(g.textList), 4)

        #
        # midpoint: -6.84879e-06
        # peak-x:   0
        # cms:      -9.65309e-05
        # fwhm:     2.3552
        #
        lst = g.textList[0].text.split( ':')
        self.assertTrue( lst[0] == 'midpoint')
        self.assertTrue( abs(float(lst[1])) < 0.0001)
        
        lst = g.textList[1].text.split( ':')
        self.assertTrue( lst[0] == 'peak-x')
        self.assertTrue( abs(float(lst[1])) < 0.0001)
        
        lst = g.textList[2].text.split( ':')
        self.assertTrue( lst[0] == 'cms')
        self.assertTrue( abs(float(lst[1])) < 0.0001)
        
        lst = g.textList[3].text.split( ':')
        self.assertTrue( lst[0] == 'fwhm')
        self.assertTrue( abs(float(lst[1])) < 2.356)
        self.assertTrue( abs(float(lst[1])) > 2.350)


    def testFsa( self): 
        print "testGQE.testFsa"
        PySpectra.cls()
        GQE.delete()
        g = GQE.Scan( name = "gauss", xMin = -5., xMax = 5., nPts = 101)
        mu = 0.12345
        sigma = 1.2345
        g.y = 1/(sigma*np.sqrt(2.*np.pi))*np.exp( -(g.y-mu)**2/(2*sigma**2))
        
        (message, xpos, xpeak, xcms, xcen) = g.fsa()

        self.assertEqual( message, 'success')
        self.assertAlmostEqual( xpos, 0.1)
        self.assertAlmostEqual( xpeak, 0.1)
        self.assertAlmostEqual( xcms, 0.1234, 3)
        self.assertAlmostEqual( xcen, 0.1234, 3)

        return 

    def testMisc( self) : 
        print "testGQE.testMisc"
        PySpectra.cls()
        GQE.delete()
        t1 = GQE.Scan( name = "t1", xMin = -5., xMax = 5., nPts = 101)
        t2 = GQE.Scan( name = "t2", xMin = -5., xMax = 5., nPts = 101)
        PySpectra.display()

        lst = GQE.getDisplayList()

        self.assertTrue( len(lst) == 2)

        self.assertTrue( GQE.info() == 2)

        self.assertTrue( GQE.getIndex( 't1') == 0)

        
    def testDoubles( self) : 

        print "testGQE.testDoubles"

        GQE.delete()

        with self.assertRaises( ValueError) as context:
            t1 = GQE.Scan( name = "t1", xMin = -5., xMax = 5., nPts = 101)
            t2 = GQE.Scan( name = "t1", xMin = -5., xMax = 5., nPts = 101)

        #print repr( context.exception)
        self.assertTrue( "GQE.Scan.__init__(): t1 exists already"
                         in context.exception)
        GQE.delete()
        with self.assertRaises( ValueError) as context:
            t1 = GQE.Image( name = "t1", data = np.empty((100, 100)))
            t1 = GQE.Image( name = "t1", data = np.empty((100, 100)))

        #print repr( context.exception)
        self.assertTrue( "GQE.Image.__init__(): t1 exists already"
                         in context.exception)
        
    def testGetIndex( self) : 

        print "testGQE.testGetIndex"

        GQE.delete()
        #
        # left-right 
        #
        x1  = np.linspace( 0., 10., 11)
        y1  = np.linspace( 0., 10., 11)
        scan1 = GQE.Scan( 't1', x = x1, y = y1)
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
        scan2 = GQE.Scan( 't2', x = x2, y = y1)

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

        if utils.getHostname() != 'haso107tk': 
            return 

        PySpectra.cls()
        GQE.delete()

        g = GQE.Scan( name = "gauss", xMin = -5., xMax = 5., nPts = 101, 
                      lineColor = 'red')
        mu = 0.
        sigma = 1.
        g.y = 1/(sigma*np.sqrt(2.*np.pi))*np.exp( -(g.y-mu)**2/(2.*sigma**2))

        g.x += 50

        g.motorNameList = ["eh_mot66"]
        proxy = PyTango.DeviceProxy( "eh_mot66")

        g.display()

        POSI = 50
        g.setArrowMisc( proxy.position)
        proxy.position = POSI
        print( "testGQE.testArrow: moving %s to %g" % (proxy.name(), POSI))
        g.setArrowSetPoint( POSI)
        while proxy.state() == PyTango.DevState.MOVING:
            g.updateArrowCurrent()
            time.sleep(1.0)

        g.display()
            
        POSI = 51
        g.setArrowMisc( proxy.position)
        proxy.position = POSI
        print( "testGQE.testArrow: moving %s to %g" % (proxy.name(), POSI))
        g.setArrowSetPoint( POSI)
        while proxy.state() == PyTango.DevState.MOVING:
            g.setArrowCurrent( proxy.position)
            time.sleep(1.0)
        return 

    def testMotorArrowMisc( self) : 

        PySpectra.cls()
        GQE.delete()

        g = GQE.Scan( name = "gauss", xMin = -5., xMax = 5., nPts = 101, 
                      lineColor = 'red')
        mu = 0.
        sigma = 1.
        g.y = 1/(sigma*np.sqrt(2.*np.pi))*np.exp( -(g.y-mu)**2/(2.*sigma**2))
        g.x += 50


        g.motorNameList = ["eh_mot66"]
        g.display()

        print( "testGQE.testArrowMisc: an arrow should appear at 50.3")
        g.setArrowMisc( 50.3)

        g.display()
        time.sleep(3.0)
        return 

    def testCheckTargetWithinLimits( self): 

        if utils.getHostname() != 'haso107tk': 
            return 

        PySpectra.cls()
        GQE.delete()

        g = GQE.Scan( name = "gauss", xMin = -5., xMax = 5., nPts = 101, 
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

        self.assertEqual( g.checkTargetWithinLimits( g.motorNameList[ 0], 51., proxy, flagConfirm = False), True)
        self.assertEqual( g.checkTargetWithinLimits( g.motorNameList[ 0], -1., proxy, flagConfirm = False), False)
        self.assertEqual( g.checkTargetWithinLimits( g.motorNameList[ 0], 151., proxy, flagConfirm = False), False)
        
        return 
         
if __name__ == "__main__":
    unittest.main()
