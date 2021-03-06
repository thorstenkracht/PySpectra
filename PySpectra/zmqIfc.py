#!/usr/bin/env python
'''
this module handles the access from remote:
  - this caan be a client using toPyspMonitor() and ZMQ
  - or pyspDoor via a queue
  
Further documentation

  HasyUtils.toPyspMonitor?
  PySpectra.toPyspLocal?
  HasyUtils.isPyspMonitorAlive?
---
'''
try:
    import PyTango
except: 
    pass
import time
import PySpectra 
import PySpectra.utils as utils
import numpy as np
import HasyUtils

def toPyspLocal( hsh): 
    '''
    toPyspLocal executes dictionaries which are received 
      - from toPyspMonitor()
      - from a Queue, from pyspDoor
      - from an application directly, maybe to simulate the toPyspMonitor interface

       Command, see PySpectra.ipython.ifc?
         {'command': ['delete']}
           delete all internal data

         {'command': ['cls']}
           clear the screen

         {'command': ['delete', 'cls']}
           deletes all internal data and clears the screen

         {'command': ['display']}
           display all GQEs

         { 'command': ['setArrowCurrent sig_gen position 1.234']}
         { 'command': ['setArrowCurrent sig_gen show']}
         { 'command': ['setArrowCurrent sig_gen hide']}
           handle the arrow pointing to the current position. sig_gen is
           the Scan containing data from the SignalCounter (MS env. variable)

         { 'command': ['setArrowSetPoint sig_gen position 1.234']}
         { 'command': ['setArrowSetPoint sig_gen show']}
         { 'command': ['setArrowSetPoint sig_gen hide']}
           handle the arrow pointing to the setpoint

         { 'command': ['setArrowMisc sig_gen position 1.234']}
         { 'command': ['setArrowMisc sig_gen show']}
         { 'command': ['setArrowMisc sig_gen hide']}
           handle the arrow pointing to a position defined e.g. by mvsa

         {'command': [u'setTitle "ascan exp_dmy01 0.0 1.0 3 0.2"']}
           set the title for the whole widget
         {'command': [u'setComment "tst_01366.fio, Wed Dec 18 10:02:09 2019"']}
           set the comment for the whole widget

         {'spock': [ 'umv eh_mot66 51']}

       Misc:
         {'isAlive': True}
           return values:
             { 'result': 'done'}
             { 'result': 'notAlive'}

         {'getDoorState': True}
           returns:
             { 'result': 'ON'}

       Scan, see PySpectra.Scan?
         {'Scan': {'name': 'eh_c01', 'xMax': 1.0, 'autoscaleX': False, 'lineColor': 'red', 'xMin': 0.0, 'nPts': 6}}
           create an empty scan. Notice, the inner dictionary is passed to the Scan constructor

         {'Scan': {'yMax': 2.0, 'symbol': '+', 'autoscaleY': False, 'autoscaleX': False, 
                   'xMax': 1.0, 'nPts': 24, 'symbolColor': 'red', 'name': 'MeshScan', 
                   'symbolSize': 5, 'lineColor': 'None', 'xMin': 0.0, 'yMin': 1.0}}
           create an empty scan setting more attributes.

         {'Scan': {'name': 'eh_mca01', 'flagMCA': True, 'lineColor': 'blue', 
                   'y': array([  0., ..., 35.,  30.]), 
                   'x': array([  0.0, ..., 2.047e+03])}}
           create an MCA scan, which is re-used

         {'command': ['setY eh_c01 0 71.41']}
           set a y-value of eh_c01, index 0

         {'command': ['setX eh_c01 0 0.0']}
           set a x-value of eh_c01, index 0

         {'command': ['setXY MeshScan 0 0.0 1.0']}
           set the x- and y-value by a single call, index is 0

         {'putData': { 'columns': [{'data': [0.0, ..., 0.96], 'name': 'eh_mot01'}, 
                                  {'data': [0.39623, ... 0.01250], 'name': 'eh_c01'}, 
                                  {'showGridY': False, 'symbolColor': 'blue', 'showGridX': False, 
                                   'name': 'eh_c02', 'yLog': False, 'symbol': '+', 
                                   'data': [0.1853, ... 0.611], 
                                   'xLog': False, 'symbolSize': 5}], 
                      'title': 'a title', 
                      'comment': 'a comment'}}
           The data are sent as a list of dictionaries containing columns. The first column 
           is the common x-axis. All columns have to have the same length. 
           In this example, the Scans eh_c01 and eh_c02 are created. The common x-axis is given by eh_mot01

         { 'putData': {'gqes': [ {'x': x, 'y': tan, 'name': 'tan'},
                                 {'x': x, 'y': cos, 'name': 'cos'},
                                 {'x': x, 'y': sin, 'name': 'sin', 
                                  'showGridY': False, 'symbolColor': 'blue', 'showGridX': True, 
                                  'yLog': False, 'symbol': '+', 
                                  'xLog': False, 'symbolSize':5}],
                       'title': 'a title', 
                       'comment': 'a comment'}}
           The data are sent as a list of dictionaries containg the x- and y-data and other
           parameters describing the Scans.

       Image, see PySPectra.PySpectra.Image?
         {'Image': {'name': 'MandelBrot', 
                    'height': 5, 'width': 5, 
                    'xMax': -0.5, 'xMin': -2.0, 
                    'yMin': 0, 'yMax': 1.5}}
           create an empty image

         { 'Image': { 'name': "MandelBrot", 'data': data, 
                      'xMin': xmin, 'xMax': xmax, 
                      'yMin': ymin, 'yMax': ymax}})
           pass the entire image data

         { 'putData': { 'images': [{'name': "Mandelbrot", 'data': data,
                                    'xMin': xmin, 'xMax': xmax, 
                                    'yMin': ymin, 'yMax': ymax}]}}
           data is a numpy array, e.g.: data = np.ndarray( (width, height), np.float64)

         {'command': ['setPixelImage Mandelbrot 1 3 200']}
           set a pixel value. the position is specified by indices

         {'command': ['setPixelWorld Mandelbrot 0.5 1.5 200']}
           set a pixel value. the position is specified by world coordinate

         Text
         {'command': ['setText MeshScan comment string "Sweep: 1/4" x 0.05 y 0.95']}
           create a text GQE for the scan MeshScan, the name of the text is comment

       Retrieve data:
         {'getData': True}
           {'getData': {'EH_C02': {'y': [0.3183, ... 0.6510], 'x': [0.0, ... 0.959]}, 
                        'EH_C01': {'y': [0.0234, ... 0.4918], 'x': [0.0, ... 0.959]}}, 
            'result': 'done'}

    '''
    #print( "zmqIfc.toPyspLocal: %s" % repr( hsh))
    argout = {}
    #
    # command
    #
    if 'command' in hsh:
        argout[ 'result'] = _execCommand( hsh)
    #
    # spock
    #
    elif 'spock' in hsh:
        argout[ 'result'] = _execSpockCommand( hsh)
    #
    # doorState
    #
    elif 'getDoorState' in hsh:
        argout[ 'result'] = _getDoorState()
    #
    # putData
    #
    elif 'putData' in hsh:
        argout[ 'result'] = _putData( hsh[ 'putData'])
    #
    # getData
    #
    elif 'getData' in hsh:
        try:
            argout[ 'getData'] = PySpectra.getData()
            argout[ 'result'] = 'done'
        except Exception as e:
            argout[ 'getData'] = {}
            argout[ 'result'] = "zmqIfc.toPyspLocal: error, %s" % repr( e)
    #
    # the 'isAlive' question comes from a toPyspMonitor() client, not from the door
    #
    elif 'isAlive' in hsh:
        argout[ 'result'] = 'done'
    #
    # image
    #
    elif 'Image' in hsh:
        try: 
            #
            # '**hsh': unpacked dictionary
            #
            PySpectra.Image( **hsh[ 'Image']) 
            argout[ 'result'] = 'done'
        except Exception as e:
            argout[ 'result'] = "zmqIfc.toPyspLocal: error, %s" % repr( e)
    #
    # Scan
    #
    elif 'Scan' in hsh:
        #
        if 'flagMCA' in hsh[ 'Scan'] and hsh[ 'Scan'][ 'flagMCA'] is True:
            _storeMCAData( hsh[ 'Scan'])
            argout[ 'result'] = 'done'; 
        else:
            try: 
                #
                # '**hsh' unpacked dictionary
                #
                PySpectra.Scan( **hsh[ 'Scan']) 
                argout[ 'result'] = 'done'
            except Exception as e:
                argout[ 'result'] = "zmqIfc.toPyspLocal: error, %s" % repr( e)
    #
    # ... else
    #
    else:
        argout[ 'result'] = "zmqIfc.toPyspLocal: error, failed to identify %s" % repr( hsh)
    #
    # getDoorState is answered with a value, not with 'done'
    #
    if not 'getDoorState' in hsh: 
        if argout[ 'result'].upper() != "DONE":
            print( "zmqIfc.toPyspLocal: no 'DONE', instead received '%s' " % argout[ 'result'])
            print( "zmqIfc.toPyspLocal: input: %s " % repr( hsh))

    #print( "zmqIfc.toPyspLocal: return %s" % repr( argout))
    return argout

