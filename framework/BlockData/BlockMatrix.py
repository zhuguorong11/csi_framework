import numpy as np
#from Tools.CSIExtractor import *
from abc import ABCMeta, abstractmethod

import pickle

class PickleFile():
    def __init__(self):
        pass

    def Read(self, aFilePath):
        return pickle.load(open(aFilePath, "rb"))

    def Write(self, aData, aFilePath):
        pickle.dump(aData, open(aFilePath, "wb"))

class BlockData(np.ndarray, metaclass=ABCMeta):
    def __new__(cls, x, type):
        obj = np.ndarray.__new__(cls, x, type)
        obj.fill(0) # set all values to zero
        return obj

    def __array_wrap__(self, out_arr, context=None):
        return np.ndarray.__array_wrap__(self, out_arr, context)

    def __reduce__(self):
        pickled_state = super(BlockData, self).__reduce__()
        new_state = pickled_state[2] + self._data_attributes() # Need to put all swag in here
        return (pickled_state[0], pickled_state[1], new_state)

    @abstractmethod
    def __setstate__(self, state):
        super(BlockData, self).__setstate__(state)

    @abstractmethod
    def _data_attributes(self):
        return ()

    @abstractmethod
    def set(self, aMatrix):
        pass # this doesnt work as well

    def store(self, aFilePath, ioHandle = PickleFile()):
        ioHandle.Write(self, aFilePath)

    def load(self, aFilePath, ioHandle = PickleFile()):
        self.set(ioHandle.Read(aFilePath))

class csiSequence(BlockData):
    def __new__(cls, s):

        # Set object information here
        obj = super().__new__(cls, (s), complex)
        obj.frms = s
        return obj

    def __array_finalize__(self, obj):
        if obj is None: return
        self.frms = getattr(obj, 'frms', None)

    def _data_attributes(self):
        return (self.frms,)

    # Need this to customize pickling
    def __setstate__(self, state):
        self.frms = state[-1]
        super(BlockData, self).__setstate__(state[0:-1])

    def set(self, aSequence):
        self[...] = aSequence

class frameMatrix(BlockData):
    def __new__(cls, trans, recv, k):
        obj = super().__new__(cls, (trans, recv, k), complex)

        # Set object information here
        obj.tx = trans
        obj.rcv = recv
        obj.k = k
        return obj

    def __array_finalize__(self, obj):
        if obj is None: return
        self.tx = getattr(obj, 'tx', None)
        self.rcv = getattr(obj, 'rcv', None)
        self.k = getattr(obj, 'k', None)

    def _data_attributes(self):
        return(self.tx, self.rcv, self.k)

    # Need this to customize pickling
    def __setstate__(self, state):
        self.tx = state[-3]
        self.rcv = state[-2]
        self.k = state[-1]

        super(BlockData, self).__setstate__(state[0:-3])

    def set(self, aMatrix):
        self[:, :, :] = aMatrix

    def set_element(self, tx, rcv, k, elemVal : complex):
        self[tx, rcv, k] = elemVal

    def get_element(self, tx,rcv, k):
        return self[tx, rcv, k]

    # Get an x-section of the 2d matrix
    def view_by_transmitter(self, tx):
        return self[tx, :, :]
    def set_by_transmitter(self, arr, tx):
        self[tx, :, :] = arr
    def view_by_receiver(self, rcv):
        return self[:, rcv, :]
    def set_by_receiver(self, arr, rcv):
        self[:, rcv, :] = arr
    def view_by_carrier(self, k):
        return self[:, :, k]
    def set_by_carrier(self, arr, k):
        self[:, :, k] = arr

