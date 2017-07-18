from BlockComponents.Step import *

class StepIFFT(TransformStep):
    def __init__(self, aProcessID):
        super().__init__(aProcessID)

    def _Execute(self, **kwargs : DataMatrix):
        return True

    def _SetConfiguration(self, config : ConfigBase):
        return True