#!/usr/bin/env python
'''
the main programs that imports pySpectraGui 
'''
import argparse, sys, os
 
import HasyUtils
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
    parser.add_argument( '--fs', dest="fontSize", action="store", default=None, help='font size')
    args = parser.parse_args()

    return args

def main():
    args = parseCLI()

    if not HasyUtils.checkDistroVsPythonVersion( __file__) :
        print( "pyspViewer*.main: %s does not match distro (Debian-9, 10)" % __file__)
        return

    if os.getenv( "DISPLAY") != ':0':
        QtGui.QApplication.setStyle( 'Cleanlooks')

    app = QtGui.QApplication(sys.argv)

    if args.fontSize is not None:
        font = QtGui.QFont( 'Sans Serif')
        font.setPixelSize( int( args.fontSize))
        app.setFont( font)

    o = PySpectra.pySpectraGuiClass.pySpectraGui( args.files)
    o.show()

    try:
        sys.exit( app.exec_())
    except Exception as e:
        print( "pyspViewer.main, exception")
        print( repr( e))

if __name__ == "__main__":
    args = parseCLI()
    if args.matplotlib is True: 
        os.environ["PYSP_USE_MATPLOTLIB"] = "True"
    else: 
        os.environ["PYSP_USE_MATPLOTLIB"] = "False"
    import PySpectra as pysp
    import PySpectra.pySpectraGuiClass
    main()

     
