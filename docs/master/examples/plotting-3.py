import viscid
from viscid.plot import mpl

f3d = viscid.load_file(_viscid_root + '/../../sample/sample_xdmf.3d.xdmf')

ax1 = mpl.plt.subplot2grid((2, 1), (0, 0))
f3d.activate_time(0)

# notice y=0.0, this is different from y=0; y=0 is the 0th index in
# y, which is this case will be y=-50.0
mpl.plot(f3d["vz"]["x = -20.0f:20.0f, y = 0.0f, z = -10.0f:10.0f"],
         style="contourf", levels=50, plot_opts="lin_0,earth")
mpl.plt.title(f3d.get_grid().format_time("UT"))

# share axes so this plot pans/zooms with the first
mpl.plt.subplot2grid((2, 1), (1, 0), sharex=ax1, sharey=ax1)
f3d.activate_time(-1)
mpl.plot(f3d["vz"]["x = -20.0f:20.0f, y = 0.0f, z = -10.0f:10.0f"],
         style="contourf", levels=50, plot_opts="lin_0,earth")
mpl.plt.title(f3d.get_grid().format_time("hms"))
mpl.tighten()