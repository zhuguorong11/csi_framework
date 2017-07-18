import matplotlib.pyplot as plt
import numpy as np
from scipy.fftpack import fft

from BlockComponents.Configuration import *
from BlockComponents.Step import *

class StepFFT(TransformStep):
    def __init__(self, aProcessID):
        super().__init__(aProcessID)
        self._mOutPorts.AddOutPort(OutPort())
        self._mInPorts.AddInPort(InPort())

    def _Execute(self, **kwargs):
        # input is a single array of numpy.
        N = kwargs['N']
        T = kwargs['T']

        x = np.linspace(0.0, N * T, N)
        y = np.sin(50.0 * 2.0 * np.pi * x) + 0.5 * np.sin(80.0 * 2.0 * np.pi * x)
        yf = fft(y)
        xf = np.linspace(0.0, 1.0 / (2.0 * T), N // 2)

        plt.plot(xf, 2.0 / N * np.abs(yf[0:N // 2]))
        plt.grid()
        plt.show()

        return True

    def _SetConfiguration(self, config : ConfigBase):
        return True

test = StepFFT('test')
config = StepConfig()

config.Read('../../config/default.yaml')

test.Configure(config)
test.Do(N = 600, T = 1.0 / 800.0)
