# do-py
A data-validation and standardization library wrapping Python dictionaries.

## Quick Start

```python
from do import DataObject

class A(DataObject):
    _restrictions = {
        'x': [int],
        'y': ([int], None),
        'z': [0, 1]
        }
```


---

## Development
Install do-py in development mode: `python setup.py develop`  
Test: `pipenv run pytest --cov ./do/ --cov-report html ./tests/ `
