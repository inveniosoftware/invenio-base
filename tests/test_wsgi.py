# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
# Copyright (C) 2024 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test wsgi application."""

import json

import pytest
from flask import Flask, jsonify, request

from invenio_base.wsgi import create_wsgi_factory, wsgi_proxyfix


def test_create_wsgi_factory():
    """Test wsgi factory creation."""
    api = Flask("api")

    @api.route("/")
    def apiview():
        return "api"

    app = Flask("app")

    @app.route("/")
    def appview():
        return "app"

    # Test factory creation
    factory = create_wsgi_factory({"/api": lambda **kwargs: api})
    app.wsgi_app = factory(app)

    with app.test_client() as client:
        assert client.get("/").status_code == 200
        assert b"app" in client.get("/").data
        assert client.get("/api/").status_code == 200
        assert b"api" in client.get("/api/").data


@pytest.mark.parametrize("proxies,data", [(2, b"4.3.2.1"), (None, b"1.2.3.4")])
def test_proxyfix_wsgi_proxies(proxies, data):
    """Test wsgi factory creation."""
    app = Flask("app")
    app.config["WSGI_PROXIES"] = proxies

    @app.route("/")
    def appview():
        return str(request.remote_addr)

    # Test factory creation
    app.wsgi_app = wsgi_proxyfix()(app)
    e = {"REMOTE_ADDR": "1.2.3.4"}

    with app.test_client() as client:
        h = {"X-Forwarded-For": "5.6.7.8, 4.3.2.1, 8.7.6.5"}
        assert client.get("/", headers=h, environ_base=e).data == data


@pytest.mark.parametrize(
    "num_proxies,proxy_config",
    [
        (n, {"x_for": n, "x_proto": n, "x_host": n, "x_port": n, "x_prefix": n})
        for n in range(2)
    ],
)
def test_proxyfix_wsgi_config(num_proxies, proxy_config):
    """Test wsgi factory creation with APP_WSGI_CONFIG set."""
    app = Flask("app")
    app.config["PROXYFIX_CONFIG"] = proxy_config

    data = [
        # application instance
        {
            "x_for": "1.2.3.4",
            "x_proto": "http",
            "x_host": "localhost",
            "x_port": "80",
            "x_prefix": "",
        },
        # proxy number 1
        {
            "x_for": "5.6.7.8",
            "x_proto": "https",
            "x_host": "host.external",
            "x_port": "443",
            "x_prefix": "prefix.external",
        },
    ]

    @app.route("/")
    def appview():
        data = {
            "x_for": request.environ.get("REMOTE_ADDR"),
            "x_proto": request.environ.get("wsgi.url_scheme"),
            "x_host": request.environ.get("SERVER_NAME"),
            "x_port": request.environ.get("SERVER_PORT"),
            "x_prefix": request.environ.get("SCRIPT_NAME"),
        }
        return jsonify(data)

    # Test factory creation
    app.wsgi_app = wsgi_proxyfix()(app)
    e = {
        "REMOTE_ADDR": data[0].get("x_for"),
        "wsgi.url_scheme": data[0].get("x_proto"),
        "HTTP_HOST": data[0].get("x_host"),
        "SERVER_PORT": data[0].get("x_port"),
        "SCRIPT_NAME": data[0].get("x_prefix"),
    }

    with app.test_client() as client:
        h = {
            "X-Forwarded-For": data[1].get("x_for"),
            "X-Forwarded-Proto": data[1].get("x_proto"),
            "X-Forwarded-Host": data[1].get("x_host"),
            "X-Forwarded-Port": data[1].get("x_port"),
            "X-Forwarded-Prefix": data[1].get("x_prefix"),
        }
        res = client.get("/", headers=h, environ_base=e)
        assert json.loads(res.get_data(as_text=True)) == data[num_proxies]
