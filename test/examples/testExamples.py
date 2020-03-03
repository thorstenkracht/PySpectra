#!/bin/env python
'''
python ./test/examples/testExamples.py testExamples.test_execTests
'''
import PySpectra
import unittest

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
            cmd = "PySpectra.%s()" % funcName
            print( cmd)
            exec cmd
            print( "%s DONE" %  cmd)
            PySpectra.procEventsLoop( 1)
        return 

        
if __name__ == "__main__":
    unittest.main()
