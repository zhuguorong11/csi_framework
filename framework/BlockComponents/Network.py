from abc import abstractmethod
from framework.BlockComponents.Configuration import *
from multiprocessing import active_children
from threading import Thread

import time

class NetworkExecBase():
    def __init__(self):
        pass

    @abstractmethod
    def execute(self, aStepMap):
        pass

class NetworkExecParallel(NetworkExecBase):
    def __init__(self):
        super().__init__()

    def execute(self, blockMap):
        pass

class Network:

    def add(self, blockObj):
        self._blockMap[blockObj.blockName] = blockObj

    def remove(self, blockObj):
        try:
            self._blockMap.pop(blockObj.blockName, None)
        except:
            raise Exception(blockObj.blockName, ' not found in network')

    def connect(self, blockA, blockB, portA = 0, portB = 0):

        try:
            outPort = self._blockMap[blockA.blockName].get_outport(portA)
            inPort = self._blockMap[blockB.blockName].get_inport(portB)
            outPort.connect_port(inPort)
        except:
            raise Exception('Failed to connect blocks.')

    def run(self):
        self._monitorThreads = []

        for blockID, block in self._blockMap.items():
            if block.is_connected() is False:
                raise Exception('Unconnected block ', block.blockName)
            else:
                t = Thread(target=self._monitor_block, args=(block,))

                self._monitorThreads.append(t)
                t.start()

        for t in self._monitorThreads:
            t.join()
            # print('Active Childeren:', active_children())


    def _monitor_block(self, node):
        node.start()
        while node.exitcode is None:
            node.join()

        if node.exitcode > 0:
            print('A node exception for', node.blockName, ' forced termination of all nodes.')
            self.terminate()

    def terminate(self, blockName = None):
        if blockName == None:
            for blockID, block in self._blockMap.items():
                block.terminate()
        else:
            block = self._blockMap[blockName]
            block.terminate()

    def configure(self, config : Configuration):
        for blockID, block in self._blockMap.items():
            block.configure(config)

    def __init__(self):
        self._blockMap = {}
        self._executionStrat = NetworkExecParallel()
