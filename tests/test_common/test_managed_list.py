"""
:date_created: 2020-06-28
"""

import pytest

from do_py import DataObject
from do_py.common import R
from do_py.common.managed_list import ManagedList, OrderedManagedList
from do_py.exceptions import RestrictionError


class Book(DataObject):
    _restrictions = {'title': R.STR, 'author': R.STR}


class Bookshelf(DataObject):
    _restrictions = {'type': ['wood', 'metal'], 'size': ['small', 'medium', 'large']}


class Library(DataObject):
    _restrictions = {'books': ManagedList(Book), 'shelves': ManagedList(Bookshelf, nullable=True)}


class TestManagedList:
    book_1 = {'title': '1', 'author': 'Author 1'}
    book_2 = {'title': '2', 'author': 'Author 2'}
    shelf_1 = {'type': 'wood', 'size': 'small'}
    shelf_2 = {'type': 'metal', 'size': 'large'}

    @pytest.mark.parametrize(
        'books',
        [
            pytest.param(None, marks=pytest.mark.xfail),
            [],
            [book_1],
            [Book(book_1)],
            [book_1, book_2],
            [Book(book_1), Book(book_2)],
        ],
    )
    @pytest.mark.parametrize(
        'shelves',
        [None, [], [shelf_1], [Bookshelf(shelf_1)], [shelf_1, shelf_2], [Bookshelf(shelf_1), Bookshelf(shelf_2)]],
    )
    def test_managed_list(self, books, shelves):
        assert Library({'books': books, 'shelves': shelves})

    def test_items_are_do_instances(self):
        """All items in the managed list should be proper DataObject instances."""
        lib = Library({'books': [self.book_1, self.book_2], 'shelves': None})
        for book in lib.books:
            assert type(book) is Book, 'Expected Book instance, got %s' % type(book)

    def test_mixed_dict_and_do_input(self):
        """List with a mix of dicts and DO instances should all become DO instances."""
        lib = Library({'books': [self.book_1, Book(self.book_2)], 'shelves': None})
        assert len(lib.books) == 2
        for book in lib.books:
            assert type(book) is Book

    def test_non_nullable_none_raises(self):
        """Non-nullable ManagedList with None data should raise RestrictionError."""
        ml = ManagedList(Book, nullable=False)
        with pytest.raises(RestrictionError):
            ml(None)

    def test_nullable_none_ok(self):
        """Nullable ManagedList with None data should succeed."""
        ml = ManagedList(Bookshelf, nullable=True)
        result = ml(None)
        assert result is None

    def test_schema_value(self):
        """schema_value should return a list containing the DO's schema."""
        ml = ManagedList(Book)
        schema = ml.schema_value
        assert isinstance(schema, list)
        assert len(schema) == 1
        assert schema[0] == Book.schema


class SortableItem(DataObject):
    _restrictions = {'name': R.STR, 'priority': R.INT}


class TestOrderedManagedList:
    """Tests for OrderedManagedList (previously had # TODO: Unit tests)."""

    def test_basic_sorting(self):
        """Items should be sorted by the key function."""

        class SortedContainer(DataObject):
            _restrictions = {'entries': OrderedManagedList(SortableItem, key=lambda x: x.priority)}

        data = {
            'entries': [
                {'name': 'c', 'priority': 3},
                {'name': 'a', 'priority': 1},
                {'name': 'b', 'priority': 2},
            ]
        }
        container = SortedContainer(data)
        priorities = [item.priority for item in container.entries]
        assert priorities == [1, 2, 3], 'Expected sorted order, got %s' % priorities

    def test_reverse_sorting(self):
        """Items should be sorted in reverse when reverse=True."""

        class ReverseSortedContainer(DataObject):
            _restrictions = {'entries': OrderedManagedList(SortableItem, key=lambda x: x.priority, reverse=True)}

        data = {
            'entries': [
                {'name': 'a', 'priority': 1},
                {'name': 'c', 'priority': 3},
                {'name': 'b', 'priority': 2},
            ]
        }
        container = ReverseSortedContainer(data)
        priorities = [item.priority for item in container.entries]
        assert priorities == [3, 2, 1], 'Expected reverse sorted order, got %s' % priorities

    def test_nullable_ordered_list(self):
        """Nullable OrderedManagedList should accept None."""

        class NullableContainer(DataObject):
            _restrictions = {'entries': OrderedManagedList(SortableItem, nullable=True, key=lambda x: x.priority)}

        container = NullableContainer({'entries': None})
        assert container.entries is None

    def test_non_nullable_ordered_list_none_raises(self):
        """Non-nullable OrderedManagedList should reject None."""
        oml = OrderedManagedList(SortableItem, key=lambda x: x.priority)
        with pytest.raises(RestrictionError):
            oml(None)

    def test_items_are_do_instances(self):
        """Items in OrderedManagedList should be DO instances after processing."""

        class SortedContainer(DataObject):
            _restrictions = {'entries': OrderedManagedList(SortableItem, key=lambda x: x.priority)}

        data = {'entries': [{'name': 'a', 'priority': 1}]}
        container = SortedContainer(data)
        assert type(container.entries[0]) is SortableItem

    def test_empty_list(self):
        """Empty list should be valid and remain empty after sorting."""

        class SortedContainer(DataObject):
            _restrictions = {'entries': OrderedManagedList(SortableItem, key=lambda x: x.priority)}

        container = SortedContainer({'entries': []})
        assert container.entries == []

    def test_non_list_input_raises(self):
        """Non-list input (e.g. string, int) should not be silently accepted."""
        ml = ManagedList(SortableItem)
        with pytest.raises(Exception):
            ml('not a list')

        with pytest.raises(Exception):
            ml(42)
