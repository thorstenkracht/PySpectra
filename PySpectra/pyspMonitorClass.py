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
import PySpectra.GQE as GQE
import PySpectra.zmqIfc as zmqIfc
import HasyUtils 

import queue, argparse, sys, os

from PyQt4 import QtCore 
from PyQt4 import QtGui 

import PyTango
import zmq, json, socket

import tngGui.lib.tngGuiClass
import tngGui.lib.devices as devices

# 
# Speed 
# -----
# notice that the value of TIMEOUT_ZMQ is not critical because  
# inside the callback function we loop on the socket as long 
# as there is input.
#
# the test:
#   python ./test/testZmqIfc.py testZmqIfc.testToPyspMonitor4
#   take 4s, for (50, 50) for TIMEOUT_ZMQ 1 to 100
TIMEOUT_ZMQ = 100
TIMEOUT_REFRESH_MAIN = 100
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
    def __init__( self, app, flagNoDoor = None, parent = None):
        super( pyspMonitor, self).__init__( parent, calledFromSardanaMonitor = True)

        self.queue = queue.Queue()
        builtins.__dict__[ 'queue'] = self.queue

        self.setWindowTitle( "pyspMonitor")
        self.app = app
        #
        # create the door member before setMonitorGui()
        #
        self.door = None
        GQE.InfoBlock.setMonitorGui( self)
        self.refreshCount = 0
        self.flagIsBusy = False
        #
        # the Jan Garrevoet option: Do not listen to the normal Door output
        #
        self.flagNoDoor = flagNoDoor
        if not self.flagNoDoor:
            self.updateTimer = QtCore.QTimer(self)
            self.updateTimer.timeout.connect( self.cb_refreshMain)
            self.updateTimer.start( int( TIMEOUT_REFRESH_MAIN))
            try: 
                if len( HasyUtils.getDoorNames()) == 0:
                    print( "pyspMonitor.__init__: no doors")
                    sys.exit( 255)
                    
                self.door = PyTango.DeviceProxy( HasyUtils.getDoorNames()[0])
            except Exception as e:
                print( "pyspMonitor.__init__: failed to get Door proxy %s" % repr(HasyUtils.getDoorNames()[0]))

        self.helpMoveAction = self.helpMenu.addAction(self.tr("Move"))
        self.helpMoveAction.triggered.connect( self.cb_helpMove)

        #
        # needed when moveMotor is launched
        #
        self.devices = None

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
            self.timerZMQ.start( TIMEOUT_ZMQ)
        except Exception as e:
            print( "pyspMonitorClass.setupZMQ(): ZMQ error (json-dict receiver)")
            print( "message: %s" % repr( e))
            print( "assuming another pyspMonitor is ready to receive json-dcts")
            pass
        return 

    def cb_timerZMQ( self):
        """
        checks whether there is a request on the ZMQ socket, 
        from toPyspMonitor()
         - mvsa or another client fetches data from the pyspMonitor
         - a client sends data to be displayed by the pyspMonitor
        """
        self.timerZMQ.stop()
        lst = zmq.select([self.sckt], [], [], 0.01)
        argout = {}
        #
        # if we received some input, we do another select to see, if 
        # more input is arriving. this way the pyspMonitor appears  
        # to be very responsive
        #
        while self.sckt in lst[0]:
            msg = self.sckt.recv()
            hsh = json.loads( msg)
            #print( "hsh %s " % repr( hsh))
            if self.flagIsBusy:
                argout = { 'result': "pyspMonitor: rejecting dct while scanning"}
            else: 
                argout = zmqIfc.execHsh( hsh)
            msg = json.dumps( argout)
            self.sckt.send( msg)
            lst = zmq.select([self.sckt], [], [], 0.1)
        #
        # mandelbrot 20x20: if we change 10 to 1, time from 15s to 10s
        #
        self.timerZMQ.start( TIMEOUT_ZMQ)

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

        for w in self.motorNameButtons: 
            w.setEnabled( flag)
            
        if self.useMatplotlib:
            self.matplotlibBtn.setEnabled( flag)
            
    def execHshLocal( self, hsh): 
        '''
        data come from the door, via a queue()
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
            GQE._scanInfo = hsh[ 'ScanInfo']
            self.configureMotorsWidget()
        else: 
            zmqIfc.execHsh( hsh)
        return 
        
    def configureMotorsWidget( self): 
        '''
        we received a scanInfo block indicating that a new scan has started
        now we configure the motors widget using information from the scanInfo block
        '''

        length = len( self.scanInfo['motors'])
        if  length == 0 or length > 3:
            _QtGui.QMessageBox.about( None, 'Info Box', 
                                      "pyspMonitorClass: # of motors == 0 or > 3") 
            return

        motorArr = self.scanInfo['motors']        
        for i in range( 3):
            if i < length: 
                self.motorNameButtons[i].setText( motorArr[i]['name'])
                #
                # invode TngGui for all motors
                #
                self.motorNameButtons[i].clicked.connect( self.makeMotorCb( motorArr[i]))
                self.motProxies[i] = PyTango.DeviceProxy( motorArr[i]['name'])
                self.motorNameButtons[i].show()
                self.motPosLabels[i].show()
            else:
                self.motorNameButtons[i].hide()
                self.motPosLabels[i].hide()

        self.nMotor = length

    def makeMotorCb( self, hsh): 
        def motorCb():
            if self.devices is None: 
                self.devices = devices.Devices()
            devSelected = None
            for dev in self.devices.allMotors: 
                if hsh[ 'name'].upper() == dev[ 'name'].upper(): 
                    devSelected = dev
                    break
            if devSelected is None: 
                raise ValueError( "pyspMonitorClass.motorCb: failed to find %s in devices" % hsh[ 'name'])
            w = tngGui.lib.tngGuiClass.launchMoveMotor( devSelected, self.devices, self.app, self.logWidget, self)
            w.show()
            return
        return motorCb
        
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
        #
        # the queue() is filled from sendHshQueue() in
        #  /home/kracht/Misc/pySpectra/PySpectra/pyspDoor.py
        #
        try:
            cnt = 0
            while True:
                hsh = self.queue.get_nowait()
                self.execHshLocal( hsh)
                self.queue.task_done()
                cnt += 1
        except queue.Empty as e:
            pass

        self.updateTimer.start( TIMEOUT_REFRESH_MAIN)
