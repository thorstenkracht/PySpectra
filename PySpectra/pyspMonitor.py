#!/usr/bin/env python
'''
the monitor (this file) and the door (pyspDoor) communicate through
a Queue() for 2 reasons: 
(1) the queue is thread-safe and 
(2) the door class does no graphics itself (which would mean that it
    needs a QAppl).

Note: we cannot include the pyspMonitorClass here. It has to be
imported at run-time since we have to make the selection 
pyqtgraph/matplotlib in advance
'''

import HasyUtils
import argparse, sys, os

from PyQt4 import QtCore
from PyQt4 import QtGui

# needed, because of
#   door = taurus.Device( HasyUtils.getLocalDoorNames()[0])
# otherwise no data records are received
#
import taurus

def parseCLI():
    parser = argparse.ArgumentParser( 
        formatter_class = argparse.RawDescriptionHelpFormatter,
        description="PySpectra Sardana Monitor", 
        epilog='''  ''')
    parser.add_argument( '-m', dest="matplotlib", action="store_true", help='graphics from matplotlib, def.: pyqtgraph')
    parser.add_argument( '-n', dest="flagNoDoor", action="store_true", help='do not receive data from a door')
    args = parser.parse_args()

    return args
        
def main( flagNoDoor):

    for i in range( len( sys.argv)): 
        if sys.argv[i] == '-m':
            del sys.argv[i]

    if os.getenv( "DISPLAY") != ':0':
        QtGui.QApplication.setStyle( 'Cleanlooks')

    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)

    o = pysp.pyspMonitorClass.pyspMonitor( flagNoDoor)
    o.show()

    import PySpectra.pyspDoor

    try:
        door = taurus.Device( HasyUtils.getLocalDoorNames()[0])
    except Exception as e:
        print( "SardanaMonitor.main: trouble connecting to door %s" % repr( HasyUtils.getLocalDoorNames()[0]))
        print( repr( e))
        sys.exit(255)

    try:
        sys.exit( app.exec_())
    except Exception as e:
        print( repr( e))

if __name__ == "__main__":
    args = parseCLI()
    if args.matplotlib is True: 
        os.environ["PYSP_USE_MATPLOTLIB"] = "True"
    else:
        os.environ["PYSP_USE_MATPLOTLIB"] = "False"
    import PySpectra.pySpectraGuiClass
    import PySpectra as pysp
    import PySpectra.pyspMonitorClass

    main( args.flagNoDoor)
