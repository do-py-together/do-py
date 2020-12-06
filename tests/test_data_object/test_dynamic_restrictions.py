"""
Test dynamic restriction class creation, inheritance and usage.
:date_created: 2020-07-10
"""
from builtins import object

import pytest

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

    @pytest.mark.parametrize('item_metadata', [
        MilkMetadata({'flavor': 'normal'}),
        pytest.param(CerealMetadata({'brand': 'cheerios'}), marks=pytest.mark.xfail)
        ])
    def test_set(self, item_metadata):
        """
        Test basic setting of a dynamic value.
        """
        breakfast = Breakfast({
            'item': 'milk',
            'item_metadata': {
                'flavor': 'chocolate'
                }
            })
        breakfast.item_metadata = item_metadata
        assert breakfast.item_metadata.flavor == 'normal'

    def test_set_in_child(self):
        """
        Test the setting in the child dynamic restriction works fine.
        """
        breakfast = Breakfast({
            'item': 'milk',
            'item_metadata': {
                'flavor': 'chocolate'
                }
            })
        assert breakfast.item_metadata.flavor == 'chocolate'
        breakfast.item_metadata.flavor = 'normal'
        assert breakfast.item_metadata.flavor == 'normal'


class TestInheritance(object):
    """
    Test inheritance and rules/checks.
    """

    @pytest.mark.xfail(raises=AssertionError)
    def test_missing_independent_key_restriction(self):
        """
        Test the compilation check that validates if a restriction is missing.
        """
        dynamic_item_2 = dynamic_restriction_mixin('invalid', 'item_metadata', milk=MilkMetadata, cereal=CerealMetadata)

        class Breakfast2(dynamic_item_2):
            """
            What is the most important meal of the day?
            """
            _restrictions = {
                'item': R('milk', 'cereal'),
                'item_metadata': R(),
                }

        assert Breakfast2

    @pytest.mark.xfail(raises=AssertionError)
    def test_missing_dependent_key_restriction(self):
        """
        Test the compilation check that validates if a restriction is missing.
        """
        dynamic_item_2 = dynamic_restriction_mixin('item', 'invalid', milk=MilkMetadata, cereal=CerealMetadata)

        class Breakfast2(dynamic_item_2):
            """
            What is the most important meal of the day?
            """
            _restrictions = {
                'item': R('milk', 'cereal'),
                'item_metadata': R(),
                }

        assert Breakfast2

    @pytest.mark.xfail(raises=AssertionError)
    def test_missing_dynamic_restriction(self):
        """
        Test that compilation blows up if we did not include all restrictions in the mixin.
        """
        dynamic_item_2 = dynamic_restriction_mixin('item', 'item_metadata', milk=MilkMetadata)

        class Breakfast2(dynamic_item_2):
            """
            What is the most important meal of the day?
            """
            _restrictions = {
                'item': R('milk', 'cereal'),
                'item_metadata': R(),
                }

        assert Breakfast2

    @pytest.mark.xfail(raises=AssertionError)
    def test_missing_class_restriction(self):
        """
        Test that compilation blows up if we did not include all restrictions from the mixin.
        """
        dynamic_item_2 = dynamic_restriction_mixin('item', 'item_metadata', milk=MilkMetadata, cereal=CerealMetadata)

        class Breakfast2(dynamic_item_2):
            """
            What is the most important meal of the day?
            """
            _restrictions = {
                'item': R('milk'),
                'item_metadata': R(),
                }

        assert Breakfast2
