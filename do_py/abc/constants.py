"""
Constants to support base_model modules.
:date_created: 2018-12-05
"""

from builtins import object


class ConstABCR(object):
    """
    Constants supporting ABCRestrictions
    """
    required = '_required_'
    unique = '_unique_'
    metaclass = '__metaclass__'
    is_abstract = '_is_abstract_'
    new = '__new__'
    state = '_state_'
    # Class types
    root = 'root'
    node = 'node'
    leaf = 'leaf'
    restrictions_allowed = [root, node]
