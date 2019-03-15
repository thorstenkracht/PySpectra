#!/usr/bin/env python
'''
the monitor (this file) and the door (pyspDoor) communicate through
a Queue() for 2 reasons: 
(1) the queue is thread-safe and 
(2) the door class does no graphics itself (which would mean that it
    needs a QAppl).

we need to put the pyspMonitor class into a separate file to 
make it run-time importable. The selection pyqtgraph/matplotlib
has to be done in advance.
'''
import __builtin__
import pySpectraGuiClass
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
class pyspMonitor( pySpectraGuiClass.pySpectraGui):
    '''
    This class listens to a queue and displays the data.
    The queue is filled from pyspDoor.
    '''
    def __init__( self, parent = None):
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
            pysp.Scan( **hsh[ 'Scan']) 
        elif hsh.has_key( 'setX'):
            scan = pysp.getScan( hsh[ 'setX'][ 'name'])
            scan.setX(  hsh[ 'setX'][ 'index'], hsh[ 'setX'][ 'x'])
        elif hsh.has_key( 'setY'):
            scan = pysp.getScan( hsh[ 'setY'][ 'name'])
            scan.setY(  hsh[ 'setY'][ 'index'], hsh[ 'setY'][ 'y'])
        else: 
            raise ValueError( "queueSM.execHsh: failed to identify key %s" % repr( hsh))
        
    def cb_refreshMain( self):

        #print "pyspMonitor.cb_refreshMain", self.refreshCount
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

        self.updateTimer.start( int( updateTime*1000))
