# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
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
from mock import Mock, patch

from invenio_base.cmd import instance


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

        if os.getenv('REQUIREMENTS') == 'devel':
            assert call(
                ['pip', 'install', '-r', 'requirements-devel.txt']
            ) == 0

        assert call(['pip', 'install', '-e', '.']) == 0
        assert pkg_resources.get_distribution(site_name)

        app = importlib.import_module(site_name + '.factory').create_app()
        with app.app_context():
            assert app.name == site_name

        assert call([site_name, '--help']) == 0
        assert call(['pip', 'uninstall', site_name, '-y']) == 0

        os.chdir(cwd)


def test_list_entry_points():
    """Test listing of entry points."""
    mock_working_set = pkg_resources.WorkingSet(entries=[])
    dist = pkg_resources.get_distribution('invenio-base')
    mock_working_set.add(dist)

    with patch('invenio_base.cmd.working_set', new=mock_working_set):
        runner = CliRunner()

        # Test select an existing entry point
        result = runner.invoke(
            instance, ['entrypoints', '-e', 'console_scripts'])
        assert result.exit_code == 0
        lines = result.output.splitlines()
        assert lines[0] == 'console_scripts'
        assert lines[1] == '  inveniomanage = invenio_base.cli:cli'

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
