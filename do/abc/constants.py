"""
Constants to support base_model modules.
:date_created: 2018-12-05
"""


class ConstABCR(object):
    """
    Constants supporting ABCRestrictions
    """
    required = '_required_'
    unique = '_unique_'
    metaclass = '__metaclass__'
    new = '__new__'
    state = '_state_'
    # Class types
    root = 'root'
    node = 'node'
    leaf = 'leaf'
    restrictions_allowed = [root, node]


class ESConstants(object):
    INTERNAL = 'internal'
    EXTERNAL = 'external'
    EXTERNAL_GTE = 'external_gte'
    allowed_version_types = [INTERNAL, EXTERNAL, EXTERNAL_GTE]
