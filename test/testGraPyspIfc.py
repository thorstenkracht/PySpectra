#!/bin/env python
'''
cd /home/kracht/Misc/pySpectra
python -m unittest discover -v

python ./test/testGraPyspIfc.py testGraPyspIfc.testCreateScan
python ./test/testGraPyspIfc.py testGraPyspIfc.testFillScan
python ./test/testGraPyspIfc.py testGraPyspIfc.testSinusScan
python ./test/testGraPyspIfc.py testGraPyspIfc.testReUse
python ./test/testGraPyspIfc.py testGraPyspIfc.testCreateHardCopy
python ./test/testGraPyspIfc.py testGraPyspIfc.testDelete
python ./test/testGraPyspIfc.py testGraPyspIfc.testMisc
python ./test/testGraPyspIfc.py testGraPyspIfc.testWrite
'''
import time
import PySpectra
import PySpectra.graPyspIfc as graPyspIfc
import PySpectra.utils as utils
import PySpectra.definitions as definitions
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

        if utils.getHostname() != definitions.hostTK: 
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

        if utils.getHostname() != definitions.hostTK: 
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

        if utils.getHostname() != definitions.hostTK: 
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

    def testReUse( self):

        graPyspIfc.setSpectra( False)

        graPyspIfc.cls()
        graPyspIfc.delete()

        (xMin, xMax, nPts) = ( 0., 10., 20)
        x = numpy.linspace( xMin, xMax, nPts) 
        y = numpy.random.random_sample( nPts)

        rand = graPyspIfc.Scan( name = "sinus", lineColor = 'blue', 
                                x = x, y = y, nPts = nPts)

        graPyspIfc.setComment( "using normal update") 

        for i in range( 5): 
            rand.y = numpy.random.random_sample( len( x))
            graPyspIfc.cls()
            graPyspIfc.display()
            PySpectra.processEventsLoop( 1)

        graPyspIfc.setComment( "using smart update") 
        graPyspIfc.cls()
        graPyspIfc.display()

        for i in range( 100): 
            rand.smartUpdateDataAndDisplay( y = numpy.random.random_sample( nPts))

        graPyspIfc.setComment( "")

        graPyspIfc.close()

        if utils.getHostname() != definitions.hostTK: 
            return 

        graPyspIfc.setSpectra( True)

        graPyspIfc.cls()
        graPyspIfc.delete()

        (xMin, xMax, nPts) = ( 0., 10., 20)
        x = numpy.linspace( xMin, xMax, nPts) 
        y = numpy.random.random_sample( nPts)

        rand = graPyspIfc.Scan( name = "sinus", lineColor = 'blue', 
                                x = x, y = y, nPts = nPts)

        for i in range( 10): 
            rand.smartUpdateDataAndDisplay( y = numpy.random.random_sample( nPts))
            time.sleep( 0.5)

        graPyspIfc.close()

        return 

    def testCreateHardCopy( self):

        print( "testGraPyspIfc.testCreateHardCopy") 
        graPyspIfc.setSpectra( False)

        graPyspIfc.cls()
        graPyspIfc.delete()

        (xMin, xMax, nPts) = ( 0., 10., 20)
        x = numpy.linspace( xMin, xMax, nPts) 
        y = numpy.random.random_sample( nPts)

        rand = graPyspIfc.Scan( name = "sinus", lineColor = 'blue', 
                                x = x, y = y, nPts = nPts)

        graPyspIfc.createHardCopy()
        graPyspIfc.createHardCopy( printer = 'hasps01', flagPrint = True)

        graPyspIfc.close()

        if utils.getHostname() != definitions.hostTK: 
            return 

        graPyspIfc.setSpectra( True)

        (xMin, xMax, nPts) = ( 0., 10., 20)
        x = numpy.linspace( xMin, xMax, nPts) 
        y = numpy.random.random_sample( nPts)

        rand = graPyspIfc.Scan( name = "sinus", lineColor = 'blue', 
                                x = x, y = y, nPts = nPts)

        graPyspIfc.createHardCopy()
        graPyspIfc.createHardCopy( printer = 'hasps01', flagPrint = True)

        graPyspIfc.close()

        print( "testGraPyspIfc.testCreateHardCopy DONE") 

        return 


    def testDelete( self):

        print( "testGraPyspIfc.testDelete") 
        graPyspIfc.setSpectra( False)

        graPyspIfc.cls()
        graPyspIfc.delete()

        (xMin, xMax, nPts) = ( 0., 10., 20)
        x = numpy.linspace( xMin, xMax, nPts) 
        y = numpy.random.random_sample( nPts)

        rand = graPyspIfc.Scan( name = "sinus", lineColor = 'blue', 
                                x = x, y = y, nPts = nPts)

        scan = graPyspIfc.getGqe( "sinus")
        self.assertEqual( scan.name, "sinus")

        graPyspIfc.deleteScan( rand)

        scan = graPyspIfc.getGqe( "sinus")
        self.assertEqual( scan, None)
        
        graPyspIfc.close()

        if utils.getHostname() != definitions.hostTK: 
            return 

        graPyspIfc.setSpectra( True)

        (xMin, xMax, nPts) = ( 0., 10., 20)
        x = numpy.linspace( xMin, xMax, nPts) 
        y = numpy.random.random_sample( nPts)

        rand = graPyspIfc.Scan( name = "sinus", lineColor = 'blue', 
                                x = x, y = y, nPts = nPts)

        scan = graPyspIfc.getGqe( "sinus")
        self.assertEqual( scan, 1)

        graPyspIfc.deleteScan( rand)

        scan = graPyspIfc.getGqe( "sinus")
        self.assertEqual( scan, 0)

        graPyspIfc.close()

        print( "testGraPyspIfc.testDelete DONE") 

        return 

    def testMisc( self):

        print( "testGraPyspIfc.testMisc")

        graPyspIfc.cls()
        graPyspIfc.delete()
 
        graPyspIfc.setSpectra( False)

        graPyspIfc.setComment( "this is a comment")
        graPyspIfc.setTitle( "this is a title")

        ret = graPyspIfc.getComment()
        self.assertEqual( ret, "this is a comment")
        ret = graPyspIfc.getTitle()
        self.assertEqual( ret, "this is a title")
        
        graPyspIfc.close()

        if utils.getHostname() != definitions.hostTK: 
            return 

        graPyspIfc.setSpectra( True)

        ret = graPyspIfc.setComment( "this is a comment")
        self.assertEqual( ret, None)
        ret = graPyspIfc.setTitle( "this is a title")
        self.assertEqual( ret, None)
        ret = graPyspIfc.getComment()
        self.assertEqual( ret, "NoComment")
        ret = graPyspIfc.getTitle()
        self.assertEqual( ret, None)

        graPyspIfc.close()

        print( "testGraPyspIfc.testMisc DONE") 

        return 

    def testWrite( self):

        print( "testGraPyspIfc.testWrite")

        graPyspIfc.cls()
        graPyspIfc.delete()
 
        graPyspIfc.setSpectra( False)


        (xMin, xMax, nPts) = ( 0., 10., 20)
        x = numpy.linspace( xMin, xMax, nPts) 
        y = numpy.random.random_sample( nPts)

        rand = graPyspIfc.Scan( name = "rand", lineColor = 'blue', 
                                x = x, y = y, nPts = nPts)

        graPyspIfc.write( names = "rand")
        graPyspIfc.close()

        if utils.getHostname() != definitions.hostTK: 
            return 

        graPyspIfc.setSpectra( True)

        (xMin, xMax, nPts) = ( 0., 10., 20)
        x = numpy.linspace( xMin, xMax, nPts) 
        y = numpy.random.random_sample( nPts)

        rand = graPyspIfc.Scan( name = "rand", lineColor = 'blue', 
                                x = x, y = y, nPts = nPts)

        with self.assertRaises( ValueError) as context:
            graPyspIfc.write()
        #print("testSetXY: %s" %  repr( context.exception))
        self.assertTrue( "graPyspIfc.write: expecting a string containing the name"
                         in context.exception)

        with self.assertRaises( ValueError) as context:
            graPyspIfc.write( ["rand"])
        #print("testSetXY: %s" %  repr( context.exception))
        self.assertTrue( "graPyspIfc.write: input must no be a list"
                         in context.exception)

        scan = graPyspIfc.getGqe( "rand")
        self.assertEqual( scan, 1)
        graPyspIfc.write( "rand")

        graPyspIfc.close()

        print( "testGraPyspIfc.testMisc DONE") 

        return 


if __name__ == "__main__":
    unittest.main()
