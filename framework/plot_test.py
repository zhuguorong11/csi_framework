from sklearn import datasets
import numpy as np
import functools as func
import matplotlib.pyplot as plt

import sys
import struct
import os

class CSI_Plot:

    def Db(self, x):
        return 20*np.log10(x)

    def InvDb(self, x):
        return 10**(x/10)

    def write_to_file(self):
        row = len(self.retCSI)
        f = open('test.py.txt', 'w')

        for n in range(len(self.retCSI)):
            csi = self.retCSI[n]
            nrx = csi['Nrx']
            ntx = csi['Ntx']

            for y in range(len(csi['csi'])):
                for z in csi['csi'][y]:
                    for x in z:
                        f.write(str(x).strip(')').strip('('))
                        f.write('\n')
        f.close()

    def csi_plot(self, scaledCSI):
        values = np.abs(np.squeeze(np.transpose(scaledCSI)))

        db = np.vectorize(self.Db)
        values = np.around(db(values), 4)

        for n in values:
            plt.plot(list(range(len(n))), n)

        plt.show()

    def __init__(self):
        self.retCSI = []
        pass


