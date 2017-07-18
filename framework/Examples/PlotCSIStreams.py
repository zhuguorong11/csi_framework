from BlockComponents.Step import *
from BlockComponents.Port import *
from Tools.CSIExtractor import *
from BlockComponents.StepNetwork import *
import matplotlib.pyplot as pl
from matplotlib import pyplot as plt
from matplotlib import cm
import numpy as np

# One improvement is stricter type checking here
# Also we have a fixed number of ports

# Sample application that demonstrates the Step, Step composite, and network advantage
class StepCSIRead(SourceStep):
    def __init__(self, aProcessID):
        super().__init__(aProcessID)
        self.deviceType = None
        self.rawFilePath = None
        self._mOutPorts.AddOutPort(OutPort())

    def _Execute(self, **kwargs : DataMatrix):
        self.deviceType = 'iwl5300'
        self.rawFilePath = '../../data/log.all_csi.6.7.6'

        device = WiFiDeviceFactory.create_device(self.deviceType)
        csiObj = CSIExtractor(device)
        csiObj.open_csi_file(self.rawFilePath)
        mtrx = csiObj.convert_to_csi_matrix()

        out = self._mOutPorts[0].GetData()
        out.data = mtrx

        self._mOutPorts.ProducePorts()
        return True

    def _SetConfiguration(self, config : ConfigBase):
        return True

class SelectCSIStreams(TransformStep):
    def __init__(self, aProcessID):
        super().__init__(aProcessID)

        self._mInPorts.AddInPort(InPort())
        self._mOutPorts.AddOutPort(OutPort())
        self._mOutPorts.AddOutPort(OutPort())
        self._mOutPorts.AddOutPort(OutPort())

    def _Execute(self, **kwargs):
        if 'data' and 'mtrx_data' in kwargs:
            out_r1 = kwargs['pair']
            csi = kwargs['mtrx_data']
            csi.data = np.absolute(csi.data[out_r1.data[0], out_r1.data[1], :, :]).T
        else:
            in_csi = self._mInPorts[0].GetData()
            out_r1 = self._mOutPorts[0].GetData()
            #    out_r2 = self._mOutPorts[1].GetData()
            #    out_r3 = self._mOutPorts[2].GetData()
            mtrx = in_csi.data

            self._mInPorts.ConsumePorts()
            self._mOutPorts.ProducePorts()

    #    problem here is we only make 1x3 plots and it is already a problem  so a solution is to make a composite
    #    out_r1.data = np.absolute(mtrx[out_r1[0], out_r1[1], :, :]).T
    #    out_r2.data = np.absolute(mtrx[0, 1, :, :]).T
    #    out_r3.data = np.absolute(mtrx[0, 2, :, :]).T


        return True

    def _SetConfiguration(self, config: ConfigBase):
        stepID = self.GetStepID()
        if config.Holds(stepID) == False:
            return False
        return True
#### ^^^^ This is one full implementation ^^^^ ####

class StepStreamsPlotComp(SinkStep, StepComposite):
    def __init__(self, aProcessID):
        # super().__init__(aProcessID)
        super(StepStreamsPlotComp, self).__init__(aProcessID)
        self._mInPorts.AddInPort(InPort())

        self.mPlot3D = StepPlot3DSurface('ChildStep')
        self.mSelect = SelectCSIStreams('ChildStep1')
        self.RegisterStep(self.mPlot3D)
        self.RegisterStep(self.mSelect)

    def _Execute(self, **kwargs):
        in_csi = self._mInPorts[0].GetData()
        mtrx = in_csi.data

        self._mInPorts.ConsumePorts()

        # Plot all pairs derived from the raw CSI data file
        if self.mSettings == 'all':
            for t in range(mtrx.tx):
                for r in range(mtrx.rcv):
                    pair = ChannelData((t, r))
                    data = ChannelData(mtrx)

                    self.mSelect.Do(pair=pair, mtrx_data=data)
                    self.mPlot3D.Do(data=data.data, label=str(t)+'x'+str(r)) #np.absolute(mtrx[t, r, :, :]).T

        # Plot the antenna pairs specified in the configuration file
        # format [2x2, 1x1, .. etc]
        elif self.mSettings == 'individual':
            for pairs in self.mPlot:
                p = pairs.split('x')
                t = int(p[0]) - 1
                r = int(p[1]) - 1
                dataPayload = np.absolute(mtrx[t, r, :, :]).T
                self.mPlot3D.Do(data=dataPayload, label=pairs)
        else:
            return False

        return True

    def _SetConfiguration(self, config: ConfigBase):
        stepID = self.GetStepID()

        if config.Holds(stepID) == False:
            return False

        self.mSettings = config[self.GetStepID()]['plot_setting'].lower()

        if self.mSettings == 'individual':
            self.mPlot = config[self.GetStepID()]['plots']

        return self.ConfigureSteps(config)

