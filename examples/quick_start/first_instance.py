"""
Make a basic DataObject.
We will make a class and call it `MyFavoriteStuff`. We
will inherit the DataObject class to gain all its wonderful features.
Here you can see we must define the '_restrictions' attribute.
"""
from do_py import DataObject, R


class MyFavoriteStuff(DataObject):
    """
    A DataObject that contains all of my favorite items.
    :restriction favorite_number: The number I favor the most. Strings not allowed.
    :restriction favorite_candy: My favorite candy, this is restricted by value.
    :restriction favorite_movie: My favorite movie. This is optional because a `None` IS allowed!
    """
    # There are two kinds of restrictions, type and value.
    _restrictions = {
        # Type restrictions restrict the type a value can have: int, str, bool, or other DataObjects's
        'favorite_number': R.INT,
        # Value restrictions restrict the value to a specific value in a list.
        'favorite_candy': R('Jolly Ranchers', 'Nerds'),
        # This is a type restriction that allows `None` as a value.
        'favorite_movie': R.NULL_STR
        }


# Instantiate your new DataObject.
instance = MyFavoriteStuff({
    'favorite_number': 1985,
    'favorite_candy': 'Jolly Ranchers',
    'favorite_movie': 'Jolly Green Giant'
    })

print(instance)
# output: MyFavoriteStuff{"favorite_candy": "Jolly Ranchers", "favorite_number": 1985, "favorite_movie": "Jolly Green Giant"}

# You can access values using dot notation or like a `dict`.
print(instance.favorite_number == instance['favorite_number'])
# output: True

print(instance.favorite_number)
print(instance.favorite_candy)
print(instance.favorite_movie)
# output: 1985
# output: Jolly Ranchers
# output: Jolly Green Giant

# Editing the values can also be done very easily.
instance.favorite_number = 2013
print(instance.favorite_number)
# output: 2013
