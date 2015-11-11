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

"""Test wsgi application."""

from __future__ import absolute_import, print_function, unicode_literals

from flask import Flask

from invenio_base.wsgi import create_wsgi_factory


def test_create_wsgi_factory():
    """Test wsgi factory creation."""
    api = Flask('api')

    @api.route("/")
    def apiview():
        return "api"

    app = Flask('app')

    @app.route("/")
    def appview():
        return "app"

    # Test factory creation
    factory = create_wsgi_factory({'/api': lambda **kwargs: api})
    app.wsgi_app = factory(app)

    with app.test_client() as client:
        assert client.get('/').status_code == 200
        assert b'app' in client.get('/').data
        assert client.get('/api/').status_code == 200
        assert b'api' in client.get('/api/').data
