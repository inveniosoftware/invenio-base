# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test cli application."""

from __future__ import absolute_import, print_function

import logging
import os
from subprocess import call

import pkg_resources
import pytest
from click.testing import CliRunner
from flask.cli import ScriptInfo
from mock import MagicMock, Mock, patch

from invenio_base.app import create_app_factory
from invenio_base.cli import instance


@pytest.fixture(autouse=True)
def force_logging():
    """Flask 0.13/1.0 changed logging to not add the default
    handler in case a handler is already installed. pytest
    automatically adds a handler to the root logger, causing
    Flask not to add a handler. This is an issue when testing
    Click output which uses the logger to output to the console.
    """
    try:
        from flask.logging import default_handler
        logger = logging.getLogger('flask.app')
        if default_handler not in logger.handlers:
            logger.handlers.append(default_handler)
    except:
        pass


def test_instance_create():
    """Test ``instance create`` command."""
    runner = CliRunner()

    # Missing arg
    result = runner.invoke(instance, ['create'])
    assert result.exit_code != 0

    # With arg
    with runner.isolated_filesystem():
        result = runner.invoke(instance, ['create', 'mysite'])
        assert result.exit_code == 0


def test_list_entry_points():
    """Test listing of entry points."""
    mock_working_set = pkg_resources.WorkingSet(entries=[])
    dist = pkg_resources.get_distribution('invenio-base')
    mock_working_set.add(dist)

    with patch('invenio_base.cli.working_set', new=mock_working_set):
        runner = CliRunner()

        # Test select an existing entry point
        result = runner.invoke(
            instance, ['entrypoints', '-e', 'console_scripts'])
        assert result.exit_code == 0
        lines = result.output.splitlines()
        assert lines[0] == 'console_scripts'
        assert lines[1] == '  inveniomanage = invenio_base.__main__:cli'

        # Test no entry point matching
        result = runner.invoke(instance, ['entrypoints', '-e', 'nothing_here'])
        assert result.exit_code == 0
        assert result.output == ""

        # By default we only show entry points groups starting with "invenio"
        dist.get_entry_map = Mock(
            return_value={
                'invenio_base.apps': {
                    'myapp': 'myapp = myapp:MyApp',
                    'app1': 'app1 = app1:MyApp'
                },
                'invenio_base.api_apps': {
                    'myapi': 'myapi = myapi:MyApp'
                },
                'console_scripts': {
                    'mycli': 'mycli = cli:main'
                },
            })
        result = runner.invoke(instance, [
            'entrypoints',
        ])
        assert result.exit_code == 0
        print(result.output.splitlines())
        lines = result.output.splitlines()
        assert lines[0] == 'invenio_base.api_apps'
        assert lines[1] == '  myapi = myapi:MyApp'
        assert lines[2] == 'invenio_base.apps'
        assert lines[3] == '  app1 = app1:MyApp'
        assert lines[4] == '  myapp = myapp:MyApp'


def test_migrate_secret_key():
    """Test cli command for SECRET_KEY change."""
    def _config_loader(app, **kwargs):
        app.config['CONFIG_LOADER'] = True
        app.config.update(kwargs)

    create_app = create_app_factory('test', config_loader=_config_loader)
    app = create_app(KWARGS_TEST=True)

    script_info = ScriptInfo(create_app=lambda info: app)

    # Check that CLI command fails when the SECRET_KEY is not set.
    with app.app_context():
        runner = CliRunner()
        result = runner.invoke(
            instance, ['migrate-secret-key', '--old-key', 'OLD_SECRET_KEY'],
            obj=script_info)
        assert result.exit_code == 1
        assert 'Error: SECRET_KEY is not set in the configuration.' in \
            result.output

    app.secret_key = "SECRET"
    with patch('pkg_resources.EntryPoint') as MockEntryPoint:
        # Test that the CLI command succeeds when the entrypoint does
        # return a function.
        entrypoint = MockEntryPoint('ep1', 'ep1')
        entrypoint.load.return_value = MagicMock()
        with patch('invenio_base.cli.iter_entry_points',
                   return_value=[entrypoint]):
            result = runner.invoke(
                instance, ['migrate-secret-key', '--old-key',
                           'OLD_SECRET_KEY'],
                obj=script_info)
            assert result.exit_code == 0
            assert entrypoint.load.called
            entrypoint.load.return_value.assert_called_with(
                old_key='OLD_SECRET_KEY'
            )
            assert 'Successfully changed secret key.' in result.output

        # Test that the CLI command fails correctly when the entrypoint does
        # not return a function.
        entrypoint = MockEntryPoint('ep2', 'ep2')
        entrypoint.load.return_value = 'ep2'
        with patch('invenio_base.cli.iter_entry_points',
                   return_value=[entrypoint]):
            result = runner.invoke(
                instance, ['migrate-secret-key', '--old-key',
                           'OLD_SECRET_KEY'],
                obj=script_info)
            assert result.exit_code == 1
            assert entrypoint.load.called
            assert 'Failed to initialize entry point' in result.output
