"""
Nest a DataObject in another DataObject.
"""
from do_py import DataObject, R


class Contact(DataObject):
    _restrictions = {
        'phone_number'
        }


class Author(DataObject):
    """
    A DataObject that contains all of my favorite items.
    :restriction id:
    :restriction favorite_candy: My favorite candy, this is restricted by value.
    :restriction favorite_movie: My favorite movie. This is optional because a `None` IS allowed!
    """
    _restrictions = {
        'id': R.INT,
        'name': R.STR,
        'contact': Contact
        }


class VideoGame(DataObject):
    """
    A DataObject that contains all of my favorite items.
    :restriction id:
    :restriction favorite_candy: My favorite candy, this is restricted by value.
    :restriction favorite_movie: My favorite movie. This is optional because a `None` IS allowed!
    """
    _restrictions = {
        'id': R.INT,
        'name': R.NULL_STR,
        'author': Author
        }


# Data objects must be instantiated at their **init** with a dictionary and
#   strict(True(default) or False)
instance = VideoGame({
    'favorite_number': 1985,
    'favorite_candy': 'Jolly Ranchers',
    'favorite_movie': 'Jolly Green Giant'
    })

print(instance)
