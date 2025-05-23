# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2022 CERN.
# Copyright (C) 2022 RERO.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test basic application."""

import importlib.metadata
import logging
import warnings
from os.path import exists, join
from unittest.mock import patch

import click
import pytest
from click.testing import CliRunner
from flask import Blueprint, Flask, current_app
from importlib_metadata import EntryPoint
from werkzeug.routing import BaseConverter

from invenio_base import __version__
from invenio_base.app import (
    _loader,
    app_loader,
    base_app,
    blueprint_loader,
    configure_warnings,
    converter_loader,
    create_app_factory,
    create_cli,
)
from invenio_base.cli import generate_secret_key

try:
    from werkzeug.middleware.dispatcher import DispatcherMiddleware
except ImportError:
    from werkzeug.wsgi import DispatcherMiddleware


class ListConverter(BaseConverter):
    """Simple list converter."""

    def to_python(self, value):
        """Return Python object."""
        return value.split("+")

    def to_url(self, values):
        """Return string."""
        return "+".join(BaseConverter.to_url(value) for value in values)


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
            "debug": [],
            "info": [],
            "warning": [],
            "error": [],
            "critical": [],
        }


class MockEntryPoint(EntryPoint):
    """Mocking of entrypoint."""

    def load(self):
        """Mock load entry point."""
        if self.name == "fail":
            raise Exception("Fail")
        return self.name


def _mock_entry_points(group=None):
    data = dict(
        entrypoint1=[
            MockEntryPoint("ep1.e1", "ep1.e1", "ep1.e1"),
            MockEntryPoint("ep1.e2", "ep1.e2", "ep1.e2"),
        ],
        entrypoint2=[
            MockEntryPoint("ep2.e1", "ep2.e1", "ep2.e1"),
            MockEntryPoint("ep2.e2", "ep2.e2", "ep2.e2"),
        ],
        entrypoint3=[
            MockEntryPoint("fail", "ep3.e1", "ep3.e1"),
        ],
        entrypoint4=[
            MockEntryPoint("mylist", "test_app:ListConverter", "mylist"),
        ],
    )
    names = data.keys() if group is None else [group]
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
    logger = logging.getLogger("py.warnings")
    handler = MockLoggingHandler()
    logger.addHandler(handler)

    # Warnings not routed through logging
    warnings.warn("Test")
    assert handler.messages["warning"] == []

    # Warnings through logging
    configure_warnings()
    warnings.warn("A warning")
    assert "A warning" in handler.messages["warning"][0]

    handler.reset()
    warnings.warn("Pending deprecation", PendingDeprecationWarning)
    warnings.warn("Deprecation", DeprecationWarning)
    assert len(handler.messages["warning"]) == 1

    handler.reset()
    warnings.simplefilter("always")
    warnings.warn("Pending deprecation", PendingDeprecationWarning)
    warnings.warn("Deprecation", DeprecationWarning)
    assert len(handler.messages["warning"]) == 2
    warnings.resetwarnings()


@patch("invenio_base.app.iter_entry_points", _mock_entry_points)
def test_loader():
    """Test loader."""
    app = Flask(__name__)
    found = []
    _loader(app, lambda x: found.append(x), entry_points=None, modules=None)
    assert found == []

    # Modules
    found = []
    _loader(app, lambda x: found.append(x), modules=["a", "b"])
    assert found == ["a", "b"]

    # Entry points
    found = []
    _loader(app, lambda x: found.append(x), entry_points=["entrypoint1", "entrypoint2"])
    assert sorted(found) == ["ep1.e1", "ep1.e2", "ep2.e1", "ep2.e2"]

    # Modules and entry points (entry points loaded before modules)
    found = []
    _loader(
        app,
        lambda x: found.append(x),
        entry_points=["entrypoint1", "entrypoint2"],
        modules=["a", "b"],
    )
    assert sorted(found) == ["a", "b", "ep1.e1", "ep1.e2", "ep2.e1", "ep2.e2"]


@patch("invenio_base.app.iter_entry_points", _mock_entry_points)
def test_loader_exceptions():
    """Test exceptions during loading."""
    app = Flask(__name__)
    handler = MockLoggingHandler()
    app.logger.addHandler(handler)

    def _raise_func():
        raise Exception()

    assert len(handler.messages["error"]) == 0
    pytest.raises(
        Exception, _loader, app, lambda x: x(), entry_points=None, modules=[_raise_func]
    )
    assert len(handler.messages["error"]) == 1

    pytest.raises(
        Exception,
        _loader,
        app,
        lambda x: x(),
        entry_points=["entrypoint3"],
        modules=None,
    )
    assert len(handler.messages["error"]) == 2


def test_app_loader():
    """Test app loader."""

    class FlaskExt(object):
        def __init__(self, app):
            self.app = app
            app.extensions["ext"] = self

    app = Flask("testapp")

    assert "ext" not in app.extensions
    app_loader(app, modules=[FlaskExt])
    assert "ext" in app.extensions
    assert app.extensions["ext"].app is app


def test_blueprint_loader():
    """Test app loader."""
    bp = Blueprint("test", "test")

    def create_blueprint_func(app):
        return Blueprint("test2", "test2")

    app = Flask("testapp")

    assert len(app.blueprints) == 0
    blueprint_loader(app, modules=[bp, create_blueprint_func])
    assert len(app.blueprints) == 2
    assert "test" in app.blueprints
    assert "test2" in app.blueprints


def test_coverter_loader():
    """Test converter loader."""
    app = Flask("testapp")

    assert "mylist" not in app.url_map.converters
    converter_loader(app, modules={"mylist": ListConverter})
    assert "mylist" in app.url_map.converters


