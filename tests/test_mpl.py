#!/usr/bin/env python
"""Kick the tires on making some simple matplotlib plots"""

from __future__ import print_function
import argparse
import sys

import numpy as np
import matplotlib.pyplot as plt

from viscid_test_common import next_plot_fname

import viscid
from viscid import logger
from viscid import vutil
from viscid.plot import vpyplot as vlt


dtype = 'float64'


def run_mpl_testA(show=False):
    logger.info("2D cell centered tests")

    x = np.array(np.linspace(-10, 10, 100), dtype=dtype)
    y = np.array(np.linspace(-10, 10, 120), dtype=dtype)
    z = np.array(np.linspace(-1, 1, 2), dtype=dtype)

    fld_s = viscid.empty([x, y, z], center='cell')
    Xcc, Ycc, Zcc = fld_s.get_crds_cc(shaped=True)  # pylint: disable=unused-variable
    fld_s[:, :, :] = np.sin(Xcc) + np.cos(Ycc)

    nrows = 4
    ncols = 1

    plt.subplot2grid((nrows, ncols), (0, 0))
    vlt.plot(fld_s, "y=20f", show=False, plot_opts="lin_0")
    plt.subplot2grid((nrows, ncols), (1, 0))
    vlt.plot(fld_s, "x=0f:20f,y=0f:5f", earth=True, show=False,
             plot_opts="x_-10_0,y_0_7")
    plt.subplot2grid((nrows, ncols), (2, 0))
    vlt.plot(fld_s, "y=0f", show=False, plot_opts="lin_-1_1")
    plt.subplot2grid((nrows, ncols), (3, 0))
    vlt.plot(fld_s, "z=0f,x=-20f:0f", earth=True, show=False, plot_opts="lin_-5_5")

    plt.suptitle("2d cell centered")
    vlt.auto_adjust_subplots()

    plt.savefig(next_plot_fname(__file__))
    if show:
        vlt.mplshow()

def run_mpl_testB(show=False):
    logger.info("3D node centered tests")

    x = np.array(np.linspace(-10, 10, 100), dtype=dtype)
    y = np.array(np.linspace(-10, 10, 120), dtype=dtype)
    z = np.array(np.linspace(-10, 10, 140), dtype=dtype)

    fld_s = viscid.empty([x, y, z], center='node')
    X, Y, Z = fld_s.get_crds_nc(shaped=True)  # pylint: disable=W0612
    fld_s[:, :, :] = np.sin(X) + np.cos(Y) - np.cos(Z)
    # print("shape: ", fld_s.data.shape)

    nrows = 4
    ncols = 1

    plt.subplot2grid((nrows, ncols), (0, 0))
    vlt.plot(fld_s, "z=0,x=:30", earth=True, plot_opts="lin_0")
    plt.subplot2grid((nrows, ncols), (1, 0))
    vlt.plot(fld_s, "z=0.75f,x=-4:-1,y=-3f:3f", earth=True)
    plt.subplot2grid((nrows, ncols), (2, 0))
    vlt.plot(fld_s, "x=-0.5f:,y=-3f:3f,z=0f", earth=True)
    plt.subplot2grid((nrows, ncols), (3, 0))
    vlt.plot(fld_s, "x=0.0f,y=-5.0f:5.0f", earth=True, plot_opts="log,g")

    plt.suptitle("3d node centered")
    vlt.auto_adjust_subplots()

    plt.savefig(next_plot_fname(__file__))
    if show:
        vlt.mplshow()

def _main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--show", "--plot", action="store_true")
    args = vutil.common_argparse(parser)

    run_mpl_testA(show=args.show)
    run_mpl_testB(show=args.show)

    return 0

if __name__ == "__main__":
    sys.exit(_main())

##
## EOF
##
