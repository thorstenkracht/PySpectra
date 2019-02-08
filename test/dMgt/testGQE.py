#!/bin/env python
'''
cd /home/kracht/Misc/pySpectra
python -m unittest discover -v

python ./test/dMgt/testGQE.py testGQE.testNextPrev
python ./test/dMgt/testGQE.py testGQE.testFillData
'''
import sys
pySpectraPath = "/home/kracht/Misc/pySpectra"
sys.path.append( pySpectraPath)

import PySpectra
import numpy as np
import unittest
import time, sys
import math 

class testGQE( unittest.TestCase):

    def test_read( self):

        PySpectra.cls()
        PySpectra.delete()
        PySpectra.read( "%s/test/data/ti_au_tio2_sio2_kat55a_0001.fio" % pySpectraPath)
        lst = PySpectra.getScanList()
        self.assertEqual( len( lst), 24)
        self.assertEqual( lst[0].name, "TI_AU_TIO2_SIO2_KAT55A_0001")
        self.assertEqual( lst[1].name, "TI_AU_TIO2_SIO2_KAT55A_0001_RING")

        #PySpectra.display()
        #PySpectra.show()
        #PySpectra.procEventsLoop()

        PySpectra.delete()
        PySpectra.read( "%s/test/data/SPLITTER_PXE_BL_22_2.dat" % pySpectraPath)
        lst = PySpectra.getScanList()
        self.assertEqual( len( lst), 4)
        self.assertEqual( lst[0].name, "scan1")
        self.assertEqual( lst[1].name, "scan2")
        self.assertEqual( lst[2].name, "scan3")
        self.assertEqual( lst[3].name, "scan4")
        
        #PySpectra.display()
        #PySpectra.show()
        #PySpectra.procEventsLoop()

    def test_doty( self):

        PySpectra.cls()
        PySpectra.delete()

        scan1 = PySpectra.Scan( name = "notdotyscan", xMin = 10., xMax = 30.0, 
                               nPts = 101, dType = np.float64,
                               color = 'red', style = 'solidLine')
        self.assertEqual( scan1.doty, False)

        scan2 = PySpectra.Scan( name = "dotyscan", xMin = 10., xMax = 30.0, 
                               nPts = 101, dType = np.float64,
                               doty = True,color = 'red', style = 'solidLine')

        self.assertEqual( scan2.doty, True)

        PySpectra.display()
        PySpectra.show()
        PySpectra.procEventsLoop()
        
    def test_createScanByLimit( self):

        PySpectra.cls()
        PySpectra.delete()

        scan = PySpectra.Scan( name = "test1", xMin = 0., xMax = 1.0, 
                               nPts = 101, dType = np.float64,
                               at = (2,2,3), color = 'red', style = 'solidLine')
        self.assertEqual( scan.xMin, 0.)
        self.assertEqual( scan.xMax, 1.)
        self.assertEqual( scan.nPts, 101)
        self.assertEqual( scan.dType, np.float64)
        self.assertEqual( len( scan.x), 101)
        self.assertEqual( scan.x.dtype, np.float64)
        self.assertEqual( len( scan.y), 101)
        self.assertEqual( scan.y.dtype, np.float64)

        self.assertEqual( scan.color, 'red')

    def test_createScanByData( self):

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
        self.assertEqual( scan.yMax, 14.)

        self.assertEqual( scan.nPts, 5)
        
        self.assertEqual( scan.x[0], 0)
        self.assertEqual( scan.x[4], 4)
        self.assertEqual( scan.y[0], 10)
        self.assertEqual( scan.y[4], 12)

        self.assertEqual( scan.currentIndex, 4)
        
    def testCreateDelete( self): 
        PySpectra.delete()
        scanLst = PySpectra.getScanList()
        self.assertEqual( len( scanLst), 0)
        PySpectra.Scan( name = 't1')
        PySpectra.Scan( name = 't2')
        PySpectra.Scan( name = 't3')
        PySpectra.Scan( name = 't4')
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
        
    def testNextPrev( self):
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

    def testFillData( self):
        PySpectra.cls()
        PySpectra.delete()
        scan = PySpectra.Scan( name = 't1', xLabel = "up to 1000 pts", 
                               nPts = 1001, yMin = -10., yMax = 10.)
        self.assertEqual( scan.currentIndex, 1000)
        scan.y = np.sin( scan.x)
        
        startTime = time.time()
        for i in range( len( scan.y)):
            scan.setY( i, math.tan( float( i)/10))
            PySpectra.display()

        diffTime = time.time() - startTime
        self.assertLess( diffTime, 5.)

if __name__ == "__main__":
    unittest.main()
