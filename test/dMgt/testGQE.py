#!/bin/env python
'''
cd /home/kracht/Misc/pySpectra
python -m unittest discover -v

python ./test/dMgt/testGQE.py testGQE.testNextPrev
python ./test/dMgt/testGQE.py testGQE.testFillData
python ./test/dMgt/testGQE.py testGQE.testCreateDelete
python ./test/dMgt/testGQE.py testGQE.testWrite
python ./test/dMgt/testGQE.py testGQE.testRead
python ./test/dMgt/testGQE.py testGQE.test_read
python ./test/dMgt/testGQE.py testGQE.testReuse
python ./test/dMgt/testGQE.py testGQE.testYGreaterThanZero
python ./test/dMgt/testGQE.py testGQE.testSetLimits
python ./test/dMgt/testGQE.py testGQE.testSetXY
python ./test/dMgt/testGQE.py testGQE.testGetXY
python ./test/dMgt/testGQE.py testGQE.testExceptions
python ./test/dMgt/testGQE.py testGQE.testMisc
python ./test/dMgt/testGQE.py testGQE.testDoubles
python ./test/dMgt/testGQE.py testGQE.testToPysp1
python ./test/dMgt/testGQE.py testGQE.testToPysp2
python ./test/dMgt/testGQE.py testGQE.testToPysp3
python ./test/dMgt/testGQE.py testGQE.testToPysp4
python ./test/dMgt/testGQE.py testGQE.testToPysp5
python ./test/dMgt/testGQE.py testGQE.testToPysp6
python ./test/dMgt/testGQE.py testGQE.testToPysp7
python ./test/dMgt/testGQE.py testGQE.test_titleAndComment
python ./test/dMgt/testGQE.py testGQE.testSSA
'''
import sys
#pySpectraPath = "/home/kracht/Misc/pySpectra"
pySpectraPath = "."
sys.path.append( pySpectraPath)

import PySpectra
import PySpectra.dMgt.GQE as gqe
import numpy as np
import unittest
import time, sys, os
import math 
import pyqtgraph as pg



