from matplotlib import pyplot as plt

import viscid
from viscid.plot import mpl

f3d = viscid.load_file(_viscid_root + '/../../sample/sample_xdmf.3d.xdmf')

ax1 = plt.subplot2grid((2, 1), (0, 0))

# notice y=0.0, this is different from y=0; y=0 is the 0th index in
# y, which is this case will be y=-50.0
mpl.plot(f3d["pp"]["y=0.0f"], style="contourf", levels=20,
         plot_opts="log,earth")

# share axes so this plot pans/zooms with the first
plt.subplot2grid((2, 1), (1, 0), sharex=ax1, sharey=ax1)
mpl.plot(f3d["vx"]["y=0.0f"], style="contourf", levels=20,
         plot_opts="earth")

plt.xlim((-20, 20))
plt.ylim((-10, 10))