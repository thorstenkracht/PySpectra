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
import __builtin__

import HasyUtils
import Queue, argparse, sys, os

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
    args = parser.parse_args()

    return args
        
def main():

    for i in range( len( sys.argv)): 
        if sys.argv[i] == '-m':
            del sys.argv[i]

    if os.getenv( "DISPLAY") != ':0':
        QtGui.QApplication.setStyle( 'Cleanlooks')

    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)

    o = pyspMonitorClass.pyspMonitor()
    o.show()

    import pyspDoor

    try:
        door = taurus.Device( HasyUtils.getLocalDoorNames()[0])
    except Exception, e:
        print "SardanaMonitor.main: trouble connecting to door", HasyUtils.getLocalDoorNames()[0]
        print repr( e)
        sys.exit(255)

    try:
        sys.exit( app.exec_())
    except Exception, e:
        print repr( e)

if __name__ == "__main__":
    args = parseCLI()
    if args.matplotlib is True: 
        print "choosing matplotlib"
        __builtin__.__dict__[ 'graphicsLib'] = 'matplotlib'
    else: 
        __builtin__.__dict__[ 'graphicsLib'] = 'pyqtgraph'
    import pySpectraGuiClass
    import PySpectra as pysp
    import pyspMonitorClass

    main()
