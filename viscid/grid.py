#!/usr/bin/env python
"""Grids contain fields and coordinates"""

from __future__ import print_function

from viscid import field
from viscid.bucket import Bucket
from viscid import tree
from viscid.vutil import tree_prefix
from viscid.calculator.evaluator import evaluate

class Grid(tree.Node):
    """Computational grid container

    Grids contain fields and coordinates. Datasets recurse to grids
    using ``__getitem__`` and get_field in order to find fields. Grids
    can also calculate fields by defining ``_get_*`` methods.

    Attributes can be overridden globally to affect all data reads of
    a given grid type. Subclasses of Grid document their own special
    attributes. For example, one can change the default vector layout
    with:

        ``viscid.grid.Grid.force_vector_layout = LAYOUT_INTERLACED``

    Attributes:
        force_vecter_layout (``field.LAYOUT_*``): force all vectors to
            be of a certain layout when they're created
            (default: LAYOUT_DEFAULT)
        longterm_field_caches (bool): If True, then when a field is
            cached, it must be explicitly removed from memory with
            "clear_cache" or using the 'with' statemnt. If False,
            "shell copies" of fields are made so that memory is freed
            when the returned instance is garbage collected.
            Default: False
    """
    topology_info = None
    geometry_info = None
    _src_crds = None
    _crds = None
    fields = None
    # so... not all grids have times? if we try to access time on a grid
    # that doesnt have one, there is probably a bug somewhere
    # time = None

    # these attributes are intended to control how fields are read
    # they can be customized by setting the class value, and inherited
    # by grids that get created in the future
    force_vector_layout = field.LAYOUT_DEFAULT
    longterm_field_caches = False

    def __init__(self, *args, **kwargs):
        super(Grid, self).__init__(*args, **kwargs)
        self.fields = Bucket(ordered=True)

    @staticmethod
    def null_transform(something):
        return something

    @property
    def field_names(self):
        return self.fields.get_primary_handles()

    @property
    def crds(self):
        if self._crds is None:
            self._crds = self._src_crds.apply_reflections()
        return self._crds

    @crds.setter
    def crds(self, val):
        self._crds = None
        self._src_crds = val

    @property
    def xl_nc(self):
        return self.crds.xl_nc

    @property
    def xh_nc(self):
        return self.crds.xh_nc

    @property
    def xl_cc(self):
        return self.crds.xl_cc

    @property
    def xh_cc(self):
        return self.crds.xh_cc

    # def set_time(self, time):
    #     self.time = time

    def set_crds(self, crds_object):
        self.crds = crds_object

    def add_field(self, *fields):
        """ Note: in XDMF reader, the grid will NOT have crds when adding
        fields, so any grid crd transforms won't be set
        """
        for f in fields:
            if isinstance(f, field.VectorField):
                f.layout = self.force_vector_layout
            self.prepare_child(f)
            self.fields[f.name] = f

    def remove_all_items(self):
        for fld in self.fields:
            self.tear_down_child(fld)
        self.fields = Bucket(ordered=True)

    def clear_cache(self):
        """clear the cache on all child fields"""
        for fld in self.fields:
            fld.clear_cache()

    def nr_times(self, *args, **kwargs):  # pylint: disable=W0613,R0201
        return 1

    def iter_times(self, *args, **kwargs):  # pylint: disable=W0613
        # FIXME: it is unclear to me what to do here, since a dataset
        # may have > 1 grid... and if so only the first will be returned...
        # i guess there is some ambiguity if there is no temporal dataset...
        with self as me:
            yield me

    def get_times(self, *args, **kwargs):
        return list(self.iter_times(*args, **kwargs))

    def get_time(self, *args, **kwargs):
        return self.get_times(*args, **kwargs)[0]

    def iter_fields(self, named=None, **kwargs):  # pylint: disable=W0613
        """ iterate over fields in a grid, if named is given, it should be a
        list of field names to iterate over
        """
        # Note: using 'with' here is better than making a shell copy
        if named is not None:
            for name in named:
                with self.fields[name] as f:
                    yield f
        else:
            for fld in self.fields:
                with fld as f:
                    yield f

    def print_tree(self, depth=-1, prefix=""):  # pylint: disable=W0613
        self.fields.print_tree(prefix=prefix + tree_prefix)

    ##################################
    ## Utility methods to get at crds
    # these are the same as something like self._src_crds['xnc']
    # or self._src_crds.get_crd()
    def get_crd_nc(self, axis, shaped=False):
        """ returns a flat ndarray of coordinates along a given axis
        axis can be crd name as string, or index, as in x==2, y==1, z==2
        """
        return self._src_crds.get_nc(axis, shaped=shaped)

    def get_crd_cc(self, axis, shaped=False):
        """ returns a flat ndarray of coordinates along a given axis
        axis can be crd name as string, or index, as in x==2, y==1, z==2
        """
        return self._src_crds.get_cc(axis, shaped=shaped)

    def get_crd_ec(self, axis, shaped=False):
        """ returns a flat ndarray of coordinates along a given axis
        axis can be crd name as string, or index, as in x==2, y==1, z==2
        """
        return self._src_crds.get_ec(axis, shaped=shaped)

    def get_crd_fc(self, axis, shaped=False):
        """ returns a flat ndarray of coordinates along a given axis
        axis can be crd name as string, or index, as in x==2, y==1, z==2
        """
        return self._src_crds.get_fc(axis, shaped=shaped)

    ## these return all crd dimensions
    # these are the same as something like self._src_crds.get_crds()
    def get_crds_nc(self, axes=None, shaped=False):
        """ returns all node centered coords as a list of ndarrays, flat if
        shaped==False, or shaped if shaped==True
        """
        return self._src_crds.get_crds_nc(axes=axes, shaped=shaped)

    def get_crds_cc(self, axes=None, shaped=False):
        """ returns all cell centered coords as a list of ndarrays, flat if
        shaped==False, or shaped if shaped==True
        """
        return self._src_crds.get_crds_cc(axes=axes, shaped=shaped)

    def get_crds_fc(self, axes=None, shaped=False):
        """ returns all face centered coords as a list of ndarrays, flat if
        shaped==False, or shaped if shaped==True
        """
        return self._src_crds.get_crds_fc(axes=axes, shaped=shaped)

    def get_crds_ec(self, axes=None, shaped=False):
        """ returns all edge centered coords as a list of ndarrays, flat if
        shaped==False, or shaped if shaped==True
        """
        return self._src_crds.get_crds_ec(axes=axes, shaped=shaped)

    ##
    def get_field(self, fldname, time=None, force_longterm_caches=False,
                  slc=None):  # pylint: disable=unused-argument
        ret = None
        try_final_slice = True

        try:
            if force_longterm_caches or self.longterm_field_caches:
                ret = self.fields[fldname]
            else:
                ret = self.fields[fldname].shell_copy(force=False)
        except KeyError:
            func = "_get_" + fldname
            if hasattr(self, func):
                ret = getattr(self, func)()
            elif len(fldname.split('=')) == 2:
                result_name, eqn = (s.strip() for s in fldname.split('='))
                ret = evaluate(self, result_name, eqn, slc=slc)
                try_final_slice = False
            else:
                raise KeyError("field not found: {0}".format(fldname))

        process_func = "_process_" + fldname
        if hasattr(self, process_func):
            ret = getattr(self, process_func)(ret)

        if hasattr(self, "_processALL"):
            ret = getattr(self, "_processALL")(ret)

        if slc is not None and try_final_slice:
            ret = ret.slice_and_keep(slc)
        return ret

    def get_grid(self, time=None):  # pylint: disable=unused-argument
        return self

    def __contains__(self, item):
        return item in self.fields

    def __len__(self):
        return len(self.fields)

    def __getitem__(self, item):
        """ returns a field by name, or if no field is found, a coordinate by
        name some crd identifier, see Coordinate.get_item for details
        """
        try:
            return self.get_field(item)
        except KeyError:
            if self._src_crds is not None and item in self._src_crds:
                return self._src_crds[item]
            else:
                raise KeyError(item)

    def __setitem__(self, fldname, fld):
        self.fields[fldname] = fld

    def __delitem__(self, fldname):
        self.fields.__delitem__(fldname)

    def __str__(self):
        return "<Grid name={0}>".format(self.name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, value, traceback):
        self.clear_cache()
        return None

##
## EOF
##
