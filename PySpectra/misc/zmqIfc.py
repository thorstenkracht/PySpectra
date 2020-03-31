#!/usr/bin/env python
'''
this module handles the access via zmq
Server: 
  + pyspMonitor
Client: 
  + spock macro
  + any python script

Functions

  - toPyspMonitor() sends the request
    handled in pyspMonitorClass.py
      cb_timerZMQ()
            msg = self.sckt.recv()
            hsh = json.loads( msg)
            ...
            argout = PySpectra.misc.zmqIfc.execHsh( hsh)
            msg = json.dumps( argout)
            self.sckt.send( msg)
  - isPyspMonitorAlive()
  - execHsh()

'''
import PySpectra 
import PySpectra.dMgt.GQE as _gqe
import PySpectra.ipython.ifc as _ifc

def toPyspMonitor( hsh, node = None):
    """
    sends a dictionary to a PyspMonitor process, 
    returns a dictionary ...
# 
# this piece of code can only be executed,   
# if the pyspMonitor.py is running
#
import PySpectra as pysp
import random
MAX = 5
pos = [float(n)/MAX for n in range( MAX)]
d1 = [random.random() for n in range( MAX)]
d2 = [random.random() for n in range( MAX)]

print( "pos %s" % repr( pos))
print( "d1: %s" % repr( d1))

hsh = { 'putData': 
           {'title': "Important Data", 
            'columns': 
            [ { 'name': "d1_mot01", 'data' : pos},
              { 'name': "d1_c01", 'data' : d1},
              { 'name': "d1_c02", 'data' : d2},
           ]}}

hsh = PySpectra.misc.zmqIfc.toPyspMonitor( hsh)
print( "return values of putData: %s" % repr( hsh) )

hsh = PySpectra.misc.zmqIfc.toPyspMonitor( { 'getData': True})
for i in range( MAX):
    if pos[i] != hsh[ 'getData']['d1_c01']['x'][i]:
        print( "error: pos[i] != x[i]")
    if d1[i] != hsh[ 'getData'][ 'd1_c01'][ 'y'][i]:
        print( "error: d1[i] != y[i]")
        
print( "getData, pos: %g" % hsh[ 'getData']['d1_c01']['x'])
print( "getData, pos: %g" % hsh[ 'getData']['d1_c01']['y'])
return

    """
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
            return { 'result': 'utils: no reply from pyspMonitor'}

def isPyspMonitorAlive( node = None):
    '''
    returns True, if there is a pyspMonitor responding to the isAlive prompt
    '''
    hsh = toPyspMonitor( { 'isAlive': True}, node = node)
    if hsh[ 'result'] == 'notAlive':
        return False
    else:
        return True