def _storeMCAData( hsh): 
    '''
    handle MCA data
      - create new Scan, if it does not exist.
      - otherwise re-use it.

    for the moment we assume that the whole sequence involving
    this function starts at pyspDoor. Therefore we treat the 
    case of a non-empty dictionary very relaxed. Just complain
    and let TK fix it.
    '''
    scan = PySpectra.getGqe( hsh[ 'name']) 
    if scan is None: 
        PySpectra.Scan( **hsh)
        return True
    
    del hsh[ 'name'] 
    del hsh[ 'flagMCA'] 

    if 'y' not in hsh: 
        raise ValueError( "zmqIfc._storeMCAData: no data, 'y' is missing")

    if len( hsh[ 'y']) != len( scan.y): 
        raise ValueError( "zmqIfc._storeMCAData: len( scan.y) %d, len( hsh[ 'y']) %d" % 
                          (len( scan.y), len( hsh[ 'y'])))

    scan.y = hsh[ 'y'][:]
    del hsh[ 'y']
    #
    # trigger a re-display
    #
    scan.lastIndex = -1

    if 'x' not in hsh: 
        return True
    
    if len( hsh[ 'x']) != len( scan.x): 
        raise ValueError( "zmqIfc._storeMCAData: len( scan.x) %d, len( hsh[ 'x']) %d" % 
                          (len( scan.x), len( hsh[ 'x'])))

    scan.x = hsh[ 'x'][:]
    del hsh[ 'x']

    if 'lineColor' in hsh: 
        scan.lineColor = hsh[ 'lineColor']
        del hsh[ 'lineColor']

    if hsh:
        print( "zmqIfc._storeMCAData: dct not empty %s" % str( hsh))

    return 


