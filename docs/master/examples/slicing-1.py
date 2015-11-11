import viscid
from viscid.plot import mpl

f3d = viscid.load_file(_viscid_root + '/../../sample/sample_xdmf.3d.xdmf')

# Notice that slices by location are done by appending an 'f' to the
# slice. This means "y=0" is not the same as "y=0f".
pp = f3d["pp"]["x = 50:-12, y = 0.0f, z = -10.0f:10.0f"]
mpl.plot(pp, style="contourf", levels=50, plot_opts="log,earth")