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

//example=quick_start/first_instance.py
//example=quick_start/restrictions.py
//example=quick_start/default_values.py
//example=quick_start/nested.py
//example=quick_start/nested_list.py

## What is a DataObject?

A DataObject allows us to create Python classes that have strictly defined fields called "restrictions". Restrictions
are defined for a DataObject using the `_restriction` attribute. See the Quick-start section.

There are two kinds of restrictions, type and value:
* Value restrictions restrict the value to a specific value in a list.
* Type restrictions restrict the type a value can have: int, str, bool, or other DataObjects.

## Advanced Uses

//example=advanced/validator.py

--------------

## Contributing

### Setup

```bash
# Install do-py in development mode
python setup.py develop

# Install all dependencies. yarn, pipenv, and then run the following command.
pipenv install --dev
```

### Testing

Run unit tests locally with `pipenv run test`. Code coverage reports for master, branches, and PRs are posted
in [CodeCov](https://codecov.io/gh/do-py-together/do-py).

#### Linting

```bash
pipenv run lint
```

## Developer Notes

This section attempts to explain the inner workings of DataObject at a high level. Our intent is to assist anyone that
wants to develop on top of Do-Py and contribute to this project. More details can be found within the docstrings of our
files, classes, and functions.

//example=contributing/intro.py
//example=contributing/init_method.py
