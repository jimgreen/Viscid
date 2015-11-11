import numpy as np
from matplotlib import pyplot as plt

import viscid
from viscid.plot import mpl

f3d = viscid.load_file(_viscid_root + '/../../sample/sample_xdmf.3d.xdmf')

times = np.array([grid.time for grid in f3d.iter_times()])
nr_times = len(times)

for i, grid in enumerate(f3d.iter_times()):
    plt.subplot2grid((nr_times, 1), (i, 0))
    mpl.plot(grid["vz"]["x = -20.0f:20.0f, y = 0.0f, z = -10.0f:10.0f"],
             plot_opts="lin_0,earth")
    mpl.plt.title(grid.format_time(".01f"))
mpl.tighten()