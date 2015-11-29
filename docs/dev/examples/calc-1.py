import numpy as np

import viscid
from viscid.plot import mpl

viscid.readers.openggcm.GGCMGrid.mhd_to_gse_on_read = 'auto'

f3d = viscid.load_file(_viscid_root + '/../../sample/sample_xdmf.3d.xdmf')
B = f3d['b']['x=-40f:15f, y=-20f:20f, z=-20f:20f']

# # these seeds can be made a little more sparse than the actual grid if
# # speed is more important than resolution
# seeds = viscid.Volume((-30.0, 0.0, -10.0), (+10.0, 0.0, +10.0), (64, 1, 32))
seeds = B.slice_and_keep('y=0f')
lines, topo = viscid.calc_streamlines(B, seeds, ibound=2.5,
                                      output=viscid.OUTPUT_BOTH)

# note that this requires so many iterations because the sample data is
# at such low resolution and the dayside current sheet is so extended
xpts_night = viscid.find_sep_points_cartesian(topo['x=:0f, y=0f'])

# bz = B['x, y=0f']
log_bmag = np.log(viscid.magnitude(B))

mpl.plot(topo, cmap='afmhot')
mpl.plot2d_lines(lines[::79], scalars=log_bmag, symdir='y')
mpl.plt.plot(xpts_night[0], xpts_night[1], 'y*', ms=20,
             markeredgecolor='k', markeredgewidth=1.0)
mpl.plt.xlim(topo.xl[0], topo.xh[0])
mpl.plt.ylim(topo.xl[2], topo.xh[2])