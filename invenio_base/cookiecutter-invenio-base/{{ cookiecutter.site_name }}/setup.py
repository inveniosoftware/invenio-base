# -*- coding: utf-8 -*-

"""{{ cookiecutter.site_name }} Invenio instance."""

import os

from setuptools import find_packages, setup

# Get the version string. Cannot be done with import!
version = {}
with open(os.path.join('{{ cookiecutter.package_name }}', 'version.py'), 'rt') as fp:
    exec(fp.read(), version)

setup(
    name='{{ cookiecutter.site_name }}',
    version=version['__version__'],
    description=__doc__,
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'console_scripts': [
            '{{ cookiecutter.package_name }} = {{ cookiecutter.package_name }}.cli:cli'
        ],
    },
    install_requires=[
        'invenio-base>=1.0.0a3',
    ],
)
