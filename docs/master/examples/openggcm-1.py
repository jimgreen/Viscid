import viscid
from viscid.readers import openggcm
from viscid.plot import mpl

openggcm.GGCMGrid.mhd_to_gse_on_read = 'auto'

f3d = viscid.load_file(_viscid_root + '/../../sample/sample_xdmf.3d.xdmf')
pp = f3d["pp"]["x = -20.0f:20.0f, y = 0.0f, z = -10.0f:10.0f"]
mpl.plot(pp, plot_opts="log,x_-30_15", earth=True)
mpl.plt.title(pp.format_time("UT"))