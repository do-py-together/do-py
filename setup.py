"""
Setup script
"""

import json
import re

import setuptools


with open('README.md', 'r') as fh:
    long_description = fh.read()

package = json.load(open('package.json', 'r'))
author = package['author']
author_name = re.search(r'<(.*)>', author).groups()[0]
author_email = re.sub('(<(?:.*)>)', '', author).strip()

setuptools.setup(
    name=package['name'],
    version=package['version'],
    author=author_name,
    author_email=author_email,
    description=package['description'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/do-py-together/do-py',
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Operating System :: OS Independent',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        ],
    keywords=['development', 'OO']
    )
