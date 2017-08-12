# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2012, 2013, 2014, 2015, 2016 CERN.
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

"""Test cli application."""

from __future__ import absolute_import, print_function, unicode_literals

import importlib
import os
from subprocess import call

import pkg_resources
from click.testing import CliRunner
from flask.cli import ScriptInfo
from mock import MagicMock, Mock, patch

from invenio_base.app import create_app_factory
from invenio_base.cli import instance


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


def test_instance_create_created_instance():
    """Test ``instance create`` command checking the resulting instance."""
    runner = CliRunner()

    # Missing arg
    result = runner.invoke(instance, ['create'])
    assert result.exit_code != 0

    # With arg
    with runner.isolated_filesystem():
        site_name = 'mysite2'
        result = runner.invoke(instance, ['create', site_name])
        assert result.exit_code == 0

        cwd = os.getcwd()
        path_to_folder = os.path.join(cwd, site_name)
        os.chdir(path_to_folder)

        assert call([
            'pip', 'install', '-e', '.[mysql,postgresql,elasticsearch2]']) == 0
        assert pkg_resources.get_distribution(site_name)

        from invenio_app.factory import create_app
        app = create_app()
        with app.app_context():
            assert app.config.get('THEME_SITENAME') == site_name

        assert call(['invenio', '--help']) == 0
        assert call(['mysite2', '--help']) == 0
        assert call(['pip', 'uninstall', site_name, '-y']) == 0

        os.chdir(cwd)


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
        result = runner.invoke(
            instance, ['entrypoints', '-e', 'nothing_here'])
        assert result.exit_code == 0
        assert result.output == ""

        # By default we only show entry points groups starting with "invenio"
        dist.get_entry_map = Mock(return_value={
            'invenio_base.apps': {
                'myapp': 'myapp = myapp:MyApp',
                'app1': 'app1 = app1:MyApp'},
            'invenio_base.api_apps': {
                'myapi': 'myapi = myapi:MyApp'},
            'console_scripts': {
                'mycli': 'mycli = cli:main'},
        })
        result = runner.invoke(instance, ['entrypoints', ])
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
        result = runner.invoke(instance,
                               ['migrate-secret-key',
                                '--old-key',
                                'OLD_SECRET_KEY'],
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
            assert result.exit_code == -1
            assert entrypoint.load.called
            assert 'Failed to initialize entry point' in result.output
