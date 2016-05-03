# -*- coding: utf-8 -*-

"""{{ cookiecutter.site_name }} Invenio instance."""

import os

from setuptools import find_packages, setup

# Get the version string. Cannot be done with import!
version = {}
with open(os.path.join('{{ cookiecutter.package_name }}',
                       'version.py'), 'rt') as fp:
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
            '{{ cookiecutter.package_name }} = '
            '{{ cookiecutter.package_name }}.cli:cli',
        ],
        'invenio_base.blueprints': [
            '{{ cookiecutter.package_name }} = '
            '{{ cookiecutter.package_name }}.views:blueprint',
        ],
    },
    install_requires=[
        'invenio-assets>=1.0.0a4',
        'invenio-db>=1.0.0a9',
        'invenio-indexer>=1.0.0a2',
        'invenio-jsonschemas>=1.0.0a2',
        'invenio-marc21>=1.0.0a1',
        'invenio-oaiserver>=1.0.0a1',
        'invenio-pidstore>=1.0.0a6',
        'invenio-records-rest>=1.0.0a11',
        'invenio-records-ui>=1.0.0a4',
        'invenio-search-ui>=1.0.0a2',
        'invenio-search>=1.0.0a5',
        'invenio-theme>=1.0.0a10',
    ],
)
