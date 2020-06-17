#!/bin/env python
'''
cd /home/kracht/Misc/pySpectra
python -m unittest discover -v

python ./test/testGraPyspIfc.py testGraPyspIfc.testCreateScan
python ./test/testGraPyspIfc.py testGraPyspIfc.testFillScan
python ./test/testGraPyspIfc.py testGraPyspIfc.testSinusScan
'''
import time
import PySpectra
import PySpectra.graPyspIfc as graPyspIfc
import numpy 
import unittest

#
# wrong, think of github: pySpectraPath = "/home/kracht/Misc/pySpectra"
pySpectraPath = "."

class testGraPyspIfc( unittest.TestCase):

    @classmethod
    def setUpClass( testGraPyspIfc):
        pass

    @classmethod
    def tearDownClass( testGraPyspIfc): 
        graPyspIfc.close()

    def testCreateScan( self):

        graPyspIfc.setSpectra( False)

        graPyspIfc.cls()
        graPyspIfc.delete()

        scan = graPyspIfc.Scan( name = "s1", lineColor = "red", nPts = 201) 
        self.assertEqual( scan.xMin, 0.)
        self.assertEqual( scan.xMax, 10.)
        self.assertEqual( scan.lineColor, "red")
        self.assertEqual( scan.nPts, 201)
        scan.display()

        PySpectra.processEventsLoop( 1)

        if utils.getHostname() != 'haso107tk': 
            return 

        graPyspIfc.setSpectra( True)

        graPyspIfc.cls()
        graPyspIfc.delete()

        scan = graPyspIfc.Scan( name = "s1", lineColor = "blue", nPts = 201) 

        self.assertEqual( scan.xMin, 0.)
        self.assertEqual( scan.xMax, 10.)
        self.assertEqual( scan.lineColor, "blue")
        self.assertEqual( scan.nPts, 201)
        scan.display()
        time.sleep(1) 
        graPyspIfc.close()

    def testFillScan( self):

        graPyspIfc.setSpectra( False)

        graPyspIfc.cls()
        graPyspIfc.delete()

        scan = graPyspIfc.Scan( name = "s1", color = "blue", nPts = 101) 

        scan.y = numpy.random.normal(size=(101))
        scan.x  = numpy.linspace( 0., 10., 101)

        scan.display()
        PySpectra.processEventsLoop( 1)

        if utils.getHostname() != 'haso107tk': 
            return 

        graPyspIfc.setSpectra( True)

        graPyspIfc.cls()
        graPyspIfc.delete()

        scan = graPyspIfc.Scan( name = "s1", color = "blue", nPts = 101) 

        scan.y = numpy.random.normal(size=(101))
        scan.x  = numpy.linspace( 0., 10., 101)

        scan.display()
        time.sleep(1) 

        graPyspIfc.close()

    def testSinusScan( self):



        graPyspIfc.setSpectra( False)

        graPyspIfc.cls()
        graPyspIfc.delete()
        sinus = graPyspIfc.Scan( name = "sinus", lineColor = 'blue', xMin = -5, xMax = 5., 
                                 yMin = -1.5, yMax = 1.5, nPts = 21, yLabel = 'sin')

        sinus.y = numpy.sin( sinus.x)

        sinus.display()
        self.assertEqual( sinus.getCurrent(), 20)
        PySpectra.processEventsLoop( 1)

        if utils.getHostname() != 'haso107tk': 
            return 


        graPyspIfc.setSpectra( True)

        graPyspIfc.cls()
        graPyspIfc.delete()

        sinus = graPyspIfc.Scan( name = "sinus", lineColor = 'blue', xMin = -5, xMax = 5., 
                                 yMin = -1.5, yMax = 1.5, nPts = 21, yLabel = 'sin')

        sinus.y = numpy.sin( sinus.x)

        sinus.display()

        time.sleep(2) 

        self.assertEqual( sinus.getCurrent(), 20)

        graPyspIfc.close()


if __name__ == "__main__":
    unittest.main()
