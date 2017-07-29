from abc import ABCMeta, abstractmethod
from Tools.ExtractorDeviceFactory import *

class DeviceExtractorBase( metaclass = ABCMeta ):
    def __init__(self, aExtractorService):
        self._mExtractor = aExtractorService
        self._mSymbolData = None

    def receiver_antenna_count(self):
        self._mExtractor.get_receiver_count()

    def transmitter_antenna_count(self):
        self._mExtractor.get_transmitter_count()

    def symbol_count(self):
        self._mExtractor.get_symbol_count()

class CSIExtractor(DeviceExtractorBase):
    def __init__(self, aExtractorService):
        super().__init__(aExtractorService)

    def sub_carrier_count(self):
        return self._mExtractor.device_subcarriers()

    def get_csi(self):
        return self._mExtractor.get_csi_symbols()

    def open_csi_file(self, aFilePath):
        self._mExtractor.open(aFilePath)

    def open_stream(self, aStreamLocation, mode = 0, bufferSize = 1):
        return self._mExtractor.open_stream(aStreamLocation, mode, bufferSize)

    def convert_to_csi_matrix(self):
        return self._mExtractor.convert_to_csi_matrix()

class RSSIExtractor(DeviceExtractorBase):
    def __init__(self, aExtractorService):
        super().__init__(aExtractorService)

    def get_rssi(self):
        self._mExtractor.get_full_RSSI()

    def get_scaled_rssi(self):
        self._mExtractor.get_scaled_RSSI()

    def open_rssi_file(self, aFilePath):
        self._mExtractor.ParseSymbolFile(aFilePath)
