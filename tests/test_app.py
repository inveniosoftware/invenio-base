# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization or
# submit itself to any jurisdiction.

"""Test basic application."""

from __future__ import absolute_import, print_function

import logging
import warnings
from os.path import exists, join

import pytest
from click.testing import CliRunner
from flask import Blueprint, Flask, current_app
from mock import patch
from pkg_resources import EntryPoint
from werkzeug.routing import BaseConverter
from werkzeug.wsgi import DispatcherMiddleware


from invenio_base import __version__
from invenio_base.app import _loader, app_loader, base_app, blueprint_loader, \
    converter_loader, configure_warnings, create_app_factory, create_cli


class ListConverter(BaseConverter):
    """Simple list converter."""

    def to_python(self, value):
        """Return Python object."""
        return value.split('+')

    def to_url(self, values):
        """Return string."""
        return '+'.join(BaseConverter.to_url(value)
                        for value in values)


#
# Mock helpers
#
class MockLoggingHandler(logging.Handler):
    """Mock logging handler to check for expected logs."""

    def __init__(self, *args, **kwargs):
        """Initialize handler."""
        self.reset()
        logging.Handler.__init__(self, *args, **kwargs)

    def emit(self, record):
        """Emit log record by saving message to internal list."""
        self.messages[record.levelname.lower()].append(record.getMessage())

    def reset(self):
        """Reset internal list of messages."""
        self.messages = {
            'debug': [],
            'info': [],
            'warning': [],
            'error': [],
            'critical': [],
        }


class MockEntryPoint(EntryPoint):
    """Mocking of entrypoint."""

    def load(self):
        """Mock load entry point."""
        if self.name == 'fail':
            raise Exception("Fail")
        return self.name


class NoRequireEntryPoint(EntryPoint):
    """Load without requirements check."""

    def load(self):
        """Mock load entry point."""
        return super(NoRequireEntryPoint, self).load(require=False)


def _mock_entry_points(name):
    data = dict(
        entrypoint1=[MockEntryPoint('ep1.e1', 'ep1.e1'),
                     MockEntryPoint('ep1.e2', 'ep1.e2'), ],
        entrypoint2=[MockEntryPoint('ep2.e1', 'ep2.e1'),
                     MockEntryPoint('ep2.e2', 'ep2.e2'), ],
        entrypoint3=[MockEntryPoint('fail', 'ep3.e1',), ],
        entrypoint4=[NoRequireEntryPoint.parse(
            'mylist = test_app:ListConverter'), ],
    )
    names = data.keys() if name is None else [name]
    for key in names:
        for entry_point in data[key]:
            yield entry_point


#
# Tests
#
def test_version():
    """Test version."""
    assert __version__


def test_configure_warnings():
    """Test warnings configuration."""
    logger = logging.getLogger('py.warnings')
    handler = MockLoggingHandler()
    logger.addHandler(handler)

    # Warnings not routed through logging
    warnings.warn("Test")
    assert handler.messages['warning'] == []

    # Warnings through logging
    configure_warnings()
    warnings.warn("A warning")
    assert "A warning" in handler.messages['warning'][0]

    handler.reset()
    warnings.warn("Pending deprecation", PendingDeprecationWarning)
    warnings.warn("Deprecation", DeprecationWarning)
    assert len(handler.messages['warning']) == 1

    handler.reset()
    warnings.simplefilter("always")
    warnings.warn("Pending deprecation", PendingDeprecationWarning)
    warnings.warn("Deprecation", DeprecationWarning)
    assert len(handler.messages['warning']) == 2
    warnings.resetwarnings()


@patch('pkg_resources.iter_entry_points', _mock_entry_points)
def test_loader():
    """Test loader."""
    app = Flask(__name__)
    found = []
    _loader(app, lambda x: found.append(x), entry_points=None, modules=None)
    assert found == []

    # Modules
    found = []
    _loader(app, lambda x: found.append(x), modules=['a', 'b'])
    assert found == ['a', 'b']

    # Entry points
    found = []
    _loader(
        app,
        lambda x: found.append(x), entry_points=['entrypoint1', 'entrypoint2'])
    assert found == ['ep1.e1', 'ep1.e2', 'ep2.e1', 'ep2.e2']

    # Modules and entry points (entry points loaded before modules)
    found = []
    _loader(
        app,
        lambda x: found.append(x),
        entry_points=['entrypoint1', 'entrypoint2'],
        modules=['a', 'b']
    )
    assert found == ['ep1.e1', 'ep1.e2', 'ep2.e1', 'ep2.e2', 'a', 'b']


@patch('pkg_resources.iter_entry_points', _mock_entry_points)
def test_loader_exceptions():
    """Test exceptions during loading."""
    app = Flask(__name__)
    handler = MockLoggingHandler()
    app.logger.addHandler(handler)

    def _raise_func():
        raise Exception()

    assert len(handler.messages['error']) == 0
    pytest.raises(
        Exception, _loader, app, lambda x: x(),
        entry_points=None, modules=[_raise_func])
    assert len(handler.messages['error']) == 1

    pytest.raises(
        Exception, _loader, app, lambda x: x(),
        entry_points=['entrypoint3'], modules=None)
    assert len(handler.messages['error']) == 2


