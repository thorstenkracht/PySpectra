#!/bin/env python
'''
cd /home/kracht/Misc/pySpectra
python -m unittest discover -v

python ./test/testSpock.py testSpock.testMv
python ./test/testSpock.py testSpock.testAscan
python ./test/testSpock.py testSpock.testMvsa

'''
import time, os
import PySpectra
import PySpectra.utils as utils
import PySpectra.definitions as definitions
import unittest
import HasyUtils

class testSpock( unittest.TestCase):

    @classmethod
    def setUpClass( testSpock):
        pass

    @classmethod
    def tearDownClass( testSpock): 
        PySpectra.close()

    def testMv( self) : 
        print "testSpock.testMv"

        if HasyUtils.getHostname() != definitions.hostTK: 
            return 

        print "testSpock.testMv, eh_mot66 to 50"
        
        hsh =  PySpectra.toPyspLocal( { 'spock': 'mv eh_mot66 50'})
        self.assertEqual( hsh[ 'result'], 'done')

        hsh =  PySpectra.toPyspLocal( { 'getDoorState': True})
        while hsh[ 'result'] == 'RUNNING': 
            time.sleep( 0.5)
            hsh =  PySpectra.toPyspLocal( { 'getDoorState': True})

        hsh =  PySpectra.toPyspLocal( { 'getDoorState': True})
        self.assertEqual( hsh[ 'result'], 'ON')

        print "testSpock.testMv, eh_mot66 to 51"
        hsh =  PySpectra.toPyspLocal( { 'spock': 'mv eh_mot66 51'})
        self.assertEqual( hsh[ 'result'], 'done')

        hsh =  PySpectra.toPyspLocal( { 'getDoorState': True})
        while hsh[ 'result'] == 'RUNNING': 
            time.sleep( 0.5)
            hsh =  PySpectra.toPyspLocal( { 'getDoorState': True})

        hsh =  PySpectra.toPyspLocal( { 'getDoorState': True})
        self.assertEqual( hsh[ 'result'], 'ON')

        return 

    def testAscan( self) : 
        print "testSpock.testAscan"

        if HasyUtils.getHostname() != definitions.hostTK: 
            return 

        ( status, wasLaunched) = utils.assertProcessRunning( "/usr/bin/pyspMonitor.py")
        print( "testSpock.testAscan: ascan eh_mot66 50 51 40 0.1")

        hsh =  PySpectra.toPyspLocal( { 'spock': 'ascan eh_mot66 50 51 40 0.1'})
        self.assertEqual( hsh[ 'result'], 'done')

        hsh =  PySpectra.toPyspLocal( { 'getDoorState': True})
        while hsh[ 'result'] != 'ON': 
            time.sleep( 0.5)
            hsh =  PySpectra.toPyspLocal( { 'getDoorState': True})

        hsh =  PySpectra.toPyspLocal( { 'getDoorState': True})
        self.assertEqual( hsh[ 'result'], 'ON')

        if wasLaunched:
            print( "testSpock.testAscan kill pyspMonitor.py") 
            os.system( "kill_proc -f pyspMonitor.py")

        return 

    def testMvsa( self) : 
        print "testSpock.testMvsa"

        if HasyUtils.getHostname() != definitions.hostTK: 
            return 

        ( status, wasLaunched) = utils.assertProcessRunning( "/usr/bin/pyspMonitor.py")
        print( "testSpock.testAscan: ascan eh_mot66 50 51 40 0.1")

        hsh =  PySpectra.toPyspLocal( { 'spock': 'ascan eh_mot66 50 51 40 0.1'})
        self.assertEqual( hsh[ 'result'], 'done')

        hsh =  PySpectra.toPyspLocal( { 'getDoorState': True})
        while hsh[ 'result'] != 'ON': 
            time.sleep( 0.5)
            hsh =  PySpectra.toPyspLocal( { 'getDoorState': True})

        hsh =  PySpectra.toPyspLocal( { 'getDoorState': True})
        self.assertEqual( hsh[ 'result'], 'ON')

        hsh =  PySpectra.toPyspLocal( { 'spock': 'mvsa peak 0'})
        self.assertEqual( hsh[ 'result'], 'done')

        if wasLaunched:
            print( "testSpock.testAscan kill pyspMonitor.py") 
            os.system( "kill_proc -f pyspMonitor.py")

        return 


if __name__ == "__main__":
    unittest.main()
