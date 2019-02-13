#!/usr/bin/env python
#
# files
#
import PyTango
import time, sys, os, math
import numpy
import __builtin__

try:
    import sardana.taurus.core.tango.sardana.macroserver as sms
except:
    try:
        import taurus.core.tango.sardana.macroserver as sms
    except:
        print "spectraDoor.py: failed to import macroserver.py"
        sys.exit(255) 

import Spectra
import pprint, math
import HasyUtils
import PySpectra as pysp

print "pyspSpectraDoor, imported"


pp = pprint.PrettyPrinter()
db = PyTango.Database()
sms.registerExtensions()

#
# this global variable is supposed to store 'self' of the spectraDoor instance
# to be called, e.g. from SardanaMonitor to send some data
#
spectraDoorInstance = None

class spectraDoor( sms.BaseDoor):

    def __init__( self, name, **kw):
        global spectraDoorInstance

        #print "spectraDoor.__init__()", name
        #pysp.setWsViewport( "DINA4L")
        self.counter_gqes = {}
        self.mcaAliases = []
        self.mcaProxies = []
        self.mcaArrays = []
        self.mcaFileName = "/tmp/temp_MCA_spectraDoor.fio"
        self.serialnoDumped = -1
        self.isMesh = False
        self.meshGoingUp = True 
        self.meshSweepCount = 1
        #
        # Mind: sometimes we loose records
        #
        self.call__init__( sms.BaseDoor, name, **kw)
        #
        # make sure that FlagDisplayAll exists
        #
        self.env = self.getEnvironment()
        if not self.env.has_key( 'FlagDisplayAll'):
            self.setEnvironment( 'FlagDisplayAll', 'True')
        spectraDoorInstance = self
        #
        # use this flag to determined whether we are currently inside a scan
        # that would mean that we cannot accept data from ZMQ
        #
        self.flagIsBusy = False
        #
        # this flag is for the CursorApp to decide whether a motor
        # may be moved
        #
        __builtin__.__dict__[ 'flagDataFromScan'] = True

    def receiveDct( self, hsh):
        #
        # putData
        #
        if self.flagIsBusy:
            return "spectraDoor: rejecting dct while scanning"
        #
        #
        #
        if 'CursorApp' in __builtin__.__dict__:
            __builtin__.__dict__['CursorApp'].close()
            del __builtin__.__dict__['CursorApp']
        #
        # this cleans the GQEs which have been created by a scan
        #
        self.cleanupSpectra()
        try: 
            __builtin__.__dict__[ 'flagDataFromScan'] = False
            Spectra.putData( hsh)
        except Exception, e:
            return "spectraDoor.receiveDct: caught %s" % repr( e)
        return "done"

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
        #   tango://haso113u.desy.de:10000/expchan/vc_ipetra/1 -> expchan/vc_ipetra/1
        #   ['tango:', '', 'haso113u.desy.de:10000', 'expchan', 'vc_ipetra', '1']
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
        # +++
        # print "get_alias: %s -> %s " % (argin, argout)
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


    def cleanupSpectra( self):
        """
        cleans the Spectra internal storage by deleting the 
        gqes from the dictionary, thereby calling the destructors
        """
        for k in self.counter_gqes.keys():
            del self.counter_gqes[k]

        pysp.delete()
        pysp.cls()

    def findNcolNrow( self, dataRecord):
        """
        nrow annd ncol depend on 
          - the number of counters
          - the number of MCAs
          - whether only one MCA is displayed (FlagDisplayAll == False)
        """

        nc = len(self.counterAliases) + len(self.mcaAliases)
        if nc == 0:
            raise Exception( "spectraDoor.findNcolNrow", "nothing selected for display")
        #
        # mesh scan: want to display also the mesh progress
        #
        if self.isMesh:
            nc += 1

        self.ncol = int(math.ceil(math.sqrt( nc)))
        self.env = self.getEnvironment()
        if len(self.mcaAliases) > 0:
            if not self.env[ 'FlagDisplayAll']:
                self.nrow = int(math.ceil((float(nc - len(self.mcaAliases))/float(self.ncol))))*2
            else:
                self.nrow = int(math.ceil((float(nc)/float(self.ncol))))
        else:
                self.nrow = int(math.ceil((float(nc)/float(self.ncol))))
        #print "spectraDoor.findNcolNrow: ncol", self.ncol, "nrow", self.nrow
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
            raise Exception( "spectraDoor.waitForFile", "%s is not created" % (filename))

        oldSize = 0
        count = 0
        while 1:
            if oldSize > 0 and oldSize == os.path.getsize(filename):
                break
            oldSize = os.path.getsize(filename)
            time.sleep( 0.02)
            if count > 10:
                raise Exception( "spectraDoor.waitForFile", "%s still not complete" % (filename))
            count += 1

        return status

    def writeFio( self):

        #if os.path.isfile( self.mcaFileName):
        #    os.remove( self.mcaFileName)

        out = open( self.mcaFileName, 'w')
        out.write("!\n")
        out.write("! created by spectraDoor.py\n")
        out.write("!\n")
        out.write("! comments\n")
        out.write("!\n")
        out.write("%c\n")
        out.write("!\n")
        out.write("!\n")
        out.write("! parameter\n")
        out.write("!\n")
        out.write("%p\n")
        out.write("!\n")
        out.write("! data\n")
        out.write("!\n")
        out.write("%d\n")
        for n in range( 0, len( self.mcaAliases)):
            out.write( " Col %d %s FLOAT \n" % ((n + 1), self.mcaAliases[n]))       
        #
        # find the longest MCA
        #
        max = 0
        for arr in self.mcaArrays:
            if len( arr) > max: 
                max = len( arr)
        for i in range( 0, max):
            rec = ""
            #
            # if a MCA is shorter than the longest append 0
            #
            for arr in self.mcaArrays:
                if len( arr) <= i:                    
                    rec = rec + " 0. "
                else:
                    rec = rec + " %g " % ( arr[i])
            rec = rec + "\n"
            out.write( rec)

        out.close()
        return

    def displayMCAs( self):
        self.mcaArrays = []
        for n in range( 0, len( self.mcaAliases)): 
            self.mcaArrays.append( self.mcaProxies[n].Value)

        self.writeFio()

        pysp.read( [self.mcaFileName, '-mca'])

        pysp.cls()

        #
        # do not delete the mca file here because another instance of the 
        # SardanaMonitor may be active
        #

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
        #print "spectraDoor>toBeDisplayed: not found", name
        return False

    def findCountersAndMCAs( self, dataRecord):
        """
        find the counter and MCA aliases and create
        the dictionary that translate them to device names
        """
        pysp.cls()
        pysp.delete()

        square = pysp.Scan( name = 'square', xMin = 0., xMax = 1.0, nPts = 21, autorangeX = True)
        for i in range( square.nPts): 
            square.setX( i, i/10.)
            square.setY( i, i*i/100.)
            pysp.display()
            time.sleep( 0.1)
        self.counterAliases = []
        self.mcaAliases = []
        self.mcaProxies = []
        self.alias_dict = {}
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
            # +++
            # !!! has to be after MCA dection because it is just the channel no. which
            # !!! tells that e.g. expchan/sis3302roi1dexp01ctrl/1 is a MCA
            # sis3302rois
            #
            elif elm.find( "expchan/sis3302roi") >= 0:
                self.counterAliases.append( alias)
            else:
                self.counterAliases.append( alias)
        # +++
        #print "alias_dict", self.alias_dict
        #print "counters", self.counterAliases
        #print "mcas", self.mcaAliases
        # 


    def prepareTitleAndSo( self, dataRecord):

        return 
        #
        # scanfile: tst.fio
        #
        if type(dataRecord[1]['data'][ 'scanfile']).__name__ == 'list':
            self.scanfile = dataRecord[1]['data'][ 'scanfile'][0]
        else:
            self.scanfile = dataRecord[1]['data'][ 'scanfile']
        if self.scanfile is None:
            raise Exception( "spectraDoor.prepareTitleAndSo", "ScanFile not defined")
        self.scandir = dataRecord[1]['data'][ 'scandir']
        if self.scandir is None:
            raise Exception( "spectraDoor.prepareTitleAndSo", "ScanDir not defined")
        self.serialno = dataRecord[1]['data'][ 'serialno']
        tpl = self.scanfile.rpartition('.')
        self.filename = "%s_%05d.%s" % (tpl[0], self.serialno, tpl[2])
        self.startTime = dataRecord[1]['data']['starttime']
        self.title = dataRecord[1]['data']['title']
        Spectra.setTitle( self.title)
        Spectra.setStartTime( self.startTime)
        Spectra.setFileName( self.filename)
        #
        # see symbolsToCheck = ['scan_dir', 'scan_id', 'scan_date', 'file_name', 'scan_cmd']
        # in /home/kracht/Spectra/Python2Spectra/gra_ifc.py
        #
        Spectra.gra_command( "file_name_ = %s" % self.filename)
        Spectra.gra_command( "scan_dir = %s" % self.scandir)
        Spectra.gra_command( "scan_id = %d" % self.serialno)
        Spectra.gra_command( "scan_date = \"%s\"" % self.startTime)
        Spectra.gra_command( "scan_cmd = \"%s\"" % self.title)

    def getPosition( self, name): 
        pos = None
        try:
            proxy = PyTango.DeviceProxy( str( name))
            while proxy.state() == PyTango.DevState.MOVING:
                time.sleep(0.1)
            pos = proxy.position
        except PyTango.DevFailed, e:
            PyTango.Except.print_exception( e)
            return 0
        return pos

    def getVelocity( self, name): 
        pos = None
        try:
            proxy = PyTango.DeviceProxy( str( name))
            velocity = proxy.velocity
        except PyTango.DevFailed, e:
            PyTango.Except.print_exception( e)
            return 0
        return velocity

    def extractMotorLimitDct( self, dataRecord): 
        #
        # the column_desc array can be found in prepareNewScan()
        #
        colArray = dataRecord[1]['data']['column_desc']
        argout = {}
        for hsh in colArray:
            if hsh.has_key( 'max_value') and hsh.has_key( 'min_value'):
                argout[hsh['name']] = [hsh['min_value'], hsh['max_value']]
        return argout

    def findScanLimits( self, dataRecord):
        '''
        look at the command line and find the start and stop values.
        these values should be chosen from a motor that is actually moved, 
        consider hkl scans where h stays at a constant position
        also set the self.motors array because ref_moveables is not correct
        '''
        #
        # get the scan limits from the title
        #
        cmd = dataRecord[1]['data']['title'].split()
        #
        # ascan exp_dmy01 0 1 10 0.2
        #
        if cmd[0] == 'ascan':
            self.start = float( cmd[2])
            self.stop =  float( cmd[3])
            self.np =    int( cmd[4])
            self.motorIndex = 0
            self.motors = [ cmd[1]]
        #
        # ascanc exp_dmy01 start stop integTime slowFactor
        #
        elif cmd[0] == 'ascanc':
            self.start = float( cmd[2])
            self.stop =  float( cmd[3])
            self.motorIndex = 0
            self.motors = [ cmd[1]]
            slowFactor = 1.
            if len( cmd) == 6:
                slowFactor = float( cmd[5])
            integTime = float( cmd[4])
            velocity = self.getVelocity( cmd[1])
            diff = math.fabs(self.stop - self.start)
            self.np = int( diff/velocity/integTime/slowFactor) + 10
            #print "+++spectraDoor: diff %g, velocity %g integTime %g np %d slowFactor %g " % ( diff, velocity, integTime, self.np, slowFactor)
            
        #
        # ascan_repeat exp_dmy01 0 1 10 0.2 2
        #
        elif cmd[0] == 'ascan_repeat':
            self.start = float( cmd[2])
            self.stop =  float( cmd[3])
            self.np =    int( cmd[4])*int(cmd[6]) + 1
            self.motorIndex = 0
            self.motors = [ cmd[1]]
        #
        # ascan_checkabs exp_dmy01 0 1 10 0.2
        #
        elif cmd[0] == 'ascan_checkabs' or \
                cmd[0] == 'ascan_absorber':
            self.start = float(cmd[2])
            self.stop = float( cmd[3])
            self.np = 2000 # we don't know beforehand how many points will be measured
            self.motorIndex = 0
            self.motors = [ cmd[1]]
        #
        # a2scan exp_dmy01 0 1 exp_dmy02 2 3 10 0.2
        #
        elif cmd[0] == 'a2scan':
            diff1 = math.fabs(float( cmd[3]) - float( cmd[2]))
            self.motors = [ cmd[1], cmd[4]]
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
            self.motors = [ cmd[1], cmd[4]]
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
            self.motors = [ cmd[1], cmd[4], cmd[7]]
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
            self.motors = [ cmd[1], cmd[4], cmd[7]]
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
            self.motors = [ cmd[1], cmd[4], cmd[7], cmd[10]]
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
            self.motors = [ cmd[1]]
            self.start = motorLimitDct[ cmd[1]][0]
            self.stop = motorLimitDct[ cmd[1]][1]

            self.np = int(cmd[4])
        #
        # dscanc eh1_dmy01 -0.1 0.1 integTime slowFactor
        #
        elif cmd[0] == 'dscanc':
            motorLimitDct = self.extractMotorLimitDct( dataRecord)
            self.motorIndex = 0
            self.motors = [ cmd[1]]
            self.start = motorLimitDct[ cmd[1]][0]
            self.stop = motorLimitDct[ cmd[1]][1]
            slowFactor = 1
            if len( cmd) == 6:
                slowFactor = float( cmd[5])
            integTime = float( cmd[4])
            velocity = self.getVelocity( cmd[1])
            diff = math.fabs(self.stop - self.start)
            self.np = int( diff/velocity/integTime/slowFactor) + 10
            #print "+++spectraDoor: diff %g, velocity %g integTime %g np %d slowFactor %g " % ( diff, velocity, integTime, self.np, slowFactor)
        #
        # dscan_repeat eh1_dmy01 -0.1 0.1 3 0.1 2
        #
        elif cmd[0] == 'dscan_repeat':
            motorLimitDct = self.extractMotorLimitDct( dataRecord)

            self.motorIndex = 0
            self.motors = [ cmd[1]]
            self.start = motorLimitDct[ cmd[1]][0]
            self.stop = motorLimitDct[ cmd[1]][1]
            self.motorIndex = 0
            self.motors = [ cmd[1]]
            #pos = self.getPosition( self.motors[ self.motorIndex])
            #self.start =  pos
            #self.stop = pos + float(cmd[3]) - float(cmd[2])
            self.np = int(cmd[4])*int(cmd[6]) + 1
        #
        # d2scan eh1_dmy01 -0.1 0.1 eh1_dmy02 -0.2 0.2 10 0.1 
        #
        elif cmd[0] == 'd2scan':
            motorLimitDct = self.extractMotorLimitDct( dataRecord)
            diff1 = math.fabs(float( cmd[3]) - float( cmd[2]))
            self.motors = [ cmd[1], cmd[4]]
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
            self.motors = [ cmd[1], cmd[4]]

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
            self.motors = [ cmd[1], cmd[4], cmd[7]]
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
            self.motors = [ cmd[1], cmd[4], cmd[7]]
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
                self.motors = [ 'e6cctrl_h']
            elif HasyUtils.isDevice( 'kozhue6cctrl_h'):
                self.motors = [ 'kozhue6cctrl_h']
            self.np = int(cmd[3])
            self.start =  float(cmd[1])
            self.stop = float(cmd[2])
        #
        # kscan 0.0 1.0 5 0.1
        #
        elif cmd[0] == 'kscan':
            if HasyUtils.isDevice( 'e6cctrl_k'):
                self.motors = [ 'e6cctrl_k']
            elif HasyUtils.isDevice( 'kozhue6cctrl_k'):
                self.motors = [ 'kozhue6cctrl_k']
            self.np = int(cmd[3])
            self.start =  float(cmd[1])
            self.stop = float(cmd[2])
        #
        # lscan 0.0 1.0 5 0.1
        #
        elif cmd[0] == 'lscan':
            if HasyUtils.isDevice( 'e6cctrl_l'):
                self.motors = [ 'e6cctrl_l']
            elif HasyUtils.isDevice( 'kozhue6cctrl_l'):
                self.motors = [ 'kozhue6cctrl_l']
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
                raise Exception( "spectraDoor.findScanLimits",
                                 "diffH == diffK == diffL == 0.")
                
            if HasyUtils.isDevice( 'e6cctrl_h'):
                self.motors = [ 'e6cctrl_h', 'e6cctrl_k', 'e6cctrl_l']
            elif HasyUtils.isDevice( 'kozhue6cctrl_k'):
                self.motors = [ 'kozhue6cctrl_h', 'kozhue6cctrl_k', 'kozhue6cctrl_l']
            else:
                raise Exception( "spectraDoor.findScanLimits",
                                 "failed to identify hkl motors")
            self.np = int(cmd[7])
            if diffH > diffK and diffH > diffL:
                self.motorIndex = 0
                pos = self.getPosition( self.motors[ self.motorIndex])                
                self.start =  float(cmd[1])
                self.stop = float(cmd[2]) 
            elif diffK > diffH and diffK > diffL:
                self.motorIndex = 1
                pos = self.getPosition( self.motors[ self.motorIndex])                
                self.start =  float(cmd[3])
                self.stop = float(cmd[4]) 
            elif diffL > diffH and diffL > diffK:
                self.motorIndex = 2
                pos = self.getPosition( self.motors[ self.motorIndex])                
                self.start =  float(cmd[5])
                self.stop = float(cmd[6]) 
            elif diffH > 0.:
                self.motorIndex = 0
                pos = self.getPosition( self.motors[ self.motorIndex])                
                self.start =  float(cmd[1])
                self.stop = float(cmd[2]) 
            elif diffK > 0.:
                self.motorIndex = 1
                pos = self.getPosition( self.motors[ self.motorIndex])                
                self.start =  float(cmd[3])
                self.stop = float(cmd[4]) 
            else:
                self.motorIndex = 2
                pos = self.getPosition( self.motors[ self.motorIndex])                
                self.start =  float(cmd[5])
                self.stop = float(cmd[6]) 
        #
        # mesh exp_dmy01 0 1 10 exp_dmy02 2 3 10 0.2 flagSShape
        # 
        elif cmd[0] == 'mesh':
            # +++
            motorLimitDct = self.extractMotorLimitDct( dataRecord)
            # +++
            self.start = float( cmd[2])
            self.stop =  float( cmd[3])
            self.np =    int( cmd[4])
            self.motorIndex = 0
            self.motors = [ cmd[1]]
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
            self.meshIndex = 0
            self.meshScan = Spectra.scanMesh( nameX = cmd[1], nameY = cmd[5], 
                                              startX = float( cmd[2]), stopX = float( cmd[3]), npX = int( cmd[4]) + 1,
                                              startY = float( cmd[6]), stopY = float( cmd[7]), npY = int( cmd[8]) + 1)
        #
        # dmesh exp_dmy01 -1 1 10 exp_dmy02 -0.5 0.5 10 0.2 flagSShape
        # +++
        elif cmd[0] == 'dmesh':
            motorLimitDct = self.extractMotorLimitDct( dataRecord)
            raise Exception( "spectraDoor.findScanLimits",
                             "dmesh!!!", 
                              dataRecord[1]['data']['title'])
        else:
            raise Exception( "spectraDoor.findScanLimits",
                             "failed to identify scan command", 
                              dataRecord[1]['data']['title'])

        #print "+++spectraDoor.findScanLimits cmd %s" % ( cmd)
        #print "+++spectraDoor.findScanLimits start %g, stop %g np %d motors %s" % ( self.start, 
        #                                                                         self.stop,
        #                                                                         self.np, 
        #                                                                         str( self.motors))
        return True
                
    def prepareNewScan( self, dataRecord):
        """
        this function is called, if a data_desc record is found
        """
        import __builtin__

        print "+++prepareNewScan"


        #
        #
        #
        if 'CursorApp' in __builtin__.__dict__:
            __builtin__.__dict__['CursorApp'].close()
            del __builtin__.__dict__['CursorApp']

        self.isMesh = False
        self.meshGoingUp = True 
        self.meshSweepCount = 1
        
        self.indexScan = 1
        # +++
        #print ">>> prepareNewScan"
        #pp.pprint( dataRecord)
        # +++
        #
        # ('',
        #  {u'data': {u'column_desc': [{u'dtype': u'int64',
        #                               u'label': u'#Pt No',
        #                               u'name': u'point_nb',
        #                               u'shape': []},
        #                              {u'dtype': u'float64',
        #                               u'instrument': None,
        #                               u'is_reference': True,
        #                               u'label': u'd1_vm02',
        #                               u'max_value': 5.0,
        #                               u'min_value': 4.0,
        #                               u'name': u'd1_vm02',
        #                               u'shape': []},
        #                              {u'conditioning': u'',
        #                               u'data_units': u'',
        #                               u'dtype': u'float64',
        #                               u'instrument': u'',
        #                               u'label': u'd1_t01',
        #                               u'name': u'haso107d1:10000/expchan/dgg2_d1_01/1',
        #                               u'normalization': 0,
        #                               u'output': True,
        #                               u'plot_axes': [],
        #                               u'plot_type': 0,
        #                               u'shape': [],
        #                               u'source': u'haso107d1:10000/expchan/dgg2_d1_01/1/Value'},
        #                              {u'conditioning': u'',
        #                               u'data_units': u'',
        #                               u'dtype': u'float64',
        #                               u'instrument': u'',
        #                               u'label': u'sig_gen',
        #                               u'name': u'haso107d1:10000/expchan/vc_sig_gen/1',
        #                               u'normalization': 0,
        #                               u'output': True,
        #                               u'plot_axes': [u'd1_vm02'],
        #                               u'plot_type': 1,
        #                               u'shape': [],
        #                               u'source': u'haso107d1:10000/expchan/vc_sig_gen/1/Value'},
        #                              {u'dtype': u'float64',
        #                               u'label': u'dt',
        #                               u'name': u'timestamp',
        #                               u'shape': []}],
        #             u'counters': [u'haso107d1:10000/expchan/vc_sig_gen/1'],
        #             u'estimatedtime': 1.1,
        #             u'ref_moveables': [u'd1_vm02'],
        #             u'scandir': u'/home/kracht/Misc/IVP/temp',
        #             u'scanfile': [u'tst.fio'],
        #             u'serialno': 5280,
        #             u'starttime': u'Mon Nov 20 09:30:39 2017',
        #             u'title': u'ascan d1_vm02 4.0 5.0 10 0.1',
        #             u'total_scan_intervals': 10},
        #   u'macro_id': u'16509eee-cdcd-11e7-b968-901b0e39aa90',
        #   u'type': u'data_desc'})
        #
        __builtin__.__dict__[ 'flagDataFromScan'] = True
        self.cleanupSpectra()
        self.findCountersAndMCAs( dataRecord)

        self.prepareTitleAndSo( dataRecord)
        self.scanInfo = HasyUtils.dataRecordToScanInfo( dataRecord)
        #
        # the motorIndex allows us to adjust the plotting to eg.g a3scans
        #
        self.motorIndex = 0
        self.motors = dataRecord[1]['data']['ref_moveables']

        self.unknownScanType = False
        try:
            self.findScanLimits( dataRecord)
        except Exception, e:
            self.unknownScanType = True
            if os.isatty(1):
                print "prepareNewScan: caught exception: ", repr(e)
            return False

        self.findNcolNrow( dataRecord)
        count = 1
        
        if self.isMesh:
            at_str = "(%d,%d,%d)" % (self.ncol, self.nrow, count)
            Spectra.gra_command( "set %s/at=%s" % (self.meshScan.gqeName, at_str))
            count += 1
        #
        # we may have scans using the condition feature
        #
        npTemp = 2*self.np

        for elm in self.counterAliases:
            at_str = "(%d,%d,%d)" % (self.ncol, self.nrow, count)
            
            self.counter_gqes[ elm] = pysp.Scan( name = elm, 
                                                 xMin = self.start, 
                                                 xMax = self.stop, 
                                                 color = 'red', 
                                                 nPts = npTemp,
                                                 autorangeX = True)

            print "+++ pyspSpectraDoor, display"
            pysp.display()
            pysp.processEvents()
            time.sleep(1)
            print "+++ pyspSpectraDoor, display, and again"
            pysp.display()
            pysp.processEvents()
            time.sleep(1)
            #+++ self.counter_gqes[elm].currentIndex = 0
            count += 1
        #+++
        #print ">>> prepareNewScan DONE "

        env = self.getEnvironment()
        if env.has_key( 'SignalCounter'):
            self.signalCounter = env['SignalCounter']
            self.signalInd = 0
            self.signalX = numpy.zeros( npTemp + 1)
            self.signalY = numpy.zeros( npTemp + 1)
        else:
            self.signalCounter = None
        return True

    def analyseSignal( self):
        env = self.getEnvironment()
        for elm in ('ssa_status', 'ssa_reason', 'ssa_cms', 'ssa_fwhm'):            
            if env.has_key( elm):
                try:
                    self.macro_server.removeEnvironment( elm)
                except:
                    pass
        if not env.has_key( 'SignalCounter'):
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
            print "--- %s \n" % HasyUtils.getDateTime()
            print "reported only once per scan"
            print "counter:   %s" % str( self.counterAliases)
            print "mca:       %s" % str( self.mcaAliases)
            print "msg:       %s" % msg
            print "ScanFile:  %s" % self.scanfile
            print "ScanDir:   %s" % self.scandir
            print "SerialNo:  %s" % self.serialno
            print "Filename:  %s" % self.filename
            print "StartTime: %s" % self.startTime
            print "Title:     %s" % self.title
            print "DataRecord: ", repr( dataRecord)

    def adjustLimits( self, elm, pos):
        '''
        this function has been written because we want to avoid autoscale/x
        which gives bad results, if we scan in reverse direction
        '''
        #print "+++ adjustLimits BEGIN x_min %g, x_max %g " % ( self.counter_gqes[elm].attributeDouble( "x_min"), 
        #                                                       self.counter_gqes[elm].attributeDouble( "x_max")) 
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
        #print "+++ adjustLimits DONE x_min %g, x_max %g " % ( self.counter_gqes[elm].attributeDouble( "x_min"), 
        #                                                       self.counter_gqes[elm].attributeDouble( "x_max")) 
        return
        
    def recordDataReceived( self, s, t, v):

        #print "+++recordDataReceived"
        try:
            dataRecord = sms.BaseDoor.recordDataReceived( self, s, t, v)
        except Exception, e:
            print "spectraDoor.recordDataReceived: caught exception"
            print e
            return

        if dataRecord == None:
            return
        # +++
        #print ">>> recordDataReceived "
        #pp.pprint( dataRecord)
        # +++

        #
        # it may happend that no 'type' is in the record, ignore
        #
        if not dataRecord[1].has_key( 'type'):
            return
        #
        # a new scan 
        # 
        if dataRecord[1]['type'] == "data_desc":
            #+++
            #pp.pprint( dataRecord)
            #+++
            self.prepareNewScan( dataRecord)
            self.flagIsBusy = True
            return

        if dataRecord[1]['type'] == "record_end":
            #
            # at the end: make sure the GQEs are sorted. 
            # This can be necessary for motors with jitter, e.g. piezos
            #
            #for elm in self.counter_gqes.keys():
            #    Spectra.gra_command( "sort %s" % elm)
            self.flagIsBusy = False
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
        #print ">>> recordDataReceived DONE"
        return dataRecord

    def extractData( self, dataRecord): 
        #
        # find the position
        #
        pos = None
        if  dataRecord[1]['data'].has_key( self.motors[ self.motorIndex]):
            pos = dataRecord[1]['data'][ self.motors[ self.motorIndex]]
        else:
            #
            # this else clause is a workaround for the fact that the
            # diffractometer motors are usually called a la e6cctrl_l.
            # but for kozhu (p08) we have kozhue6cctrl_l 
            #
            found = False
            for key in dataRecord[1]['data']:
                if key.find( self.motors[ self.motorIndex]) > 0:
                    self.motors[ self.motorIndex] = key
                    pos = dataRecord[1]['data'][ self.motors[ self.motorIndex]]
                    found = True
                    break
            if not found:
                raise Exception( "spectraDoor.extractData",
                                 "key error %s" % (self.motors[ self.motorIndex]))
        if pos is None:
            raise Exception( "spectraDoor.recordDataReceived",
                             "key error %s" % (self.motors[ self.motorIndex]))
        #
        # for mesh scans we also need the y-position
        #
        if self.isMesh:
            try:
                posY = dataRecord[1]['data'][ self.meshYMotor]
            except Exception, e:
                print "spectraDoor.extractData: caught exception"
                print e
                return

        #
        # the loop over the counters, extract the data
        #
        for elm in self.counter_gqes.keys():
            if not dataRecord[1]['data'].has_key( self.alias_dict[elm]):
                self.dumpDataRecord( "Missing key %s" % (self.alias_dict[elm]), dataRecord)
                continue

            data  = dataRecord[1]['data'][self.alias_dict[elm]]
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
                    print "spectraDoor: missing data point no. ", np - 1 
            
            if self.isMesh and self.indexScan > 1:
                posOld = self.counter_gqes[ elm].getX( self.indexScan - 2)
                self.handleMeshScanIndices( dataRecord[1]['data'][ 'point_nb'], pos, posOld, posY)
                        
            #
            # 27.10.2015: for haspp09mag to handle <nodata>
            # 
            if data is None:
                self.dumpDataRecord( "data == None", dataRecord)
                self.counter_gqes[ elm].setY( self.indexScan - 1, 0.)
            else:
                if type( data) is list:
                    if len( data) == 1:
                        data = data[0]
                    else:
                        self.dumpDataRecord( "unexpected data type %s (%s) is not float" % (type( data), str( data)), dataRecord)
                        data = 0.
                        
                if not type( data) is float:
                    self.dumpDataRecord( "type(data) (%s) is not float" % str( data), dataRecord)
                    #+++self.counter_gqes[ elm].setY( self.indexScan - 1, 0.)
                else:
                    #+++self.counter_gqes[ elm].setY( self.indexScan - 1, data)
                    pass
            
            #+++self.counter_gqes[ elm].setX( self.indexScan - 1, pos)
            #
            # 20.11.2017
            #   test, whether pos is within the windows limits.
            #   it may be outside e.g. for piezo motors that have a jitter.
            #   in this case we make a careful adjustment of the limits - 
            #   no autoscale/x because the scan may be in revers direction
            #
            #if pos < self.counter_gqes[elm].attributeDouble( "x_min") or \
            #   pos > self.counter_gqes[elm].attributeDouble( "x_max"):
            #    self.adjustLimits( elm, pos)
            #if elm == self.signalCounter:
            #    self.signalX[ self.signalInd] = pos
            #    self.signalY[ self.signalInd] = data
            #    self.signalInd += 1
            #    self.analyseSignal()

            #Spectra.gra_command( "autoscale/y %s" % elm)

        if self.isMesh:
            self.displayMeshScan( pos, posY)

        if len( self.mcaAliases) > 0:
            self.displayMCAs()

        self.indexScan += 1

        pysp.display()
        pysp.processEvents()

    def displayMeshScan( self, pos, posY):
        self.meshScan.setX( self.meshIndex, pos)
        self.meshScan.setY( self.meshIndex, posY)
        self.meshIndex += 1

    def handleMeshScanIndices( self, np, pos, posOld, posY):
        '''
        the question is whether we have to reset indexScan and signalInd: 
        this has to be done during mesh scans between the sweeps
                self.meshSShape = True
        '''
        return 
        if not self.meshSShape:
            if self.meshGoingUp and pos < posOld:
                self.indexScan = 1
                self.signalInd = 0
                self.meshSweepCount += 1
                Spectra.gra_command( "set %s.1/string=\"SweepCount: %d/%d\"" % (self.meshScan.gqeName, 
                                                                              self.meshSweepCount, self.meshSweepCountTotal))
                #print "+++spectraDoor.handleMeshScanIndices-1: np %d  pos %g, posOld %g" % (np, pos, posOld)
            elif not self.meshGoingUp and pos > posOld:
                self.indexScan = 1
                self.signalInd = 0
                self.meshSweepCount += 1
                Spectra.gra_command( "set %s.1/string=\"SweepCount: %d/%d\"" % (self.meshScan.gqeName, self.meshSweepCount, self.meshSweepCountTotal))
                #print "+++spectraDoor.handleMeshScanIndices-2: np %d  pos %g, posOld %g" % (np, pos, posOld)
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
                    Spectra.gra_command( "set %s.1/string=\"SweepCount: %d/%d\"" % (self.meshScan.gqeName, self.meshSweepCount, self.meshSweepCountTotal))
                    #+++print "spectraDoor.handleMeshScanIndices-3: np %d  pos %g, posOld %g" % (np, pos, posOld)
            else:
                if self.almostEqual( pos, posOld):
                    self.meshGoingUp = True
                    self.indexScan = 1
                    self.signalInd = 0
                    self.meshSweepCount += 1
                    Spectra.gra_command( "set %s.1/string=\"SweepCount: %d/%d\"" % (self.meshScan.gqeName, self.meshSweepCount, self.meshSweepCountTotal))
                    #+++print "spectraDoor.handleMeshScanIndices-4: np %d  pos %g, posOld %g" % (np, pos, posOld)

    def almostEqual( self, pos, posOld):
        if math.fabs( pos - posOld) < 1.0E-6:
            return True
        else:
            return False
        
# 
import taurus
factory = taurus.Factory()

factory.registerDeviceClass( 'Door',  spectraDoor)
#
# returns a spectraDoor
#

