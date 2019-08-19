"""
Utils to support base_model modules.
:date_created: 2018-12-05
"""

from kilimanjaro_src.misc.my_utils import PulsemAuthors, classproperty as utils_classproperty
from kilimanjaro_src.resource.base_model.abc_restrictions.messages import SystemMessages


__author__ = PulsemAuthors.Tim

classproperty = utils_classproperty  # TODO: Custom classproperty to support ABCRestrictions specifically


def compare_cls(cls_name, other):
    """
    Util to adhere to DRY concept for comparing class names. This is used to make sure abstract classes are
    not instantiated.
    :param cls_name:
    :param other:
    :raises: NotImplementedError
    """
    if cls_name == other:
        raise NotImplementedError(SystemMessages.instantiation_error)


def already_declared(_cls_ref, attr_name, attrs):
    if getattr(_cls_ref, attr_name, ()):
        for attr in attrs:
            if attr in getattr(_cls_ref, attr_name):
                return attr


def es_doc_id_maker(instance, params):
    """
    Create elasticsearch document ID
    :param instance:
    :param params: list of params required to make the key
    :return:
    :rtype: str
    """
    return '-'.join([str(instance[p]) for p in params])
