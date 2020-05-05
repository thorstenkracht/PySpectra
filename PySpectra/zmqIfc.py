#!/usr/bin/env python
'''
this module handles the access from remote:
  - this caan be a client using toPyspMonitor() and ZMQ
  - or pyspDoor via a queue
  
Further documentation

  PySpectra.toPyspMonitor?
  PySpectra.execHsh?
  PySpectra.isPyspMonitorAlive?
---
'''
import PyTango
import time
import PySpectra 
import PySpectra.utils as utils
import numpy as np

def execHsh( hsh): 
    '''
    execHsh executes dictionaries which are received 
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
                   'x': array([  0.0, ..., 2.047e+03]), 'reUse': True}}
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
    #print( "zmqIfc.execHsh: %s" % repr( hsh))
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
            argout[ 'result'] = "zmqIfc.execHsh: error, %s" % repr( e)
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
            argout[ 'result'] = "zmqIfc.execHsh: error, %s" % repr( e)
    #
    # Scan
    #
    elif 'Scan' in hsh:
        try: 
            #
            # '**hsh' unpacked dictionary
            #
            PySpectra.Scan( **hsh[ 'Scan']) 
            argout[ 'result'] = 'done'
        except Exception as e:
            argout[ 'result'] = "zmqIfc.execHsh: error, %s" % repr( e)
    #
    # ... else
    #
    else:
        argout[ 'result'] = "zmqIfc.execHsh: error, failed to identify %s" % repr( hsh)
    #
    # getDoorState is answered with a value, not with 'done'
    #
    if not 'getDoorState' in hsh: 
        if argout[ 'result'].upper() != "DONE":
            print( "zmqIfc.execHsh: no 'DONE', instead received '%s' " % argout[ 'result'])
            print( "zmqIfc.execHsh: input: %s " % repr( hsh))

    #print( "zmqIfc.execHsh: return %s" % repr( argout))
    return argout

def _replaceNumpyArrays( hsh): 
    """
    find numpy arrays in the hsh and replace the by lists
    """
    for k in list( hsh.keys()): 
        if type( hsh[ k]) is dict:
            _replaceNumpyArrays( hsh[ k])
            continue
        if type( hsh[ k]) is list:
            for elm in hsh[ k]: 
                if type( elm) is dict:
                    _replaceNumpyArrays( elm)
        if type( hsh[ k]) is np.ndarray: 
            #
            # Images, that have been created by tolist() need width and height
            # if width and height are not supplied, take them from .shape
            #
            if len( hsh[ k].shape) == 2:
                if not 'width' in hsh: 
                    hsh[ 'width'] = hsh[ k].shape[0]
                if not 'height' in hsh: 
                    hsh[ 'height'] = hsh[ k].shape[1]
            hsh[ k] = hsh[ k].tolist()

    return

def toPyspMonitor( hsh, node = None, testAlive = False):
    '''
    Send a dictionary to the pyspMonitor process. 

    The pyspMonitor processes the dictionary by calling PySpectra.execHsh()

    testAlive == True: 
        it is checked whether a pyspMonitor process responds to isAlive
        if there is no answer: the process is launched

    Example: 
      ret = PySpectra.toPyspMonitor( {'command': ['delete', 'cls', 'create s1', 'display']})
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
        return { 'result': "zmqIfc.toPyspMonitor: failed to connect to %s" % node}
    
    _replaceNumpyArrays( hsh)

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

def isPyspMonitorAlive( node = None):
    '''
    returns True, if there is a pyspMonitor responding to the isAlive prompt
    '''
    hsh = toPyspMonitor( { 'isAlive': True}, node = node, testAlive = False)
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
            raise Exception( "zmqIfc._putData", "expecting 'columns', 'gqes', 'setPixelImage', 'setPixelWorld'")
    except Exception as e: 
        argout = "zmqIfc._putData: %s" % repr( e)

    return argout

def _execCommand( hsh): 
    '''
    passes PySpectra commands to pysp.ipython.ifc.command()

    called from 
      - execHsh()
    
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

    called from execHsh()
    
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
    res = toPyspMonitor( { 'isAlive': True}, testAlive = False) 
    if res[ 'result'] == 'done': 
        return( True, False)
    else: 
        #
        # even if the pyspMonitor does not reply to 'isAlive', 
        # the process may exist
        #
        if utils.findProcessByName( "/usr/bin/pyspMonitor.py"):
            utils.killProcess( "/usr/bin/pyspMonitor.py")
        
        return utils.assertProcessRunning( "/usr/bin/pyspMonitor.py")

def killPyspMonitor():
    ''' 
    kill processes named /usr/bin/pyspMonitor.py
    ''' 
    return utils.killProcess( '/usr/bin/pyspMonitor.py')

