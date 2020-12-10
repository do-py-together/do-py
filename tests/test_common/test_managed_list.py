"""
:date_created: 2020-06-28
"""

from builtins import object

import pytest

from do_py import DataObject
from do_py.common import R
from do_py.common.managed_list import ManagedList


class Book(DataObject):
    _restrictions = {
        'title': R.STR,
        'author': R.STR
        }


class Bookshelf(DataObject):
    _restrictions = {
        'type': ['wood', 'metal'],
        'size': ['small', 'medium', 'large']
        }


class Library(DataObject):
    _restrictions = {
        'books': ManagedList(Book),
        'shelves': ManagedList(Bookshelf, nullable=True)
        }


class TestManagedList(object):
    book_1 = {
        'title': '1',
        'author': 'Author 1'
        }
    book_2 = {
        'title': '2',
        'author': 'Author 2'
        }
    shelf_1 = {
        'type': 'wood',
        'size': 'small'
        }
    shelf_2 = {
        'type': 'metal',
        'size': 'large'
        }

    @pytest.mark.parametrize('books', [
        pytest.param(None, marks=pytest.mark.xfail),
        [],
        [book_1],
        [Book(book_1)],
        [book_1, book_2],
        [Book(book_1), Book(book_2)]
        ])
    @pytest.mark.parametrize('shelves', [
        None,
        [],
        [shelf_1],
        [Bookshelf(shelf_1)],
        [shelf_1, shelf_2],
        [Bookshelf(shelf_1), Bookshelf(shelf_2)]
        ])
    def test_managed_list(self, books, shelves):
        assert Library({
            'books': books,
            'shelves': shelves
            })
