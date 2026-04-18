"""
Test dynamic restriction class creation, inheritance and usage.
:date_created: 2020-07-10
"""

import pytest

from do_py import DataObject, R
from do_py.data_object.dynamic_restrictions import DynamicRestrictions, dynamic_restriction_mixin
from do_py.exceptions import DataObjectError


class MilkMetadata(DataObject):
    """
    Full of vitamins and minerals
    """

    _restrictions = {'flavor': R('chocolate', 'normal')}


class CerealMetadata(DataObject):
    """
    Delicious.
    """

    _restrictions = {'brand': R('frosted-flakes', 'cheerios')}


dynamic_item = dynamic_restriction_mixin('item', 'item_metadata', milk=MilkMetadata, cereal=CerealMetadata)


class Breakfast(dynamic_item):
    """
    What is the most important meal of the day?
    """

    _restrictions = {'item': R('milk', 'cereal'), 'item_metadata': R(), 'name': R.NULL_STR}

    def __init__(self, data=None, **kwargs):
        if data and 'name' not in data:
            data['name'] = None
        super().__init__(data=data, **kwargs)


class TestDynamicDataObject:
    """
    Test basic usages of the Breakfast example.
    """

    def test_init(self):
        """
        Test basic instantiation.
        """
        breakfast = Breakfast({'item': 'milk', 'item_metadata': {'flavor': 'chocolate'}})
        assert breakfast.item == 'milk'
        assert isinstance(breakfast.item_metadata, MilkMetadata)
        assert breakfast.item_metadata.flavor == 'chocolate'

    @pytest.mark.parametrize(
        'item_metadata',
        [
            MilkMetadata({'flavor': 'normal'}),
            pytest.param(CerealMetadata({'brand': 'cheerios'}), marks=pytest.mark.xfail),
        ],
    )
    def test_set(self, item_metadata):
        """
        Test basic setting of a dynamic value.
        """
        breakfast = Breakfast({'item': 'milk', 'item_metadata': {'flavor': 'chocolate'}})
        breakfast.item_metadata = item_metadata
        assert breakfast.item_metadata.flavor == 'normal'

    def test_set_in_child(self):
        """
        Test the setting in the child dynamic restriction works fine.
        """
        breakfast = Breakfast({'item': 'milk', 'item_metadata': {'flavor': 'chocolate'}})
        assert breakfast.item_metadata.flavor == 'chocolate'
        breakfast.item_metadata.flavor = 'normal'
        assert breakfast.item_metadata.flavor == 'normal'


class TestDynamicSetItem:
    """Test __setitem__ paths for dynamic restrictions."""

    def test_setitem_dependent_key_valid(self):
        """Setting the dependent key with matching data should succeed."""
        breakfast = Breakfast({'item': 'milk', 'item_metadata': {'flavor': 'chocolate'}})
        breakfast['item_metadata'] = MilkMetadata({'flavor': 'normal'})
        assert breakfast.item_metadata.flavor == 'normal'

    def test_setitem_dependent_key_mismatched_restriction(self):
        """Setting the dependent key with mismatched data should fail with DataObjectError."""
        breakfast = Breakfast({'item': 'milk', 'item_metadata': {'flavor': 'chocolate'}})
        with pytest.raises(DataObjectError):
            breakfast['item_metadata'] = CerealMetadata({'brand': 'cheerios'})

    def test_setitem_non_dynamic_key(self):
        """Setting a key that is not dynamic should work normally."""
        breakfast = Breakfast({'item': 'milk', 'item_metadata': {'flavor': 'chocolate'}})
        breakfast['name'] = 'morning milk'
        assert breakfast.name == 'morning milk'

    def test_setitem_dependent_key_update(self):
        """Setting the dependent key with a new valid value of the same type should succeed."""
        milk = Breakfast({'item': 'milk', 'item_metadata': {'flavor': 'chocolate'}})
        milk.item_metadata = MilkMetadata({'flavor': 'normal'})
        assert milk._restrictions['item_metadata'] == MilkMetadata
        assert milk.item_metadata.flavor == 'normal'

    def test_setitem_independent_key_revalidates_dependent(self):
        """Changing the independent key triggers revalidation of the dependent value.

        Since the existing dependent value (MilkMetadata) doesn't match the new restriction
        (CerealMetadata), this correctly raises an error. The independent and dependent keys
        are coupled — you cannot change one without the other being compatible.
        """
        breakfast = Breakfast({'item': 'milk', 'item_metadata': {'flavor': 'chocolate'}})
        assert breakfast._restrictions['item_metadata'] == MilkMetadata
        # Changing independent key revalidates the existing dependent value against the new restriction
        with pytest.raises(DataObjectError):
            breakfast['item'] = 'cereal'