def test_app_loader():
    """Test app loader."""
    class FlaskExt(object):
        def __init__(self, app):
            self.app = app
            app.extensions['ext'] = self

    app = Flask('testapp')

    assert 'ext' not in app.extensions
    app_loader(app, modules=[FlaskExt])
    assert 'ext' in app.extensions
    assert app.extensions['ext'].app is app


def test_blueprint_loader():
    """Test app loader."""
    bp = Blueprint('test', 'test')
    app = Flask('testapp')

    assert len(app.blueprints) == 0
    blueprint_loader(app, modules=[bp])
    assert len(app.blueprints) == 1


def test_coverter_loader():
    """Test converter loader."""
    app = Flask('testapp')

    assert 'mylist' not in app.url_map.converters
    converter_loader(app, modules={'mylist': ListConverter})
    assert 'mylist' in app.url_map.converters


@patch('pkg_resources.iter_entry_points', _mock_entry_points)
def test_coverter_loader_from_entry_points():
    """Test converter loader."""
    app = Flask('testapp')

    assert 'mylist' not in app.url_map.converters
    converter_loader(app, entry_points=['entrypoint4'])
    assert 'mylist' in app.url_map.converters


@patch('pkg_resources.iter_entry_points', _mock_entry_points)
def test_coverter_loader_fail():
    """Test converter loader."""
    app = Flask('testapp')

    with pytest.raises(Exception):
        converter_loader(app, entry_points=['entrypoint3'])


def test_base_app(tmppath):
    """Test base app creation."""
    # Test default static_url_path and CLI initialization
    app = base_app('test')
    assert app.name == 'test'
    assert app.cli
    assert app.static_url_path == '/static'
    assert app.instance_path != tmppath

    # Test specifying instance path
    app = base_app('test', instance_path=tmppath)
    assert app.instance_path == tmppath
    assert exists(app.instance_path)
    assert app.static_folder is None

    # Test automatic instance path creation
    newpath = join(tmppath, 'test')
    assert not exists(newpath)
    app = base_app('test', instance_path=newpath)
    assert exists(newpath)
    assert app.static_folder is None

    # Test static folder
    staticpath = join(tmppath, 'teststatic')
    app = base_app('test', static_folder=staticpath)
    assert app.static_folder == staticpath
    assert app.instance_path is not None

    # Test static + instance folder
    staticpath = join(tmppath, 'teststatic')
    app = base_app('test', instance_path=tmppath,
                   static_folder=staticpath)
    assert app.static_folder == staticpath
    assert app.instance_path == tmppath

    # Test choice loader
    searchpath = join(tmppath, "tpls")
    app = base_app('test', template_folder=searchpath)
    assert app.jinja_loader.searchpath == [searchpath]

    app = base_app('test')
    assert app.jinja_loader.searchpath == [join(app.root_path, 'templates')]


def test_create_app_factory():
    """Test app factory factory."""
    class FlaskExt(object):
        def __init__(self, app):
            self.app = app
            app.extensions['ext'] = self

    bp = Blueprint('test', 'test')

    # Create app
    create_app = create_app_factory(
        'test', blueprints=[bp], extensions=[FlaskExt])
    assert callable(create_app)

    app = create_app()
    assert app.name == 'test'
    assert len(app.blueprints) == 1
    assert 'ext' in app.extensions


def test_create_app_factory_config_loader():
    """Test app factory conf loader."""
    def _config_loader(app, **kwargs):
        app.config['CONFIG_LOADER'] = True
        app.config.update(kwargs)

    create_app = create_app_factory('test', config_loader=_config_loader)
    app = create_app(KWARGS_TEST=True)
    assert app.config['CONFIG_LOADER']
    assert app.config['KWARGS_TEST']


def test_create_app_factory_wsgi_factory():
    """Test app factory wsgi factory."""
    def _wsgi_factory(app):
        return DispatcherMiddleware(app.wsgi_app, {'/test': Flask('dispatch')})

    create_app = create_app_factory('test', wsgi_factory=_wsgi_factory)
    app = create_app()
    assert isinstance(app.wsgi_app, DispatcherMiddleware)


def test_create_cli_with_app():
    """Test create cli."""
    app_name = 'mycmdtest'
    create_app = create_app_factory(app_name)
    cli = create_cli(create_app=create_app)

    @cli.command()
    def test_cmd():
        print(current_app.name, current_app.debug)

    runner = CliRunner()
    result = runner.invoke(cli)
    assert result.exit_code == 0

    result = runner.invoke(cli, ['test_cmd'])
    assert result.exit_code == 0
    assert u'{0} False\n'.format(app_name) in result.output

    result = runner.invoke(cli, ['--debug', 'test_cmd'])
    assert result.exit_code == 0
    assert u'{0} True\n'.format(app_name) in result.output


def test_create_cli_without_app():
    """Test create cli."""
    from invenio_base.cli import cli

    @cli.command()
    def test_cmd():
        print(current_app.name)

    runner = CliRunner()
    result = runner.invoke(cli)
    assert result.exit_code == 0

    result = runner.invoke(cli, ['test_cmd'])
    assert result.exit_code != 0
    assert 'FLASK_APP' in result.output
