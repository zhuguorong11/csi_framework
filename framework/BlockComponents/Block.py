from multiprocessing import Process
from BlockComponents.Configuration import *
from BlockComponents.Port import *
from framework.BlockData.BlockMatrix import *

# Force reference passing on immutable data.
class DataWrapper:
    def __init__(self, val=None):
        self.data = val

class BlockBase (Process, metaclass=ABCMeta):

    # Template method set up for execution
    @abstractmethod
    def _execute(self, **kwargs) -> bool:
        pass

    # Template method to handle configuration of encapsulated algorithm
    @abstractmethod
    def _set_configuration(self, config : Configuration) -> bool:
        pass

    # Template method to check ports for network object
    @abstractmethod
    def is_connected(self) -> bool:
        pass

    def terminate(self):
        if self._mBlockState == BlockStatus.RUNNING:
            print('Block Terminated ', self.blockName)
            super().terminate()
            self._mBlockState = BlockStatus.UNCONFIGURED
        else:
            raise Exception('Process is not running')

    # Overwrite Process start method with step state logic, before calling start process of parent.
    def start(self):
        if self._mBlockState == BlockStatus.READY:
            self._mBlockState = BlockStatus.STARTED
            super().start()
            self._mBlockState = BlockStatus.RUNNING
        elif self._mBlockState == BlockStatus.UNCONFIGURED:
            raise Exception('Block is UNCONFIGURED')
        elif self._mBlockState == BlockStatus.RUNNING:
            raise Exception('Block is still PROCESSING')
        else:
            raise Exception('Failed to start block processing for:', self._blockID)

    # Multiprocessing mode
    def run(self):
        if self._mBlockState == BlockStatus.STARTED:

            if self._execute() == False:
                raise Exception('Node failed')
            else:
                self._mBlockState = BlockStatus.READY
        else:
            raise Exception('Block is not ready')

    # Use only for standalone mode.
    def do(self, **kwargs):
        if self._mBlockState == BlockStatus.READY:
            self._mBlockState = BlockStatus.RUNNING

            if self._execute(**kwargs) == True:
                self._mBlockState = BlockStatus.READY
            else:
                self._mBlockState = BlockStatus.UNCONFIGURED

        elif self._mBlockState == BlockStatus.UNCONFIGURED:
            raise Exception('Step is UNCONFIGURED')
        elif self._mBlockState == BlockStatus.RUNNING:
            raise Exception('Step is still PROCESSING')
        else:
            raise Exception('Failed to start step processing for:', self._blockID)

    def configure(self, config : Configuration):
        # We pass some parameters to the base configuration class first. (Template Method Pattern)
        if self._mBlockState not in [BlockStatus.RUNNING, BlockStatus.STARTED]:
            if self._set_configuration(config) == True:
                self._mBlockState = BlockStatus.READY
            else:
                self._mBlockState = BlockStatus.UNCONFIGURED
        else:
            raise Exception('Can not configure running block!')

    def get_outport(self, portID):
        if self._mOutPorts != None:
            return self._mOutPorts[portID]
        else:
            raise NotImplementedError

    def get_inport(self, portID):
        if self._mInPorts != None:
            return self._mInPorts[portID]
        else:
            raise NotImplementedError

    def get_block_id(self):
        return self._blockID

    def __init__(self, uniqueBlockName):
        super(BlockBase, self).__init__()
        self._blockID = self.__class__.__name__ + '_' + uniqueBlockName
        self.blockName = uniqueBlockName
        self._mBlockState = BlockStatus.UNCONFIGURED
        self._mInPorts = None
        self._mOutPorts = None

class SourceBlock(BlockBase, metaclass=ABCMeta):
    @staticmethod
    def type():
        return BlockType.SOURCE

    def is_connected(self):
        return self._mOutPorts.is_connected()

    def __init__(self, stepID):
        super().__init__(stepID)
        self._mOutPorts = PortList(PortType.OUT)

class TransformBlock(BlockBase, metaclass=ABCMeta):
    @staticmethod
    def type():
        return BlockType.TRANSFORM

    def is_connected(self):
        return self._mOutPorts.is_connected() and self._mInPorts.is_connected()

    def __init__(self, stepID):
        super().__init__(stepID)
        self._mInPorts = PortList(PortType.IN)
        self._mOutPorts = PortList(PortType.OUT)

class SinkBlock(BlockBase, metaclass=ABCMeta):
    @staticmethod
    def type():
        return BlockType.SINK

    def is_connected(self):
        return self._mInPorts.is_connected()

    def __init__(self, stepID):
        super().__init__(stepID)
        self._mInPorts = PortList(PortType.IN)

class BlockComposite (BlockBase):

    def register(self, blockObj : BlockBase):
        self.mChildBlocks.append(blockObj)

    def configure(self, config : Configuration):

        try:
            for block in self.mChildBlocks:
                block.Configure(config)
        except:
            return False

        return True

    def __init__(self, aBlockID):
        super().__init__(aBlockID)
        self.mChildBlocks = []


