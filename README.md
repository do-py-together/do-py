# Do-Py
Do-Py, shorthand for DataObject Python, is a data-validation and standardization library wrapping Python dictionaries.

![release](https://img.shields.io/github/package-json/v/do-py-together/do-py?label=release&logo=release&style=flat-square)
![build](https://img.shields.io/github/workflow/status/do-py-together/do-py/test?style=flat-square)
![coverage](https://img.shields.io/codecov/c/github/do-py-together/do-py?style=flat-square)
![dependencies](https://img.shields.io/librariesio/release/pypi/do-py?style=flat-square)

##### Project milestones

![Beta ready](https://img.shields.io/github/milestones/progress/do-py-together/do-py/1?label=Issues%20until%20Beta&style=flat-square)
![Stable ready](https://img.shields.io/github/milestones/progress/do-py-together/do-py/2?label=Issues%20until%20Stable&style=flat-square)

## Quick-Start

### Make a basic DataObject.
We will make a class and call it `MyFavoriteStuff`. We
will inherit the DataObject class to gain all its wonderful features.
Here you can see we must define the '_restrictions' attribute.
```python
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
```


### Using restrictions.

Restrictions are written using `do_py.R`. `R` allows developers to define custom value restrictions as well as type
restrictions using the special shortcuts. Here are a few examples of how you can write value restrictions and type
restrictions using the type short-cuts.
```python
from do_py import DataObject, R


class TypeShorCuts(DataObject):
    """
    All of the restrictions written for this DataObject us R's type shortcuts.
    """
    _restrictions = {
        # integer
        'int': R.INT,
        'nullable_int': R.NULL_INT,
        # string
        'str': R.STR,
        'nullable_str': R.NULL_STR,
        # bool
        'bool': R.BOOL,
        # date and datetime
        'date': R.DATE,
        'nullable_date': R.NULL_DATE,
        'datetime': R.DATETIME,
        'nullable_datetime': R.NULL_DATETIME,
        # other (these are rarely used(aqw
        'set': R.SET,
        'list': R.LIST,
        }


class ValueRestrictions(DataObject):
    """
    All of the restrictions for this class are value restrictions.
    """
    _restrictions = {
        # number values
        'integers': R(1, 2, 3),
        'integers and None': R(1, 2, 3, None),
        # string values
        'strings': R('hello', 'hi', 'sup'),
        'nullable_strings': R('hello', 'hi', 'sup', None),
        }
```


### Give the DataObject default values.
DataObjects are able to define the default value for their restrictions. If a developer is not sure
if a value will be available, defaults are a very useful utility. We have updated the original example to have
a default value for it's restriction `favorite_candy.`

In order to use the default value when instantiating a DataObject, we must instantiate it in non-strict mode.

Strict instantiation is used by default. In strict instantiation, the data passed in must contain all the
keys defined in the DataObject's `_restrictions`.

With non-strict initialization, it is acceptable to have some keys missing per DO _restrictions. For all missing keys,
the default restriction value is used. This section provides an example of using a DataObject in non-strict mode
so that we can use the default values for `favorite_candy`.
```python
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
```


### Nest a DataObject in another DataObject.
```python
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
```


### Nest a list of DataObjects in another DataObject.
```python
from do_py import DataObject, R
from do_py.common.managed_list import ManagedList


class Book(DataObject):
    """
    There are multiple books in the library!
    :restriction name: Name of the book.
    :restriction author: The author of the book.
    """
    _restrictions = {
        'name': R.STR,
        'author': R.STR,
        }


class Library(DataObject):
    """
    This DataObject represents a library which contains multiple books.
    :restriction city: The city the library is located in.
    :restriction books: A list of instances of the DataObject "Book".
    """
    _restrictions = {
        'city': R.STR,
        'books': ManagedList(Book)
        }
```



## What is a DataObject?

A DataObject allows us to create Python classes that have strictly defined fields called "restrictions". Restrictions
are defined for a DataObject using the `_restriction` attribute. See the Quick-start section.

There are two kinds of restrictions, type and value:
* Value restrictions restrict the value to a specific value in a list.
* Type restrictions restrict the type a value can have: int, str, bool, or other DataObjects.

## Advanced Uses

### Advanced DataObject validations.

Certain use-cases require more complex validations or restrictions that cannot be supported without code execution.
The parent class `Validator` allows us to execute code at instantiation and any time a key is updated. A child of
`Validator` is required to define a `_validate` instance method.
```python
from do_py import R
from do_py.data_object.validator import Validator


class Validated(Validator):
    """
    This DataObject validates that we only have one of key or id, but not both. Since this can't be accomplished only
    using restrictions, we are inheriting from `Validator` so we can attach extra validations.
    """
    _restrictions = {
        'key': R.NULL_STR,
        'id': R.NULL_INT
        }

    def _validate(self):
        """
        Validate that we have exactly one of key or id.

        This function runs at instantiation and any time the instance is updated.
        """
        assert any([self.key, self.id]) and not all([self.key, self.id]), \
            'We need exactly one of id or key to not be None.'
```
