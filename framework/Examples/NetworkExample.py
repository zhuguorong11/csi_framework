from BlockComponents.StepNetwork import *
from BlockComponents.Step import *
from BlockData.DataMatrix import *
from BlockComponents.Port import *
from BlockComponents.Configuration import *

class StepA (SourceStep):
    def __init__(self, name):
        super().__init__(name)
        self._mConfig = None
        self.mParam1 = None
        self.mParam2 = None
        self.mParam3 = None

    #   Default step has one input and output port
    #   self._mInPorts.AddInPort(InPort())
        self._mOutPorts.AddOutPort(OutPort()) # should this be internal to Step (?) -> Might want to attach stuff to a Source or Sink Step

    def _Execute(self, **kwargs : DataMatrix):
        inData = csiMatrix('')
        outData = self._mOutPorts[0].GetData()
        outData.data = inData.data + ' A'

        self._mOutPorts[0].Produce()
        return True

    def _SetConfiguration(self, config : ConfigBase): # filename is step_a_config.py
        return True

        self._mConfig = config[self.GetStepID()]
        try:
            self.mParam1 = self._mConfig['param_1']
            self.mParam2 = self._mConfig['param_2']
            self.mParam3 = self._mConfig['param_3']
        except:
            print('Configuration failed for:', self.GetStepID())
            return False

        return True

class StepB (SourceStep):
    def __init__(self, name):
        super().__init__(name)

    #   Default step has one input and output port
    #   self._mInPorts.AddInPort(InPort())
        self._mOutPorts.AddOutPort(OutPort())

    def _Execute(self, **kwargs : DataMatrix):
        inData = csiMatrix('')
        outData = self._mOutPorts[0].GetData()
        outData.data = inData.data + ' B'

        self._mOutPorts[0].Produce()
        return True

    def _SetConfiguration(self, config: ConfigBase):
        return True

class StepC (TransformStep):
    def __init__(self, name):
        super().__init__(name)

    #   Default step has one input and output port
        self._mInPorts.AddInPort(InPort()) # No difference between inport and output, can combine the add step
        self._mInPorts.AddInPort(InPort())
        self._mOutPorts.AddOutPort(OutPort())

    def _Execute(self, **kwargs : DataMatrix):
        inData = self._mInPorts[0].GetData()
        inData1 = self._mInPorts[1].GetData()
        outData = self._mOutPorts[0].GetData()

        outData.data = inData.data + ' ' + inData1.data + ' C'

        self._mInPorts.ConsumePorts()
        self._mOutPorts[0].Produce()
        return True

    def _SetConfiguration(self, config: ConfigBase):
        return True

class StepD (TransformStep):
    def __init__(self, name):
        super().__init__(name)
    #   Default step has one input and output port
        self._mInPorts.AddInPort(InPort())
        self._mInPorts.AddInPort(InPort())
        self._mOutPorts.AddOutPort(OutPort())

    def _Execute(self, **kwargs : DataMatrix):
        inData = self._mInPorts[0].GetData()
        inData1 = self._mInPorts[1].GetData()
        outData = self._mOutPorts[0].GetData()

        outData.data = inData.data + ' ' + inData1.data + ' D'

        self._mInPorts.ConsumePorts()
        self._mOutPorts[0].Produce()
        return True

    def _SetConfiguration(self, config: ConfigBase):
        return True

class StepZ(SourceStep):
    def __init__(self, name):
        super().__init__(name)
    #   Default step has one input and output port
    #   self._mInPorts.AddInPort(InPort())
        self._mOutPorts.AddOutPort(OutPort())

    def _Execute(self, **kwargs : DataMatrix):
        inData = csiMatrix('')
        outData = self._mOutPorts[0].GetData()
        outData.data = inData.data + ' Z'

        self._mOutPorts[0].Produce()
        return True

    def _SetConfiguration(self, config: ConfigBase):
        return True

class StepE(TransformStep):
    def __init__(self, name):
        super().__init__(name)
    #   Default step has one input and output port
        self._mInPorts.AddInPort(InPort())
        self._mOutPorts.AddOutPort(OutPort())
        self._mOutPorts.AddOutPort(OutPort())

    def _Execute(self, **kwargs : DataMatrix):
        inData = self._mInPorts[0].GetData()
        outData = self._mOutPorts[0].GetData()
        outData1 = self._mOutPorts[1].GetData()

        outData.data = inData.data + ' E'
        outData1.data = inData.data + ' E'

        self._mInPorts[0].Consume()
        self._mOutPorts.ProducePorts()
        return True

    def _SetConfiguration(self, config: ConfigBase):
        return True

class StepX(SinkStep):

    def __init__(self, name):
        super().__init__(name)
    #   Default step has one input and output port
        self._mInPorts.AddInPort(InPort())
    #   self._mOutPorts.AddOutPort(OutPort())

    def _Execute(self, **kwargs : DataMatrix):
        inData = self._mInPorts[0].GetData()
        #   outData = self._mOutPorts[0].GetData()
        print('X step output:', inData.data)
        #   self.Do(inData, outData)
        self._mInPorts[0].Consume()
        return True

    def _SetConfiguration(self, config: ConfigBase):
        return True

class StepY(SinkStep):

    def __init__(self, name):
        super().__init__(name)
   #    Default step has one input and output port
        self._mInPorts.AddInPort(InPort())
   #    self._mOutPorts.AddOutPort(OutPort())

    def _Execute(self, **kwargs : DataMatrix):
        inData = self._mInPorts[0].GetData()
        print('Y step input:', inData.data)
        #   outData = self._mOutPorts[0].GetData()
        self._mInPorts[0].Consume()
        return True

    def _SetConfiguration(self, config: ConfigBase):
        return True
''' > C -> D
    |
A ->|
    > E -> Z
'''

a = StepA('A_SRC')
b = StepB('B_SRC')
c = StepC('C_TR')
d = StepD('D_TR')
e = StepE('E_TR')
x = StepX('X_SNK')
y = StepY('Y_SNK')
z = StepZ('Z_SRC')

net = StepNetwork()
net.AddStep(x)
net.AddStep(y)
net.AddStep(a)
net.AddStep(b)
net.AddStep(c)
net.AddStep(d)
net.AddStep(e)
net.AddStep(z)

# Need to modifiy these and add source and destination portNo
net.ConnectStep('A_SRC', 'C_TR', 0, 0)
net.ConnectStep('B_SRC', 'C_TR', 0, 1)
net.ConnectStep('Z_SRC', 'D_TR', 0, 0)
net.ConnectStep('C_TR', 'D_TR', 0, 1)
net.ConnectStep('D_TR', 'E_TR', 0, 0)
net.ConnectStep('E_TR', 'X_SNK', 0, 0)
net.ConnectStep('E_TR', 'Y_SNK', 1, 0)

config = StepConfig()
config.Read('../../config/default.yaml')

net.ConfigureSteps(config)
net.DoNetwork()

"""
Sample Network:
                         +--> X
A -->                    |
    |--> C --> D --> E --+
B -->          ^         |
               |         +--> Y
           Z --+
"""

'''
Configuration Example
t = StepA('StepA')
config = StepConfig()

config.Read('../../config/default.yaml')
print(config.GetStepParams('StepA'))
print(config.GetParamFromStep('StepA', 'param_1'))
print(config['StepA']['param_2'])

t.Configure(config) # Always need to call Configure !!!
t.Do()
'''