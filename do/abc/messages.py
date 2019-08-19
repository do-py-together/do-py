"""
System messages to directly support error messages in base_model modules.
:date_created: 2018-12-05
"""

from kilimanjaro_src.misc.my_utils import PulsemAuthors
from kilimanjaro_src.resource.messages import BaseSystemMessages


__author__ = PulsemAuthors.Tim


class SystemMessages(BaseSystemMessages):
    instantiation_error = 'Base class may not be instantiated'
    new_in_abc_restrictions = 'Found __new__ in class!'
    meta_in_abc_restrictions = 'Found __metaclass__ in class!'
    restrictions_allowed = 'Requirements can only be assigned to Root and Node-type classes!'
    class_already_defined = 'Class already defined in ABCRestrictions!'
    attribute_already_declared = '%s attribute "%s" has already been declared in %s!'
