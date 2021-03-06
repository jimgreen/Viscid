#!/usr/bin/env python
""" test docstring """

from __future__ import print_function
import re
from itertools import chain
from operator import itemgetter

import numpy as np

import viscid
from viscid import logger
from viscid.compat import string_types
from viscid.bucket import Bucket
from viscid import tree
from viscid import vutil
from viscid.vutil import tree_prefix
from viscid.sliceutil import to_slice

class Dataset(tree.Node):
    """Datasets contain grids or other datasets

    Note:
        Datasets should probably be created using a vfile's
        `_make_dataset` to make sure the info dict is propogated
        appropriately

    It is the programmer's responsibility to ensure objects added to a AOEUIDH
    dataset have __getitem__ and get_fields methods, this is not
    enforced
    """
    children = None  # Bucket or (time, grid)
    active_child = None

    topology_info = None
    geometry_info = None
    crds = None

    def __init__(self, *args, **kwargs):
        """info is for information that is shared for a whole
        tree, from vfile all the way down to fields
        """
        super(Dataset, self).__init__(*args, **kwargs)
        self.children = Bucket(ordered=True)
        self.active_child = None

    def add(self, child, set_active=True):
        self.prepare_child(child)
        self.children[child.name] = child
        if set_active:
            self.active_child = child

    def _clear_cache(self):
        for child in self.children:
            child.clear_cache()

    def clear_cache(self):
        """Clear all childrens' caches"""
        self._clear_cache()

    def remove_all_items(self):
        for child in self.children:
            self.tear_down_child(child)
            child.remove_all_items()
        self.children = Bucket(ordered=True)

    def activate(self, child_handle):
        """ it may not look like it, but this will recursively look
        in my active child for the handle because it uses getitem """
        self.active_child = self.children[child_handle]

    def activate_time(self, time):
        """ this is basically 'activate' except it specifically picks out
        temporal datasets, and does all children, not just the active child """
        for child in self.children:
            try:
                child.activate_time(time)
            except AttributeError:
                pass

    def nr_times(self, slice_str=":"):
        for child in self.children:
            try:
                return child.nr_times(slice_str)
            except AttributeError:
                pass
        raise RuntimeError("I find no temporal datasets")

    def iter_times(self, slice_str=":"):
        for child in self.children:
            try:
                return child.iter_times(slice_str)
            except AttributeError:
                pass
        raise RuntimeError("I find no temporal datasets")

    def get_times(self, slice_str=":"):
        return list(self.iter_times(slice_str=slice_str))

    def get_time(self, slice_str=":"):
        try:
            return next(self.iter_times(slice_str))
        except StopIteration:
            raise RuntimeError("Dataset has no time slices")

    def iter_fields(self, time=None, named=None):
        """ generator for fields in the active dataset,
        this will recurse down to a grid """
        child = self.active_child

        if child is None:
            logger.error("Could not get appropriate child...")
            return None
        else:
            return child.iter_fields(time=time, named=named)

    def print_tree(self, depth=-1, prefix=""):
        if prefix == "":
            print(self)
            prefix += tree_prefix

        for child in self.children:
            suffix = ""
            if child is self.active_child:
                suffix = " <-- active"
            print("{0}{1}{2}".format(prefix, child, suffix))
            if depth != 0:
                child.print_tree(depth=depth - 1, prefix=prefix + tree_prefix)

    # def get_non_dataset(self):
    #     """ recurse down datasets until active_grid is not a subclass
    #         of Dataset """
    #     if isinstance(self.activate_grid, Dataset):
    #         return self.active_grid.get_non_dataset()
    #     else:
    #         return self.active_grid

    def get_field(self, fldname, time=None, slc=None):
        """ recurse down active children to get a field """
        child = self.active_child

        if child is None:
            logger.error("Could not get appropriate child...")
            return None
        else:
            return child.get_field(fldname, time=time, slc=slc)

    def get_grid(self, time=None):
        """ recurse down active children to get a field """
        child = self.active_child

        if child is None:
            logger.error("Could not get appropriate child...")
            return None
        else:
            return child.get_grid(time=time)

    def get_child(self, item):
        """ get a child from this Dataset,  """
        return self.children[item]

    def __getitem__(self, item):
        """ if a child exists with handle, return it, else ask
        the active child if it knows what you want """
        if item in self.children:
            return self.get_child(item)
        elif self.active_child is not None:
            return self.active_child[item]
        else:
            raise KeyError()

    def __delitem__(self, item):
        child = self.get_child(item)
        child.clear_cache()
        self.children.remove_item(child)

    def __len__(self):
        return self.children.__len__()

    def __setitem__(self, name, child):
        # um... is this kosher??
        child.name = name
        self.add(child)

    def __contains__(self, item):
        if item in self.children:
            return True
        # FIXME: this might cause a bug somewhere someday
        if item in self.active_child:
            return True
        return False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, value, traceback):
        self.clear_cache()
        return None

    def __iter__(self):
        return self.children.__iter__()

    # def __next__(self):
    #     raise NotImplementedError()


