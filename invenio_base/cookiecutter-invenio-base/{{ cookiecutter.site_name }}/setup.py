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
        'flask.commands': [
        ],
        'invenio_base.blueprints': [
            '{{ cookiecutter.package_name }} = '
            '{{ cookiecutter.package_name }}.views:blueprint',
        ],
        'invenio_config.module': [
            '{{ cookiecutter.package_name }} = '
            '{{ cookiecutter.package_name }}.config',
        ],
    },
    install_requires=[
        'Flask>=0.11.1',
        'invenio-app>=1.0.0a1',
        'invenio-assets>=1.0.0a4',
        'invenio-base>=1.0.0a11',
        'invenio-config>=1.0.0b1',
        'invenio-db>=1.0.0a9',
        'invenio-indexer>=1.0.0a2',
        'invenio-jsonschemas>=1.0.0a5',
        'invenio-marc21>=1.0.0a1',
        'invenio-oaiserver>=1.0.0a1',
        'invenio-pidstore>=1.0.0a6',
        'invenio-records-rest>=1.0.0a11',
        'invenio-records-ui>=1.0.0a4',
        'invenio-search-ui>=1.0.0a2',
        'invenio-search>=1.0.0a5',
        'invenio-theme>=1.0.0a17',
    ],
)
