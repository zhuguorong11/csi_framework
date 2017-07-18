from BlockComponents.Block import *
from framework.BlockComponents.Network import *
from framework.BlockComponents.Configuration import *

from framework.Tools.ExtractorDeviceFactory import *
from framework.Tools.CSIExtractor import *

import time

class BlockCSIRead(SourceBlock):
    def __init__(self, aProcessID):
        super().__init__(aProcessID)
        self.deviceType = None
        self.rawFilePath = None
        self._mOutPorts.add_port(ChannelType.MATRIX, (3, 3, 30, 1452))

    def _execute(self, **kwargs):
        deviceType = 'iwl5300'
        rawFilePath = '../../data/csi.dat'

        device = WiFiDeviceFactory.create_device(deviceType)
        csiObj = CSIExtractor(device)
        csiObj.open_csi_file(rawFilePath)

        mtrx = csiObj.convert_to_csi_matrix()

        print('Sending data...')
        self._mOutPorts[0].put(mtrx)

        print('CSI_READ Send:', mtrx.shape)
        print('Sleeping for next broadcast...')

    def _set_configuration(self, config : Configuration):
        return True

class BlockTransform(TransformBlock):
    def __init__(self, aProcessID):
        super().__init__(aProcessID)

        self._mOutPorts.add_port(ChannelType.MATRIX, (3, 3, 30, 1452))
        self._mInPorts.add_port(ChannelType.MATRIX, (3, 3, 30, 1452))

    def _execute(self, **kwargs):
        import os
        print("process id = ", os.getpid())
        print('Transform: Waiting...')
        in_data = self._mInPorts[0].get()
        time.sleep(1)
        print('Transform: Received')
        self._mOutPorts[0].put(in_data)
        print('Transform: Sent to Sink')

    def _set_configuration(self, config : Configuration):
        return True

class BlockSink(SinkBlock):
    def __init__(self, aProcessID):
        super().__init__(aProcessID)
        self._mInPorts.add_port(ChannelType.MATRIX, (3, 3, 30, 1452))

    def _execute(self, **kwargs):
        import os
        print("process id = ", os.getpid())
        print('SINK: Waiting..')
        in_data = self._mInPorts[0].get()
        print('SINK: Received...', in_data.shape)

    def _set_configuration(self, config: Configuration):
        return True

if __name__ == '__main__':
    print('Multiprocessing test')

    # Sequential example:
    read = BlockCSIRead('read')
    transform = BlockTransform('transform')
    sink = BlockSink('sink')

    network = Network()
    network.add(read)
    network.add(transform)
    network.add(sink)

    network.connect(read, transform)
    network.connect(transform, sink)

    configuration = BlockConfiguration()
    network.configure(configuration)

    network.run()

    '''
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

    read.join()
    transform.join()
    sink.join()
    '''





