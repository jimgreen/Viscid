import numpy as np

import viscid
from viscid.plot import mpl

viscid.readers.openggcm.GGCMGrid.mhd_to_gse_on_read = 'auto'

f3d = viscid.load_file(_viscid_root + '/../../sample/sample_xdmf.3d.xdmf')
B = f3d['b']['x=-40f:15f, y=-20f:20f, z=-20f:20f']

# Fields can be used as seeds to get one seed per grid point
seeds = B.slice_keep('y=0f')
lines, topo_night = viscid.calc_streamlines(B, seeds, ibound=2.5,
                                            output=viscid.OUTPUT_BOTH)
xpts_night = viscid.find_sep_points_cartesian(topo_night['x=:0f, y=0f'])

# The dayside is done separately here because the sample data is at such
# low resolution. Super-sampling the grid with the seeds can sometimes help
# in these cases.
day_seeds = viscid.Volume((7.0, 0.0, -5.0), (12.0, 0.0, 5.0), (16, 1, 16))
_, topo_day = viscid.calc_streamlines(B, day_seeds, ibound=2.5,
                                      output=viscid.OUTPUT_TOPOLOGY)
xpts_day = viscid.find_sep_points_cartesian(topo_day)

log_bmag = np.log(viscid.magnitude(B))

clim = (min(np.min(topo_day), np.min(topo_night)),
        max(np.max(topo_day), np.max(topo_night)))
mpl.plot(topo_night, cmap='afmhot', clim=clim)
mpl.plot(topo_day, cmap='afmhot', clim=clim, colorbar=None)

mpl.plot2d_lines(lines[::79], scalars=log_bmag, symdir='y')
mpl.plt.plot(xpts_night[0], xpts_night[1], 'y*', ms=20,
             markeredgecolor='k', markeredgewidth=1.0)
mpl.plt.plot(xpts_day[0], xpts_day[1], 'y*', ms=20,
             markeredgecolor='k', markeredgewidth=1.0)
mpl.plt.xlim(topo_night.xl[0], topo_night.xh[0])
mpl.plt.ylim(topo_night.xl[2], topo_night.xh[2])

# since seeds is a Field, we can use it to determine mhd|gse
mpl.plot_earth(seeds.slice_reduce(":"))