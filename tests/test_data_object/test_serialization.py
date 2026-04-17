"""
Test serialization round-trips, __copy__, __deepcopy__, and schema for DataObject.
:date_created: 2026-04-17
"""

import json
from copy import copy, deepcopy
from datetime import date, datetime

from do_py import DataObject, R
from do_py.common.managed_datetime import MgdDatetime
from do_py.common.managed_list import ManagedList
from do_py.utils.json_encoder import MyJSONEncoder


class Flat(DataObject):
    _restrictions = {'x': R.INT, 'y': R.STR, 'z': R(1, 2, 3)}


class Inner(DataObject):
    _restrictions = {'val': R.INT}


class Nested(DataObject):
    _restrictions = {'inner': Inner, 'label': R.STR}


class NullableNested(DataObject):
    _restrictions = {'inner': R(Inner, type(None)), 'label': R.STR}


class WithDatetime(DataObject):
    _restrictions = {'dt': MgdDatetime.datetime(), 'd': MgdDatetime.date()}


class WithList(DataObject):
    _restrictions = {'things': ManagedList(Inner)}


class TestRoundTrip:
    """Test DataObject → dict → JSON → dict → DataObject round-trips."""

    def test_flat_round_trip(self):
        original = Flat({'x': 1, 'y': 'hello', 'z': 2})
        json_str = json.dumps(dict(original), cls=MyJSONEncoder)
        restored = Flat(json.loads(json_str))
        assert dict(restored) == dict(original)

    def test_nested_round_trip(self):
        original = Nested({'inner': {'val': 42}, 'label': 'test'})
        json_str = json.dumps(dict(original), cls=MyJSONEncoder)
        loaded = json.loads(json_str)
        restored = Nested(loaded)
        assert restored.inner.val == 42
        assert restored.label == 'test'

    def test_nullable_nested_round_trip_with_value(self):
        original = NullableNested({'inner': {'val': 10}, 'label': 'ok'})
        json_str = json.dumps(dict(original), cls=MyJSONEncoder)
        restored = NullableNested(json.loads(json_str))
        assert restored.inner.val == 10

    def test_nullable_nested_round_trip_with_none(self):
        original = NullableNested({'inner': None, 'label': 'ok'})
        json_str = json.dumps(dict(original), cls=MyJSONEncoder)
        restored = NullableNested(json.loads(json_str))
        assert restored.inner is None

    def test_datetime_round_trip(self):
        dt_now = datetime.now().replace(microsecond=0)
        d_today = date.today()
        original = WithDatetime({'dt': dt_now, 'd': d_today})
        json_str = json.dumps(dict(original), cls=MyJSONEncoder)
        loaded = json.loads(json_str)
        restored = WithDatetime(loaded)
        assert restored.dt == dt_now
        assert restored.d == d_today

    def test_managed_list_round_trip(self):
        original = WithList({'things': [{'val': 1}, {'val': 2}]})
        json_str = json.dumps(dict(original), cls=MyJSONEncoder)
        loaded = json.loads(json_str)
        restored = WithList(loaded)
        assert len(restored.things) == 2
        assert restored.things[0].val == 1
        assert restored.things[1].val == 2


class TestCopy:
    """Test __copy__ returns a plain dict."""

    def test_shallow_copy_is_dict(self):
        original = Flat({'x': 1, 'y': 'hello', 'z': 2})
        copied = copy(original)
        assert type(copied) is dict
        assert copied == dict(original)

    def test_shallow_copy_nested_shared_reference(self):
        """Shallow copy shares nested object references."""
        original = Nested({'inner': {'val': 42}, 'label': 'test'})
        copied = copy(original)
        assert type(copied) is dict
        # Nested object should be shared by reference
        assert copied['inner'] is original['inner']


class TestDeepCopy:
    """Test __deepcopy__ returns a plain dict with independent nested data."""

    def test_deepcopy_is_dict(self):
        original = Flat({'x': 1, 'y': 'hello', 'z': 2})
        copied = deepcopy(original)
        assert type(copied) is dict
        assert copied == dict(original)

    def test_deepcopy_nested_independent(self):
        """Deep copy produces independent nested data."""
        original = Nested({'inner': {'val': 42}, 'label': 'test'})
        copied = deepcopy(original)
        assert type(copied) is dict
        # Nested data should be independent
        assert copied['inner'] is not original['inner']

    def test_deepcopy_back_to_dataobject(self):
        """Deep-copied dict can be used to create a new DataObject."""
        original = Nested({'inner': {'val': 42}, 'label': 'test'})
        copied = deepcopy(original)
        restored = Nested(copied)
        assert restored.inner.val == 42
        assert restored.label == 'test'


class TestSchema:
    """Test the schema classproperty."""

    def test_flat_schema(self):
        schema = Flat.schema
        assert 'x' in schema
        assert 'y' in schema
        assert 'z' in schema

    def test_nested_schema(self):
        schema = Nested.schema
        assert 'inner' in schema
        assert 'label' in schema
        # Inner schema should be a dict with 'val'
        assert 'val' in schema['inner']

    def test_nullable_nested_schema(self):
        schema = NullableNested.schema
        assert 'inner' in schema
        assert 'val' in schema['inner']

    def test_schema_is_cached(self):
        """Accessing schema twice returns the same object (cached)."""
        s1 = Flat.schema
        s2 = Flat.schema
        assert s1 is s2
