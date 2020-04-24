#!/usr/bin/env python
'''
this module handles the access from remote:
  - this caan be a client using toPyspMonitor() and ZMQ
  - or pyspDoor via a queue
  
Further documentation

  PySpectra.zmqIfc.toPyspMonitor?
  PySpectra.zmqIfc.execHsh?
  PySpectra.zmqIfc.isPyspMonitorAlive?
---
'''
import PyTango
import time
import PySpectra 
import PySpectra.GQE as GQE
import PySpectra.utils as utils

def execHsh( hsh): 
    '''
    this function executes dictionaries which are received 
      - from another client which called toPyspMonitor() to send
        a dictionary via ZMQ to pyspMonitor.py, specific: cb_timerZMQ()
      - from Queue, from pyspDoor
      - from an application directly, maybe to simulation the toPyspMonitor interface

     hsh: 
       commands, list of commands: PySpectra.ipython.ifc?
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
           handle the arrow pointing to the current position

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

       Misc
         {'isAlive': True}
           return values:
             {u'result': u'done'}
             {'result': 'notAlive'}
         {'getDoorState': True}
           returns:
             { 'result': 'ON'}

       Scan
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

       Image 
         {'Image': {'name': 'MandelBrot', 
                    'height': 5, 'width': 5, 
                    'xMax': -0.5, 'xMin': -2.0, 
                    'yMin': 0, 'yMax': 1.5}}
           create an empty image

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

       Retrieve data
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
            argout[ 'getData'] = GQE.getData()
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
            GQE.Image( **hsh[ 'Image']) 
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
            GQE.Scan( **hsh[ 'Scan']) 
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

def toPyspMonitor( hsh, node = None):
    '''
    Send a dictionary to pyspMonitor. 
    The dictionary syntax can be found here 
      PySpectra.zmqIfc.execHsh?

    Example: 
      (status, wasLaunched) = PySpectra.utils.assertPyspMonitorRunning()

      ret = PySpectra.zmqIfc.toPyspMonitor( {'command': ['delete', 'cls', 'create s1', 'display']})
      if ret[ 'result'] != 'done': 
          print( "error" % ret[ 'result'])
    ---
    '''

    import zmq, json, socket

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
        return { 'result': "utils.toPyspMonitor: failed to connect to %s" % node}

    hshEnc = json.dumps( hsh)
    try:
        res = sckt.send( hshEnc)
    except Exception as e:
        sckt.close()
        return { 'result': "TgUtils.toPyspMonitor: exception by send() %s" % repr(e)}
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
            return json.loads( hshEnc)
        else: 
            sckt.close()
            context.term()
            return { 'result': 'notAlive'}
    else:
        lst = zmq.select([sckt], [], [], 3.0)
        if sckt in lst[0]:
            hshEnc = sckt.recv() 
            sckt.close()
            context.term()
            return json.loads( hshEnc)
        else: 
            sckt.close()
            context.term()
            return { 'result': 'zmqIfc.toPyspMonitor: communication time-out'}

def isPyspMonitorAlive( node = None):
    '''
    returns True, if there is a pyspMonitor responding to the isAlive prompt
    '''
    hsh = toPyspMonitor( { 'isAlive': True}, node = node)
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
    if 'title' not in hsh:
        GQE.setTitle( "NoTitle")
    else:
        GQE.setTitle( hsh[ 'title'])

    try: 
        #
        #hsh = { 'putData': {'columns': [{'data': x, 'name': 'xaxis'},
        #                                {'data': tan, 'name': 'tan'},
        #                                {'data': cos, 'name': 'cos'},
        #                                {'data': sin, 'name': 'sin',
        #                                 'showGridY': False, 'symbolColor': 'blue', 'showGridX': False, 
        #                                 'yLog': False, 'symbol': '+', 
        #                                 'xLog': False, 'symbolSize':5}]}}
        #
        if 'columns' in hsh:
            GQE.delete()
            PySpectra.cls()
            argout = GQE.fillDataByColumns( hsh)
        elif 'gqes' in hsh:
            GQE.delete()
            PySpectra.cls()
            try: 
                argout = GQE.fillDataByGqes( hsh)
            except Exception as e: 
                print( "zmqIfc: %s" % repr( e))
        #
        # hsh = { 'putData': 
        #         { 'name': "MandelBrot",
        #           'type': 'image', 
        #           'xMin': xmin, 'xMax': xmax, 'width': width, 
        #           'yMin': ymin, 'yMax': ymax, 'height': height}}
        #
        elif 'type' in hsh and hsh[ 'type'] == 'image':
            del hsh[ 'type']
            GQE.Image( **hsh)
            argout = "done"
        #
        #_PySpectra.zmqIfc.execHsh( { 'putData': 
        #                { 'images': [{'name': "Mandelbrot", 'data': data,
        #                              'xMin': xmin, 'xMax': xmax, 
        #                              'yMin': ymin, 'yMax': ymax}]}})
        #
        elif 'images' in hsh:
            for h in hsh[ 'images']: 
                GQE.Image( **h)
            argout = "done"
        else:
            raise Exception( "zmqIfc._putData", "expecting 'columns', 'gqes', 'setPixelImage', 'setPixelWorld'")
    except Exception as e: 
        argout = "utils.zmqIfc._putData: %s" % repr( e)

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
                return "zmqIfc._execCommand: error from ifc.command %s for %s" % ( ret, cmd)
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
        door = GQE.InfoBlock.getDoorProxy()
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

    door = GQE.InfoBlock.getDoorProxy()
    argout = "%s" % repr( door.state())
    return argout.split( '.')[-1]

#
# I don't know whether the following function is really needed - 
# syntactical sugar perhaps
#
def assertPyspMonitorRunning(): 
    """
    returns (status, wasLaunched)
    """
    return utils.assertProcessRunning( "/usr/bin/pyspMonitor.py")


def killPyspMonitor():
    ''' 
    kill processes named /usr/bin/pyspMonitor.py
    ''' 
    return utils.killProcess( '/usr/bin/pyspMonitor.py')

