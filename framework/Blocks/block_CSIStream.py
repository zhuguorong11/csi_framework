from framework.BlockComponents.Block import *
from framework.BlockComponents.Network import *

from framework.Tools.ExtractorDeviceFactory import *
from framework.Tools.CSIExtractor import *
import matplotlib.pyplot as plt
#plt.matplotlib_fname()
from multiprocessing import Queue


class BlockCSIStream(SourceBlock):
    def __init__(self, aProcessID):
        super().__init__(aProcessID)
        self.deviceType = None
        self.rawFilePath = None
        self._mOutPorts.add_port(ChannelType.STREAM)

    def _execute(self, **kwargs):
        device = WiFiDeviceFactory.create_device(self.deviceType)
        csiObj = CSIExtractor(device)

        p = csiObj.open_stream(self.rawFilePath, mode=0)# Mode is REPLAY | LIVE

        while p is not None:
            self._mOutPorts[0].put(p)
            p = csiObj.open_stream(self.rawFilePath)

    def _set_configuration(self, config : Configuration):
        blockID = self.get_block_id()
        if config.exists(blockID) == True:
            self.deviceType = config[blockID]['device_type']
            self.rawFilePath = config[blockID]['stream_src']
            return True
        else:
            return False

class BlockSelect(TransformBlock):
    def __init__(self, aProcessID):
        super().__init__(aProcessID)

        self._mOutPorts.add_port(ChannelType.STREAM)
        self._mOutPorts.add_port(ChannelType.STREAM)
        self._mInPorts.add_port(ChannelType.STREAM)

    def _execute(self, **kwargs):

        while True:
            data = csiMatrix(3, 3, 30, 10)
            for i in range(10):
                in_data = self._mInPorts[0].get()
                data.set_frame(i, in_data[:, :, :, 0])

            p = self.stream_1.split('x')
            t_1 = int(p[0]) - 1
            r_1 = int(p[1]) - 1
            k_1 = int(p[2]) - 1
            stream_1 = data.get_stream(t_1, r_1, k_1)

            p = self.stream_2.split('x')
            t_2 = int(p[0]) - 1
            r_2 = int(p[1]) - 1
            k_2 = int(p[2]) - 1
            stream_2 = data.get_stream(t_2, r_2, k_2)

            self._mOutPorts[0].put(stream_1)
            self._mOutPorts[1].put(stream_2)

    def _set_configuration(self, config : Configuration):
        blockID = self.get_block_id()
        if config.exists(blockID) == True:
            self.stream_1 = config[blockID]['stream_1']
            self.stream_2 = config[blockID]['stream_2']
            return True
        else:
            return False

class BlockPlot(SinkBlock):
    def __init__(self, aProcessID, pipe1, pipe2):
        super().__init__(aProcessID)
        self._mInPorts.add_port(ChannelType.STREAM)
        self._mInPorts.add_port(ChannelType.STREAM)
        self.pipe1 = pipe1
        self.pipe2 = pipe2

    def scale(self, data):
        s1 = csiSequence(10)
        s1.set(data)
        s1 = np.absolute(data)
        s1[s1 < 1] = np.nan
        s1 = 20 * np.log10(s1)
        y = s1.tolist()
        return y

    def _execute(self, **kwargs):

        plt.ion()
        x = 0
        yBuff = []
        while True:
            print('Sink Waiting..')

            in_data1 = self.scale(self._mInPorts[0].get())
            in_data2 = self.scale(self._mInPorts[1].get())

            for x in in_data1:
                self.pipe1.put(x)

            for x in in_data2:
                self.pipe2.put(x)

            '''
            x = x + len(y)
            #print('sink shape:', s1.shape)

            z = range(x)
            yBuff.extend(y)
            #y = range(i)
            # plt.gca().cla() # optionally clear axes
            plt.plot(z, yBuff)
            plt.title(self.plotTitle)
            plt.draw()
            plt.pause(0.1)
            '''

    def plot(self, streamA, streamB, streamC):
        pass

    def _set_configuration(self, config: Configuration):
        blockID = self.get_block_id()
        if config.exists(blockID) == True:
            self.plotTitle = config[blockID]['title']
            return True
        else:
            return False

stream = BlockCSIStream('input')
select = BlockSelect('selector')

d1 = Queue()
d2 = Queue()

plotter = BlockPlot('plot', d1, d2)

configuration = BlockConfiguration()
configuration.read('../Examples/config_streaming.yaml')

network = Network()
network.add(stream)
network.add(select)
network.add(plotter)

network.connect(stream, select)
network.connect(select, plotter, 0, 0)
network.connect(select, plotter, 1, 1)

network.configure(configuration)
network.run()

# This code below should have been run inside the plotter function.
plt.ion()
i = 0
yBuff = []
y2Buff = []
while True:
    x = range(i)
    # y = range(i)
    # plt.gca().cla() # optionally clear axes
    val1 = d1.get()
    val2 = d2.get()
    print('val1:', val1, ' val2:', val2)
    yBuff.append(val1)
    y2Buff.append(val2)

    plt.plot(yBuff)
    plt.plot(y2Buff)
    plt.title('Live Stream')
    plt.draw()
    plt.pause(0.1)
    i = i + 1
# End of the Plotting Code

# deviceType = 'iwl5300'
# rawFilePath = '../../data/csi.dat'