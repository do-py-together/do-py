# Do-Py
![release](https://img.shields.io/github/package-json/v/do-py-together/do-py?label=release&logo=release&style=flat-square)
![build](https://img.shields.io/github/workflow/status/do-py-together/do-py/test?style=flat-square)
![coverage](https://img.shields.io/codecov/c/github/do-py-together/do-py?style=flat-square)
![dependencies](https://img.shields.io/librariesio/release/pypi/do-py?style=flat-square)

##### Our milestones
![Beta ready](https://img.shields.io/github/milestones/progress/do-py-together/do-py/1?label=Issues%20until%20Beta&style=flat-square)
![Stable ready](https://img.shields.io/github/milestones/progress/do-py-together/do-py/2?label=Issues%20until%20Stable&style=flat-square)

Do-Py, shorthand for DataObject Python, is a data-validation and 
standardization library wrapping Python dictionaries.

## Quick-start

Making a basic DataObject.

```python
from do_py import DataObject
from do_py.common import R

# Here is an example. We will make a class and call it MyFavoriteStuff. We 
# will inherit the DataObject class to gain all its wonderful features. 
# Here you can see we must define the '_restrictions' attribute.
class MyFavoriteStuff(DataObject):
    """
    A DataObject that contains all of my favorite items.
    :restriction favorite_number: The number I favor the most. Strings not allowed.
    :restriction favorite_food: My favorite food, only valid values are strings!
    :restriction favorite_movie: My favorite movie. This is optional because a `None` IS allowed!
    """
    _restrictions = {
        'favorite_number': R.INT,
        'favorite_food': R.STR,
        'favorite_movie': R.NULL_STR
        }

# Data objects must be instantiated at their **init** with a dictionary and 
#   strict(True(default) or False)
instance = MyFavoriteStuff({
    'favorite_number': 1985,
    'favorite_food': 'Jolly Ranchers',
    'favorite_movie': 'Jolly Green Giant'
    })

print(instance)
# output: MyFavoriteStuff{"favorite_food": "Jolly Ranchers", "favorite_number": 1985, "favorite_movie": "Jolly Green Giant"}
```


## What is a DataObject?

A DataObject is class that has special properties and uses that allow us 
to define data in a way that helps to maintain its validity through the system.

```python
from do_py.abc import ABCRestrictions
from do_py.data_object import RestrictedDictMixin


@ABCRestrictions.require('_restrictions')
class DataObject(RestrictedDictMixin):
    """
    You will notice that in this DataObject there is an ABCRestrictions 
    decorator, this simply states that the **_restrictions** attribute 
    **must be present** in the DataObject. This is just a way of using a decorator 
    to require certain items be present in the class. This helps to promote strictness 
    so that a class cannot even be created without the proper attributes.
    """
```


At its most basic level a data object is built of something called a restricted dict mix in. 
A `RestrictedDictMixin` is simply a class that inherits from python dict type. This just 
allows for certain parts of the built in python dictionary to be excluded to help prevent 
unwanted things from occurring. In this class it just takes several of the built in 
functions and turns them off.


#### Strict

In strict initialization, data must contain all the keys required by DO _restrictions.

Strict instantiation is when the data objects restriction dictionary has 
to have all of the defined keys in it be populated upon instantiation.

In this example you can see that the _restrictions is a dictionary that is 
being defined with names of the variables on the left between the quotes and 
its data restriction to the right.

To instantiate this data object with strict instantiation it is as easy as

```python
import MyFavoriteStuff


MyFavoriteStuff(dict(favorite_number=1, favorite_food='Pizza', favorite_movie='The third Star Wars'), strict=True)
# output: MyFavoriteStuff{"favorite_food": "Pizza", "favorite_number": 1, "favorite_movie": "The third Star Wars"}
```

#### Non-strict

In non-strict initialization, it is acceptable to have some keys missing 
per DO _restrictions. For all missing keys, the default restriction value is used.

Non-strict instantiation is when it is okay to have some of the keys that 
are in the restrictions dictionary not be present upon instantiation.

To instantiate this data object with non-strict instantiation

```python
import MyFavoriteStuff


MyFavoriteStuff(dict(favorite_number=1, favorite_food='Pizza'), strict=False)
# output: MyFavoriteStuff{"favorite_food": "Pizza", "favorite_number": 1, "favorite_movie": null}
```

You can see here that we left **favorite_movie** out of the dictionary that 
we use to instantiate the data object. Normally this would cause an error but 
because we instantiated it with strict=False we are allowed to do so.

Once the data object has been instantiated you should know exactly what data 
types it should accept and if it should require all of them upon instantiation.

You can access the values of the properties with either a dot notation or a 
key notation.

```python
import MyFavoriteStuff


MyFavoriteStuff['favorite_food'] == MyFavoriteStuff.favorite_food
print(MyFavoriteStuff.favorite_food)
# output: 'Pizza'
```

This will output the current value that is being held by the key name in the 
restrictions dictionary.

Editing the values can also be done very easily.

```python
print(MyFavoriteStuff)
# output: MyFavoriteStuff{"favorite_food": "Pizza", "favorite_number": 1, "favorite_movie": 'The Third Star Wars'}
MyFavoriteStuff.favorite_food = 'Pasta'
print(MyFavoriteStuff.favorite_food)
# output: MyFavoriteStuff{"favorite_food": "Pasta", "favorite_number": 1, "favorite_movie": 'The Third Star Wars'}
```

--------------

## Contributing
### Setup

#### Install do-py in development mode
```bash
python setup.py develop
```

#### Install all dependencies
Install yarn, pipenv, and then run the following command.
```bash
pipenv install --dev
```

### Testing & Code Quality
Code coverage reports for master, branches, and PRs 
are posted [here in CodeCov](https://codecov.io/gh/do-py-together/do-py).

####  Run unit tests
```
yarn test 
```

#### Run linter
```bash
pipenv run lint
```

### Advanced (Special Functions)

A data object has a special '****init****' function that is responsible for a 
few things. It grabs the setting for strict, and calls the validate_data function 
on itself.

This is a very important function. Notice that we pass validate_data 3 variables 
(not counting cls). **_restrictions** is the dictionary we defined in our DataObject 
in this example its the three restrictions (engine, number_of_wheels, air_conditioning).

**d** stands for data in this case. This variable takes the data we pass in as a 
dictionary upon instantiation.

Finally we have the variable **strict.** This is only used if the user wants to 
use strict=False instantiation.

Now we arrive at the validate_data function. If no data was passed in we use an 
empty dictionary. Next we make sure we have no unaccounted keys in the data that 
were not declared inside the _restrictions dictionary. We then check if the keys 
inside the _restrictions dictionary belong to the data. An error will be raised in 
this case, unless strict=False. In this case the default value for the restriction 
will be used and added to the **_dict** attribute. Once all the keys have been 
checked they will all be inside the **_dict** assuming that there we no errors. 
Finally, we return _dict. So whenever a DataObject is instantiated, you will receive 
a return containing a dictionary of all the data.

```python
class RaceCar(DataObject):
    """
    Example DataObject class
    """
    _restrictions = {
        'engine': R.STR,
        'number_of_wheels': R.INT,
        'air_conditioning': R.BOOL
        }

# Example DataObject instantiation
RaceCar(dict(engine='v8', number_of_wheels=4, air_conditioning=True))

# Below is the dunder init function for DataObject as well as its dependent validate data
def __init__(self, data=None, strict=True):
    self._strict = strict
    super(DataObject, self).__init__(self._validate_data(self._restrictions, data, strict=strict))
    # NOTE: Now that we are done loading, we go back to strict mode
    self._strict = True

@classmethod
def _validate_data(cls, _restrictions, d, strict=True):
    _dict = dict()
    d = {} if d is None else d
    # NOTE: Unrestricted keys are never allowed.
    for k in list(d.keys()):
        if k not in _restrictions:
            raise DataObjectError.from_unknown_key(k, cls)

    # NOTE: Use default in strict for missing keys in data.
    for k, v in _restrictions.items():
        if k not in d:
            if strict:
                raise DataObjectError.from_required_key(k, cls)
            else:
                _dict[k] = v.default
        else:
            try:
                _dict[k] = v(d[k], strict=strict)
            except RestrictionError as e:
                raise DataObjectError.from_restriction_error(k, cls, e)

    return _dict
```
