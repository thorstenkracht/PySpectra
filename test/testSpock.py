#!/bin/env python
'''
cd /home/kracht/Misc/pySpectra
python -m unittest discover -v

python ./test/testSpock.py testSpock.testMv
python ./test/testSpock.py testSpock.testAscan

'''
import time, os
import PySpectra
import PySpectra.misc.zmqIfc as zmqIfc
import PySpectra.misc.utils as utils
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

        if HasyUtils.getHostname() != 'haso107tk': 
            return 

        print "testSpock.testMv, eh_mot66 to 50"
        
        hsh =  zmqIfc.execHsh( { 'spock': 'mv eh_mot66 50'})
        self.assertEqual( hsh[ 'result'], 'done')

        hsh =  zmqIfc.execHsh( { 'getDoorState': True})
        while hsh[ 'result'] == 'RUNNING': 
            time.sleep( 0.5)
            hsh =  zmqIfc.execHsh( { 'getDoorState': True})

        hsh =  zmqIfc.execHsh( { 'getDoorState': True})
        self.assertEqual( hsh[ 'result'], 'ON')

        print "testSpock.testMv, eh_mot66 to 51"
        hsh =  zmqIfc.execHsh( { 'spock': 'mv eh_mot66 51'})
        self.assertEqual( hsh[ 'result'], 'done')

        hsh =  zmqIfc.execHsh( { 'getDoorState': True})
        while hsh[ 'result'] == 'RUNNING': 
            time.sleep( 0.5)
            hsh =  zmqIfc.execHsh( { 'getDoorState': True})

        hsh =  zmqIfc.execHsh( { 'getDoorState': True})
        self.assertEqual( hsh[ 'result'], 'ON')

        return 

    def testAscan( self) : 
        print "testSpock.testAscan"

        if HasyUtils.getHostname() != 'haso107tk': 
            return 

        ( status, wasLaunched) = utils.assertProcessRunning( "/usr/bin/pyspMonitor.py")
        print( "testSpock.testAscan: ascan eh_mot66 50 51 40 0.1")

        hsh =  zmqIfc.execHsh( { 'spock': 'ascan eh_mot66 50 51 40 0.1'})
        self.assertEqual( hsh[ 'result'], 'done')

        hsh =  zmqIfc.execHsh( { 'getDoorState': True})
        while hsh[ 'result'] == 'RUNNING': 
            time.sleep( 0.5)
            hsh =  zmqIfc.execHsh( { 'getDoorState': True})

        hsh =  zmqIfc.execHsh( { 'getDoorState': True})
        self.assertEqual( hsh[ 'result'], 'ON')

        if wasLaunched:
            print( "testSpock.testAscan kill pyspMonitor.py") 
            os.system( "kill_proc -f pyspMonitor.py")

        return 

if __name__ == "__main__":
    unittest.main()
