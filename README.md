# Dataflow network framework 
Example networks in folder framework/examples:

 * Real-time signal plotter in LiveStreamPlot.py 
 * Network with shared memory channels between blocks in example SharedMemBlock.py
 * Network with streaming channels in StreamingBlock.py 

Implementation of Block and Channel classes in framework/BlockComponents. 

More info and larger network implementations to come! 


And here's the streaming plotter example: 

```python
from framework.BlockComponents.Block import *
from framework.BlockComponents.Network import *

from framework.Tools.ExtractorDeviceFactory import *
from framework.Tools.CSIExtractor import *
import matplotlib.pyplot as plt

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

	def scale(self, data):
		data = np.absolute(data)
		data[data < 1] = np.nan
		data = 20 * np.log10(data)
		return data

	def _execute(self, **kwargs):
		while True:
			data = frameMatrix(3,3,30)
			data.set(self._mInPorts[0].get())

			p = self.stream_1.split('x')
			t_1 = int(p[0]) - 1
			r_1 = int(p[1]) - 1
			k_1 = int(p[2]) - 1
			stream_1 = data.get_stream(t_1, r_1, k_1)
			stream_1 = scale(stream_1)

			p = self.stream_2.split('x')
			t_2 = int(p[0]) - 1
			r_2 = int(p[1]) - 1
			k_2 = int(p[2]) - 1
			stream_2 = data.get_stream(t_2, r_2, k_2)
			stream_2 = scale(stream_2) 

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
    def __init__(self, aProcessID):
        super().__init__(aProcessID)
        self._mInPorts.add_port(ChannelType.STREAM)
        self._mInPorts.add_port(ChannelType.STREAM)

    def _execute(self, **kwargs):
        plt.ion()
        yBuff = []
        y2Buff = []
        i = 0
        while True:
            x = range(i)
            val1 = self._mInPorts[0].get()
            val2 = self._mInPorts[1].get()

            yBuff.append(val1[0])
            y2Buff.append(val2[0])

            plt.plot(yBuff)
            plt.plot(y2Buff)
            plt.title('Live Stream')
            plt.draw()
            plt.pause(0.1)
            i = i + 1 

    def _set_configuration(self, config: Configuration):
        blockID = self.get_block_id()
        if config.exists(blockID) == True:
            self.plotTitle = config[blockID]['title']
            return True
        else:
            return False

stream = BlockCSIStream('input')
select = BlockSelect('selector')

plotter = BlockPlot('plot')

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
```



### ToDo:

 * Cleanup old step class implementations 
 * Create learning + signal processing blocks

