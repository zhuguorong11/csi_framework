from BlockComponents.Configuration import *

class ProcessBase ( metaclass = ABCMeta ):

    @abstractmethod
    def Transform(self, data):
        pass

    @abstractmethod
    def Configure(self, configObj : ConfigManager):
        pass

    def Do(self, data):
        output = self.Transform(data)

        if self.port.isConnected == True:
            self.port.Input(output)

    def Attach(self, nextProcessObj):
        self.port.ConnectOut(nextProcessObj)

    def Detach(self):
        self.port.Disconnect()
        pass

    def __init__(self, configObj = None):
        self.port = Ports()
        self.result = 1
        pass

class ProcessComposite (ProcessBase):
    pass

class PortBase():
    def __init__(self):
        pass

class InPort(PortBase):
    def __init__(self):
        super().__init__()
        pass

class OutPort(PortBase):
    def __int__(self):
        super().__init__()
        pass

class Ports ():

    def Input(self, dataObj):
        self.outputPort.Do(dataObj)

    def ConnectOut(self, processObj : ProcessBase):
        self.outputPort = processObj
        self.isConnected = True

    def Disconnect(self):
        self.outputPort = None
        self.isConnected = False

    def __init__(self):
        self.outputPort = None
        self.isConnected = False

class InverseProcess (ProcessBase):
    def Transform(self, data : list):
        data.data = [-1*x for x in data.data]
        return data
    pass

    def Configure(self, configObj):
        pass

    def __init__(self):
        super().__init__()
        pass

class ScaleProcess (ProcessBase):
    def Transform(self, data : list):
        data.data = sum([10*x for x in data.data])
        return data

    def Configure(self, configObj):
        pass

    def __init__(self):
        super().__init__()

class ScaleInverseProcess (ProcessBase):
    def Transform(self, data):
        test = InverseProcess()
        next = ScaleProcess()

        test.Attach(next)
        result = test.Do(data)
        return result

    def Configure(self, configObj : ConfigManager):
        pass

    def __init__(self):
        super().__init__()

class dataObj:
    def __init__(self, x):
        self.data = x

data = dataObj([1,2,3,4,5,6,7,8,9])

test = ScaleInverseProcess()
test.Do(data)

print('tt', data.data)
print(data.data)


