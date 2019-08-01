"""
Setup script
"""

import setuptools


with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='do',
    version='0.0.1',
    author='Tim Davis',
    author_email='author@example.com',
    description='Standardized data structures for Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/timdavis3991/do-py',
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
