# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test wsgi application."""

from __future__ import absolute_import, print_function

import pytest
from flask import Flask, request

from invenio_base.wsgi import create_wsgi_factory, wsgi_proxyfix


def test_create_wsgi_factory():
    """Test wsgi factory creation."""
    api = Flask('api')

    @api.route('/')
    def apiview():
        return 'api'

    app = Flask('app')

    @app.route('/')
    def appview():
        return 'app'

    # Test factory creation
    factory = create_wsgi_factory({'/api': lambda **kwargs: api})
    app.wsgi_app = factory(app)

    with app.test_client() as client:
        assert client.get('/').status_code == 200
        assert b'app' in client.get('/').data
        assert client.get('/api/').status_code == 200
        assert b'api' in client.get('/api/').data


@pytest.mark.parametrize('proxies,data', [
    (2, b'4.3.2.1'), (None, b'1.2.3.4')
])
def test_proxyfix(proxies, data):
    """Test wsgi factory creation."""
    app = Flask('app')
    app.config['WSGI_PROXIES'] = proxies

    @app.route('/')
    def appview():
        return str(request.remote_addr)

    # Test factory creation
    app.wsgi_app = wsgi_proxyfix()(app)
    e = {'REMOTE_ADDR': '1.2.3.4'}

    with app.test_client() as client:
        h = {'X-Forwarded-For': '5.6.7.8, 4.3.2.1, 8.7.6.5'}
        assert client.get('/', headers=h, environ_base=e).data == data
