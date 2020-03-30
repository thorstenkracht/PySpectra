#!/bin/env python
'''
python ./test/examples/testExamples.py testExamples.test_execTests
'''
import PySpectra
import unittest
import PySpectra.examples.exampleCode
import sys
sys.path.append( "/home/kracht/Misc/pySpectra")

class testExamples( unittest.TestCase):
 
    @classmethod
    def setUpClass( testExamples):
        pass

    @classmethod
    def tearDownClass( testExamples): 
        PySpectra.close()

    def test_execTests( self):
        '''
        get the functions of ./PySpectra/examples/exampleCode.py and execute them
        '''
        for funcName in dir( PySpectra.examples.exampleCode):
            if funcName.find( 'example') != 0:
                continue
            cmd = "PySpectra.examples.exampleCode.%s()" % funcName
            print( "testExamples: executing %s" % cmd)
            exec cmd
            print( "%s DONE" %  cmd)
            PySpectra.procEventsLoop( 1)
        return 

         
if __name__ == "__main__":
    unittest.main()
