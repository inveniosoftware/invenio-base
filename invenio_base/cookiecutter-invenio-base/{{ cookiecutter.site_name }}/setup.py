# -*- coding: utf-8 -*-

"""{{ cookiecutter.site_name }} setup script."""

import os
import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

tests_require = [
    'check-manifest>=0.25',
    'coverage>=4.0',
    'isort>=4.2.2',
    'pep257>=0.7.0',
    'pytest-cache>=1.0',
    'pytest-cov>=1.8.0',
    'pytest-pep8>=1.0.6',
    'pytest>=2.8.0',
]

extras_require = {
    'docs': [
        'Sphinx>=1.3',
    ],
    'tests': tests_require,
}

extras_require['all'] = []
for reqs in extras_require.values():
    extras_require['all'].extend(reqs)

setup_requires = [
    'Babel>=1.3',
]

install_requires = [
    'Flask-BabelEx>=0.9.2',
    'invenio-base>=1.0.0a3',
]

packages = find_packages()


class PyTest(TestCommand):
    """PyTest Test."""

    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        """Init pytest."""
        TestCommand.initialize_options(self)
        self.pytest_args = []
        try:
            from ConfigParser import ConfigParser
        except ImportError:
            from configparser import ConfigParser
        config = ConfigParser()
        config.read('pytest.ini')
        self.pytest_args = config.get('pytest', 'addopts').split(' ')

    def finalize_options(self):
        """Finalize pytest."""
        TestCommand.finalize_options(self)
        if hasattr(self, '_test_args'):
            self.test_suite = ''
        else:
            self.test_args = []
            self.test_suite = True

    def run_tests(self):
        """Run tests."""
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('{{ cookiecutter.package_name }}', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='{{ cookiecutter.site_name }}',
    version=version,
    description=__doc__,
    license='GPLv2',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'console_scripts': [
            '{{ cookiecutter.package_name }} = {{ cookiecutter.package_name }}.cli:cli'
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Development Status :: 1 - Planning',
    ],
    cmdclass={'test': PyTest},
)
