import viscid
from viscid.plot import mpl

f3d = viscid.load_file(_viscid_root + '/../../sample/sample_xdmf.3d.xdmf')
# notice y=0.0, this is different from y=0; y=0 is the 0th index in
# y, which is this case will be y=-50.0
pp = f3d["pp"]["y=0.0f"]
mpl.plot(pp, plot_opts="log")