# do-py
A data-validation and standardization library wrapping Python dictionaries.

## Quick Start

```python
from do_py import DataObject

class A(DataObject):
    _restrictions = {
        'x': [int],
        'z': [0, 1]
        }
```
---

## Development
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

####  Run unit tests
```
yarn test 
```

#### Run linter
```bash
pipenv run lint
```
