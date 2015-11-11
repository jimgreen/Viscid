import numpy as np
from matplotlib import pyplot as plt
import matplotlib.dates as mdates

import viscid
from viscid.readers import openggcm

openggcm.GGCMGrid.mhd_to_gse_on_read = 'auto'

f3d = viscid.load_file(_viscid_root + '/../../sample/sample_xdmf.3d.xdmf')

ntimes = f3d.nr_times()
t = [None] * ntimes
pressure = np.zeros((ntimes,), dtype='f4')

for i, grid in enumerate(f3d.iter_times()):
    t[i] = grid.time_as_datetime()
    pressure[i] = grid['pp']['x=10.0f, y=0.0f, z=0.0f']
plt.plot(t, pressure)
plt.ylabel('Pressure')

dateFmt = mdates.DateFormatter('%H:%M:%S')
# dateFmt = mdates.DateFormatter('%Y-%m-%d %H:%M:%S')
plt.gca().xaxis.set_major_formatter(dateFmt)
plt.gcf().autofmt_xdate()
plt.gca().grid(True)