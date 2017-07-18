import yaml
from abc import ABCMeta, abstractmethod

class Configuration(metaclass=ABCMeta):
    @abstractmethod
    def __getitem__(self, item):
        pass

    @abstractmethod
    def __setitem__(self, key, value):
        pass

    @abstractmethod
    def set_block_parameter(self, aBlockID, aParamKey, aValue):
        pass

    @abstractmethod
    def get_block_parameters(self, aBlockID):
        pass

    @abstractmethod
    def write(self, aFilePath):
        pass

    @abstractmethod
    def read(self, aFilePath):
        pass

    @abstractmethod
    def exists(self, aBlockID):
        pass

class BlockConfiguration(Configuration):

    def __getitem__(self, item):
        return self._mConfigFile[item]

    def __setitem__(self, key, value):
        self._mConfigFile[key] = value

    def set_block_parameter(self, aBlockID, aParamKey, aValue):
        self._mConfigFile[aBlockID][aParamKey] = aValue

    def get_block_parameters(self, aBlockID):
        return self._mConfigFile[aBlockID]

    def exists(self, aBlockID):
        if aBlockID in self._mConfigFile:
            return True
        else:
            return False

    def write(self, aFilePath):
        with open(aFilePath, 'w') as stream:
            try:
                yaml.dump(self._mConfigFile, stream, default_flow_style = False)
            except yaml.YAMLError as exc:
                print(exc)
                return False
        return True

    def read(self, aFilePath):
        with open(aFilePath, 'r') as stream:
            try:
                self._mConfigFile = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                return False
            return True

    def __init__(self):
        self._mConfigFile = {}
