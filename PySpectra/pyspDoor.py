#!/usr/bin/env python
'''
the Door which communicates to pyspMonitor via a queue

the Door is the sender using sendHshQueue()

be sure to 'senv JsonRecorder True' 
'''
import PyTango
import time, sys, os, math
import numpy as np
import HasyUtils

try:
    import sardana.taurus.core.tango.sardana.macroserver as sms
except Exception as e:
    print( "pyspDoor.py: failed to import macroserver.py")
    print( "  reason: %s" % repr( e))
    if HasyUtils.getPythonVersionSardana() == '/usr/bin/python3':
        print( "  consider to start pyspMonitor3.py")
    print( "  exiting")
    sys.exit(255) 

import pprint, math
import builtins

pp = pprint.PrettyPrinter()
db = PyTango.Database()
sms.registerExtensions()

flagPrintOnce1 = False 
#
# this global variable is supposed to store 'self' of the pyspDoor instance
# to be called, e.g. from SardanaMonitor to send some data
#
pyspDoorInstance = None

class pyspDoor( sms.BaseDoor):

    def __init__( self, name, **kw):
        global pyspDoorInstance

        #print( "pyspDoor.__init__() %s" % name)
        #pysp.setWsViewport( "DINA4L")
        self.queue = builtins.__dict__[ 'queue']
        
        #self.counter_gqes = {}
        self.posOld = []
        self.mcaAliases = []
        self.mcaProxies = []
        self.mcaArrays = []
        self.mcaFileName = "/tmp/temp_MCA_pyspDoor.fio"
        self.serialnoDumped = -1
        self.isMesh = False
        self.meshGoingUp = True 
        self.meshSweepCount = 1
        self.scanNo = 0
        self.signalCounter = None
        #
        # Mind: sometimes we loose records
        #
        self.call__init__( sms.BaseDoor, name, **kw)
        #
        # make sure that FlagDisplayAll exists
        #
        self.env = self.getEnvironment()
        if 'FlagDisplayAll' not in self.env:
            self.setEnvironment( 'FlagDisplayAll', 'True')
        pyspDoorInstance = self
        #
        # use this flag to determined whether we are currently inside a scan
        # that would mean that we cannot accept data from ZMQ
        #
        self.flagIsBusy = False
        #
        # this flag is for the CursorApp to decide whether a motor
        # may be moved
        #

    def get_alias( self, argin):
        """
        return the alias of a device name, strip TANGO_HOST info, if necessary
        need to strip: haso107klx:10000/expchan/hasysis3820ctrl/1 -> expchan/hasysis3820ctrl/1 
        """
        #
        # if argin does not contain a "/" it's probably an alias
        #
        if argin.find("/") == -1:
            return argin

        temp = argin
        #
        # the new measurement group: 
        #   tango://haso107tk.desy.de:10000/expchan/vc_ipetra/1 -> expchan/vc_ipetra/1
        #   ['tango:', '', 'haso107tk.desy.de:10000', 'expchan', 'vc_ipetra', '1']
        #
        if argin.find( 'tango') == 0:
            lst = argin.split("/")
            temp = "/".join(lst[3:])
        #
        # haso107klx:10000/expchan/hasysis3820ctrl/1 -> expchan/hasysis3820ctrl/1
        #
        elif argin.find( '0000') >= 0:
            lst = argin.split("/")
            temp = "/".join(lst[1:])
        try:
            argout = db.get_alias( temp)
        except:
            #
            # haso107klx:10000/expchan/hasysis3820ctrl/1
            # -> expchan_hasysus3820ctrl_1 (Spectra compliant)
            #
            argout = "_".join(lst[-3:])
        #
        # motor_d1.01_position
        #
        if argout.find( ".") > 0:
            lst = argout.split( '.')
            argout = "_".join( lst)
        # 
        # print( "get_alias: %s -> %s " % (argin, argout))
        # get_alias: haso107d1:10000/expchan/sis3820_d1/1 -> d1_c01 
        # get_alias: haso107d1:10000/expchan/vc_sig_gen/1 -> sig_gen 
        # get_alias: haso107d1:10000/expchan/vc_ipetra/1 -> ipetra 
        # 
        return argout

    def get_proxy( self, argin):
        """
        return the proxy to the device name specified by argin
        """
        argout = PyTango.DeviceProxy( argin)
        return argout

    def cleanupPysp( self):
        """
        cleans the internal storage and the graphics screen.
        """
        self.sendHshQueue( { 'command': ['delete', 'cls']})
        return 

    def waitForFile( self, filename):
        """
        returns True, if the file exists and is no longer opened by the MS
        for 1 - 4 MCAs (8192 channels) the wait time is about 0.25s
        """
        startTime = time.time()
        #
        # the following loop terminates with count equal 0, in general.
        # however, now and then there are small delays
        #
        for count in range(0,10):
            if os.path.exists( filename):
                status = True
                break
            time.sleep(0.05)
        if not status:
            raise Exception( "pyspDoor.waitForFile", "%s is not created" % (filename))

        oldSize = 0
        count = 0
        while 1:
            if oldSize > 0 and oldSize == os.path.getsize(filename):
                break
            oldSize = os.path.getsize(filename)
            time.sleep( 0.02)
            if count > 10:
                raise Exception( "pyspDoor.waitForFile", "%s still not complete" % (filename))
            count += 1

        return status

    def displayMCAs( self):
        for n in range( 0, len( self.mcaAliases)):
            y = self.mcaProxies[n].Value
            x = np.arange( 0., len( y), 1)
            #
            # Re-use the scan. Otherwise we have these flickering displays
            #
            self.sendHshQueue( { 'Scan': { 'name': self.mcaAliases[n],
                                           'flagMCA': True, 
                                           'lineColor': 'blue', 
                                           'x': x, 
                                           'y': y}}) 
            

    def toBeDisplayed( self, name, dataRecord):
        """
        returns True, if name has plot_type == 1
        """
        # ('',
        # {u'data': {u'column_desc': [{...}, 
        #                             {u'conditioning': u'',
        #                              u'data_units': u'No unit',
        #                              u'dtype': u'',
        #                              u'instrument': u'',
        #                              u'label': u'exp_doris',
        #                              u'name': u'haso107klx:10000/expchan/doris_exp_doris/1',
        #                              u'normalization': 0,
        #                              u'output': True,
        #                              u'plot_axes': [u'exp_dmy01'],
        #                              u'plot_type': 0,
        #                              u'shape': [],
        #                              u'source': u'haso107klx:10000/expchan/doris_exp_doris/1/value'},

        for col in dataRecord[1]['data'][ 'column_desc']:
            #
            # MCAs do not appear in the column_desc, assume they are displayed
            #
            if name.find( 'mca') >= 0:
                return True
            if name.find( 'sis3302') >= 0:
                return True

            if name == col['name']:
                if col['plot_type']:
                    return True
                else:
                    return False
        #print( "pyspDoor>toBeDisplayed: not found %s" % name)
        return False

    def findCountersAndMCAs( self, dataRecord):
        """
        find the counter and MCA aliases and create
        the dictionary that translate them to device names
        """
        #print( "findCountersAndMCAs")
        self.counterAliases = []
        self.mcaAliases = []
        self.mcaProxies = []
        self.alias_dict = {}
        #
        # just for display, calculated from counters
        #
        self.displayCounterHsh = {}
        #
        # u'counters': [u'haso107klx:10000/expchan/hasysis3820ctrl/1',
        #               u'haso107klx:10000/expchan/hasyvfcadcctrl/1'],
        #
        # u'counters': [u'haspp09mono:10000/expchan/sis3302_exp/1',
        #                u'haspp09mono:10000/expchan/sis3302roisis3302exp.01ctrl/1',
        #                u'haspp09mono:10000/expchan/sis3302roisis3302exp.01ctrl/2',
        #                u'haspp09mono:10000/expchan/sis3302roisis3302exp.01ctrl/3'],
        for elm in dataRecord[1]['data'][ 'counters']:
            if not self.toBeDisplayed( elm, dataRecord):
                continue
            alias = self.get_alias( str(elm))
            if alias is None:
                continue
            self.alias_dict[alias] = elm
            #
            # 'mca; appears also in SCA names, sca_exp_mca01_0_1000
            #
            if elm.find( "pc/sca_") >= 0:
                self.counterAliases.append( alias)
            #
            # mca8715rois
            #
            elif elm.find( "expchan/mca8715roi") >= 0:
                self.counterAliases.append( alias)
            #
            # the mcas
            #
            elif ( elm.find( "expchan/mca") >= 0 or 
                   elm.find( "expchan/sis3302_") >= 0 or
                   elm.find( "expchan/sis3302ms1dexp03ctrl/1") >= 0 or
                   elm.find( "expchan/sis3302roi1dexp01ctrl/1") >= 0 or
                   elm.find( "expchan/sis3302ms1dexp01ctrl/1") >= 0 ):
                self.mcaAliases.append( alias)
                self.mcaProxies.append( self.get_proxy( str(elm)))
            # 
            # !!! has to be after MCA dection because it is just the channel no. which
            # !!! tells that e.g. expchan/sis3302roi1dexp01ctrl/1 is a MCA
            # sis3302rois
            #
            elif elm.find( "expchan/sis3302roi") >= 0:
                self.counterAliases.append( alias)
            else:
                self.counterAliases.append( alias)
        # +++
        #print( "alias_dict %s" % repr( self.alias_dict))
        #print( "counters %s" % repr( self.counterAliases))
        #print( "mcas %s" % repr( self.mcaAliases))

        self.handleDisplayCounters()
        return 

    def handleDisplayCounters( self): 
        """
        called from findCountersAndMCAs and prepareNewScan


        p09/door/haso107tk.01 [62]: senv useDisplayCounters True
        useDisplayCounters = True
        
        p09/door/haso107tk.01 [63]: senv displayCounters "{ 'vfc_ratio': 'DataDict[ \'eh_vfc01\']/DataDict[ \'eh_vfc02\']'}"
        displayCounters = {'vfc_ratio': "DataDict[ 'eh_vfc01']/DataDict[ 'eh_vfc02']"}


        p09/door/haso107tk.01 [74]: import HasyUtils
        p09/door/haso107tk.01 [75]: hsh = { 'vfc_ratio': "DataDict[ 'eh_vfc01']/DataDict[ 'eh_vfc02']"}
        p09/door/haso107tk.01 [76]: HasyUtils.setEnv( "displayCounters", hsh)


        """
        self.useDisplayCounters = HasyUtils.getEnv( "useDisplayCounters")

        if self.useDisplayCounters is None or \
           type( self.useDisplayCounters) is bool and self.useDisplayCounters == False or \
           type( self.useDisplayCounters) is str and self.useDisplayCounters == "False":
            self.useDisplayCounters = False
            self.displayCounterHsh = {}
            return 
            
        self.useDisplayCounters = True
        hsh = HasyUtils.getEnv( "displayCounters")
        if hsh is not None: 
            if type( hsh) is dict: 
                self.displayCounterHsh = {}
                for k in list( hsh.keys()):
                    self.displayCounterHsh[ k] = hsh[ k]
            else: 
                print( "pyspDoor.__init__: displayCounters is not a dict, but %s" % repr( type( hsh)))
                sys.exit( 255)
        else: 
            print( "pyspDoor.handleDisplayCounters: useDisplayCounters == True but no displayCounters dict")
            sys.exit( 255)

        return 

    def prepareTitleAndSo( self, dataRecord):

        #
        # scanfile: tst.fio
        #
        if type(dataRecord[1]['data'][ 'scanfile']).__name__ == 'list':
            self.scanfile = dataRecord[1]['data'][ 'scanfile'][0]
        else:
            self.scanfile = dataRecord[1]['data'][ 'scanfile']
        if self.scanfile is None:
            raise Exception( "pyspDoor.prepareTitleAndSo", "ScanFile not defined")
        self.scandir = dataRecord[1]['data'][ 'scandir']
        if self.scandir is None:
            raise Exception( "pyspDoor.prepareTitleAndSo", "ScanDir not defined")
        self.serialno = dataRecord[1]['data'][ 'serialno']
        tpl = self.scanfile.rpartition('.')
        self.filename = "%s_%05d.%s" % (tpl[0], self.serialno, tpl[2])
        self.startTime = dataRecord[1]['data']['starttime']
        self.title = dataRecord[1]['data']['title']
        if self.title.find( 'fscan') == 0: 
            self.title = HasyUtils.repairFscanTitle(self.title)
            self.isFscan = True

        self.sendHshQueue( { 'command': ["setTitle " + self.title]})
        self.sendHshQueue( { 'command': ["setComment \"%s, %s\"" % (self.filename, self.startTime)]})

    def getPosition( self, name): 
        pos = None
        try:
            proxy = PyTango.DeviceProxy( str( name))
            while proxy.state() == PyTango.DevState.MOVING:
                time.sleep(0.1)
            pos = proxy.position
        except PyTango.DevFailed as e:
            PyTango.Except.print_exception( e)
            return 0
        return pos

    def getVelocity( self, name): 
        pos = None
        try:
            proxy = PyTango.DeviceProxy( str( name))
            velocity = proxy.velocity
        except PyTango.DevFailed as e:
            PyTango.Except.print_exception( e)
            return 0
        return velocity

    def extractMotorLimitDct( self, dataRecord): 
        #
        # the column_desc array can be found in prepareNewScan()
        #
        # returns, e.g. 
        #  {
        #    exp_dmy01:[0.0, 2.0],
        #    exp_dmy02:[-1.0, 3.0],
        #  }
        #
        colArray = dataRecord[1]['data']['column_desc']
        argout = {}
        for hsh in colArray:
            if 'max_value' in hsh and 'min_value' in hsh:
                argout[hsh['name']] = [hsh['min_value'], hsh['max_value']]
        return argout

    def findScanLimits( self, dataRecord):
        '''
        look at the command line and find the start and stop values.
        these values should be chosen from a motor that is actually moved, 
        consider hkl scans where h stays at a constant position
        also set the self.motorNameList array because ref_moveables is not correct
        '''
        #
        # get the scan limits from the title
        #
        #
        # get the scan limits from the title
        #
        if dataRecord[1]['data']['title'].find( 'fscan') == 0: 
            cmd = HasyUtils.repairFscanTitle( dataRecord[1]['data']['title']).split()
        else: 
            cmd = dataRecord[1]['data']['title'].split()
        #
        # ascan exp_dmy01 0 1 10 0.2
        #
        if cmd[0] == 'ascan':
            self.start = float( cmd[2])
            self.stop =  float( cmd[3])
            self.np =    int( cmd[4])
            self.motorIndex = 0
            self.motorNameList = [ cmd[1]]
        #
        # ascanc exp_dmy01 start stop integTime slowFactor
        #
        elif cmd[0] == 'ascanc':
            self.start = float( cmd[2])
            self.stop =  float( cmd[3])
            self.motorIndex = 0
            self.motorNameList = [ cmd[1]]
            slowFactor = 1.
            if len( cmd) == 6:
                slowFactor = float( cmd[5])
            integTime = float( cmd[4])
            velocity = self.getVelocity( cmd[1])
            diff = math.fabs(self.stop - self.start)
            self.np = int( diff/velocity/integTime/slowFactor) + 10
        #
        # ascan_repeat exp_dmy01 0 1 10 0.2 2
        #
        elif cmd[0] == 'ascan_repeat':
            self.start = float( cmd[2])
            self.stop =  float( cmd[3])
            self.np =    int( cmd[4])*int(cmd[6]) + 1
            self.motorIndex = 0
            self.motorNameList = [ cmd[1]]
        #
        # ascan_checkabs exp_dmy01 0 1 10 0.2
        #
        elif cmd[0] == 'ascan_checkabs' or \
                cmd[0] == 'ascan_absorber':
            self.start = float(cmd[2])
            self.stop = float( cmd[3])
            self.np = 2000 # we don't know beforehand how many points will be measured
            self.motorIndex = 0
            self.motorNameList = [ cmd[1]]
        #
        # a2scan exp_dmy01 0 1 exp_dmy02 2 3 10 0.2
        #
        elif cmd[0] == 'a2scan':
            diff1 = math.fabs(float( cmd[3]) - float( cmd[2]))
            self.motorNameList = [ cmd[1], cmd[4]]
            self.np =    int( cmd[7])
            if diff1 == 0.:
                self.start = float( cmd[5])
                self.stop =  float( cmd[6])
                self.motorIndex = 1
            else:
                self.start = float( cmd[2])
                self.stop =  float( cmd[3])
                self.motorIndex = 0
        #
        # a2scanc exp_dmy01 start1 stop1 exp_dmy02 start2 stop2 integ_time
        #
        elif cmd[0] == 'a2scanc':
            diff1 = math.fabs(float( cmd[3]) - float( cmd[2]))
            self.motorNameList = [ cmd[1], cmd[4]]
            if diff1 == 0.:
                self.start = float( cmd[5])
                self.stop =  float( cmd[6])
                self.motorIndex = 1
            else:
                self.start = float( cmd[2])
                self.stop =  float( cmd[3])
                self.motorIndex = 0
            slowFactor = 1
            if len( cmd) == 9:
                slowFactor = float( cmd[8])
            integTime = float( cmd[7])
            diff1 = math.fabs( float( cmd[3]) - float( cmd[2]))
            diff2 = math.fabs( float( cmd[6]) - float( cmd[5]))
            np1 = int( diff1/self.getVelocity( cmd[1])/integTime/slowFactor) + 10
            np2 = int( diff2/self.getVelocity( cmd[4])/integTime/slowFactor) + 10
            self.np = max( np1, np2)
        #
        # a3scan exp_dmy01 0 1 exp_dmy02 2 3 exp_dmy03 3 4 10 0.2
        #
        elif cmd[0] == 'a3scan':
            diff1 = math.fabs(float( cmd[3]) - float( cmd[2]))
            diff2 = math.fabs(float( cmd[6]) - float( cmd[5]))
            self.motorNameList = [ cmd[1], cmd[4], cmd[7]]
            self.np =    int( cmd[10])
            if diff2  == 0. and diff1 == 0.:
                self.start = float( cmd[8])
                self.stop =  float( cmd[9])
                self.motorIndex = 2
            elif diff1 == 0.:
                self.start = float( cmd[5])
                self.stop =  float( cmd[6])
                self.motorIndex = 1
            else:
                self.start = float( cmd[2])
                self.stop =  float( cmd[3])
                self.motorIndex = 0
        #
        # a3scanc exp_dmy01 0 1 exp_dmy02 2 3 exp_dmy03 3 4 integtTime slowFactor
        #
        elif cmd[0] == 'a3scanc':
            diff1 = math.fabs(float( cmd[3]) - float( cmd[2]))
            diff2 = math.fabs(float( cmd[6]) - float( cmd[5]))
            self.motorNameList = [ cmd[1], cmd[4], cmd[7]]
            if diff2  == 0. and diff1 == 0.:
                self.start = float( cmd[8])
                self.stop =  float( cmd[9])
                self.motorIndex = 2
            elif diff1 == 0.:
                self.start = float( cmd[5])
                self.stop =  float( cmd[6])
                self.motorIndex = 1
            else:
                self.start = float( cmd[2])
                self.stop =  float( cmd[3])
                self.motorIndex = 0
            slowFactor = 1
            if len( cmd) == 12:
                slowFactor = float( cmd[11])
            integTime = float( cmd[10])
            diff1 = math.fabs( float( cmd[3]) - float( cmd[2]))
            diff2 = math.fabs( float( cmd[6]) - float( cmd[5]))
            diff3 = math.fabs( float( cmd[9]) - float( cmd[8]))
            np1 = int( diff1/self.getVelocity( cmd[1])/integTime/slowFactor) + 10
            np2 = int( diff2/self.getVelocity( cmd[4])/integTime/slowFactor) + 10
            np3 = int( diff3/self.getVelocity( cmd[7])/integTime/slowFactor) + 10
            self.np = max( np1, np2, np3)
        #
        # a4scan exp_dmy01 0 1 exp_dmy02 2 3 exp_dmy03 3 4 exp_dmy04 4 5 10 0.2
        #
        elif cmd[0] == 'a4scan':
            diff1 = math.fabs(float( cmd[3]) - float( cmd[2]))
            diff2 = math.fabs(float( cmd[6]) - float( cmd[5]))
            diff3 = math.fabs(float( cmd[9]) - float( cmd[8]))
            self.motorNameList = [ cmd[1], cmd[4], cmd[7], cmd[10]]
            self.np =    int( cmd[13])
            if diff3 == 0 and diff2 == 0. and diff1 == 0.:
                self.start = float( cmd[11])
                self.stop =  float( cmd[12])
                self.motorIndex = 3
            elif diff2 == 0. and diff1 == 0.:
                self.start = float( cmd[8])
                self.stop =  float( cmd[9])
                self.motorIndex = 2
            elif diff1 == 0.:
                self.start = float( cmd[5])
                self.stop =  float( cmd[6])
                self.motorIndex = 1
            else:
                self.start = float( cmd[2])
                self.stop =  float( cmd[3])
                self.motorIndex = 0
        #
        # dscan eh1_dmy01 -0.1 0.1 3 0.1 
        #
        elif cmd[0] == 'dscan':
            #
            # {u'd1_vm02': [4.004897701573356, 5.004897701573356]}
            #
            motorLimitDct = self.extractMotorLimitDct( dataRecord)

            self.motorIndex = 0
            self.motorNameList = [ cmd[1]]
            self.start = motorLimitDct[ cmd[1]][0]
            self.stop = motorLimitDct[ cmd[1]][1]

            self.np = int(cmd[4])
        #
        # dscanc eh1_dmy01 -0.1 0.1 integTime slowFactor
        #
        elif cmd[0] == 'dscanc':
            motorLimitDct = self.extractMotorLimitDct( dataRecord)
            self.motorIndex = 0
            self.motorNameList = [ cmd[1]]
            self.start = motorLimitDct[ cmd[1]][0]
            self.stop = motorLimitDct[ cmd[1]][1]
            slowFactor = 1
            if len( cmd) == 6:
                slowFactor = float( cmd[5])
            integTime = float( cmd[4])
            velocity = self.getVelocity( cmd[1])
            diff = math.fabs(self.stop - self.start)
            self.np = int( diff/velocity/integTime/slowFactor) + 10
        #
        # dscan_repeat eh1_dmy01 -0.1 0.1 3 0.1 2
        #
        elif cmd[0] == 'dscan_repeat':
            motorLimitDct = self.extractMotorLimitDct( dataRecord)

            self.motorIndex = 0
            self.motorNameList = [ cmd[1]]
            self.start = motorLimitDct[ cmd[1]][0]
            self.stop = motorLimitDct[ cmd[1]][1]
            self.motorIndex = 0
            self.motorNameList = [ cmd[1]]
            #pos = self.getPosition( self.motorNameList[ self.motorIndex])
            #self.start =  pos
            #self.stop = pos + float(cmd[3]) - float(cmd[2])
            self.np = int(cmd[4])*int(cmd[6]) + 1
        #
        # d2scan eh1_dmy01 -0.1 0.1 eh1_dmy02 -0.2 0.2 10 0.1 
        #
        elif cmd[0] == 'd2scan':
            motorLimitDct = self.extractMotorLimitDct( dataRecord)
            diff1 = math.fabs(float( cmd[3]) - float( cmd[2]))
            self.motorNameList = [ cmd[1], cmd[4]]
            self.np = int(cmd[7])

            if diff1 == 0.:
                self.motorIndex = 1
                self.start =  motorLimitDct[ cmd[4]][0]
                self.stop = motorLimitDct[ cmd[4]][1]
            else:
                self.motorIndex = 0
                self.start =  motorLimitDct[ cmd[1]][0]
                self.stop = motorLimitDct[ cmd[1]][1]
        #
        # d2scanc eh1_dmy01 -0.1 0.1 eh1_dmy02 -0.2 0.2 integTime slowFactor
        #
        elif cmd[0] == 'd2scanc':
            motorLimitDct = self.extractMotorLimitDct( dataRecord)
            diff1 = math.fabs(float( cmd[3]) - float( cmd[2]))
            self.motorNameList = [ cmd[1], cmd[4]]

            if diff1 == 0.:
                self.motorIndex = 1
                self.start =  motorLimitDct[ cmd[4]][0]
                self.stop = motorLimitDct[ cmd[4]][1]
            else:
                self.motorIndex = 0
                self.start =  motorLimitDct[ cmd[1]][0]
                self.stop = motorLimitDct[ cmd[1]][1]
            slowFactor = 1
            if len( cmd) == 9:
                slowFactor = float( cmd[8])
            integTime = float( cmd[7])
            diff1 = math.fabs( motorLimitDct[ cmd[1]][1] - motorLimitDct[ cmd[1]][0])
            diff2 = math.fabs( motorLimitDct[ cmd[4]][1] - motorLimitDct[ cmd[4]][0])
            np1 = int( diff1/self.getVelocity( cmd[1])/integTime/slowFactor) + 10
            np2 = int( diff2/self.getVelocity( cmd[4])/integTime/slowFactor) + 10
            self.np = max( np1, np2)
        #
        # d3scan eh1_dmy01 -0.1 0.1 eh1_dmy02 -0.2 0.2 eh1_dmy03 -0.3 0.3 10 0.1 
        #
        elif cmd[0] == 'd3scan':
            motorLimitDct = self.extractMotorLimitDct( dataRecord)

            diff1 = math.fabs(float( cmd[3]) - float( cmd[2]))
            diff2 = math.fabs(float( cmd[6]) - float( cmd[5]))
            self.motorNameList = [ cmd[1], cmd[4], cmd[7]]
            self.np = int(cmd[10])
            #
            # getPosition() returns after the move has finished - but
            # it has to be started!
            #
            time.sleep(0.5)
            if diff1 == 0. and diff2 == 0.:
                self.motorIndex = 2
                self.start =  motorLimitDct[ cmd[7]][0]
                self.stop = motorLimitDct[ cmd[7]][1]
            elif diff1 == 0.:
                self.motorIndex = 1
                self.start =  motorLimitDct[ cmd[4]][0]
                self.stop = motorLimitDct[ cmd[4]][1]
            else:
                self.motorIndex = 0
                self.start =  motorLimitDct[ cmd[1]][0]
                self.stop = motorLimitDct[ cmd[1]][1]
        #
        # d3scanc eh1_dmy01 -0.1 0.1 eh1_dmy02 -0.2 0.2 eh1_dmy03 -0.3 0.3 integTime slowFactor
        #
        elif cmd[0] == 'd3scanc':
            motorLimitDct = self.extractMotorLimitDct( dataRecord)

            diff1 = math.fabs(float( cmd[3]) - float( cmd[2]))
            diff2 = math.fabs(float( cmd[6]) - float( cmd[5]))
            self.motorNameList = [ cmd[1], cmd[4], cmd[7]]
            #
            # getPosition() returns after the move has finished - but
            # it has to be started!
            #
            time.sleep(0.5)
            if diff1 == 0. and diff2 == 0.:
                self.motorIndex = 2
                self.start =  motorLimitDct[ cmd[7]][0]
                self.stop = motorLimitDct[ cmd[7]][1]
            elif diff1 == 0.:
                self.motorIndex = 1
                self.start =  motorLimitDct[ cmd[4]][0]
                self.stop = motorLimitDct[ cmd[4]][1]
            else:
                self.motorIndex = 0
                self.start =  motorLimitDct[ cmd[1]][0]
                self.stop = motorLimitDct[ cmd[1]][1]
            slowFactor = 1
            if len( cmd) == 12:
                slowFactor = float( cmd[11])
            integTime = float( cmd[10])
            diff1 = math.fabs( motorLimitDct[ cmd[1]][1] - motorLimitDct[ cmd[1]][0])
            diff2 = math.fabs( motorLimitDct[ cmd[4]][1] - motorLimitDct[ cmd[4]][0])
            diff3 = math.fabs( motorLimitDct[ cmd[7]][1] - motorLimitDct[ cmd[7]][0])
            np1 = int( diff1/self.getVelocity( cmd[1])/integTime/slowFactor) + 10
            np2 = int( diff2/self.getVelocity( cmd[4])/integTime/slowFactor) + 10
            np3 = int( diff3/self.getVelocity( cmd[7])/integTime/slowFactor) + 10
            self.np = max( np1, np2, np3)
        #
        # hscan 0.0 1.0 5 0.1
        #
        elif cmd[0] == 'hscan':
            if HasyUtils.isDevice( 'e6cctrl_h'):
                self.motorNameList = [ 'e6cctrl_h']
            elif HasyUtils.isDevice( 'kozhue6cctrl_h'):
                self.motorNameList = [ 'kozhue6cctrl_h']
            self.np = int(cmd[3])
            self.start =  float(cmd[1])
            self.stop = float(cmd[2])
        #
        # kscan 0.0 1.0 5 0.1
        #
        elif cmd[0] == 'kscan':
            if HasyUtils.isDevice( 'e6cctrl_k'):
                self.motorNameList = [ 'e6cctrl_k']
            elif HasyUtils.isDevice( 'kozhue6cctrl_k'):
                self.motorNameList = [ 'kozhue6cctrl_k']
            self.np = int(cmd[3])
            self.start =  float(cmd[1])
            self.stop = float(cmd[2])
        #
        # lscan 0.0 1.0 5 0.1
        #
        elif cmd[0] == 'lscan':
            if HasyUtils.isDevice( 'e6cctrl_l'):
                self.motorNameList = [ 'e6cctrl_l']
            elif HasyUtils.isDevice( 'kozhue6cctrl_l'):
                self.motorNameList = [ 'kozhue6cctrl_l']
            self.np = int(cmd[3])
            self.start =  float(cmd[1])
            self.stop = float(cmd[2])
        #
        # hklscan 1.0 1.0 0.0 1.0 0.0 0.0 5 0.1
        #
        elif cmd[0] == 'hklscan':
            diffH = math.fabs(float( cmd[2]) - float( cmd[1]))
            diffK = math.fabs(float( cmd[4]) - float( cmd[3]))
            diffL = math.fabs(float( cmd[6]) - float( cmd[5]))
            if diffH == 0. and diffK == 0. and diffL == 0.:
                raise Exception( "pyspDoor.findScanLimits",
                                 "diffH == diffK == diffL == 0.")
                
            if HasyUtils.isDevice( 'e6cctrl_h'):
                self.motorNameList = [ 'e6cctrl_h', 'e6cctrl_k', 'e6cctrl_l']
            elif HasyUtils.isDevice( 'kozhue6cctrl_k'):
                self.motorNameList = [ 'kozhue6cctrl_h', 'kozhue6cctrl_k', 'kozhue6cctrl_l']
            else:
                raise Exception( "pyspDoor.findScanLimits",
                                 "failed to identify hkl motors")
            self.np = int(cmd[7])
            if diffH > diffK and diffH > diffL:
                self.motorIndex = 0
                pos = self.getPosition( self.motorNameList[ self.motorIndex])                
                self.start =  float(cmd[1])
                self.stop = float(cmd[2]) 
            elif diffK > diffH and diffK > diffL:
                self.motorIndex = 1
                pos = self.getPosition( self.motorNameList[ self.motorIndex])                
                self.start =  float(cmd[3])
                self.stop = float(cmd[4]) 
            elif diffL > diffH and diffL > diffK:
                self.motorIndex = 2
                pos = self.getPosition( self.motorNameList[ self.motorIndex])                
                self.start =  float(cmd[5])
                self.stop = float(cmd[6]) 
            elif diffH > 0.:
                self.motorIndex = 0
                pos = self.getPosition( self.motorNameList[ self.motorIndex])                
                self.start =  float(cmd[1])
                self.stop = float(cmd[2]) 
            elif diffK > 0.:
                self.motorIndex = 1
                pos = self.getPosition( self.motorNameList[ self.motorIndex])                
                self.start =  float(cmd[3])
                self.stop = float(cmd[4]) 
            else:
                self.motorIndex = 2
                pos = self.getPosition( self.motorNameList[ self.motorIndex])                
                self.start =  float(cmd[5])
                self.stop = float(cmd[6]) 
        #
        # mesh exp_dmy01 0 1 10 exp_dmy02 2 3 10 0.2 flagSShape
        # 
        elif cmd[0] == 'mesh':
            motorLimitDct = self.extractMotorLimitDct( dataRecord)
            self.start = float( cmd[2])
            self.stop =  float( cmd[3])
            self.np =    int( cmd[4])
            self.motorIndex = 0
            self.motorNameList = [ cmd[1]]
            self.isMesh = True
            self.meshYMotor = cmd[5]
            self.meshSweepCount = 1
            self.meshSweepCountTotal = int( cmd[8]) + 1
            if cmd[10].lower() == 'true':
                self.meshSShape = True
            else:
                self.meshSShape = False
            #
            # during mesh scans the data is plotted only within sweeps.
            # If a new sweep is started, the indexScan is reset. 
            # 
            if self.stop > self.start:
                self.meshGoingUp = True
            else:
                self.meshGoingUp = False
            #
            # self.indexScan controlls the counter GQEs during sweeps
            # self.indexMesh controlls the index of MeshScan
            #
            self.indexMesh = 0

            #self.sendHshQueue( { 'Scan': { 'name': 'MeshScan',
            #                          'xMin': float( cmd[2]), 
            #                          'xMax': float( cmd[3]), 
            #                          'yMin': float( cmd[6]), 
            #                          'yMax': float( cmd[7]), 
            #                          'symbolColor': 'red',
            #                          'symbolSize': 5,
            #                          'lineColor': 'None',
            #                          'symbol': '+',
            #                          'nPts': (int( cmd[4]) + 1)* (int( cmd[8]) + 1), 
            #                          'autoscaleX': False,
            #                          'autoscaleY': False}})

            self.sendHshQueue( { 'Image': { 'name': 'MeshImage',
                                      'xMin': float( cmd[2]), 
                                      'xMax': float( cmd[3]), 
                                      'yMin': float( cmd[6]), 
                                      'yMax': float( cmd[7]), 
                                      'width': (int( cmd[4]) + 1), 
                                      'height': (int( cmd[8]) + 1)}}) 
            #
            # the text should be present already during the first display
            # otherwise the textItem is missing
            #
            #self.sendHshQueue( { 'command': [ "setText MeshScan comment string \"Sweep: 1/%d\" x 0.05 y 0.95" % self.meshSweepCountTotal]})
        #
        # dmesh exp_dmy01 -1 1 10 exp_dmy02 -0.5 0.5 10 0.2 flagSShape
        # 
        elif cmd[0] == 'dmesh':
            motorLimitDct = self.extractMotorLimitDct( dataRecord)
            self.start = float( motorLimitDct[ cmd[1]][0])
            self.stop = float( motorLimitDct[ cmd[1]][1])
            self.np =    int( cmd[4])
            self.motorIndex = 0
            self.motorNameList = [ cmd[1]]
            self.isMesh = True
            self.meshYMotor = cmd[5]
            self.meshSweepCount = 1
            self.meshSweepCountTotal = int( cmd[8]) + 1
            if cmd[10].lower() == 'true':
                self.meshSShape = True
            else:
                self.meshSShape = False
            #
            # during mesh scans the data is plotted only within sweeps.
            # If a new sweep is started, the indexScan is reset. 
            # 
            if self.stop > self.start:
                self.meshGoingUp = True
            else:
                self.meshGoingUp = False
            #
            # self.indexScan controlls the counter GQEs during sweeps
            # self.indexMesh controlls the index of MeshScan
            #
            self.indexMesh = 0

            self.sendHshQueue( { 'Image': { 'name': 'MeshImage',
                                      'xMin': float( self.start), 
                                      'xMax': float( self.stop), 
                                      'yMin': float( motorLimitDct[ cmd[5]][0]), 
                                      'yMax': float( motorLimitDct[ cmd[5]][1]), 
                                      'width': (int( cmd[4]) + 1), 
                                      'height': (int( cmd[8]) + 1)}}) 
        #
        # a real fscan command line: 
        #   fscan 'x=[0,1,2,3,4],y=[10,11,12,13,14]' 0.1 "exp_dmy01" 'x' "exp_dmy02" 'y'
        # is reduced to 
        #   fscan np=5 0.1 exp_dmy01 exp_dmy02 
        # to save space
        #
        elif cmd[0] == 'fscan':
            self.motors = cmd[3:]
            self.np = int(cmd[1].split( '=')[1])
            self.start = 0
            self.stop =  100.
            self.motorIndex = 0
        else:
            raise Exception( "pyspDoor.findScanLimits",
                             "failed to identify scan command", 
                              dataRecord[1]['data']['title'])

        #print( "pyspDoor.findScanLimits cmd %s" % ( cmd))
        #print( "pyspDoor.findScanLimits start %g, stop %g np %d motors %s" % ( self.start, 
        #                                                                         self.stop,
        #                                                                         self.np, 
        #                                                                         str( self.motorNameList)))
        return True
                
    def prepareNewScan( self, dataRecord):
        """
        this function is called, if a data_desc record is found
        """

        #print( "\n---------- prepareNewScan")

        self.isFscan = False
        self.isMesh = False
        self.meshGoingUp = True 
        self.meshSweepCount = 1
        self.posOld = []
        
        self.handleDisplayCounters()

        #
        # scrollAreaFiles.setEnabled( False)
        # scrollAreaScans.setEnabled( False)
        #
        self.sendHshQueue( { 'newScan': True})

        self.indexScan = 1

        self.cleanupPysp()
        self.findCountersAndMCAs( dataRecord)

        self.prepareTitleAndSo( dataRecord)
        self.scanInfo = HasyUtils.dataRecordToScanInfo( dataRecord)
        #
        # the motorIndex allows us to adjust the plotting to eg.g a3scans
        #
        self.motorIndex = 0
        self.motorNameList = dataRecord[1]['data']['ref_moveables']
        #
        # get the environment for every scan
        #
        self.env = self.getEnvironment()
        if 'SignalCounter' in self.env:
            self.signalCounter = self.env[ 'SignalCounter']
        else: 
            global flagPrintOnce1
            self.signalCounter = None
            if not flagPrintOnce1: 
                print( "pyspDoor.prepareNewScan: no SignalCounter (MS environment) ") 
                flagPrintOnce1 = True

        self.unknownScanType = False
        try:
            self.findScanLimits( dataRecord)
        except Exception as e:
            self.unknownScanType = True
            if os.isatty(1):
                print( "prepareNewScan: caught exception: ", repr(e))
            return False

        #
        # sending the scanInfo makes GQE.Scan to create a new move() and
        # to prepare the motorsWidget of the GUI
        #
        self.scanInfo[ 'motorIndex'] = self.motorIndex
        
        self.sendHshQueue( { 'ScanInfo': self.scanInfo})
        
        #
        # we may have scans using the condition feature
        # 12.10.2020: '2.*self.np' -> '3.*self.np' because p09 repeated every point
        #
        npTemp = int( 3.*self.np)

        autox = False
        if self.isFscan: 
            autox = True

        self.scanNo += 1
        for elm in self.counterAliases:
            self.sendHshQueue( { 'Scan': { 'name': elm,
                                           'xMin': self.start,
                                           'xMax': self.stop,
                                           'lineColor': 'red',
                                           'nPts': npTemp,
                                           'motorNameList': self.motorNameList, 
                                           'autoscaleX': autox}})
        if self.useDisplayCounters: 
            for elm in list( self.displayCounterHsh.keys()):
                self.sendHshQueue( { 'Scan': { 'name': elm,
                                               'xMin': self.start,
                                               'xMax': self.stop,
                                               'lineColor': 'red',
                                               'nPts': npTemp,
                                               'motorNameList': self.motorNameList, 
                                                'autoscaleX': autox}})
            
        env = self.getEnvironment()
        if 'SignalCounter' in env:
            self.signalCounter = env['SignalCounter']
            self.signalInd = 0
        #    self.signalX = np.zeros( npTemp + 1)
        #    self.signalY = np.zeros( npTemp + 1)
        else:
            self.signalCounter = None

        self.sendHshQueue( {'command': ['display']})

        return True

    def analyseSignalObsolete( self):
        env = self.getEnvironment()
        for elm in ('ssa_status', 'ssa_reason', 'ssa_cms', 'ssa_fwhm'):            
            if elm in env:
                try:
                    self.macro_server.removeEnvironment( elm)
                except:
                    pass
        if 'SignalCounter' not in env:
            return

        dct = HasyUtils.ssa( self.signalX, self.signalY)
        if dct['status'] == 1:
            self.setEnvironment( 'ssa_status', 1) 
            self.setEnvironment( 'ssa_cms', dct['cms'])
            self.setEnvironment( 'ssa_fwhm', dct['fwhm'])
        else:
            self.setEnvironment( 'ssa_status', 0)
            self.setEnvironment( 'ssa_reason', dct['reason'])
            pass
        
        return

    def dumpDataRecord( self, msg, dataRecord):
        if self.serialnoDumped == self.serialno:
            return
        self.serialnoDumped = self.serialno
        out = open( '/online_dir/SardanaMonitor.log', 'a') 
        out.write( "--- %s \n" % HasyUtils.getDateTime())
        out.write( "reported only once per scan \n")
        out.write( "counter:   %s \n" % str( self.counterAliases))
        out.write( "mca:       %s \n" % str( self.mcaAliases))
        out.write( "msg:       %s \n" % msg)
        out.write( "ScanFile:  %s\n" % self.scanfile)
        out.write( "ScanDir:   %s\n" % self.scandir)
        out.write( "SerialNo:  %s\n" % self.serialno)
        out.write( "Filename:  %s\n" % self.filename)
        out.write( "StartTime: %s\n" % self.startTime)
        out.write( "Title:     %s\n" % self.title)
        out.write( repr( dataRecord) + "\n")
        out.close()
        if os.isatty(1):
            print( "--- %s \n" % HasyUtils.getDateTime())
            print( "reported only once per scan")
            print( "counter:   %s" % str( self.counterAliases))
            print( "mca:       %s" % str( self.mcaAliases))
            print( "msg:       %s" % msg)
            print( "ScanFile:  %s" % self.scanfile)
            print( "ScanDir:   %s" % self.scandir)
            print( "SerialNo:  %s" % self.serialno)
            print( "Filename:  %s" % self.filename)
            print( "StartTime: %s" % self.startTime)
            print( "Title:     %s" % self.title)
            print( "DataRecord: %s" % repr( dataRecord))

    def adjustLimitsObsolete( self, elm, pos):
        '''
        this function has been written because we want to avoid autoscale/x
        which gives bad results, if we scan in reverse direction
        '''
        #print( "adjustLimits BEGIN x_min %g, x_max %g " % ( self.counter_gqes[elm].attributeDouble( "x_min"), 
        #                                                       self.counter_gqes[elm].attributeDouble( "x_max")))
        # 
        return 
        x_tic = self.counter_gqes[elm].attributeDouble( "x_tic")
        count = 0
        while pos < self.counter_gqes[elm].attributeDouble( "x_min"):
            temp = self.counter_gqes[elm].attributeDouble( "x_min") - x_tic; 
            Spectra.gra_command( "set %s/x_min=%g" % (elm, temp))
            count += 1
            if count > 5:
                break
        count = 0
        while pos > self.counter_gqes[elm].attributeDouble( "x_max"):
            temp = self.counter_gqes[elm].attributeDouble( "x_max") + x_tic; 
            Spectra.gra_command( "set %s/x_max=%g" % (elm, temp))
            count += 1
            if count > 5:
                break
        #print( "adjustLimits DONE x_min %g, x_max %g " % ( self.counter_gqes[elm].attributeDouble( "x_min"), 
        #                                                       self.counter_gqes[elm].attributeDouble( "x_max")))
        return
        
    def recordDataReceived( self, s, t, v):

        #print( ">>> recordDataReceived")
        try:
            dataRecord = sms.BaseDoor.recordDataReceived( self, s, t, v)
        except Exception as e:
            print( "pyspDoor.recordDataReceived: caught exception")
            print( repr(e))
            return

        if dataRecord == None:
            return
        # +++
        #print( ">>> recordDataReceived ")
        #pp.pprint( dataRecord)
        # 

        #
        # it may happend that no 'type' is in the record, ignore
        #
        if 'type' not in dataRecord[1]:
            return
        #
        # a new scan 
        # 
        if dataRecord[1]['type'] == "data_desc":
            #+++
            #pp.pprint( dataRecord)
            
            self.prepareNewScan( dataRecord)
            self.flagIsBusy = True
            return

        if dataRecord[1]['type'] == "record_end":
            #
            # at the end: make sure the GQEs are sorted. 
            # This can be necessary for motors with jitter, e.g. piezos
            #
            #for elm in list( self.counter_gqes.keys()):
            #    Spectra.gra_command( "sort %s" % elm)
            self.flagIsBusy = False
            #
            # scrollAreaFiles.setEnabled( True)
            # scrollAreaScans.setEnabled( True)
            #
            self.sendHshQueue( { 'endScan': True})
            return
 
        # ('',
        # {u'data': {u'exp_mot65': 0.10000000000000001,
        #            u'haso107klx:10000/expchan/hasydgg2ctrl/1': 1.0,
        #            u'haso107klx:10000/expchan/hasysis3820ctrl/1': 116.0,
        #            u'haso107klx:10000/expchan/hasyvfcadcctrl/1': 4181.2631578947367,
        #            u'point_nb': 3,
        #            u'timestamp': 6.0719890594482422},
        #   u'macro_id': u'4452f8cc-ecfb-11e1-b0ca-3860778b70a3',
        #   u'type': u'record_data'})

        
        if not dataRecord[1]['type'] == "record_data":
            return 

        if not hasattr( self, 'unknownScanType'):
            return 

        if self.unknownScanType: 
            return 

        self.extractData( dataRecord)

        # +++ 
        #print( ">>> recordDataReceived DONE")
        return dataRecord

    def extractData( self, dataRecord): 
        #
        # find the position
        #
        pos = None
        if  self.motorNameList[ self.motorIndex] in dataRecord[1]['data']:
            pos = dataRecord[1]['data'][ self.motorNameList[ self.motorIndex]]
        else:
            #
            # this else clause is a workaround for the fact that the
            # diffractometer motors are usually called a la e6cctrl_l.
            # but for kozhu (p08) we have kozhue6cctrl_l 
            #
            found = False
            for key in dataRecord[1]['data']:
                if key.find( self.motorNameList[ self.motorIndex]) > 0:
                    self.motorNameList[ self.motorIndex] = key
                    pos = dataRecord[1]['data'][ self.motorNameList[ self.motorIndex]]
                    found = True
                    break
            if not found:
                raise Exception( "pyspDoor.extractData",
                                 "key error %s" % (self.motorNameList[ self.motorIndex]))
        if pos is None:
            raise Exception( "pyspDoor.recordDataReceived",
                             "key error %s" % (self.motorNameList[ self.motorIndex]))
        #
        # for mesh scans we also need the y-position
        #
        if self.isMesh:
            try:
                posY = dataRecord[1]['data'][ self.meshYMotor]
            except Exception as e:
                print( "pyspDoor.extractData: caught exception")
                print( repr( e))
                return

        #
        # the loop over the counters, extract the data
        #
        signal = None
        #
        # DataDict for the displayCounters
        #
        DataDict = {}
        for alias in self.counterAliases:
                
            if self.alias_dict[alias] not in dataRecord[1]['data']:
                self.dumpDataRecord( "Missing key %s" % (self.alias_dict[alias]), dataRecord)
                continue

            data  = dataRecord[1]['data'][self.alias_dict[alias]]
            if self.signalCounter is not None and alias.upper() == self.signalCounter.upper(): 
                signal = data
            #
            # the first point has np == 0, but 
            # we must not use np for the index of the data elements
            # because the first record may got lost (slow motor). so 
            # we use the internal counter indexScan
            # np  = dataRecord[1]['data'][ 'point_nb']
            #
            if os.isatty(1):
                np  = dataRecord[1]['data'][ 'point_nb']
                if np == 1 and  self.indexScan == 1:
                    print( "pyspDoor: missing data point no. %d" % (np - 1 ))
            
            if self.isMesh and self.indexScan > 1:
                posOld = pos
                if len( self.posOld) > 0: 
                    posOld = self.posOld[-1]
                #posOld = self.counter_gqes[ elm].getX( self.indexScan - 2)
                self.handleMeshScanIndices( dataRecord[1]['data'][ 'point_nb'], pos, posOld, posY)
                        
            #
            # 27.10.2015: for haspp09mag to handle <nodata>
            # 
            if data is None:
                self.dumpDataRecord( "data == None", dataRecord)
                self.sendHshQueue( { 'command': ['setY %s %d %s' % (alias, self.indexScan - 1, repr(0.))]})
                DataDict[ alias] = 0.
            else:
                if type( data) is list:
                    if len( data) == 1:
                        data = data[0]
                        DataDict[ alias] = data[0]
                    else:
                        self.dumpDataRecord( "unexpected data type %s (%s) is not float" % 
                                             (type( data), str( data)), dataRecord)
                        DataDict[ alias] = 0.
                        data = 0.
                        
                if not type( data) is float:
                    self.dumpDataRecord( "type(data) (%s) is not float" % str( data), dataRecord)
                    self.sendHshQueue( { 'command': ['setY %s %d %s' % (alias, self.indexScan - 1, repr(0.))]})
                    DataDict[ alias] = 0.
                else:
                    self.sendHshQueue( { 'command': ['setY %s %d %s' % (alias, self.indexScan - 1, repr(data))]})
                    DataDict[ alias] = data
                    pass

            DataDict[ 'x'] = pos
            self.sendHshQueue( { 'command': ['setX %s %d %s' % (alias, self.indexScan - 1, repr(pos))]})

        if self.useDisplayCounters: 
            for alias in list( self.displayCounterHsh.keys()): 
                cmd = "data = %s" % self.displayCounterHsh[ alias]
                try: 
                    exec( cmd)
                except Exception as e: 
                    print( "pyspDoor, evaluating \n  '%s'\n caused an error, data to 0" % cmd)
                    print( repr( e))
                    data = 0.
                self.sendHshQueue( { 'command': ['setX %s %d %s' % (alias, self.indexScan - 1, DataDict[ 'x'])]})
                self.sendHshQueue( { 'command': ['setY %s %d %s' % (alias, self.indexScan - 1, data)]})
            
        if self.isMesh:
            self.displayMeshScan( pos, posY, signal)

        self.posOld.append( pos)

        if len( self.mcaAliases) > 0:
            self.displayMCAs()
            
        self.sendHshQueue( { 'command': ['display']})

        self.indexScan += 1

    def sendHshQueue( self, hsh): 
        '''
        sends a dictionary to the pyspMonitor via queue(): 
        handled by: 
          /home/kracht/Misc/pySpectra/PySpectra/pyspMonitorClass.py
            cb_refreshMain( )
        '''
        #print( "pyspDoor.sendHshQueue: %s" % repr( hsh))
        #
        # the queue is emptied in 
        #   /home/kracht/Misc/pySpectra/PySpectra/pyspMonitorClass.py
        # from there a call is made to 
        #   PySpectra.toPyspLocal( hsh)
        #
        try:
            self.queue.put( hsh)
        except Exception as e:
            print( "queueSpectraDoor.sendHshQueue")
            print( "hsh %s" % repr( hsh))
            print( "exception %s" % repr( e))
            raise ValueError( "pyspDoor.sendHshQueue: something went wrong")

        return 

    def displayMeshScan( self, pos, posY, signal):
        #self.sendHshQueue( { 'command': ['setXY MeshScan %d %s %s' % (self.indexMesh, repr(pos), repr(posY))]})
        if signal is None:
            self.sendHshQueue( { 'command': ['setPixelWorld MeshImage %g %g 50.' % (pos, posY)]})
        else:
            self.sendHshQueue( { 'command': ['setPixelWorld MeshImage %g %g %g' % (pos, posY, signal)]})
        self.indexMesh += 1

    def handleMeshScanIndices( self, np, pos, posOld, posY):
        '''
        the question is whether we have to reset indexScan and signalInd: 
        this has to be done during mesh scans between the sweeps
                self.meshSShape = True
        '''
        if not self.meshSShape:
            if self.meshGoingUp and pos < posOld:
                self.indexScan = 1
                self.signalInd = 0
                self.meshSweepCount += 1
            elif not self.meshGoingUp and pos > posOld:
                self.indexScan = 1
                self.signalInd = 0
                self.meshSweepCount += 1
        else:
            #
            # for non-sShape scans: each turning point is repeated
            #
            if self.meshGoingUp:
                if self.almostEqual( pos, posOld):
                    self.meshGoingUp = False
                    self.indexScan = 1
                    self.signalInd = 0
                    self.meshSweepCount += 1
            else:
                if self.almostEqual( pos, posOld):
                    self.meshGoingUp = True
                    self.indexScan = 1
                    self.signalInd = 0
                    self.meshSweepCount += 1

        #self.sendHshQueue( { 'command': [ "setText MeshScan comment string \"Sweep: %d/%d\"" % \
        #                             ( self.meshSweepCount, self.meshSweepCountTotal)]})
        return 

    def almostEqual( self, pos, posOld):
        if math.fabs( pos - posOld) < 1.0E-6:
            return True
        else:
            return False
        
# 
import taurus
factory = taurus.Factory()
factory.registerDeviceClass( 'Door',  pyspDoor)
#
# returns a pyspDoor
#

