"""
Give the DataObject restriction default values.
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
    :restriction favorite_number: The number I favor the most. Strings not allowed.
    :restriction favorite_candy: If we don't know what someone's favorite candy is, the default is "Unknown".
    :restriction favorite_movie: My favorite movie. This is optional because a `None` IS allowed!
    """
    _restrictions = {
        'favorite_number': R.INT,
        'favorite_candy': R('Jolly Ranchers', 'Nerds', 'Unknown', default='Unknown'),
        'favorite_movie': R.NULL_STR
        }


# In order to use the default value when instantiating a DataObject, we must instantiate it in non-strict mode.
instance = MyFavoriteStuff({
    'favorite_number': 1985,
    'favorite_candy': 'Jolly Ranchers'
    }, strict=False)

print(instance)
# output: MyFavoriteStuff{"favorite_candy": "Jolly Ranchers", "favorite_number": 1985, "favorite_movie": null}
print(instance.favorite_candy)
# output: Jolly Ranchers
