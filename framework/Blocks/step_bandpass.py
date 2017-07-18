from BlockComponents.Port import *
from BlockComponents.Step import *

class StepA (SourceStep):
    def __init__(self):
        super().__init__('ProcA')

    #   Default step has one input and output port
    #   self._mInPorts.AddInPort(InPort())
        self._mOutPorts.AddOutPort(OutPort()) # should this be internal to Step (?) -> Might want to attach stuff to a Source or Sink Step

    def Do(self):
        inData = csiMatrix('')
        outData = self._mOutPorts[0].GetData()
        outData.data = inData.data + ' A'

        self._mOutPorts[0].Produce()

class BandPassFilter (StepBase):
    # Protected Methods
    # Return True or False on success/failure
    def _Execute(self, **kwargs : DataMatrix):
        data = kwargs['data']
        data.data = data.data * 2
        return True

    # Use this method to set Configuration parameters of the module.
    # Return True after configuration
    def _SetConfiguration(self, config : ConfigBase):
        # Use the set processName to extract the correct configurations from the config classess
        return True

    def __init__(self, uniqueStepName):
        super().__init__(uniqueStepName)
        self._mOutPorts.AddOutPort(OutPort()) # should this be internal to Step (?) -> Might want to attach stuff to a Source or Sink Step

