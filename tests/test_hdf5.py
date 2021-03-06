#!/usr/bin/env python
"""Test saving fields to an HDF5 + XDMF pair"""

from __future__ import print_function
import argparse
import os
import sys

import matplotlib.pyplot as plt
import numpy as np

from viscid_test_common import next_plot_fname

import viscid
from viscid import vutil
from viscid.plot import vpyplot as vlt


def _main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--show", "--plot", action="store_true")
    parser.add_argument("--keep", action="store_true")
    args = vutil.common_argparse(parser)

    # setup a simple force free field
    x = np.linspace(-2, 2, 20)
    y = np.linspace(-2.5, 2.5, 25)
    z = np.linspace(-3, 3, 30)
    psi = viscid.empty([x, y, z], name='psi', center='node')
    b = viscid.empty([x, y, z], nr_comps=3, name='b', center='cell',
                     layout='interlaced')

    X, Y, Z = psi.get_crds_nc("xyz", shaped=True)
    Xcc, Ycc, Zcc = psi.get_crds_cc("xyz", shaped=True)
    psi[:, :, :] = 0.5 * (X**2 + Y**2 - Z**2)
    b['x'] = Xcc
    b['y'] = Ycc
    b['z'] = -Zcc

    # save an hdf5 file with companion xdmf file
    h5_fname = os.path.join(viscid.sample_dir, "test.h5")
    viscid.save_fields(h5_fname, [psi, b])

    # load the companion xdmf file
    xdmf_fname = h5_fname[:-3] + ".xdmf"
    f = viscid.load_file(xdmf_fname)
    plt.subplot(131)
    vlt.plot(f['psi'], "y=0")
    plt.subplot(132)
    vlt.plot(f['b'].component_fields()[0], "y=0")
    plt.subplot(133)
    vlt.plot(f['b'].component_fields()[2], "y=0")

    plt.savefig(next_plot_fname(__file__))
    if args.show:
        plt.show()

    if not args.keep:
        os.remove(h5_fname)
        os.remove(xdmf_fname)

    return 0

if __name__ == "__main__":
    sys.exit(_main())

##
## EOF
##
