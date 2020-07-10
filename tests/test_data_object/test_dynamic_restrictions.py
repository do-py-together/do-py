"""
Test dynamic restriction class creation, inheritance and usage.
TODO:
    1) Inheritance checks like restrictions existing etc.
    2) Validator inheritance.
    3) Test coverage 100%.
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


dynamic_item = dynamic_restriction_mixin('item', 'item_metadata', milk=MilkMetadata, cereal=CerealMetadata)


class Breakfast(dynamic_item):
    """
    What is the most important meal of the day?
    """
    _restrictions = {
        'item': R('milk', 'cereal'),
        'item_metadata': R(),
        }

    def _validate(self):
        print 'validate'
        print self.item_metadata


class TestDynamicDataObject(object):
    """
    Test basic usages of the Breakfast example.
    """

    def test_init(self):
        """
        Test basic instantiation.
        """
        breakfast = Breakfast({
            'item': 'milk',
            'item_metadata': {
                'flavor': 'chocolate'
                }
            })
        assert breakfast.item == 'milk'
        assert isinstance(breakfast.item_metadata, MilkMetadata)
        assert breakfast.item_metadata.flavor == 'chocolate'

    def test_set(self):
        """
        Test basic setting of a dynamic value.
        """
        breakfast = Breakfast({
            'item': 'milk',
            'item_metadata': {
                'flavor': 'chocolate'
                }
            })
        breakfast.item_metadata = MilkMetadata({
            'flavor': 'normal'
            })
        assert breakfast.item_metadata.flavor == 'normal'
