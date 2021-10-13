# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
# Copyright (C) 2021      TU Wien.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Base package for building Invenio application factories."""

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()
history = open('CHANGES.rst').read()


# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('invenio_base', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']


tests_require = [
    'mock>=1.3.0',
    'invenio-config>=1.0.0',
    'pytest-invenio>=1.4.0'
]

extras_require = {
    'docs': [
        'Sphinx>=3',
    ],
    'tests': tests_require,
}

extras_require['all'] = []
for reqs in extras_require.values():
    extras_require['all'].extend(reqs)

setup_requires = [
    'pytest-runner>=2.6.2',
]

install_requires = [
    'blinker>=1.4',
    'Flask>=1.0.4,<3.0',
    'Werkzeug>=1.0.1,<3.0',
    'six>=1.12.0',
]

packages = find_packages()

setup(
    name='invenio-base',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    keywords='invenio',
    license='MIT',
    author='CERN',
    author_email='info@inveniosoftware.org',
    url='https://github.com/inveniosoftware/invenio-base',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'console_scripts': [
            'inveniomanage = invenio_base.__main__:cli',
        ],
        'flask.commands': [
            'instance = invenio_base.cli:instance',
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Development Status :: 5 - Production/Stable',
    ],
)
