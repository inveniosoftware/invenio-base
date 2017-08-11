# -*- coding: utf-8 -*-

"""{{ cookiecutter.site_name }} Invenio instance."""

import os

from setuptools import find_packages, setup

# Get the version string. Cannot be done with import!
version = {}
with open(os.path.join('{{ cookiecutter.package_name }}',
                       'version.py'), 'rt') as fp:
    exec(fp.read(), version)

invenio_db_version = '>=1.0.0b8,<1.1.0'

extras_require = {
    # Databases
    'mysql': [
        'invenio-db[mysql]' + invenio_db_version,
    ],
    'postgresql': [
        'invenio-db[postgresql]' + invenio_db_version,
    ],
    # Elasticsearch version
    'elasticsearch2': [
        'elasticsearch>=2.0.0,<3.0.0',
        'elasticsearch-dsl>=2.0.0,<3.0.0',
    ],
}

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
            '{{ cookiecutter.package_name }} = invenio_app.cli:cli'
        ],
        'invenio_config.module': [
            '{{ cookiecutter.package_name }} = '
            '{{ cookiecutter.package_name }}.config',
        ],
    },
    install_requires=[
        # TODO: Below dependencies should be replaced with:
        #  'inveno[base,auth,metadata]>=3.0.0,<3.1.0'
        # Base bundle
        'invenio-admin>=1.0.0b3,<1.1.0',
        'invenio-assets>=1.0.0b6,<1.1.0',
        'invenio-base>=1.0.0a14,<1.1.0',
        'invenio-celery>=1.0.0b3,<1.1.0',
        'invenio-cache>=1.0.0b1,<1.1.0',
        'invenio-config>=1.0.0b3,<1.1.0',
        'invenio-formatter>=1.0.0b3,<1.1.0',
        'invenio-i18n>=1.0.0b4,<1.1.0',
        'invenio-logging>=1.0.0b2,<1.1.0',
        'invenio-mail>=1.0.0b1,<1.1.0',
        'invenio-rest[cors]>=1.0.0b1,<1.1.0',
        'invenio-theme>=1.0.0b4,<1.1.0',
        # Auth bundle
        'invenio-access>=1.0.0b1,<1.1.0',
        'invenio-accounts>=1.0.0b8,<1.1.0',
        'invenio-oauth2server>=1.0.0b1,<1.1.0',
        'invenio-oauthclient>=1.0.0b2,<1.1.0',
        'invenio-userprofiles>=1.0.0b1,<1.1.0',
        # Metadata bundle
        'invenio-indexer>=1.0.0a10,<1.1.0',
        'invenio-jsonschemas>=1.0.0a5,<1.1.0',
        'invenio-oaiserver>=1.0.0a13,<1.1.0',
        'invenio-pidstore>=1.0.0b2,<1.1.0',
        'invenio-records-rest>=1.0.0b1,<1.1.0',
        'invenio-records-ui>=1.0.0a9,<1.1.0',
        'invenio-records>=1.0.0b1,<1.1.0',
        'invenio-search-ui>=1.0.0a7,<1.1.0',
        'invenio-search>=1.0.0a10,<1.1.0',
        # App
        'invenio-app>=1.0.0b1,<1.1.0',
    ],
    extras_require=extras_require,
)
