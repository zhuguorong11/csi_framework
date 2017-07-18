from abc import ABCMeta, abstractmethod
from multiprocessing import Queue, Lock, Event

import framework.thirdparty.sharedmem as sm
from BlockComponents.Enums import *

class ChannelBase(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def put(self, val):
        pass

    @abstractmethod
    def get(self):
        pass

    @abstractmethod
    def size(self):
        pass

class StreamChannel(ChannelBase):
    def __init__(self):
        super().__init__()
        self.mData = Queue()
    #   print('Queue SetUp::', self.mData.full()) This works well, but not implemented yet! check for wait signal.

    def put(self, val):
        self.mData.put(val, block=True)

    def get(self):
        return self.mData.get(block=True)

    def size(self):
        return self.mData.qsize()

class MatrixChannel(ChannelBase):
    def __init__(self, dims, type=complex):
        super().__init__()
        self.sharedData = sm.sharedmem.empty(dims, dtype=type)
        self.lock = Lock()
        self.event = Event()

    def put(self, matrixVal):
        if matrixVal.shape != self.sharedData.shape:
            raise Exception('Matrix dimension mismatch expected:', self.sharedData.shape, \
                            ' received:', matrixVal.shape)
        with self.lock:
            self.sharedData[:] = matrixVal
            self.event.set()

    def get(self):
        self.event.wait()
        with self.lock:
            self.event.clear()
            return self.sharedData

    def size(self):
        return len(self.sharedData)

class OutPort:
    def connect_port(self, inPort):
        try:
            inPort.set_channel(self._dataChannel, self._channelType)
            self._isConnected = True
        except:
            self._isConnected = False

    def put(self, val):
        if self._isConnected == False:
            raise Exception('Port not connected!')

        self._dataChannel.put(val)

    def buffer_size(self):
        return self._dataChannel.size()

    def is_connected(self):
        return self._isConnected

    def __init__(self, type, dimensions=None):
        self._isConnected = False
        self._channelType = type

        if type == ChannelType.STREAM:
            self._dataChannel = StreamChannel()
        elif type == ChannelType.MATRIX:
            self._dataChannel = MatrixChannel(dimensions)
        else:
            raise Exception('Undefined port type!')

class InPort:

    def set_channel(self, sharedDataObject, channelType):
        if channelType == self._portDataType:
            self._dataChannel = sharedDataObject
            self._isConnected = True
        else:
            raise Exception('Port types incompatible')

    def get(self):
        if self._isConnected == True:
            return self._dataChannel.get()
        else:
            raise Exception('Unconnected InPort')

    def buffer_size(self):
        return self._dataChannel.qsize()

    def is_connected(self):
        return self._isConnected

    def __init__(self, dataType):
        self._isConnected = False
        self._portDataType = dataType

class PortList:
    def __init__(self, aPortType):
        self._ports = []
        self._mPtr = 0
        self.portType = aPortType

    def __getitem__(self, item):
        return self._ports[item]

    def __setitem__(self, key, value):
        self._ports[key] = value

    def __iter__(self):
        return self

    def __next__(self):
        if self._mPtr < len(self._ports):
            self._mPtr += 1
            return self._ports[self._mPtr - 1]
        else:
            self._mPtr = 0
            raise StopIteration()

    def __delitem__(self, portNo):
        del self._ports[portNo]

    def __len__(self):
        return len(self._ports)

    def add_port(self, aDataType, dimensions=None):
        if self.portType == PortType.OUT:
            self._ports.append(OutPort(aDataType, dimensions))
        else:
            self._ports.append(InPort(aDataType))

    def count(self):
        return len(self._ports)

    def is_connected(self):
        if len(self._ports) == 0:
            return False

        for port in self._ports:
            if port.is_connected() == False:
                return False
        return True

'''
inp = InPort(ChannelType.STREAM)
outp = OutPort(ChannelType.STREAM)
outp.connect_port(inp)
outp.put('new')
print('read:', inp.get())
'''