#!/usr/bin/env python
'''
the monitor (this file) and the door (pyspDoor) communicate through
a Queue() for 2 reasons: (1) the queue is thread-safe and (2) the
door class does no graphics itself (which would mean that it
needs a QAppl).
'''
import __builtin__
#__builtin__.__dict__[ 'graphicsLib'] = 'matplotlib'
__builtin__.__dict__[ 'graphicsLib'] = 'pyqtgraph'

import pySpectraGui
import PySpectra as pysp

import HasyUtils
import Queue, argparse, sys, os
from taurus.external.qt import QtGui 
from taurus.external.qt import QtCore
from taurus.qt.qtgui.application import TaurusApplication 
import taurus

updateTime = 0.1

#
# ===
#
class pyspMonitor( pySpectraGui.pySpectraGui):
    '''
    This class listens to a queue and displays the data.
    The queue is filled from pyspDoor.
    '''
    def __init__( self, parent = None):
        print "pyspMonitor.__init__"
        super( pyspMonitor, self).__init__( parent)

        self.queue = Queue.Queue()
        __builtin__.__dict__[ 'queue'] = self.queue

        self.refreshCount = 0
        self.updateTimer = QtCore.QTimer(self)
        self.updateTimer.timeout.connect( self.cb_refreshMain)
        self.updateTimer.start( int( updateTime*1000))

    def execHsh( self, hsh): 
        #print "queueSM.execHsh", repr( hsh)

        if hsh.has_key( 'cls'):
            pysp.cls()
        elif hsh.has_key( 'delete'):
            if hsh[ 'delete'] is None:
                pysp.delete()
            else: 
                pysp.delete( hsh[ 'delete'])
        elif hsh.has_key( 'display'):
            if hsh[ 'display'] is None:
                pysp.display()
            else: 
                pysp.display( hsh[ 'display'])
        elif hsh.has_key( 'setTitle'):
            pysp.setTitle( hsh[ 'setTitle'])
        elif hsh.has_key( 'setComment'):
            pysp.setComment( hsh[ 'setComment'])
        elif hsh.has_key( 'Scan'):
            if hsh[ 'Scan'].has_key( 'x'):
                if hsh[ 'Scan'].has_key( 'reUse'):
                    pysp.Scan( name = hsh[ 'Scan'][ 'name'], 
                               reUse = True, 
                               x = hsh[ 'Scan'][ 'x'], 
                               y = hsh[ 'Scan'][ 'y'])
                else:
                    pysp.Scan( name = hsh[ 'Scan'][ 'name'], 
                               x = hsh[ 'Scan'][ 'x'], 
                               y = hsh[ 'Scan'][ 'y'])
            else:
                pysp.Scan( name = hsh[ 'Scan'][ 'name'], 
                           color = hsh[ 'Scan'][ 'color'], 
                           autorangeX = hsh[ 'Scan'][ 'autorangeX'], 
                           xMax = hsh[ 'Scan'][ 'xMax'], 
                           xMin = hsh[ 'Scan'][ 'xMin'], 
                           nPts = hsh[ 'Scan'][ 'nPts'])
        elif hsh.has_key( 'setX'):
            scan = pysp.getScan( hsh[ 'setX'][ 'name'])
            scan.setX(  hsh[ 'setX'][ 'index'], hsh[ 'setX'][ 'x'])
        elif hsh.has_key( 'setY'):
            scan = pysp.getScan( hsh[ 'setY'][ 'name'])
            scan.setY(  hsh[ 'setY'][ 'index'], hsh[ 'setY'][ 'y'])
        else: 
            raise ValueError( "queueSM.execHsh: failed to identify key %s" % repr( hsh))
        
    def cb_refreshMain( self):

        print "pyspMonitor.cb_refreshMain", self.refreshCount
        #
        # without stop() the timer continues
        #
        self.updateTimer.stop()

        self.refreshCount += 1

        try:
            cnt = 0
            while True:
                hsh = self.queue.get_nowait()
                self.execHsh( hsh)
                self.queue.task_done()
                cnt += 1
        except Queue.Empty, e:
            pass
            if cnt > 0:
                print "pyspMonitor.cb_refreshMain: queue is empty, after", cnt

        self.updateTimer.start( int( updateTime*1000))
        

def parseCLI():
    parser = argparse.ArgumentParser( 
        formatter_class = argparse.RawDescriptionHelpFormatter,
        description="PySpectra Sardana Monitor", 
        epilog='''\
  pyspMonitor.py 
    ''')
    #parser.add_argument( '-m', dest="matplotlib", action="store_true", help='graphics from matplotlib')
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
        #app = QtGui.QApplication(sys.argv)
        app = TaurusApplication( sys.argv)

    o = pyspMonitor()
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
    #args = parseCLI()
    #if args.matplotlib is True: 
    #    print "choosing matplotlib"
    #    __builtin__.__dict__[ 'graphicsLib'] = 'matplotlib'
    #else: 
    #    __builtin__.__dict__[ 'graphicsLib'] = 'pyqtgraph'
    main()
