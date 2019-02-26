# PySpectra

A program to display 1-dimensional data using pyqtgraph or matplotlib.

Interfaces:

* Monitor pyspMonitor.py (uses pyspDoor.py) 

* GUI: pyspViewer.py
    
* ipython:

    alias PySpectra='ipython --profile=PySpectra'

    /home/<user>/.ipython/profile_PySpectra/startup/00-start.py

    ```
    #!/usr/bin/env python
    import __builtin__
    #__builtin__.__dict__[ 'graphicsLib'] = 'matplotlib'
    __builtin__.__dict__[ 'graphicsLib'] = 'pyqtgraph'
    import PySpectra as pysp
    import numpy as np
    import PySpectra.ipython.startup
    ```

    ```
    create t1
    pysp.t1.y = np.sin( pysp.t1.x)
    display
    delete
    cls
    ```

* Python API
    ```
    #!/usr/bin/env python
    import __builtin__
    #__builtin__.__dict__[ 'graphicsLib'] = 'matplotlib'
    __builtin__.__dict__[ 'graphicsLib'] = 'pyqtgraph'
    pysp.create( "t1")
    pysp.create( "t2")
    pysp.display()
    pysp.delete()
    pysp.cls()
    ```


