#!/usr/bin/env python
'''
the monitor (this file) and the door (pyspDoor) communicate through
a queue() for 2 reasons: 
(1) the queue is thread-safe and 
(2) the door class does no graphics itself (which would mean that it
    needs a QAppl).

we need to put the pyspMonitor class into a separate file to 
make it run-time importable. The selection pyqtgraph/matplotlib
has to be done in advance.
'''
import builtins
import pySpectraGuiClass
import PySpectra as pysp
import HasyUtils 

import queue, argparse, sys, os

from PyQt4 import QtCore 
from PyQt4 import QtGui 

import PyTango as _PyTango
import zmq, json, socket

updateTime = 0.1


#
#
#
flagGraphicsOnly = False

#
# ===
#
class pyspMonitor( pySpectraGuiClass.pySpectraGui):
    '''
    This class listens to a queue and displays the data.
    The queue is filled from pyspDoor.
    '''
    def __init__( self, flagNoDoor = None, parent = None):
        super( pyspMonitor, self).__init__( parent, calledFromSardanaMonitor = True)

        self.queue = queue.Queue()
        builtins.__dict__[ 'queue'] = self.queue

        self.refreshCount = 0
        self.flagIsBusy = False
        #
        # the Jan Garrevoet option: Do not listen to the normal Door output
        #
        self.flagNoDoor = flagNoDoor
        if not self.flagNoDoor:
            self.updateTimer = QtCore.QTimer(self)
            self.updateTimer.timeout.connect( self.cb_refreshMain)
            self.updateTimer.start( int( updateTime*1000))
            try: 
                if len( HasyUtils.getDoorNames()) == 0:
                    print( "pyspMonitor.__init__: no doors")
                    sys.exit( 255)
                    
                self.door = _PyTango.DeviceProxy( HasyUtils.getDoorNames()[0])
            except Exception as e:
                print( "pyspMonitor.__init__: failed to get Door proxy %s" % repr(HasyUtils.getDoorNames()[0]))

        self.helpMoveAction = self.helpMenu.addAction(self.tr("Move"))
        self.helpMoveAction.triggered.connect( self.cb_helpMove)

        self.setupZMQ()

    def setupZMQ( self): 
        #
        # the zmq interface allows other processes to send data
        # to the pyspMonitor which are then displayed, via toPyspMonitor()
        #
        self.context = zmq.Context()
        self.sckt = self.context.socket(zmq.REP)
        #
        # don't use localhost. it is a different interface
        #
        try:
            self.sckt.bind( "tcp://%s:7779" % socket.gethostbyname( socket.getfqdn()))
            self.timerZMQ = QtCore.QTimer( self)
            self.timerZMQ.timeout.connect( self.cb_timerZMQ)
            self.timerZMQ.start(100)
        except Exception as e:
            print( "pyspMonitorMain.__init__(): ZMQ error (json-dict receiver)")
            print( "message: %s" % repr( e))
            print( "assuming another pyspMonitor is ready to receive json-dcts")
            pass
        return 

    def cb_timerZMQ( self):
        #
        # checks whether there is a request on the ZMQ socket, 
        # from toPyspMonitor()
        #   - mvsa or another client fetches data from the pyspMonitor
        #   - a client sends data to be displayed by the pyspMonitor
        #
        self.timerZMQ.stop()
        lst = zmq.select([self.sckt], [], [], 0.1)
        argout = {}
        if self.sckt in lst[0]:
            msg = self.sckt.recv()
            hsh = json.loads( msg)
            if self.flagIsBusy:
                return "pyspMonitor: rejecting dct while scanning"
            argout = pysp.toPysp( hsh)
            msg = json.dumps( argout)
            self.sckt.send( msg)
        #
        # mandelbrot 20x20: if we change 10 to 1, time from 15s to 10s
        #
        self.timerZMQ.start(10)

    def cb_helpMove(self):
        QtGui.QMessageBox.about(self, self.tr("Help Move"), self.tr(
                "<h3> Move</h3>"
                "A motor can be moved by"
                "<ul>"
                "<li> Select a single scan for display</li>"
                "<li> Click into the Scan</li>"
                "</ul>"
                " The user is asked for confimation before the move is executed"
                ))

    def setCertainWidgetEnabled( self, flag):
        '''
        enable/display widgets while a scan is active
        '''

        self.fileMenu.setEnabled( flag)
        self.utilsMenu.setEnabled( flag)
        self.optionsMenu.setEnabled( flag)
        self.configMenu.setEnabled( flag)
        self.examplesMenu.setEnabled( flag)

        self.all.setEnabled( flag)
        self.checked.setEnabled( flag)
        self.clsBtn.setEnabled( flag)
        self.deleteBtn.setEnabled( flag)
        self.back.setEnabled( flag)
        self.next.setEnabled( flag)
        self.refreshFiles.setEnabled( flag)
        self.scrollAreaFiles.setEnabled( flag)
        self.scrollAreaScans.setEnabled( flag)
        if self.useMatplotlib:
            self.matplotlibBtn.setEnabled( flag)

    def execHsh( self, hsh): 
        '''
        data come from the door
        '''
        #print( "pyspMonitorClass.queueSM.execHsh %s " % repr( hsh))

        if 'newScan' in hsh and hsh[ 'newScan']: 
            self.setCertainWidgetEnabled( False)
            self.flagIsBusy = True
        elif 'endScan' in hsh and hsh[ 'endScan']: 
            self.setCertainWidgetEnabled( True)
            self.flagIsBusy = False
        #
        # the scanInfo dictionary is sent when a new scan starts
        #
        elif 'ScanInfo' in hsh:
            self.scanInfo = hsh[ 'ScanInfo']
            self.configureMotorsWidget()
        else: 
            pysp.toPysp( hsh)
        
    def configureMotorsWidget( self): 
        '''
        we received a scanInfo block indicating that a new scan has started
        now we configure the motors widget using information from the scanInfo block
        '''
        pysp.GQE.setMonitorGui( self)

        length = len( self.scanInfo['motors'])
        if  length == 0 or length > 3:
            _QtGui.QMessageBox.about( None, 'Info Box', 
                                      "pyspMonitorClass: # of motors == 0 or > 3") 
            return

        motorArr = self.scanInfo['motors']        
        for i in range( 3):
            if i < length: 
                self.motNameLabels[i].setText( motorArr[i]['name'])
                self.motProxies[i] = _PyTango.DeviceProxy( motorArr[i]['name'])
                self.motNameLabels[i].show()
                self.motPosLabels[i].show()
            else:
                self.motNameLabels[i].hide()
                self.motPosLabels[i].hide()

        self.nMotor = length

    def cb_refreshMain( self):
        '''
        this function receives data from the door
        '''
        #print( "pyspMonitor.cb_refreshMain %d" % self.refreshCount)
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
        except queue.Empty as e:
            pass

        self.updateTimer.start( int( updateTime*1000))
