#!/usr/bin/env python
'''
PySpectra displays 1D data

PySpectra.Scan()
  a class returnint a scan object

  scan = PySpectra.Scan( name = 't1')

PySpectra.cls()
  clear the screen screen

PySpectra.delete()
  delete all or selected scans
  
  PySpectra.delete()
    delete all scans

  PySpectra.delete( ['t1', 't2')
    delete selected scans

PySpectra.display()
  display all or selected scans
  
  PySpectra.display()
    display all scans

  PySpectra.display( ['t1', 't2'])
    display selected scans

PySpectra.overlay( src, trgt)
  plot src in the viewport of trgt

'''
from dMgt.GQE import *
from dMgt.calc import *

import __builtin__
try:
    if __builtin__.__dict__[ 'graphicsLib'] == 'matplotlib':
        from mtpltlb.graphics import *
    else: 
        from pqtgrph.graphics import *
except: 
    from pqtgrph.graphics import *

from utils import *
import ipython.ifc 
