"""
Nest a DataObject in another DataObject.
"""
from do_py import DataObject, R


class Contact(DataObject):
    _restrictions = {
        'phone_number': R.STR
        }


class Author(DataObject):
    """
    This DataObject is nested under `VideoGame` and nests `Contact`.
    :restriction id:
    :restriction name:
    :restriction contact: Nested DataObject that represents contact information for this author.
    """
    _restrictions = {
        'id': R.INT,
        'name': R.STR,
        'contact': Contact
        }


class VideoGame(DataObject):
    """
    This DataObject is nested under nests `Author`.
    :restriction id:
    :restriction name:
    :restriction author: Nested DataObject that represents author information for this video game.
    """
    _restrictions = {
        'id': R.INT,
        'name': R.NULL_STR,
        'author': Author
        }


# Data objects must be instantiated at their **init** with a dictionary and strict True(default) or False.
instance = VideoGame({
    'id': 1985,
    'name': 'The Game',
    'author': {
        'id': 3,
        'name': 'You Lose',
        'contact': {
            'phone_number': '555-555-5555'
            }
        }
    }, strict=False)
print(instance)
# output: VideoGame{"author": {"contact": {"phone_number": "555-555-5555"}, "id": 3, "name": "You Lose"}, "id": 1985, "name": "The Game"}
