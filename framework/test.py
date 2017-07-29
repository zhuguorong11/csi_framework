from urllib.request import urlopen
from io import BytesIO, StringIO
import csv
import numpy as np
from datetime import datetime
import scipy.signal as signal
import matplotlib.pyplot as plt

#----- Test Code ------
import time, os
file = open('csi_test.dat')
file1 = open('csi_test1.dat')

while 1:
    where = file.tell()
    line = file.readline()
    if not line:
        time.sleep(1)
        file.seek(where)
    else:
        print(line)
        file1.write(line)
        file1.flush()
        os.fsync(file1.fileno())
# ------ End Test Code -----


startdate = '20111118'
enddate = '20121125'

# Read data from LOBO buoy
response = urlopen('http://lobo.satlantic.com/cgi-data/nph-data.cgi?min_date='
                           + startdate + '&max_date=' + enddate + '&y=temperature')

data = BytesIO(response.read()).read().decode('UTF-8')
data = StringIO(data)

r = csv.DictReader(data,
                   dialect=csv.Sniffer().sniff(data.read(1000)))
data.seek(0)

# Break the file into two lists
date, temp = [], []
date, temp = zip(*[(datetime.strptime(x['date [AST]'], "%Y-%m-%d %H:%M:%S"), \
                    x['temperature [C]']) for x in r if x['temperature [C]'] is not None])

# temp needs to be converted from a "list" into a numpy array...
temp = np.array(temp)
temp = temp.astype(np.float)  # ...of floats
print(temp)
exit()

# First, design the Buterworth filter
N = 2  # Filter order
Wn = 0.01  # Cutoff frequency
B, A = signal.butter(N, Wn, output='ba')

# Second, apply the filter
tempf = signal.filtfilt(B, A, temp)

# Make plots
fig = plt.figure()
ax1 = fig.add_subplot(211)
plt.plot(date, temp, 'b-')
plt.plot(date, tempf, 'r-', linewidth=2)
plt.ylabel("Temperature (oC)")
plt.legend(['Original', 'Filtered'])
plt.title("Temperature from LOBO (Halifax, Canada)")
ax1.axes.get_xaxis().set_visible(False)

ax1 = fig.add_subplot(212)
plt.plot(date, temp - tempf, 'b-')
plt.ylabel("Temperature (oC)")
plt.xlabel("Date")
plt.legend(['Residuals'])

plt.show()