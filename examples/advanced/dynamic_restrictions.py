"""
WIP
"""
from do_py import DataObject, R

from do_py.data_object.dynamic_restrictions import dynamic_restriction_mixin


class MilkMetadata(DataObject):
    """
    Full of vitamins and minerals
    """
    _restrictions = {
        'flavor': R('chocolate', 'normal')
        }


class CerealMetadata(DataObject):
    """
    Delicious.
    """
    _restrictions = {
        'brand': R('frosted-flakes', 'cheerios')
        }


# `dynamic_restriction_mixin` dynamically creates and returns a parent class for us to inherit.
dynamic_item = dynamic_restriction_mixin('item', 'item_metadata', milk=MilkMetadata, cereal=CerealMetadata)


class Breakfast(dynamic_item):
    """
    What is the most important meal of the day?

    The restriction for `item_metadata` depends on the value of `item`.
    """
    _restrictions = {
        'item': R('milk', 'cereal'),
        'item_metadata': R(),
        }