class StepPlot3DSurface(SinkStep):
    def __init__(self, aProcessID):
        super().__init__(aProcessID)
        self._mInPorts.AddInPort(InPort())

    def _Execute(self, **kwargs ):

        # Data is either passed into the Step via Do()
        # or buffered at the inPort.
        if 'data' and 'label' in kwargs:
            f = kwargs['data']
            fileLabel = '_' + kwargs['label']
        else:
            inData = self._mInPorts[0].GetData()
            self._mInPorts[0].Consume()
            f = inData.data
            fileLabel = ''

        # Coarse check for the correct dimensions
        if len(f.shape) != 2:
            raise Exception('Dimension Error')

        fig = plt.figure()
        ax = fig.gca(projection='3d')

        # Sub-carriers count (30)
        X = np.arange(0, f.shape[1], 1)
        # Samples counts (29)
        Y = np.arange(0, f.shape[0], 1)
        X, Y = np.meshgrid(X, Y)

        f[ f < 1] = np.nan
        f = 20*np.log10(f)

        norm = cm.colors.Normalize(vmin=np.nanmin(f) + 5, vmax=np.nanmax(f), clip=False)

        surf = ax.plot_surface(X, Y, f, rstride=1, cstride=1, norm=norm, cmap=cm.jet, linewidth=0, antialiased=True)
        ax.set_zlim3d(0, np.nanmax(f) + 10)
        ax.set_xlabel('Sub-carriers')
        ax.set_ylabel('Symbol samples')
        ax.set_zlabel('Amplitude (dB)')
        fig.colorbar(surf, shrink=0.5, aspect=5)

        if self.mDisplayPlot == True:
            #plt.show()
            pass
        if self.mExportFile != '':
            fig.savefig(self.mExportFile + self.GetStepID() + fileLabel + '.png')
            #pass
        return True

    def _SetConfiguration(self, config: ConfigBase):
        stepID = self.GetStepID()

        if config.Holds(stepID) == False:
            return False

        self.mExportFile = config[stepID]['export_directory']
        self.mDisplayPlot = config[stepID]['display_plot']
        return True

networkConfig = StepConfig()
networkConfig.Read('PlotCSIStreams.yaml')
plotter = StepStreamsPlotComp('ParentStep1')
csi = StepCSIRead('Input')
print('plotter', plotter.Type())
network = StepNetwork()
network.AddStep(csi)
network.AddStep(plotter)

network.ConnectStep('Input', 'ParentStep1')
network.ConfigureSteps(networkConfig)
network.SetNetworkStrategy(NetworkExecNaive())
network.DoNetwork()

'''
csi = StepCSIRead('Input')
#csi.Configure(networkConfig)
#test = DataMatrix()
#csi.Do(input=test)
#print(test.data)

plotter = StepStreamsPlotComp('ParentStep1')
# plotter.Configure(networkConfig)

# csi._mOutPorts[0].ConnectToIn(plotter._mInPorts[0])

# csi.Do()
# plotter.Do()

network = StepNetwork()
network.AddStep(csi)
network.AddStep(plotter)
network.ConnectStep('Input', 'ParentStep')
network.ConfigureSteps(networkConfig)
network.SetNetworkStrategy(NetworkExecNaive())
network.DoNetwork()
'''
'''
csi = StepCSIRead('Input')
csi.Configure(networkConfig)

app = StepPlotCSIStreams('Demux')
app.Configure(networkConfig)

x = StepPlot3DSurface('R1')
x.Configure(networkConfig)

y = StepPlot3DSurface('R2')
y.Configure(networkConfig)

z = StepPlot3DSurface('R3')
z.Configure(networkConfig)

# Put network setup in here !

# This is the simple port set-up without network
csi._mOutPorts[0].ConnectToIn(app._mInPorts[0])
app._mOutPorts[0].ConnectToIn(x._mInPorts[0])
app._mOutPorts[1].ConnectToIn(y._mInPorts[0])
app._mOutPorts[2].ConnectToIn(z._mInPorts[0])

csi.Do()
app.Do()
x.Do()
y.Do()
z.Do()
'''
