"""
Nest a list of DataObjects in another DataObject.
"""
from do_py import DataObject, R
from do_py.common.managed_list import ManagedList


class Book(DataObject):
    """
    There are multiple books in the library!
    :restriction name: Name of the book.
    :restriction author: The author of the book.
    """
    _restrictions = {
        'name': R.STR,
        'author': R.STR,
        }


class Library(DataObject):
    """
    This DataObject represents a library which contains multiple books.
    :restriction city: The city the library is located in.
    :restriction books: A list of instances of the DataObject "Book".
    """
    _restrictions = {
        'city': R.STR,
        'books': ManagedList(Book)
        }
