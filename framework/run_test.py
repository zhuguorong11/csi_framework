from BlockComponents.Configuration import ConfigManager
from Blocks.step_bandpass import *

data = PrimaryMatrix(1)
data1 = PrimaryMatrix(-1)
print('data pre:', data.data)

a = BandPassFilter()
a.Configure(ConfigManager())
a.Do(data=data)

print('data post:', data.data)

