#!/bin/env python
'''
python ./test/testUtils.py testUtils.test_ssa
'''
import sys
import PySpectra
import PySpectra.GQE as GQE
import numpy as np
import unittest
import time, sys, os
import math 

class testUtils( unittest.TestCase):


    @classmethod
    def setUpClass( testUtils):
        pass
    @classmethod
    def tearDownClass( testUtils): 
        PySpectra.close()

    def test_ssa( self):
        '''
        overlay 2 scans
        '''
        PySpectra.cls()
        GQE.delete()
        g = GQE.Scan( name = "gauss", xMin = -5., xMax = 5., nPts = 101, lineColor = 'red')
        mu = 0.
        sigma = 1.
        g.y = 1/(sigma*np.sqrt(2.*np.pi))*np.exp( -(g.y-mu)**2/(2.*sigma**2))

        hsh = PySpectra.utils.ssa( g.x, g.y)
        self.assertEqual( hsh[ 'status'], 1)
        self.assertEqual( hsh[ 'midpoint'], 0.)
        self.assertAlmostEqual( hsh[ 'l_back'], 2.521e-5)
        self.assertAlmostEqual( hsh[ 'r_back'], 2.521e-5)
        self.assertAlmostEqual( hsh[ 'integral'], 0.9997473505)
        self.assertEqual( hsh[ 'reason'], 0)
        self.assertEqual( hsh[ 'peak_x'], 0)
        self.assertAlmostEqual( hsh[ 'peak_y'], 0.3989170740)
        self.assertAlmostEqual( hsh[ 'cms'], 1.2989313e-16)
        self.assertAlmostEqual( hsh[ 'fwhm'], 2.35522977)
        self.assertAlmostEqual( hsh[ 'back_int'], 0.0002520637)

        print repr( hsh)
        
if __name__ == "__main__":
    unittest.main()
