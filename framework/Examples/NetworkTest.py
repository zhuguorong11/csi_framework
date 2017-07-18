from BlockComponents.StepNetwork import *
from BlockComponents.Step import *
from BlockComponents.Port import *
from BlockComponents.Configuration import *

class StepA (SourceStep):
    def __init__(self, name):
        super().__init__(name)
        self._mConfig = None
        self.mParam1 = None
        self.mParam2 = None
        self.mParam3 = None

        self._mOutPorts.AddOutPort(OutPort()) # should this be internal to Step (?) -> Might want to attach stuff to a Source or Sink Step
        self._mOutPorts.AddOutPort(OutPort())

    def _Execute(self, **kwargs : DataMatrix):
        inData = csiMatrix('')
        outData = self._mOutPorts[0].GetData()
        outData1 = self._mOutPorts[1].GetData()

        outData.data = inData.data + ' A'
        outData1.data = inData.data + ' A'
        print('stapA')
        print(inData)
        print(outData)
        print(outData1)

        self._mOutPorts[0].Produce()
        self._mOutPorts[1].Produce()
        return True

    def _SetConfiguration(self, config : ConfigBase): # filename is step_a_config.py
        return True

class StepC (TransformStep):
    def __init__(self, name):
        super().__init__(name)

        self._mInPorts.AddInPort(InPort()) # No difference between inport and output, can combine the add step
        self._mOutPorts.AddOutPort(OutPort())

    def _Execute(self, **kwargs : DataMatrix):
        inData = self._mInPorts[0].GetData()
        outData = self._mOutPorts[0].GetData()

        outData.data = inData.data + ' C'
        print('stapC')
        print('in:', inData)
        print('out:', outData)
        self._mInPorts.ConsumePorts()
        self._mOutPorts[0].Produce()
        return True

    def _SetConfiguration(self, config: ConfigBase):
        return True

class StepB(TransformStep):
    def __init__(self, name):
        super().__init__(name)
        self._mInPorts.AddInPort(InPort())
        self._mOutPorts.AddOutPort(OutPort())

    def _Execute(self, **kwargs : DataMatrix):
        inData = self._mInPorts[0].GetData()
        outData = self._mOutPorts[0].GetData()

        outData.data = inData.data + ' B'
        print('stapB')
        print('in:',inData)
        print('out:',outData)

        self._mInPorts[0].Consume()
        self._mOutPorts.ProducePorts()
        return True

    def _SetConfiguration(self, config: ConfigBase):
        return True

class StepD(SinkStep):

    def __init__(self, name):
        super().__init__(name)
        self._mInPorts.AddInPort(InPort())

    def _Execute(self, **kwargs : DataMatrix):
        inData = self._mInPorts[0].GetData()
        print('stapD')
        print(inData)

        print('D step output: ', inData.data)
        self._mInPorts[0].Consume()
        return True

    def _SetConfiguration(self, config: ConfigBase):
        return True

class StepZ(SinkStep):

    def __init__(self, name):
        super().__init__(name)
        self._mInPorts.AddInPort(InPort())

    def _Execute(self, **kwargs : DataMatrix):
        inData = self._mInPorts[0].GetData()
        print('stapZ')
        print(inData)

        print('Z step input: ', inData.data)
        self._mInPorts[0].Consume()
        return True

    def _SetConfiguration(self, config: ConfigBase):
        return True

'''
    > C -> D
    |
A ->|
    |
    > B -> Z
'''

a = StepA('A_SRC')
b = StepB('B_TR')
c = StepC('C_TR')
d = StepD('D_SNK')
z = StepZ('Z_SNK')

net = StepNetwork()
net.AddStep(a)
net.AddStep(b)
net.AddStep(c)
net.AddStep(d)
net.AddStep(z)

# Need to modifiy these and add source and destination portNo
net.ConnectStep('A_SRC', 'C_TR', 0, 0)
net.ConnectStep('A_SRC', 'B_TR', 1, 0)
net.ConnectStep('B_TR', 'Z_SNK', 0, 0)
net.ConnectStep('C_TR', 'D_SNK', 0, 0)

config = StepConfig()
config.Read('../../config/default.yaml')

net.ConfigureSteps(config)
net.SetNetworkStrategy(NetworkExecNaive())

net.DoNetwork()

print('done')