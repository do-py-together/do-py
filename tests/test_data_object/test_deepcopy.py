"""
:date_created: 2021-09-23
"""
from copy import deepcopy

from builtins import object

from do_py import R
from do_py.data_object import DataObject, Restriction


class Address(DataObject):
    """
    DataObject to standardize address representation and storage. Validates if state belongs to country.
    """
    _restrictions = {
        'street': R.STR,
        'street2': R.NULL_STR,
        'city': R.STR,
        }


class TestDataObjectCopy(object):
    """
    Copying the restrictions of an object is a very useful way to have objects with similar keys.
    """

    def test_dictcopy(self):
        """
        Test rebuilding the restrictions after cloning via `dict`.
        """
        copy = dict(Address._restrictions)
        for key in copy:
            Restriction.legacy(copy[key])

    def test_deepcopy(self):
        """
        Test rebuilding the restrictions after cloning via `deepcopy`. `deepcopy` uses memoization to store a
            previously copied instance.
        """
        copy = deepcopy(Address._restrictions)
        for key in copy:
            Restriction.legacy(copy[key])
