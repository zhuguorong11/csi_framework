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
        self._mOutPorts.add_port(ChannelType.STREAM)


    def _execute(self, **kwargs):
        deviceType = 'iwl5300'
        rawFilePath = '../../data/csi.dat'

        device = WiFiDeviceFactory.create_device(deviceType)
        csiObj = CSIExtractor(device)
        csiObj.open_csi_file(rawFilePath)

        mtrx = csiObj.convert_to_csi_matrix()
        chnl = kwargs['input']
        print('Read:: ', chnl.data)
        return True


    def _set_configuration(self, config : Configuration):
        return True

class BlockTransform(TransformBlock):
    def __init__(self, aProcessID):
        super().__init__(aProcessID)
        self._mInPorts.add_port(ChannelType.STREAM)

    def _execute(self, **kwargs):
        print('BlockTransform')
        return True

    def _set_configuration(self, config : Configuration):
        return True

class BlockSink(SinkBlock):
    def __init__(self, aProcessID):
        super().__init__(aProcessID)

    def _execute(self, **kwargs):
        pass

    def _set_configuration(self, config: Configuration):
        return True

if __name__ == '__main__':
    print('Multiprocessing test')

    read = BlockCSIRead('read')
    transform = BlockTransform('transform')
    sink = BlockSink('sink')

    configuration = BlockConfiguration()
    read.configure(configuration)
    transform.configure(configuration)
    sink.configure(configuration)

    chnl = DataWrapper('Daniel')
    read.do(input=chnl)
    transform.do()

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





