#!/usr/bin/env python
'''
the main programs that imports pySpectraGui
'''
import __builtin__
#__builtin__.__dict__[ 'graphicsLib'] = 'matplotlib'
#__builtin__.__dict__[ 'graphicsLib'] = 'pyqtgraph'
#import PySpectra as pysp
#import pySpectraGui

import argparse, sys, os
from PyQt4 import QtGui, QtCore

def parseCLI():
    parser = argparse.ArgumentParser( 
        formatter_class = argparse.RawDescriptionHelpFormatter,
        description="Sardana Monitor Queue Version", 
        epilog='''\
  queueSM.py -m 
    uses matplotlib
    ''')

    parser.add_argument( 'files', nargs='*', help='file name pattern')
    parser.add_argument( '-m', dest="matplotlib", action="store_true", help='graphics from matplotlib')
    args = parser.parse_args()

    return args

def main():
    args = parseCLI()

    if os.getenv( "DISPLAY") != ':0':
        QtGui.QApplication.setStyle( 'Cleanlooks')

    app = QtGui.QApplication(sys.argv)

    o = pySpectraGuiClass.pySpectraGui( args.files)
    o.show()

    try:
        sys.exit( app.exec_())
    except Exception, e:
        print repr( e)

if __name__ == "__main__":
    args = parseCLI()
    if args.matplotlib is True: 
        __builtin__.__dict__[ 'graphicsLib'] = 'matplotlib'
    else: 
        __builtin__.__dict__[ 'graphicsLib'] = 'pyqtgraph'
    import PySpectra as pysp
    import pySpectraGuiClass
    main()

     