def mandelbrot( c, maxiter):
    z = c
    for n in range(maxiter):
        if abs(z) > 2:
            return n
        z = z*z + c
    return 0

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
        PySpectra.procEventsLoop( 1)

        PySpectra.cls()
        PySpectra.delete()
        PySpectra.setTitle( "there is only a title, no comment")
        PySpectra.Scan( "t1")
        PySpectra.display()
        PySpectra.procEventsLoop( 1)

        PySpectra.cls()
        PySpectra.delete()
        PySpectra.setComment( "there is only a comment")
        PySpectra.Scan( "t1")
        PySpectra.display()
        PySpectra.procEventsLoop( 1)

        print "testGQE.test_titleAndComment DONE"
    
    def test_readMca_v1( self):

        print "testGQE.test_readMca_v1"

        PySpectra.cls()
        PySpectra.delete()
        PySpectra.read( "%s/test/data/tst_09153_mca_s1.fio" % pySpectraPath, flagMCA = True)
        lst = PySpectra.getGqeList()
        self.assertEqual( len( lst), 1)
        self.assertEqual( lst[0].name, "d1_mca01")
        self.assertEqual( lst[0].nPts, 2048)
        
        PySpectra.display()
        #PySpectra.show()
        print "the graphics window should contain 1 MCA plot now"
        PySpectra.procEventsLoop( 1)

        print "testGQE.test_readMca_v1 DONE"

    def test_readMca_v2( self):

        print "testGQE.test_readMca_v2"

        PySpectra.cls()
        PySpectra.delete()
        PySpectra.read( "%s/test/data/tst_09154_mca_s1.fio" % pySpectraPath, flagMCA = True)
        lst = PySpectra.getGqeList()
        self.assertEqual( len( lst), 2)
        self.assertEqual( lst[0].name, "d1_mca01")
        self.assertEqual( lst[0].nPts, 8192)
        self.assertEqual( lst[1].name, "d1_mca02")
        self.assertEqual( lst[1].nPts, 8192)
        
        PySpectra.display()
        #PySpectra.show()
        print "the graphics window should contain 2 MCA plots now"
        PySpectra.procEventsLoop( 1)

        print "testGQE.test_readMca_v2 DONE"

    def test_read( self):

        print "testGQE.test_read"

        PySpectra.cls()
        PySpectra.delete()
        PySpectra.read( "%s/test/data/ti_au_tio2_sio2_kat55a_0001.fio" % pySpectraPath)
        lst = PySpectra.getGqeList()
        self.assertEqual( len( lst), 24)
        self.assertEqual( lst[0].name, "TI_AU_TIO2_SIO2_KAT55A_0001")
        self.assertEqual( lst[1].name, "TI_AU_TIO2_SIO2_KAT55A_0001_RING")
        
        PySpectra.display()
        #PySpectra.show()
        print "the graphics window should contain 24 plots now"
        PySpectra.procEventsLoop( 1)

        PySpectra.cls()
        PySpectra.delete()
        print "reading splitter"
        PySpectra.read( "%s/test/data/SPLITTER_PXE_BL_22_2.dat" % pySpectraPath)
        print "reading splitter DONE"
        lst = PySpectra.getGqeList()
        print "scanList", repr( lst)
        self.assertEqual( len( lst), 4)
        self.assertEqual( lst[0].name, "scan1")
        self.assertEqual( lst[1].name, "scan2")
        self.assertEqual( lst[2].name, "scan3")
        self.assertEqual( lst[3].name, "scan4")
        
        PySpectra.display()
        #PySpectra.show()
        PySpectra.procEventsLoop( 1)

        print "testGQE.test_read DONE"

    def test_doty( self):

        print "testGQE.test_doty"

        PySpectra.cls()
        PySpectra.delete()

        scan1 = PySpectra.Scan( name = "notdotyscan", xMin = 10., xMax = 30.0, 
                               nPts = 101, dType = np.float64,
                               lineColor = 'red', lineStyle = 'solidLine')
        self.assertEqual( scan1.doty, False)

        scan2 = PySpectra.Scan( name = "dotyscan", xMin = 10., xMax = 30.0, 
                               nPts = 101, dType = np.float64,
                               doty = True,lineColor = 'red', lineStyle = 'solidLine')

        self.assertEqual( scan2.doty, True)

        PySpectra.display()
        #PySpectra.show()
        PySpectra.procEventsLoop( 1)

        print "testGQE.test_doty DONE"
        
    def test_createScanByLimit( self):

        print "testGQE.test_createScanByLimit"

        PySpectra.cls()
        PySpectra.delete()

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

        print "testGQE.test_createScanByLimit DONE"

    def test_createScanByData( self):

        print "testGQE.test_createScanByData"

        PySpectra.cls()
        PySpectra.delete()
        try:
            scan = PySpectra.Scan( name = 't1', x = [0, 1, 2, 3, 4])
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

        print "testGQE.test_createScanByData, DONE"
        
    def testCreateDelete( self): 
        print "testGQE.testCreateDelete"
        PySpectra.delete()
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

        print "testGQE.testCreateDelete, DONE"
        
    def testNextPrev( self):
        print "testGQE.testNextPrev"
        PySpectra.delete()
        PySpectra.Scan( name = 't1')
        PySpectra.Scan( name = 't2')
        PySpectra.Scan( name = 't3')
        PySpectra.Scan( name = 't4')
        self.assertEqual( gqe.nextScan().name, 't1')
        self.assertEqual( gqe.nextScan().name, 't2')
        self.assertEqual( gqe.nextScan().name, 't3')
        self.assertEqual( gqe.nextScan().name, 't4')
        self.assertEqual( gqe.nextScan().name, 't1')
        PySpectra.delete()
        PySpectra.Scan( name = 't1')
        PySpectra.Scan( name = 't2')
        PySpectra.Scan( name = 't3')
        PySpectra.Scan( name = 't4')
        self.assertEqual( gqe.prevScan().name, 't1')
        self.assertEqual( gqe.prevScan().name, 't4')
        self.assertEqual( gqe.prevScan().name, 't3')
        self.assertEqual( gqe.prevScan().name, 't2')
        self.assertEqual( gqe.prevScan().name, 't1')

        print "testGQE.testNextPrev, DONE"

    def testFillData( self):
        print "testGQE.testFillData"
        PySpectra.cls()
        PySpectra.delete()
        scan = PySpectra.Scan( name = 't1', xLabel = "up to 200 pts", 
                               nPts = 201, yMin = -10., yMax = 10.)
        self.assertEqual( scan.currentIndex, 200)
        #scan.y = np.tan( scan.x)
        
        startTime = time.time()
        for i in range( len( scan.y)):
            scan.setY( i, math.tan( float( i)/10))
            PySpectra.display()

        diffTime = time.time() - startTime
        self.assertLess( diffTime, 8)

        print "testGQE.testFillData, DONE"

    def testWrite( self): 
        print "testGQE.testWrite"
        PySpectra.cls()
        PySpectra.delete()
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
        print "testGQE.testRead"
        PySpectra.cls()
        PySpectra.delete()
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


    def testReuse( self): 
        print "testGQE.testReuse"
        PySpectra.cls()
        PySpectra.delete()
        scan = PySpectra.Scan( name = 't1', xLabel = "100 pts, going to be re-used", 
                               nPts = 100, yMin = -10., yMax = 10.)

        for i in range( 10):
            data = np.random.normal(size=(1,100))
            x1  = np.linspace( 0., 10., 100)
            PySpectra.display()
            PySpectra.procEventsLoop( 1)
            scan = PySpectra.Scan( name = 't1', reUse = True, x = x1, y = data[0])

    def testYGreaterThanZero( self): 
        print "testGQE.testYGreaterThanZero"
        PySpectra.cls()
        PySpectra.delete()
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

    def testSetLimits( self): 
        print "testGQE.testSetLimits"
        PySpectra.cls()
        PySpectra.delete()
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
        print "testGQE.testSetXY"
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
        print repr( context.exception)
        self.assertTrue( "GQE.Scan.setXY: t1, index 101 out of range [0, 100]"
                         in context.exception)

    def testGetXY( self) : 
        print "testGQE.testSetXY"
        PySpectra.cls()
        PySpectra.delete()
        x  = np.linspace( 0., 10., 100)
        y  = np.linspace( 0., 10., 100)
        scan = PySpectra.Scan( 't1', x = x, y = y)

        scan.setX( 0, 12)
        self.assertEqual( scan.getX( 0), 12)
        scan.setY( 0, 12)
        self.assertEqual( scan.getY(0), 12)
        
    def testExceptions( self): 
        print "testGQE.testExceptions"
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
        print "testGQE.testSSA"
        PySpectra.cls()
        PySpectra.delete()
        g = PySpectra.Scan( name = "gauss", xMin = -5., xMax = 5., nPts = 101)
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


    def testMisc( self) : 
        print "testGQE.testMisc"
        PySpectra.cls()
        PySpectra.delete()
        t1 = PySpectra.Scan( name = "t1", xMin = -5., xMax = 5., nPts = 101)
        t2 = PySpectra.Scan( name = "t2", xMin = -5., xMax = 5., nPts = 101)
        PySpectra.display()

        lst = PySpectra.dMgt.GQE.getDisplayList()

        self.assertTrue( len(lst) == 2)

        self.assertTrue( PySpectra.dMgt.GQE.info() == 2)

        self.assertTrue( PySpectra.dMgt.GQE.getIndex( 't1') == 0)

        
    def testDoubles( self) : 

        print "testGQE.testDoubles"

        PySpectra.delete()

        with self.assertRaises( ValueError) as context:
            t1 = PySpectra.Scan( name = "t1", xMin = -5., xMax = 5., nPts = 101)
            t2 = PySpectra.Scan( name = "t1", xMin = -5., xMax = 5., nPts = 101)

        #print repr( context.exception)
        self.assertTrue( "GQE.Scan.__init__(): t1 exists already"
                         in context.exception)
        PySpectra.delete()
        with self.assertRaises( ValueError) as context:
            t1 = PySpectra.Image( name = "t1", data = np.empty((100, 100)))
            t1 = PySpectra.Image( name = "t1", data = np.empty((100, 100)))

        #print repr( context.exception)
        self.assertTrue( "GQE.Image.__init__(): t1 exists already"
                         in context.exception)

        
    def testToPysp1( self) : 
        import random
        print "testGQE.testToPysp1"

        hsh = PySpectra.toPysp( { 'command': ['cls', 'delete']})
        self.assertEqual( hsh[ 'result'], 'done')

        MAX = 25
        pos = [float(n)/MAX for n in range( MAX)]
        d1 = [random.random() for n in range( MAX)]
        d2 = [random.random() for n in range( MAX)]
        hsh = PySpectra.toPysp( { 'putData': {'title': "Important Data", 
                                              'comment': "a comment", 
                                              'columns': 
                                              [ { 'name': "eh_mot01", 'data' : pos},
                                                { 'name': "eh_c01", 'data' : d1},
                                                { 'name': "eh_c02", 'data' : d2, 
                                                  'symbolColor': 'blue', 'symbol': '+', 'symbolSize': 5, 
                                                  'xLog': False, 'yLog': False, 
                                                  'showGridX': False, 'showGridY': False}]}})
        self.assertEqual( hsh[ 'result'], 'done')
        PySpectra.toPysp( { 'command': ['display']})
        self.assertEqual( hsh[ 'result'], 'done')
        PySpectra.procEventsLoop( 1)
        lst = PySpectra.getGqeList()
        self.assertEqual( len( lst), 2)
        self.assertEqual( lst[0].name, "eh_c01")
        self.assertEqual( lst[1].name, "eh_c02")
        
        #
        # retrieve the data 
        #
        hsh = PySpectra.toPysp( { 'getData': True})
        self.assertEqual( hsh[ 'result'], 'done')
        #
        # ... and compare.
        #
        for i in range( MAX):
            self.assertEqual( pos[i], hsh[ 'getData']['EH_C01']['x'][i])
            self.assertEqual( d1[i], hsh[ 'getData']['EH_C01']['y'][i])
            self.assertEqual( d2[i], hsh[ 'getData']['EH_C02']['y'][i])
        print "testGQE.testToPysp1 DONE"
        return 
        
    def testToPysp2( self) : 
        import random
        print "testGQE.testToPysp1"

        hsh = PySpectra.toPysp( { 'command': ['cls', 'delete']})
        self.assertEqual( hsh[ 'result'], 'done')
        MAX = 25
        pos = [float(n)/MAX for n in range( MAX)]
        d1 = [random.random() for n in range( MAX)]
        d2 = [random.random() for n in range( MAX)]
        hsh = PySpectra.toPysp( { 'Scan': { 'name': "d1", 'x': pos, 'y': d1}})
        self.assertEqual( hsh[ 'result'], 'done')
        hsh = PySpectra.toPysp( { 'Scan': { 'name': "d2", 'x': pos, 'y': d2}})
        self.assertEqual( hsh[ 'result'], 'done')

        PySpectra.toPysp( { 'command': ['setTitle \"a title\"']})
        self.assertEqual( hsh[ 'result'], 'done')
        PySpectra.toPysp( { 'command': ['setComment \"a comment\"']})
        self.assertEqual( hsh[ 'result'], 'done')
        PySpectra.toPysp( { 'command': ['display']})
        self.assertEqual( hsh[ 'result'], 'done')
        PySpectra.procEventsLoop( 1)
        lst = PySpectra.getGqeList()
        self.assertEqual( len( lst), 2)
        self.assertEqual( lst[0].name, "d1")
        self.assertEqual( lst[1].name, "d2")

        #
        # retrieve the data and compare
        #
        hsh = PySpectra.toPysp( { 'getData': True})
        for i in range( MAX):
            self.assertEqual( pos[i], hsh[ 'getData']['D1']['x'][i])
            self.assertEqual( d1[i], hsh[ 'getData']['D1']['y'][i])
            self.assertEqual( d2[i], hsh[ 'getData']['D2']['y'][i])
        #
        # set y-values 
        #
        for i in range( MAX):
            PySpectra.toPysp( { 'command': ['setY d1 %d %g' % (i, float(i)/10.)]})
        #
        # and compare
        #
        o = PySpectra.getGqe( 'd1')
        for i in range( MAX):
            self.assertEqual( o.y[i], float(i)/10.)
        
        PySpectra.toPysp( { 'command': ['cls', 'display']})
        self.assertEqual( hsh[ 'result'], 'done')
        PySpectra.procEventsLoop( 1)

        
        print "testGQE.testToPysp2 DONE"
        return 

    def testToPysp3( self) : 
        '''
        set the mandelbrot pixel in pixel numbers (whole numbers)
        '''
        hsh = PySpectra.toPysp( { 'command': ['cls', 'delete']})
        self.assertEqual( hsh[ 'result'], 'done')
        hsh = PySpectra.toPysp( { 'command': ['setWsViewport dina5s']})
        self.assertEqual( hsh[ 'result'], 'done')

        (xmin, xmax) = (-2.,-0.5)
        (ymin, ymax) = (0, 1.5)
        (width, height) = (100, 100)
        maxiter = 25

        #
        # do the clean-up before we start
        #
        hsh =  PySpectra.toPysp( { 'command': ['delete', 'setWsViewport DINA5S', 'cls']})
        self.assertEqual( hsh[ 'result'], 'done')

        #
        # create the image
        #
        hsh = { 'Image': 
                { 'name': "MandelBrot",
                  'xMin': xmin, 'xMax': xmax, 'width': width, 
                  'yMin': ymin, 'yMax': ymax, 'height': height}}

        hsh = PySpectra.toPysp( hsh)
        self.assertEqual( hsh[ 'result'], 'done')
        #
        # fill the image, pixel by pixel
        #
        r1 = np.linspace(xmin, xmax, width)
        r2 = np.linspace(ymin, ymax, height)
        for i in range(width):
            for j in range(height):
                res = mandelbrot(r1[i] + 1j*r2[j],maxiter)
                hsh = { 'command': [ 'setPixelImage MandelBrot %d %d %g' % ( i, j, res)]}
                hsh = PySpectra.toPysp( hsh)
                self.assertEqual( hsh[ 'result'], 'done')
            hsh =  PySpectra.toPysp( { 'command': ['cls', 'display']})
            self.assertEqual( hsh[ 'result'], 'done')
        PySpectra.procEventsLoop( 1)

    def testToPysp4( self) : 
        '''
        set the mandelbrot pixel in world coordinates
        '''
        hsh = PySpectra.toPysp( { 'command': ['cls', 'delete']})
        self.assertEqual( hsh[ 'result'], 'done')
        hsh = PySpectra.toPysp( { 'command': ['setWsViewport dina5s']})
        self.assertEqual( hsh[ 'result'], 'done')

        (xmin, xmax) = (-2.,-0.5)
        (ymin, ymax) = (0, 1.5)
        (width, height) = (100, 100)
        maxiter = 25

        #
        # do the clean-up before we start
        #
        hsh =  PySpectra.toPysp( { 'command': ['delete', 'setWsViewport DINA5S', 'cls']})
        self.assertEqual( hsh[ 'result'], 'done')

        #
        # create the image
        #
        hsh = { 'Image': 
                { 'name': "MandelBrot",
                  'xMin': xmin, 'xMax': xmax, 'width': width, 
                  'yMin': ymin, 'yMax': ymax, 'height': height}}

        hsh = PySpectra.toPysp( hsh)
        self.assertEqual( hsh[ 'result'], 'done')
        #
        # fill the image, pixel by pixel
        #
        r1 = np.linspace(xmin, xmax, width)
        r2 = np.linspace(ymin, ymax, height)
        for i in range(width):
            for j in range(height):
                res = mandelbrot(r1[i] + 1j*r2[j],maxiter)
                hsh = { 'command': [ 'setPixelWorld MandelBrot %g %g %g' % ( r1[i], r2[j], res)]}
                hsh = PySpectra.toPysp( hsh)
                self.assertEqual( hsh[ 'result'], 'done')
            hsh =  PySpectra.toPysp( { 'command': ['cls', 'display']})
            self.assertEqual( hsh[ 'result'], 'done')
        PySpectra.procEventsLoop( 1)

    def testToPysp5( self) : 
        hsh = PySpectra.toPysp( { 'command': ['cls', 'delete']})
        self.assertEqual( hsh[ 'result'], 'done')
        hsh = PySpectra.toPysp( { 'command': ['setWsViewport dina5s']})
        self.assertEqual( hsh[ 'result'], 'done')

        (xmin, xmax) = (-2.,-0.5)
        (ymin, ymax) = (0, 1.5)
        (width, height) = (100, 100)
        maxiter = 25

        #
        # do the clean-up before we start
        #
        hsh =  PySpectra.toPysp( { 'command': ['delete', 'setWsViewport DINA5S', 'cls']})
        self.assertEqual( hsh[ 'result'], 'done')

        #
        # create the image
        #
        hsh = { 'Image': 
                { 'name': "MandelBrot",
                  'xMin': xmin, 'xMax': xmax, 'width': width, 
                  'yMin': ymin, 'yMax': ymax, 'height': height}}

        hsh = PySpectra.toPysp( hsh)
        self.assertEqual( hsh[ 'result'], 'done')
        #
        # fill the image, pixel by pixel
        #
        r1 = np.linspace(xmin, xmax, width)
        r2 = np.linspace(ymin, ymax, height)
        for i in range(width):
            for j in range(height):
                res = mandelbrot(r1[i] + 1j*r2[j],maxiter)
                hsh = { 'putData': 
                         { 'name': "MandelBrot",
                           'noDisplay': True, 
                           'setPixelWorld': ( r1[i], r2[j], res)}}
                hsh = PySpectra.toPysp( hsh)
                self.assertEqual( hsh[ 'result'], 'done')
            hsh =  PySpectra.toPysp( { 'command': ['cls', 'display']})
            self.assertEqual( hsh[ 'result'], 'done')
        PySpectra.procEventsLoop( 1)

    def testToPysp6( self) : 
        '''
        use putData to transfer a complete image at once
        '''
        hsh = PySpectra.toPysp( { 'command': ['cls', 'delete']})
        self.assertEqual( hsh[ 'result'], 'done')
        hsh = PySpectra.toPysp( { 'command': ['setWsViewport dina5s']})
        self.assertEqual( hsh[ 'result'], 'done')

        (xmin, xmax) = (-2.,-0.5)
        (ymin, ymax) = (0, 1.5)
        (width, height) = (100, 100)
        maxiter = 25

        #
        # do the clean-up before we start
        #
        hsh =  PySpectra.toPysp( { 'command': ['delete', 'setWsViewport DINA5S', 'cls']})
        self.assertEqual( hsh[ 'result'], 'done')

        #
        # fill the image, pixel by pixel
        #
        r1 = np.linspace(xmin, xmax, width)
        r2 = np.linspace(ymin, ymax, height)
        data = np.ndarray( (width, height), np.float64)
        for i in range(width):
            for j in range(height):
                res = mandelbrot(r1[i] + 1j*r2[j],maxiter)
                data[i][j] = int( res)

        hsh = PySpectra.toPysp( { 'putData': 
                        { 'images': [{'name': "MandelBrot", 'data': data,
                                      'xMin': xmin, 'xMax': xmax, 
                                      'yMin': ymin, 'yMax': ymax}]}})
        self.assertEqual( hsh[ 'result'], 'done')

        hsh =  PySpectra.toPysp( { 'command': ['cls', 'display']})
        self.assertEqual( hsh[ 'result'], 'done')
        PySpectra.procEventsLoop( 1)

    def testToPysp7( self) : 
        '''
        use Image to transfer a complete image at once
        '''
        hsh = PySpectra.toPysp( { 'command': ['cls', 'delete']})
        self.assertEqual( hsh[ 'result'], 'done')
        hsh = PySpectra.toPysp( { 'command': ['setWsViewport dina5s']})
        self.assertEqual( hsh[ 'result'], 'done')

        (xmin, xmax) = (-2.,-0.5)
        (ymin, ymax) = (0, 1.5)
        (width, height) = (100, 100)
        maxiter = 25

        #
        # do the clean-up before we start
        #
        hsh =  PySpectra.toPysp( { 'command': ['delete', 'setWsViewport DINA5S', 'cls']})
        self.assertEqual( hsh[ 'result'], 'done')

        #
        # fill the image, pixel by pixel
        #
        r1 = np.linspace(xmin, xmax, width)
        r2 = np.linspace(ymin, ymax, height)
        data = np.ndarray( (width, height), np.float64)
        for i in range(width):
            for j in range(height):
                res = mandelbrot(r1[i] + 1j*r2[j],maxiter)
                data[i][j] = int( res)

        hsh = PySpectra.toPysp( { 'Image': 
                                  { 'name': "MandelBrot", 'data': data, 
                                    'xMin': xmin, 'xMax': xmax, 
                                    'yMin': ymin, 'yMax': ymax, 
                                  }})
        self.assertEqual( hsh[ 'result'], 'done')

        hsh =  PySpectra.toPysp( { 'command': ['cls', 'display']})
        self.assertEqual( hsh[ 'result'], 'done')
        o = PySpectra.getGqe( "Mandelbrot")
        self.assertEqual( o.height, 100)
        self.assertEqual( o.width, 100)
        self.assertEqual( o.xMin, xmin)
        self.assertEqual( o.xMax, xmax)
        self.assertEqual( o.yMin, ymin)
        self.assertEqual( o.yMax, ymax)
        print dir(o)
        PySpectra.procEventsLoop( 1)

if __name__ == "__main__":
    unittest.main()
