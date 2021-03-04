"""
Give the DataObject default values.
DataObjects are able to define the default value for their restrictions. If a developer is not sure
if a value will be available, defaults are a very useful utility. We have updated the original example to have
a default value for it's restriction `favorite_candy.`

In order to use the default value when instantiating a DataObject, we must instantiate it in non-strict mode.

Strict instantiation is used by default. In strict instantiation, the data passed in must contain all the
keys defined in the DataObject's `_restrictions`.

With non-strict initialization, it is acceptable to have some keys missing per DO _restrictions. For all missing keys,
the default restriction value is used. This section provides an example of using a DataObject in non-strict mode
so that we can use the default values for `favorite_candy`.
"""
from do_py import DataObject, R


class MyFavoriteStuff(DataObject):
    """
    :restriction favorite_number: The default value is 1.
    :restriction favorite_candy: The default value is is "Unknown".
    :restriction favorite_movie: When nullable, the default value is `None`.
    """
    _restrictions = {
        'favorite_number': R.INT.with_default(1),
        'favorite_candy': R('Jolly Ranchers', 'Nerds', 'Unknown', default='Unknown'),
        'favorite_movie': R.NULL_STR
        }


# In order to use the default value when instantiating a DataObject, we must instantiate it in non-strict mode.
# Any values that are not provided will use defaults.
instance = MyFavoriteStuff({}, strict=False)

print(instance)
# output: MyFavoriteStuff{"favorite_candy": "Unknown", "favorite_number": 1, "favorite_movie": null}
