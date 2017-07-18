from Blocks.step_bandpass import *

class FilterComposite (StepComposite):

    def _Execute(self, **kwargs : DataMatrix):
        data = kwargs['data']
        self.mFilterA.Do(data=data)
        self.mFilterB.Do(data=data)
        return True

    def _SetConfiguration(self, config : ConfigBase):
        return self.ConfigureSteps(config)

    def __init__(self):
        super().__init__()

        self.mFilterA = BandPassFilter('FilterA')
        self.mFilterB = BandPassFilter('FilterB')

        self.RegisterStep(self.mFilterA)
        self.RegisterStep(self.mFilterB)

print('testing code:')
comp = FilterComposite()
#comp.Configure(StepConfig())

tdata = csiMatrix(-1)
comp.Do(data=tdata)
print('final val:', tdata.data)