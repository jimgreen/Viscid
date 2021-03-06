.. Viscid documentation master file, created by
   sphinx-quickstart on Tue Jul  2 01:44:29 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Viscid: Visualizing Plasma Simulations in Python
================================================

.. raw:: html

    <style type="text/css">
    div.figure img {
        border-radius: 25px;
    }
    </style>

.. figure:: images/3d_cropped.png
    :align: right
    :width: 400px
    :alt: Mayavi Example
    :target: tutorial/mayavi.html

Viscid is a python framework to visualize scientific data on structured meshes. The following file types are understood,

+ XDMF + HDF5
+ OpenGGCM jrrle (3df, p[xyz], iof)
+ OpenGGCM binary (3df, p[xyz], iof)
+ Athena (bin, hst, tab)
+ ASCII

There is also preliminary support for reading and plotting AMR datasets from XDMF files.

Below are some simple examples to get you started with Viscid. There are some far more interesting examples in the ``Viscid/tests`` directory, but they are not always as straight forward or documented as the examples here.

Source Code
-----------

Both the master and dev branches make every attempt to be usable (thanks to continuous integration), but the obvious caveats exist, i.e. the dev branch has more cool new features but it isn't *as* tested.

===================  ================  ========================================================
Branch               Test Status       Docs
===================  ================  ========================================================
`master <master_>`_  |travis-master|   `html <html_master_>`_, `test summary <tests_master_>`_
`dev <dev_>`_        |travis-dev|      `html <html_dev_>`_, `test summary <tests_dev_>`_
===================  ================  ========================================================

.. _master: https://github.com/KristoforMaynard/Viscid
.. _html_master: http://kristoformaynard.github.io/Viscid/docs/master/index.html
.. _tests_master: http://kristoformaynard.github.io/Viscid/summary/master-2.7/index.html
.. |travis-master| raw:: html

  <a href="https://travis-ci.org/KristoforMaynard/Viscid">
   <img src="https://travis-ci.org/KristoforMaynard/Viscid.svg?branch=master"
  </a>

.. _dev: https://github.com/KristoforMaynard/Viscid/tree/dev
.. _html_dev: http://kristoformaynard.github.io/Viscid/docs/dev/index.html
.. _tests_dev: http://kristoformaynard.github.io/Viscid/summary/dev-2.7/index.html
.. |travis-dev| raw:: html

  <a href="https://travis-ci.org/KristoforMaynard/Viscid">
   <img src="https://travis-ci.org/KristoforMaynard/Viscid.svg?branch=dev"
  </a>

Quickstart
----------

Please refer to the quickstart instructions in :doc:`installation`.

Contents
--------

.. toctree::
  :maxdepth: 1

  ChangeLog<changes>

.. toctree::
  :maxdepth: 2

  installation
  philosophy
  tutorial/index
  tips_and_tricks
  functions
  plot_options
  mpl_style_gallery
  custom_behavior
  dev_guide
  extending_readers

.. toctree::
  :maxdepth: 1

  API<api/viscid>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
