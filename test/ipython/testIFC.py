#!/bin/env python
'''
cd /home/kracht/Misc/pySpectra
python -m unittest discover -v

python ./test/ipython/testIFC.py testIFC.test_create
python ./test/ipython/testIFC.py testIFC.test_pdf
'''
import sys
##pySpectraPath = "/home/kracht/Misc/pySpectra"
#pySpectraPath = "."
#sys.path.append( pySpectraPath)

import PySpectra
#import PySpectra.dMgt.GQE as gqe
import numpy as np
import unittest
import time, sys, os
import math 

class testIFC( unittest.TestCase):

    @classmethod
    def setUpClass( testIFC):
        pass

    @classmethod
    def tearDownClass( testIFC): 
        PySpectra.close()

    def test_create1( self):
        PySpectra.cls()
        PySpectra.delete()
        PySpectra.ipython.ifc.command( "create s1 0 10 100")
        lst = PySpectra.getScanList()
        self.assertEqual( len( lst), 1)
        self.assertEqual( lst[0].name, "s1")
        self.assertEqual( lst[0].nPts, 100)
        self.assertEqual( lst[0].xMin, 0.)
        self.assertEqual( lst[0].xMax, 10.)
        PySpectra.delete()

    def test_create( self):

        print "testIFC.test_create"

        PySpectra.cls()
        PySpectra.delete()
        PySpectra.ipython.ifc.command( "create s1")
        lst = PySpectra.getScanList()
        self.assertEqual( len( lst), 1)
        self.assertEqual( lst[0].name, "s1")
        PySpectra.ipython.ifc.command( "display s1")

        PySpectra.ipython.ifc.command( "derivative s1")
        lst = PySpectra.getScanList()
        self.assertEqual( lst[1].name, "s1_derivative")
        self.assertEqual( len( lst), 2)

        PySpectra.ipython.ifc.command( "antiderivative s1")
        lst = PySpectra.getScanList()
        self.assertEqual( lst[2].name, "s1_antiderivative")
        self.assertEqual( len( lst), 3)

        PySpectra.ipython.ifc.command( "delete s1")
        PySpectra.ipython.ifc.command( "delete s1_derivative")
        PySpectra.ipython.ifc.command( "delete s1_antiderivative")
        lst = PySpectra.getScanList()
        self.assertEqual( len( lst), 0)

    def test_cls( self):

        print "testIFC.test_cls"

        PySpectra.ipython.ifc.command( "cls")

    def test_show( self):

        print "testIFC.test_show"

        PySpectra.cls()
        PySpectra.delete()
        PySpectra.ipython.ifc.command( "create s1")
        PySpectra.ipython.ifc.command( "show s1")

    def test_title( self): 
        PySpectra.cls()
        PySpectra.delete()
        PySpectra.ipython.ifc.command( "create s1")
        PySpectra.ipython.ifc.command( "setTitle hallo")

        ret = PySpectra.getTitle()
        self.assertEqual( ret, "hallo")

    def test_comment( self): 
        PySpectra.cls()
        PySpectra.delete()
        PySpectra.ipython.ifc.command( "setComment AComment")

        ret = PySpectra.getComment()
        self.assertEqual( ret, "AComment")

    def test_y2my( self): 
        PySpectra.cls()
        PySpectra.delete()
        PySpectra.ipython.ifc.command( "create s1")
        PySpectra.ipython.ifc.command( "y2my s1")

        lst = PySpectra.getScanList()
        self.assertEqual( lst[1].name, "s1_y2my")
        self.assertEqual( len( lst), 2)

    def test_wsViewPort( self): 
        PySpectra.cls()
        PySpectra.delete()
        PySpectra.ipython.ifc.command( "setWsViewport DINA4")

    def test_overlay( self): 
        PySpectra.cls()
        PySpectra.delete()
        PySpectra.ipython.ifc.command( "create s1")
        PySpectra.ipython.ifc.command( "create s2")
        PySpectra.ipython.ifc.command( "overlay s1 s2")
        PySpectra.delete()

    def test_pdf( self): 
        PySpectra.cls()
        PySpectra.delete()
        PySpectra.ipython.ifc.command( "create s1")
        PySpectra.ipython.ifc.command( "createPDF testPDF")
        self.assertEqual( os.path.exists( 'testPDF.pdf'), True)
        os.remove( 'testPDF.pdf') 

        PySpectra.delete()


if __name__ == "__main__":
    unittest.main()
