# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017 CERN.
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

"""Test signals."""

from __future__ import absolute_import, print_function, unicode_literals

from invenio_base.app import create_app_factory
from invenio_base.signals import app_created, app_loaded


def test_create_app_factory():
    """Test signals sending."""
    calls = {'created': 0, 'loaded': 0}
    create_app = create_app_factory('test')

    def _receiver(name):
        def _inner(sender, app=None):
            calls[name] += 1
            calls['{}_app'.format(name)] = app
        return _inner

    app_created.connect(_receiver('created'), sender=create_app, weak=False)
    app_loaded.connect(_receiver('loaded'), sender=create_app, weak=False)

    assert callable(create_app)

    app = create_app()
    assert calls['created'] == 1
    assert calls['loaded'] == 1
    assert calls['created_app'] is app
    assert calls['loaded_app'] is app