class TestDynamicInstanceIsolation:
    """Verify that two instances with different dynamic restrictions don't share state."""

    def test_two_instances_independent(self):
        """Two instances with different items should have independent restrictions."""
        milk = Breakfast({'item': 'milk', 'item_metadata': MilkMetadata({'flavor': 'chocolate'})})
        cereal = Breakfast({'item': 'cereal', 'item_metadata': CerealMetadata({'brand': 'cheerios'})})

        assert milk._restrictions['item_metadata'] == MilkMetadata
        assert cereal._restrictions['item_metadata'] == CerealMetadata

        # Mutating one should not affect the other
        milk.item_metadata.flavor = 'normal'
        assert cereal.item_metadata.brand == 'cheerios'

    def test_class_restrictions_untouched(self):
        """Class-level restrictions should never be mutated by instance creation."""
        assert Breakfast._restrictions['item_metadata'] == R()
        Breakfast({'item': 'milk', 'item_metadata': {'flavor': 'chocolate'}})
        assert Breakfast._restrictions['item_metadata'] == R()


class TestDynamicRestrictionsManagedRestriction:
    """Direct tests for the DynamicRestrictions ManagedRestrictions class."""

    def test_valid_dynamic_restrictions(self):
        """DynamicRestrictions.manage should succeed with valid DO mappings."""
        dr = DynamicRestrictions()
        result = dr({'milk': MilkMetadata, 'cereal': CerealMetadata})
        assert result == {'milk': MilkMetadata, 'cereal': CerealMetadata}

    def test_empty_dict_fails(self):
        """DynamicRestrictions.manage should fail with an empty dict."""
        dr = DynamicRestrictions()
        with pytest.raises(AssertionError, match='empty'):
            dr({})

    def test_non_dataobject_value_fails(self):
        """DynamicRestrictions.manage should fail if a value is not a DataObject."""
        dr = DynamicRestrictions()
        with pytest.raises(AssertionError):
            dr({'bad': int})


class TestInheritance:
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

    def test_restrictions(self):
        """
        Test that the restrictions update when the value is updated.
        """
        # Validate the starting condition.
        assert Breakfast._restrictions['item_metadata'] == R()
        milk = Breakfast({'item': 'milk', 'item_metadata': MilkMetadata({'flavor': 'chocolate'})})
        # Ensure the instance's restrictions were updated correctly.
        assert milk._restrictions['item_metadata'] == MilkMetadata

        # Validate the class restrictions were not touched.
        assert Breakfast._restrictions['item_metadata'] == R()

        # Validate a second instance is created correctly and the restrictions do not clash.
        milk = Breakfast({'item': 'cereal', 'item_metadata': CerealMetadata({'brand': 'cheerios'})})
        assert milk._restrictions['item_metadata'] == CerealMetadata
        assert Breakfast._restrictions['item_metadata'] == R()

    def test_restriction_update_by_value(self):
        """
        Test that the restrictions update when the value is updated.
        """
        # Validate the starting condition.
        assert Breakfast._restrictions['item_metadata'] == R()
        milk = Breakfast({'item': 'milk', 'item_metadata': MilkMetadata({'flavor': 'chocolate'})})
        # Ensure the instance's restrictions were updated correctly.
        assert milk._restrictions['item_metadata'] == MilkMetadata

        cereal = Breakfast({'item': 'cereal', 'item_metadata': CerealMetadata({'brand': 'frosted-flakes'})})
        assert cereal._restrictions['item_metadata'] == CerealMetadata
        assert milk._restrictions['item_metadata'] == MilkMetadata
