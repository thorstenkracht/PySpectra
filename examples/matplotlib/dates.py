#!/usr/bin/env python
import matplotlib.pyplot as plt

def main():

    dates = [ 737070.,  737071.,  737072.,  737073.,  737074.,  737075.,
              737076.,  737077.,  737078.,  737079.,  737080.]

    s = [ 0., 1, 2.5, 3, 4, 5, 6, 3.5, 8, 9, 5]
    fig, ax = plt.subplots()
    plt.plot_date(dates, s, xdate = True)
    
    plt.show()

if __name__ == "__main__":
    main()
