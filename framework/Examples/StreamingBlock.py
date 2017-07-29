from framework.BlockComponents.Block import *
from framework.BlockComponents.Port import *
from framework.BlockComponents.Network import *

from framework.Tools.ExtractorDeviceFactory import *
from framework.Tools.CSIExtractor import *

import time

class BlockCSIRead(SourceBlock):
    def __init__(self, aProcessID):
        super().__init__(aProcessID)
        self.deviceType = None
        self.rawFilePath = None
        self._mOutPorts.add_port(ChannelType.STREAM)

    def _execute(self, **kwargs):
        deviceType = 'iwl5300'
        rawFilePath = '../../data/csi.dat'

        device = WiFiDeviceFactory.create_device(deviceType)
        csiObj = CSIExtractor(device)
        csiObj.open_csi_file(rawFilePath)

        mtrx = csiObj.convert_to_csi_matrix()
        x = 0

        while True:
            for i in range(mtrx.shape[3]):
                self._mOutPorts[0].put(mtrx[:, :, :, i])
                x += 1

            print('Sleeping for next broadcast...')
            time.sleep(5)

    def _set_configuration(self, config: Configuration):
        return True

class BlockTransform(TransformBlock):
    def __init__(self, aProcessID):
        super().__init__(aProcessID)

        self._mOutPorts.add_port(ChannelType.STREAM)
        self._mInPorts.add_port(ChannelType.STREAM)

    def _execute(self, **kwargs):
        i = 0
        while True:
            i += 1
            in_data = self._mInPorts[0].get()
            time.sleep(.5)
            self._mOutPorts[0].put(in_data)
            #raise Exception('FAILED TRANFORM BLOCK')
            return False

    def _set_configuration(self, config: Configuration):
        return True

class BlockSink(SinkBlock):
    def __init__(self, aProcessID):
        super().__init__(aProcessID)
        self._mInPorts.add_port(ChannelType.STREAM)

    def _execute(self, **kwargs):
        print('Sink Started')

        i = 0
        while True:
            i += 1
            print('Sink Waiting..')
            in_data = self._mInPorts[0].get()
            time.sleep(2)

            if i % 10 == 0:
                print('sink read:', in_data)


    def _set_configuration(self, config: Configuration):
        return True

if __name__ == '__main__':
    print('Multiprocessing test')

    read = BlockCSIRead('read')
    transform = BlockTransform('transform')
    sink = BlockSink('sink')

    network = Network()
    network.add(read)
    network.add(transform)
    network.add(sink)

    network.connect(read, transform)
    network.connect(transform, sink)

    config = BlockConfiguration()
    network.configure(config)

    network.run()

    '''
    # Streaming example:
    read = BlockCSIRead('read')
    transform = BlockTransform('transform')
    sink = BlockSink('sink')

    # Step network responsibility :
    readPort = read.get_outport(0)
    readPort.connect_port(transform.get_inport(0))
    transformPort = transform.get_outport(0)
    transformPort.connect_port(sink.get_inport(0))

    test = StepConfig()

    read.configure(test)
    transform.configure(test)
    sink.configure(test)

    read.start()
    transform.start()
    sink.start()
    '''