class DatasetTemporal(Dataset):
    """
    Note:
        Datasets should probably be created using a vfile's
        `_make_dataset` to make sure the info dict is propogated
        appropriately
    """
    _last_ind = 0
    # _all_times = None

    def __init__(self, *args, **kwargs):
        super(DatasetTemporal, self).__init__(*args, **kwargs)
        # ok, i want more control over my childen than a bucket can give
        # TODO: it's kind of a kludge to create a bucket then destroy it
        # so soon, but it's not a big deal
        self.children = []
        # self._all_times = []

    def add(self, child, set_active=True):
        if child is None:
            raise RuntimeError()
        if child.time is None:
            child.time = 0.0
            logger.error("A child with no time? Something is strange...")
        # this keeps the children in time order
        self.prepare_child(child)
        self.children.append((child.time, child))
        self.children.sort(key=itemgetter(0))
        # binary in sorting... maybe more efficient?
        # bisect.insort(self.children, (child.time, child))
        if set_active:
            self.active_child = child

    def remove_all_items(self):
        for child in self.children:
            self.tear_down_child(child[1])
            child[1].remove_all_items()
        self.children = []

    def clear_cache(self):
        """Clear all childrens' caches"""
        for child in self.children:
            child[1].clear_cache()

    def activate(self, time):
        self.active_child = self.get_child(time)

    def activate_time(self, time):
        """ this is basically 'activate' except it specifically picks out
        temporal datasets """
        self.activate(time)

    #############################################################################
    ## here begins a slew of functions that make specifying a time / time slice
    ## super general
    @staticmethod
    def _parse_time_slice_str(slc_str):
        r"""
        Args:
            slc_str (str): must be a single string containing a single
                time slice

        Returns:
            one of {int, string, or slice (can contain ints,
            floats, or strings)}

        Note:
            Individual elements of the slice can look like an int,
            float with trailing 'f', or they can have the form
            [A-Z]+[\d:]+\.\d*. This last one is a datetime-like
            representation with some preceding letters. The preceding
            letters are
        """
        # regex parse the sting into a list of datetime-like strings,
        # integers, floats, and bare colons that mark the slices
        # Note: for datetime-like strings, the letters preceeding a datetime
        # are necessary, otherwise 02:20:30.01 would have more than one meaning
        rstr = (r"\s*(?:(?!:)[A-Z]+[-\d:T]+\.\d*|:|[-+]?[0-9]*\.?[0-9]+f?)\s*|"
                r"[-+]?[0-9]+")
        r = re.compile(rstr, re.I)

        all_times = r.findall(slc_str)
        if len(all_times) == 1 and all_times[0] != ":":
            return vutil.str_to_value(all_times[0])

        # fill in implied slice colons, then replace them with something
        # unique... like !!
        all_times += [':'] * (2 - all_times.count(':'))
        all_times = [s if s != ":" else "!!" for s in all_times]
        # this is kinda silly, but turn all times back into a string,
        # then split it again, this is the easiest way to parse something
        # like '1::2'
        ret = "".join(all_times).split("!!")
        # convert empty -> None, ints -> ints and floats->floats
        for i, val in enumerate(ret):
            ret[i] = vutil.str_to_value(val)
        if len(ret) > 3:
            raise ValueError("Could not decipher slice: '{0}'. Perhaps you're "
                             "missing some letters in front of a time "
                             "string?".format(slc_str))
        # trim trailing dots
        ret = [r.rstrip('.') if hasattr(r, 'rstrip') else r for r in ret]
        return slice(*ret)

    def as_floating_t(self, t, none_passthrough=False):
        t_as_s = None
        try:
            t = vutil.str_to_value(t)

            if viscid.is_timedelta_like(t, conservative=True):
                t_as_s = viscid.as_timedelta(t).total_seconds()
            elif viscid.is_datetime_like(t, conservative=True):
                delta_t = viscid.as_datetime64(t) - self.basetime
                t_as_s = viscid.as_timedelta(delta_t).total_seconds()
            elif not isinstance(t, (int, np.integer, type(None))):
                t_as_s = float(t)
        except AttributeError:
            if t is None:
                if none_passthrough:
                    pass
                else:
                    t = 0.0
            else:
                t_as_s = float(t)

        return t_as_s

    def _slice_time(self, slc=":"):
        """
        Args:
            slc (str, slice, list): can be a single string containing
                slices, slices, ints, floats, datetime objects, or a
                list of any of the above.

        Returns:
            list of slices (containing integers only) or ints
        """
        # print("SLC::", slc)
        if not isinstance(slc, (list, tuple)):
            slc = [slc]

        # expand strings that are comma separated lists of strings
        _slc = []
        for s in slc:
            if isinstance(s, string_types):
                for _ in s.split(','):
                    _slc.append(_)
            else:
                _slc.append(s)
        slc = _slc

        ret = []
        times = np.array([child[0] for child in self.children])
        for s in slc:
            if isinstance(s, string_types):
                s = self._parse_time_slice_str(s)

            if isinstance(s, slice):
                single_val = False
                slc_lst = [s.start, s.stop, s.step]
            else:
                single_val = True
                slc_lst = [s]

            # do translation from string/datetime/etc -> floats
            for i in range(min(len(slc_lst), 2)):
                try:
                    slc_lst[i] = int(slc_lst[i])
                except (ValueError, TypeError):
                    t_as_s = self.as_floating_t(slc_lst[i], none_passthrough=True)

                    if t_as_s is not None:
                        slc_lst[i] = "{0}f".format(t_as_s)

            if single_val:
                ret.append(to_slice(times, slc_lst[0]))
            else:
                ret.append(to_slice(times, slc_lst))

        return ret

    def _time_slice_to_iterator(self, slc):
        """
        Args:
            slc: a slice (containing ints only) or an int, or a list
                of any of the above

        Returns:
            a flat iterator of self.children of all the slices chained
        """
        if not isinstance(slc, (list, tuple)):
            slc = [slc]

        child_iter_lst = []
        for s in slc:
            if isinstance(s, slice):
                inds = range(len(self.children))[s]
                it = (self.children[i] for i in inds)
                child_iter_lst.append(it)
            else:
                child_iter_lst.append([self.children[s]])
        return chain(*child_iter_lst)

    def nr_times(self, slice_str=":"):
        slc = self._slice_time(slice_str)
        child_iterator = self._time_slice_to_iterator(slc)
        return len(list(child_iterator))

    def iter_times(self, slice_str=":"):
        slc = self._slice_time(slice_str)
        child_iterator = self._time_slice_to_iterator(slc)

        for child in child_iterator:
            # FIXME: this isn't general, but so far the only files we're
            # read have only contained one Grid / AMRGrid. Without get_grid()
            # here, the context manager will unload the file when done, but
            # that's not what we wanted here, we wanted to just clear caches
            with child[1].get_grid() as target:
                yield target

    def get_times(self, slice_str=":"):
        return list(self.iter_times(slice_str=slice_str))

    def get_time(self, slice_str=":"):
        return self.get_times(slice_str)[0]

    ## ok, that's enough for the time stuff
    ########################################

    def iter_fields(self, time=None, named=None):
        """ generator for fields in the active dataset,
        this will recurse down to a grid """
        if time is not None:
            child = self.get_child(time)
        else:
            child = self.active_child

        if child is None:
            logger.error("Could not get appropriate child...")
            return None
        else:
            return child.iter_fields(time=time, named=named)

    def print_tree(self, depth=-1, prefix=""):
        if prefix == "":
            print(self)
            prefix += tree_prefix

        for child in self.children:
            suffix = ""
            if child[1] is self.active_child:
                suffix = " <-- active"
            print("{0}{1} (t={2}){3}".format(prefix, child, child[0], suffix))
            if depth != 0:
                child[1].print_tree(depth=depth - 1, prefix=prefix + tree_prefix)

    def get_field(self, fldname, time=None, slc=None):
        """ recurse down active children to get a field """
        if time is not None:
            child = self.get_child(time)
        else:
            child = self.active_child

        if child is None:
            logger.error("Could not get appropriate child...")
            return None
        else:
            return child.get_field(fldname, time=time, slc=None)

    def get_grid(self, time=None):
        """ recurse down active children to get a field """
        if time is not None:
            child = self.get_child(time)
        else:
            child = self.active_child

        if child is None:
            logger.error("Could not get appropriate child...")
            return None
        else:
            return child.get_grid(time=time)

    def get_child(self, item):
        """ if item is an int and < len(children), it is an index in a list,
        else I will find the cloest time to float(item) """
        # print(">> get_child:", item)
        # print(">> slice is:", self._slice_time(item))
        # always just return the first slice's child... is this wrong?
        child = self.children[self._slice_time(item)[0]][1]
        return child

    def __contains__(self, item):
        if isinstance(item, int) and item > 0 and item < len(self.children):
            return True
        if isinstance(item, string_types) and item[-1] == 'f':
            try:
                val = float(item[:-1])
                if val >= self.children[0][0] and val <= self.children[-1][0]:
                    return True
                else:
                    return False
            except ValueError:
                pass
        return item in self.active_child

    def __iter__(self):
        for child in self.children:
            yield child[1]

    # def __getitem__(self, item):
    #     """ Get a dataitem or list of dataitems based on time, grid, and
    #         varname. the 'active' components are given by default, but varname
    #         is manditory, else how am i supposed to know what to serve up for
    #         you. Examples:
    #         dataset[time, 'gridhandle', 'varname'] == DataItem
    #         dataset['time', 'gridhandle', 'varname'] == DataItem
    #         dataset[timeslice, 'gridhandle', 'varname'] == list of DataItems
    #         dataset[time, 'varname'] == DataItem using active grid
    #         dataset['varname'] == DataItem using active time / active grid
    #         """
    #     req_grid = None

    #     if not isinstance(item, tuple):
    #         item = (item,)

    #     varname = item[-1]
    #     nr_times = len(item) - 1 # -1 for varname
    #     try:
    #         if len(item) > 1:
    #             req_grid = self.grids[item[-2]]
    #     except KeyError:
    #         pass
    #     if not req_grid:
    #         req_grid = self.active_grid
    #         nr_times -= 1

    #     if nr_times == 0:
    #         grids = [self.grid_by_time(self.active_time)]
    #     else:
    #         grids = [self.grid_by_time(t) for t in item[:nr_times]]

    #     if len(grids) == 1:
    #         return grids[0][varname]
    #     else:
    #         return [g[varname] for g in grids]

    # def grid_by_time(self, time):
    #     """ returns grid for this specific time, time can also be a slice """
    #     if isinstance(time, slice):
    #         pass
    #     else:
    #         pass