def execHsh( hsh): 
    '''
    this function executes dictionaries which are received from 
      - ZMQ, from another client calling toPyspMonitor()
      - Queue, from pyspDoor
      - from an application directly (to simulate the to toPyspMonitor() interface

     hsh: 
       Misc
         {'command': ['delete']}
           delete all internal data
         {'command': ['cls']}
           clear the screen
         {'command': ['delete', 'cls']}
           deletes all internal data and clears the screen
         {'command': ['display']}
           a display command

       Title and comment for the whole widget
         {'command': [u'setTitle ascan exp_dmy01 0.0 1.0 3 0.2']}
           set the title 
         {'command': [u'setComment "tst_01366.fio, Wed Dec 18 10:02:09 2019"']}
           set the comment

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
         {'putData': {'columns': [{'data': [0.0, ..., 0.96], 'name': 'eh_mot01'}, 
                                  {'data': [0.39623, ... 0.01250], 'name': 'eh_c01'}, 
                                  {'showGridY': False, 'symbolColor': 'blue', 'showGridX': False, 
                                   'name': 'eh_c02', 'yLog': False, 'symbol': '+', 
                                   'data': [0.1853, ... 0.611], 
                                   'xLog': False, 'symbolSize': 5}], 
                      'title': 'a title', 
                      'comment': 'a comment'}}
           create the scans eh_c01 and eh_c02. The common x-axis is given by eh_mot01

       Image 
         {'Image': {'name': 'MandelBrot', 
                    'height': 5, 'width': 5, 
                    'xMax': -0.5, 'xMin': -2.0, 
                    'yMin': 0, 'yMax': 1.5}}
           create an empty image
         {'putData': {'images': [{'data': array([[0, 0, 0, ..., 0, 0, 0],
                                                 [0, 0, 0, ..., 1, 1, 1]], dtype=int32), 
                                  'name': 'MandelBrot'}]}
           create an image from a 2D array
         {'Image': {'data': data, 'name': "Mandelbrot"}}
           create an image by sending the data, e.g. data = np.ndarray( (width, height), _np.int32)
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
    if 'command' in hsh:
        argout[ 'result'] = commandIfc( hsh)
    elif 'putData' in hsh:
        argout[ 'result'] = _putData( hsh[ 'putData'])
    elif 'getData' in hsh:
        try:
            argout[ 'getData'] = _gqe.getData()
            argout[ 'result'] = 'done'
        except Exception as e:
            argout[ 'getData'] = {}
            argout[ 'result'] = "zmqIfc.execHsh: error, %s" % repr( e)
    #
    # the 'isAlive' question comes from a toPyspMonitor() client, not from the door
    #
    elif 'isAlive' in hsh:
        argout[ 'result'] = 'done'
    elif 'Image' in hsh:
        try: 
            #
            # '**hsh': unpacked dictionary
            #
            _gqe.Image( **hsh[ 'Image']) 
            argout[ 'result'] = 'done'
        except Exception as e:
            argout[ 'result'] = "zmqIfc.execHsh: error, %s" % repr( e)
    elif 'Scan' in hsh:
        try: 
            #
            # '**hsh' unpacked dictionary
            #
            _gqe.Scan( **hsh[ 'Scan']) 
            argout[ 'result'] = 'done'
        except Exception as e:
            argout[ 'result'] = "zmqIfc.execHsh: error, %s" % repr( e)
    else:
        argout[ 'result'] = "zmqIfc.execHsh: error, failed to identify %s" % repr( hsh)

    #print( "zmqIfc.execHsh: return %s" % repr( argout))
    return argout

def _putData( hsh):
    '''
    a plot is created based on a dictionary 
    the use case: some data are sent pyspMonitor
    '''

    argout = 'n.n.'
    if 'title' not in hsh:
        _gqe.setTitle( "NoTitle")
    else:
        _gqe.setTitle( hsh[ 'title'])

    if 'columns' in hsh:
        _gqe.delete()
        PySpectra.cls()
        argout = _gqe.fillDataByColumns( hsh)
    elif 'gqes' in hsh:
        _gqe.delete()
        PySpectra.cls()
        argout = _gqe.fillDataByGqes( hsh)
    #
    # hsh = { 'putData': 
    #         { 'name': "MandelBrot",
    #           'type': 'image', 
    #           'xMin': xmin, 'xMax': xmax, 'width': width, 
    #           'yMin': ymin, 'yMax': ymax, 'height': height}}
    #
    elif 'type' in hsh and hsh[ 'type'] == 'image':
        del hsh[ 'type']
        _gqe.Image( **hsh)
        argout = "done"
    #
    #_PySpectra.misc.zmqIfc.execHsh( { 'putData': 
    #                { 'images': [{'name': "Mandelbrot", 'data': data,
    #                              'xMin': xmin, 'xMax': xmax, 
    #                              'yMin': ymin, 'yMax': ymax}]}})
    #
    elif 'images' in hsh:
        for h in hsh[ 'images']: 
            _gqe.Image( **h)
        argout = "done"
    elif 'setPixelImage' in hsh or 'setPixelWorld' in hsh:
        argout = _gqe.fillDataImage( hsh)
    elif 'setXY' in hsh:
        argout = _gqe.fillDataXY( hsh)
    else:
        raise Exception( "zmqIfc._putData", "expecting 'columns', 'gqes', 'setPixelImage', 'setPixelWorld'")

    return argout

def commandIfc( hsh): 
    '''
    passes commands to pysp.ipython.ifc.command()

    called from execHsh()
    
    List of commands: 
      hsh = { 'command': ['cls', 'display']}
    Single commands
    hsh = { 'command': 'display'}
    '''
    argout = "n.n."
    if type( hsh[ 'command']) == list:
        for cmd in hsh[ 'command']: 
            ret = _ifc.command( cmd)
            argout += "%s -> %s;" % (cmd, repr( ret))

        return "done"

    ret = _ifc.command( hsh[ 'command'])
    argout = "%s -> %s" % (hsh[ 'command'], repr( ret))
    return argout
