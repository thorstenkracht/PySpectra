#!/bin/env python

import PySpectra
import numpy as np
import unittest

class testGQE( unittest.TestCase):
        
    def test_createSlot( self):
        print "test_createSlot"
        obj = PySpectra.dMgt.GQE.Slot( name = "test1")
        self.assertEqual( obj.name, "test1")
        del obj
        
    def test_createScan( self):
        print "test_createScan"
        slot = PySpectra.dMgt.GQE.Slot( name = "scan1")
        scan = PySpectra.dMgt.GQE.Scan( slot, xMin = 0., xMax = 1.0, np = 101, dType = np.float64)
        self.assertEqual( scan.xMin, 0.)
        self.assertEqual( scan.xMax, 1.)
        self.assertEqual( scan.np, 101)
        self.assertEqual( scan.dType, np.float64)

if __name__ == "__main__":
    unittest.main()
