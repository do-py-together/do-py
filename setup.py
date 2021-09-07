"""
Setup script
"""
from __future__ import print_function

import json
import os
import re

import setuptools


dir_path = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(dir_path, 'README.md'), 'r') as fh:
    long_description = fh.read()

package = json.load(open(os.path.join(dir_path, 'package.json'), 'r'))
author = package['author']
author_name = re.sub('(<(?:.*)>)', '', author).strip()
author_email = re.search(r'<(.*)>', author).groups()[0]

announcement = 'Building for version %s' % package['version']
print('%s' % ''.join(['*'] * len(announcement)))
print(announcement)
print('%s\n\n' % ''.join(['*'] * len(announcement)))

setuptools.setup(
    name=package['name'],
    version=package['version'],
    author=author_name,
    author_email=author_email,
    description=package['description'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/do-py-together/do-py',
    install_requires=[
        'future==0.18.2'
        ],
    packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
    # https://pypi.org/classifiers/
    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Operating System :: OS Independent',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        ],
    keywords=['development', 'OO']
    )
