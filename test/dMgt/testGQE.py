#!/bin/env python
'''
cd /home/kracht/Misc/pySpectra
python -m unittest discover -v

python ./test/dMgt/testGQE.py testGQE.testNextPrev
python ./test/dMgt/testGQE.py testGQE.testFillData
python ./test/dMgt/testGQE.py testGQE.testCreateDelete
python ./test/dMgt/testGQE.py testGQE.testWrite
python ./test/dMgt/testGQE.py testGQE.testReuse
python ./test/dMgt/testGQE.py testGQE.testYGreaterThanZero
python ./test/dMgt/testGQE.py testGQE.testSetLimits
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

class testGQE( unittest.TestCase):

    def test_titleAndComment( self):

        print "testGQE.test_titleAndComment"
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
        lst = PySpectra.getScanList()
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
        lst = PySpectra.getScanList()
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
        lst = PySpectra.getScanList()
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
        lst = PySpectra.getScanList()
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
            self.assertEqual( str( e), "GQE.Scan.__init__: if 'x' or 'y' then both have to be supplied")
        try:
            scan = PySpectra.Scan( name = 't1', y = [0, 1, 2, 3, 4])
        except ValueError, e:
            self.assertEqual( str( e), "GQE.Scan.__init__: if 'x' or 'y' then both have to be supplied")

        lst = PySpectra.getScanList()
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
        scanLst = PySpectra.getScanList()
        self.assertEqual( len( scanLst), 0)
        PySpectra.Scan( name = 't1')
        PySpectra.Scan( name = 't2')
        PySpectra.Scan( name = 't3')
        PySpectra.Scan( name = 't4')
        PySpectra.display()
        scanLst = PySpectra.getScanList()
        self.assertEqual( len( scanLst), 4)
        PySpectra.delete( [ 't1', 't2'])
        scanLst = PySpectra.getScanList()
        self.assertEqual( len( scanLst), 2)
        self.assertEqual( scanLst[0].name, 't3')
        self.assertEqual( scanLst[1].name, 't4')
        PySpectra.delete()
        scanLst = PySpectra.getScanList()
        self.assertEqual( len( scanLst), 0)

        print "testGQE.testCreateDelete, DONE"
        
    def testNextPrev( self):
        print "testGQE.testNextPrev"
        PySpectra.delete()
        PySpectra.Scan( name = 't1')
        PySpectra.Scan( name = 't2')
        PySpectra.Scan( name = 't3')
        PySpectra.Scan( name = 't4')
        self.assertEqual( gqe._nextScan().name, 't1')
        self.assertEqual( gqe._nextScan().name, 't2')
        self.assertEqual( gqe._nextScan().name, 't3')
        self.assertEqual( gqe._nextScan().name, 't4')
        self.assertEqual( gqe._nextScan().name, 't1')
        PySpectra.delete()
        PySpectra.Scan( name = 't1')
        PySpectra.Scan( name = 't2')
        PySpectra.Scan( name = 't3')
        PySpectra.Scan( name = 't4')
        self.assertEqual( gqe._prevScan().name, 't1')
        self.assertEqual( gqe._prevScan().name, 't4')
        self.assertEqual( gqe._prevScan().name, 't3')
        self.assertEqual( gqe._prevScan().name, 't2')
        self.assertEqual( gqe._prevScan().name, 't1')

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
        self.assertLess( diffTime, 5.)

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

        scanLst = PySpectra.getScanList()
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

if __name__ == "__main__":
    unittest.main()