class csiMatrix(BlockData):
    def __new__(cls, trans, recv, k, s):
        obj = super().__new__(cls, (trans,recv,k, s), complex)

        # Set object information here
        obj.tx = trans
        obj.rcv = recv
        obj.k = k
        obj.frms = s
        return obj

    def __array_finalize__(self, obj):
        if obj is None: return
        self.tx = getattr(obj, 'tx', None)
        self.rcv = getattr(obj, 'rcv', None)
        self.k = getattr(obj, 'k', None)
        self.frms = getattr(obj, 'frms', None)

    def _data_attributes(self):
        return (self.tx, self.rcv, self.k, self.frms)

    # Need this to customize pickling
    def __setstate__(self, state):
        self.tx = state[-4]
        self.rcv = state[-3]
        self.k = state[-2]
        self.frms = state[-1]
        super(BlockData, self).__setstate__(state[0:-4])

    def set(self, aMatrix):
        self[:, :, :, :] = aMatrix

    def get_frame(self, frameIndex):
        frame = frameMatrix(self.tx, self.rcv, self.k)
        frame.set(self[:, :, :, frameIndex])
        return frame

    def view_frame(self, frameIndex):
        return self[:, :, :, frameIndex]

    def set_frame(self, frameIndex, arrFrame : frameMatrix):
        self[:, :, :, frameIndex] = arrFrame

    def get_stream(self, trans, recv, subIndex):
        sequence = csiSequence(self.frms)
        sequence.set(self[trans, recv, subIndex, :]) #.copy()
        return sequence

    def view_stream(self, trans, recv, subIndex):
        return self[trans, recv, subIndex, :]

    def set_stream(self, trans, recv, subIndex, arrStream):
        self[trans, recv, subIndex, :] = arrStream

    def view_segment(self, sStart, sEnd):
        return self[:, :, :, sStart : sEnd]

    def get_segment(self, sStart, sEnd):
        matrix = csiMatrix(self.tx, self.rcv, self.k, sEnd - sStart)
        matrix.set(self[:, :, :, sStart : sEnd])
        return matrix

    def set_segment(self, mtrxSegment, sStart, sEnd):
        self[:, :, :, sStart : sEnd] = mtrxSegment

class fMatrix(BlockData):
    def __new__(cls, samples, features):
        # Set object information here
       # obj = super().__new__(cls, samples, 'int32, ' + str(features) + 'float32')
        obj = super().__new__(cls, (samples, features), float)
        obj.samples = samples
        obj.features = features
        return obj

    def __array_finalize__(self, obj):
        if obj is None: return
        self.samples = getattr(obj, 'samples', None)
        self.features = getattr(obj, 'features', None)

    def _data_attributes(self):
        return (self.samples, self.features)

    # Need this to customize pickling
    def __setstate__(self, state):
        self.samples = state[-1]
        self.features = state[-2]
        super(BlockData, self).__setstate__(state[0:-2])

    def set_features(self, sampleIndex, fList):
        self[sampleIndex] = np.array(fList)

    def set_feature(self, sampleIndex, featureIndex, value):
        self[sampleIndex][featureIndex] = value

    def get_class(self):
        return self[:, 0].toList()

    def get_features(self):
        return self[:, 1:]

    def set(self, fMatrix):
        self[...] = fMatrix
"""
test1 = fMatrix(10, 3)
test = fMatrix(10, 3)

test.fill(10)
test1.Set(test)
# print(test1.GetFeatures())
a = csiStream(10)
a.fill(1)
print(a)

# a.Store('new.pkl')
# a.Load('new.pkl')

#print(x)

z = frameMatrix(3, 3, 30)
x = frameMatrix(3, 3, 30)
x.fill(4)
np.save('test',x)
z = np.load('test.npy')
# x.Store('data.pkl')
# z.Load('data.pkl')
print(z)
# z.Set(x)
# print(z)

x = csiMatrix(3, 3, 30, 10)
y = csiMatrix(3, 3, 30, 10)
x.fill(4)
z = y.GetFrame(8)#.copy()
# print(type(z))
# print(z.shape)
# z.fill(44)
# y.SetFrame(8, z)
test = y.GetSegment(8, 9)
# print(z.shape)
z.fill(22)
# test.fill(33)
# print(y[:,:,:,8])
# print(z.k)
# print(test.shape)
# y.SetSegment(test, 8, 10) # [8, 10)

# print(y[:,:,:,9])
y.fill(6)
x.fill(5)

x = np.multiply(x,y)
# print(x.GetFrame(3))
# print(frameMatrix(1,5,1))
x.SetFrame(3, z)
# print(x[:,:,:,3])
"""