def toPyspMonitorNowInHasyUtils( hsh, node = None, testAlive = False):
    '''
    Send a dictionary to the pyspMonitor process via ZMQ. 
    pyspMonitor processes the dictionary by calling PySpectra.toPyspLocal()

    testAlive == True: 
        it is checked whether a pyspMonitor process responds to 
        the { 'isAlive': True} dictionary. 
          if not, pyspMonitor is launched

    Example: 
      if not PySpectra.isPyspMonitorAlive():
          return False
      ret = HasyUtils.toPyspMonitor( {'command': ['delete', 'cls', 'create s1', 'display']})
      if ret[ 'result'] != 'done': 
          print( "error" % ret[ 'result'])

    ---
    '''
    import zmq, json, socket

    #
    # testAlive == True reduces the rate from 625 Hz to 360 Hz
    #
    if testAlive: 
        (status, wasLaunched) = assertPyspMonitorRunning()
        if not status: 
            raise ValueError( "zmqIfc.toPyspMonitor: trouble with pyspMonitor")

    if node is None:
        node = socket.gethostbyname( socket.getfqdn())

    context = zmq.Context()
    sckt = context.socket(zmq.REQ)
    #
    # prevent context.term() from hanging, if the message
    # is not consumed by a receiver.
    #
    sckt.setsockopt(zmq.LINGER, 1)
    try:
        sckt.connect('tcp://%s:7779' % node)
    except Exception as e:
        sckt.close()
        print( "zmqIfc.toPyspMonitor: connected failed %s" % repr( e))
        return { 'result': "zmqIfc.toPyspMonitor: failed to connect to %s" % node}

    # print( "zmqIfc.toPyspMonitor: connected to tcp://%s:7779" % node)
    
    HasyUtils.replaceNumpyArrays( hsh)

    #print( "zmqIfc.toPyspMonitor: sending %s" % hsh)

    hshEnc = json.dumps( hsh)
    try:
        res = sckt.send( hshEnc)
    except Exception as e:
        sckt.close()
        return { 'result': "zmqIfc.toPyspMonitor: exception by send() %s" % repr(e)}
    #
    # PyspMonitor receives the Dct, processes it and then
    # returns the message. This may take some time. To pass
    # 4 arrays, each with 10000 pts takes 2.3s
    #
    if 'isAlive' in hsh:
        lst = zmq.select([sckt], [], [], 0.5)
        if sckt in lst[0]:
            hshEnc = sckt.recv() 
            sckt.close()
            context.term()
            argout = json.loads( hshEnc)
        else: 
            sckt.close()
            context.term()
            argout = { 'result': 'notAlive'}
    else:
        lst = zmq.select([sckt], [], [], 3.0)
        if sckt in lst[0]:
            hshEnc = sckt.recv() 
            sckt.close()
            context.term()
            argout = json.loads( hshEnc) 

        else: 
            sckt.close()
            context.term()
            argout = { 'result': 'zmqIfc.toPyspMonitor: communication time-out'}

    #print( "zmqIfc.toPyspMonitor: received %s" % argout)
    return argout

