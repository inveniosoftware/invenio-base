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

import os
from subprocess import call

from click.testing import CliRunner

from invenio_base.cmd import instance


def test_instance_create():
    """Test startproject command."""
    runner = CliRunner()

    # Missing arg
    result = runner.invoke(instance, ['create'])
    assert result.exit_code != 0

    # With arg
    with runner.isolated_filesystem():
        result = runner.invoke(instance, ['create', 'mysite'])
        assert result.exit_code == 0


def test_instance_create_created_project():
    """Test startproject command checking the result project."""
    runner = CliRunner()

    # Missing arg
    result = runner.invoke(instance, ['create'])
    assert result.exit_code != 0

    # With arg
    with runner.isolated_filesystem():
        site_name = 'mysite2'
        result = runner.invoke(instance, ['create', site_name])
        assert result.exit_code == 0
        path_to_folder = os.path.join(os.getcwd(), site_name)
        path_to_manage = os.path.join(path_to_folder, 'manage.py')
        assert call(['python',  path_to_manage]) == 0