@patch("invenio_base.app.iter_entry_points", _mock_entry_points)
def test_coverter_loader_from_entry_points():
    """Test converter loader."""
    app = Flask("testapp")

    assert "mylist" not in app.url_map.converters
    converter_loader(app, entry_points=["entrypoint4"])
    assert "mylist" in app.url_map.converters


@patch("invenio_base.app.iter_entry_points", _mock_entry_points)
def test_coverter_loader_fail():
    """Test converter loader."""
    app = Flask("testapp")

    with pytest.raises(Exception):
        converter_loader(app, entry_points=["entrypoint3"])


def test_base_app(tmp_path):
    """Test base app creation."""
    # Test default static_url_path and CLI initialization
    app = base_app("test")
    assert app.name == "test"
    assert app.cli
    assert app.static_url_path == "/static"
    assert app.instance_path != tmp_path

    # Test specifying instance path
    app = base_app("test", instance_path=tmp_path)
    assert app.instance_path == tmp_path
    assert exists(app.instance_path)
    assert app.static_folder is None

    # Test automatic instance path creation
    newpath = join(tmp_path, "test")
    assert not exists(newpath)
    app = base_app("test", instance_path=newpath)
    assert exists(newpath)
    assert app.static_folder is None

    # Test static folder
    staticpath = join(tmp_path, "teststatic")
    app = base_app("test", static_folder=staticpath)
    assert app.static_folder == staticpath
    assert app.instance_path is not None

    # Test static + instance folder
    staticpath = join(tmp_path, "teststatic")
    app = base_app("test", instance_path=tmp_path, static_folder=staticpath)
    assert app.static_folder == staticpath
    assert app.instance_path == tmp_path

    # Test choice loader
    searchpath = join(tmp_path, "tpls")
    app = base_app("test", template_folder=searchpath)
    assert app.jinja_loader.searchpath == [searchpath]

    app = base_app("test")
    assert app.jinja_loader.searchpath == [join(app.root_path, "templates")]


def test_base_app_class(tmp_path):
    """Test using custom Flask application class."""

    class CustomFlask(Flask):
        pass

    app = base_app("test", app_class=CustomFlask)
    assert isinstance(app, CustomFlask)


def test_create_app_factory():
    """Test app factory factory."""

    class FlaskExt(object):
        def __init__(self, app):
            self.app = app
            app.extensions["ext"] = self

    bp = Blueprint("test", "test")

    # Create app
    create_app = create_app_factory("test", blueprints=[bp], extensions=[FlaskExt])
    assert callable(create_app)

    app = create_app()
    assert app.name == "test"
    assert len(app.blueprints) == 1
    assert "ext" in app.extensions


def test_create_app_debug_flag():
    """Test debug flag propagation (needed by CLI)."""
    create_app = create_app_factory("test")

    assert create_app().debug is False
    assert create_app(debug=True).debug is True


def test_callable_instance_path(tmp_path):
    """Test instance path evaluation."""

    def instance_path():
        return tmp_path

    app = create_app_factory("test", instance_path=instance_path)()
    assert app.instance_path == tmp_path
    assert app.static_folder is None


def test_callable_static_path(tmp_path):
    """Test static path evaluation."""

    def static_folder():
        return join(tmp_path, "teststatic")

    app = create_app_factory("test", static_folder=static_folder)()
    assert app.static_folder == join(tmp_path, "teststatic")
    assert app.instance_path is not None


def test_create_app_factory_config_loader():
    """Test app factory conf loader."""

    def _config_loader(app, **kwargs):
        app.config["CONFIG_LOADER"] = True
        app.config.update(kwargs)

    create_app = create_app_factory("test", config_loader=_config_loader)
    app = create_app(KWARGS_TEST=True)
    assert app.config["CONFIG_LOADER"]
    assert app.config["KWARGS_TEST"]


def test_create_app_factory_wsgi_factory():
    """Test app factory wsgi factory."""

    def _wsgi_factory(app):
        return DispatcherMiddleware(app.wsgi_app, {"/test": Flask("dispatch")})

    create_app = create_app_factory("test", wsgi_factory=_wsgi_factory)
    app = create_app()
    assert isinstance(app.wsgi_app, DispatcherMiddleware)


def test_create_cli_with_app():
    """Test create cli."""
    app_name = "mycmdtest"
    create_app = create_app_factory(app_name)
    cli = create_cli(create_app=create_app)

    @cli.command()
    def test_cmd():
        click.echo(f"{current_app.name} {current_app.debug}")

    runner = CliRunner()
    result = runner.invoke(cli)
    if importlib.metadata.version("click") < "8.2.0":
        assert result.exit_code == 0
    else:
        assert result.exit_code == 2

    result = runner.invoke(cli, ["test-cmd"])
    if importlib.metadata.version("click") < "8.2.0":
        assert result.exit_code == 0
        assert f"{app_name} False\n" in result.output
    else:
        assert result.exit_code == 2
        assert "No such command 'test-cmd'" in result.output


def test_create_cli_without_app():
    """Test create cli."""
    from invenio_base.__main__ import cli

    @cli.command()
    def test_cmd():
        click.echo(current_app.name)

    runner = CliRunner()
    result = runner.invoke(cli)
    if importlib.metadata.version("click") < "8.2.0":
        assert result.exit_code == 0
    else:
        assert result.exit_code == 2


def test_generate_secret_key():
    """Test generation of a secret key."""
    v1 = generate_secret_key()
    v2 = generate_secret_key()
    assert len(v1) == len(v2) == 256
    assert v1 != v2
