# PySpectra

A program to display 1-dimensional data

Interfaces:

* GUI: pyspViewer.py
    
* ipython:

    alias PySpectra='ipython --profile=PySpectra'

    /home/<user>/.ipython/profile_PySpectra/startup/00-start.py

    ```
    #!/usr/bin/env python
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
    pysp.create( "t1")
    pysp.create( "t2")
    pysp.display()
    pysp.delete()
    pysp.cls()
    ```


