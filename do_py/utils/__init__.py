"""
Useful methods, classes, and tools.
An important note on utils is that they should have no dependencies on the rest of the project.
"""
from .json_encoder import MyJSONEncoder
from .properties import cached_property, classproperty, is_cached_property, is_classmethod, is_property
