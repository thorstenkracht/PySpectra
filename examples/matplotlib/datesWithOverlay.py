#!/usr/bin/env python
import matplotlib.pyplot as plt

def main():

    dates = [ 737070.,  737071.,  737072.,  737073.,  737074.]

    s1 = [ 0., 1, 2.5, 3, 4]
    s2 = [ 0., 1, 2, 1, 2]
    fig, ax1 = plt.subplots()
    
    ax1.plot_date(dates, s1, "b", xdate = True)

    ax2 = ax1.twinx()

    ax2.plot_date( dates, s2, "g", xdate = True)
    plt.show()

if __name__ == "__main__":
    main()
