#!/usr/bin/env python
'''
'''
import taurus
import time

def main():
    import HasyUtils
    import demoDoor_v3

    door = taurus.Device( HasyUtils.getLocalDoorNames()[0])

    while True: 
        time.sleep(0.1)

if __name__ == "__main__":
    main()
    

