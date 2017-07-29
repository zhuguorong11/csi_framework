from BlockComponents.InPort import *
from BlockComponents.InPortList import *
from BlockComponents.OutPort import *
from BlockComponents.OutPortList import *
from BlockComponents.Step import ProcessBase


class ProcessType: SOURCE, SINK, TRANSFORM, ANALYSIS = range(4)

### Works now ok
#test = InPortList(InPort())
#print('test:', test[0])

class StepBase:
    def GetName(self):
        return self.name

    def InPortsCanConsume(self):
        # For all processes except Sources, we can only consume after data has been produced at the input.
        return self._mInPorts.CanConsume()

    def IsConnected(self):
        return self._mOutPorts.AllPortsConnected() or self._mInPorts.AllPortsConnected()

    def ShowConnections(self):
        print(self.name)
        self._mInPorts.ShowAllConnections()
        self._mOutPorts.ShowAllConnections()

    def GetInPort(self, portNo = 0):
        return self._mInPorts[portNo]

    def GetOutPort(self, portNo = 0):
        return self._mOutPorts[portNo]

    def __init__(self, name):
        self.name = name
        self._mInPorts = InPortList()
        self._mOutPorts = OutPortList()

class ProcA (ProcessBase):
    def Type(self):
        return ProcessType.SINK

    def __init__(self):
        super().__init__('ProcA')

        # Default step has one input and output port
        self._mInPorts.AddInPort(InPort())
        self._mOutPorts.AddOutPort(OutPort())

    def Do(self):
        inData = self._mInPorts[0].GetData()
        outData = self._mOutPorts[0].GetData()

        outData.data = inData.data + ' A'
        self._mInPorts[0].Consume()
        self._mOutPorts[0].Produce()

class ProcGenerator(ProcessBase):
    def Type(self):
        return ProcessType.SOURCE

    def __init__(self):
        super().__init__('Generator')

        # Default step has one input and output port
        self._mInPorts.AddInPort(InPort())
        self._mOutPorts.AddOutPort(OutPort())

    def Do(self):
        # inData = self._inPort.GetData()
        inData = PrimaryMatrix('Start:')
        outData = self._mOutPorts[0].GetData()
        outData.data = inData.data + ' G'

        self._mOutPorts[0].Produce()

class ProcB (ProcessBase):
    def Type(self):
        return ProcessType.TRANSFORM

    def __init__(self):
        super().__init__('ProcB')

        # Default step has one input and output port
        self._mInPorts.AddInPort(InPort())
        self._mOutPorts.AddOutPort(OutPort())

    def Do(self):
        inData = self._mInPorts[0].GetData()
        outData = self._mOutPorts[0].GetData()
        outData.data = inData.data + ' B'
        self._mInPorts[0].Consume()
        self._mOutPorts[0].Produce()

class ProcE(ProcessBase): #Sink Process
    def __init__(self):
        super().__init__('ProcE')

    def DummyDo(self):
        inData = self._mInPorts[0].GetData()
        outData = self._mOutPorts[0].GetData()
        #self.Do(inData, outData)
"""
b = ProcB()
c = ProcE()
a = ProcA()
#b = ProcB()
d = ProcGenerator()
#d._outPort.ConnectToIn(a._inPort)

net = StepNetwork()
net.AddStep('GEN', d)
net.AddStep('PROC_B', b)
net.AddStep('SK', a)
net.ConnectStep('GEN', 'PROC_B')
net.ConnectStep('PROC_B', 'SK')
net.DoProcessing()

d.ShowConnections()
a.ShowConnections()
print(a._mOutPorts[0].GetData().data)
"""
#a._outPort.ConnectToIn(b._inPort)
#b._outPort.ConnectToIn(c._inPort)

#d.ShowConnections()
#a.ShowConnections()
#b.ShowConnections()
#c.ShowConnections()

#inputMatrix = PrimaryMatrix('A ')
#d.DummyDo(inputMatrix)
#a.DummyDo()
#b.DummyDo()
#c.DummyDo()
#print(c._outPort.GetData().data)