def isPyspMonitorAliveNowInHasyUtils( node = None):
    '''
    returns True, if there is a pyspMonitor responding to the isAlive prompt
    '''
    hsh = HasyUtils.toPyspMonitor( { 'isAlive': True}, node = node, testAlive = False)
    if hsh[ 'result'] == 'notAlive':
        return False
    else:
        return True

def _putData( hsh):
    '''
    a plot is created based on a dictionary 
    the use case: some data are sent pyspMonitor
    '''

    argout = 'n.n.'
    if 'title' in hsh:
        PySpectra.setTitle( hsh[ 'title'])

    try: 
        if 'columns' in hsh:
            PySpectra.delete()
            PySpectra.cls()
            argout = utils.createScansByColumns( hsh)
        elif 'gqes' in hsh:
            PySpectra.delete()
            PySpectra.cls()
            try: 
                argout = utils.createScansByGqes( hsh)
            except Exception as e: 
                print( "zmqIfc: %s" % repr( e))
        elif 'images' in hsh:
            for h in hsh[ 'images']: 
                PySpectra.Image( **h)
            argout = "done"
        else:
            raise Exception( "zmqIfc._putData", "expecting 'columns', 'gqes'")
    except Exception as e: 
        argout = "zmqIfc._putData: %s" % repr( e)

    return argout

def _execCommand( hsh): 
    '''
    passes PySpectra commands to pysp.ipython.ifc.command()

    called from 
      - toPyspLocal()
    
    List of commands: 
      hsh = { 'command': ['cls', 'display']}
    Single commands
    hsh = { 'command': 'display'}
    '''
    import PySpectra.ipython.ifc as ifc
    argout = "n.n."
    if type( hsh[ 'command']) == list:
        for cmd in hsh[ 'command']: 
            ret = ifc.command( cmd)
            if ret != 'done':
                return "zmqIfc._execCommand: '%s' was answered by %s" % ( cmd, ret)
        return "done"

    argout = ifc.command( hsh[ 'command'])
    return argout

def _execSpockCommand( hsh): 
    '''
    sends spock commands to a door

    called from toPyspLocal()
    
    It is always a single command because the macroserver
    will be busy when executing the first command and
    we don't want to wait for completion

      hsh = { 'spock': 'mv eh_mot66 51'}
    '''
    import PySpectra.tangoIfc as tangoIfc

    if type( hsh[ 'spock']) == list:
        argout = "zmqIfc.execSpockCommand: not expecting a list"
        return argout

    argout = "done"
    try: 
        door = PySpectra.InfoBlock.getDoorProxy()
        lst = hsh[ 'spock'].split( " ")
        door.RunMacro( lst)
    except Exception as e: 
        argout = "zmqIfc.execSpockCommand: %s" % repr( e)
    return argout

def _getDoorState():
    """
    the client starts a macro by issuing a spock command, 
    then senses the state of the door to see, if it's done
    """
    import PySpectra.tangoIfc as tangoIfc

    door = PySpectra.InfoBlock.getDoorProxy()
    argout = "%s" % repr( door.state())
    return argout.split( '.')[-1]

#
# I don't know whether the following function is really needed - 
# syntactical sugar perhaps
#
def assertPyspMonitorRunning(): 
    """
    returns (status, wasLaunched)

    it tests whether the pyspMonitor responds to isAlive. 
    If so, the function return rather quickly.

    Otherwise we call assertProcessRunning() which may take some time
    """
    res = HasyUtils.toPyspMonitor( { 'isAlive': True}, testAlive = False) 
    if res[ 'result'] == 'done': 
        return( True, False)
    else: 
        #
        # even if the pyspMonitor does not reply to 'isAlive', 
        # the process may exist
        #
        if utils.findProcessByName( "/usr/bin/pyspMonitor.py"):
            utils.killProcess( "/usr/bin/pyspMonitor.py")
        if utils.findProcessByName( "/usr/bin/pyspMonitor3.py"):
            utils.killProcess( "/usr/bin/pyspMonitor3.py")
        
        if HasyUtils.getPythonVersionSardana() == '/usr/bin/python': 
            return utils.assertProcessRunning( "/usr/bin/pyspMonitor.py")
        else: 
            return utils.assertProcessRunning( "/usr/bin/pyspMonitor3.py")

def killPyspMonitor():
    ''' 
    kill processes named /usr/bin/pyspMonitor.py
    ''' 
    return utils.killProcess( '/usr/bin/pyspMonitor.py')

