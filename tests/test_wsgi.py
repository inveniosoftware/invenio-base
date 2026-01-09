# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
# Copyright (C) 2024 Graz University of Technology.
# Copyright (C) 2026 Northwestern University.
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


@pytest.mark.parametrize(
    "num_proxies",
    # We test with a configuration expecting 0 up to 3 proxies even though information
    # for 2 proxies only is sent. This is to test/illustrate how edge case
    # configurations are interpreted.
    [n for n in range(4)],
)
def test_proxyfix_wsgi_config(num_proxies):
    app = Flask("app")
    app.config["PROXYFIX_CONFIG"] = {
        "x_for": num_proxies,
        "x_proto": num_proxies,
        "x_host": num_proxies,
        "x_port": num_proxies,
        "x_prefix": num_proxies,
    }

    @app.route("/")
    def appview():
        data = {
            "REMOTE_ADDR": request.environ.get("REMOTE_ADDR"),
            "wsgi.url_scheme": request.environ.get("wsgi.url_scheme"),
            "SERVER_NAME": request.environ.get("SERVER_NAME"),
            "SERVER_PORT": request.environ.get("SERVER_PORT"),
            "SCRIPT_NAME": request.environ.get("SCRIPT_NAME"),
        }
        return data

    # last value being that of the last client itself (proxy) before the application
    # i.e. the first 2 will be part of X-FORWARDED-* headers but not the last
    remote_addrs = ["1.2.3.4", "5.6.7.8", "9.10.11.12"]
    # last values of the lists below being that of the test server
    # Flask+Werkzeug sets those and we are just being explicit.
    wsgi_url_schemes = ["https", "https", "http"]
    server_names = ["host1.client", "host2.client", "localhost"]
    server_ports = ["443", "443", "80"]
    script_names = ["/prefix1", "/prefix2", ""]

    app.wsgi_app = wsgi_proxyfix()(app)

    with app.test_client() as client:
        res = client.get(
            "/",
            # headers sent by last client/proxy to application
            # always sent as though 2 proxies in front
            headers={
                "X-Forwarded-For": ",".join(remote_addrs[:2]),
                "X-Forwarded-Proto": ",".join(wsgi_url_schemes[:2]),
                "X-Forwarded-Host": ",".join(server_names[:2]),
                "X-Forwarded-Port": ",".join(server_ports[:2]),
                "X-Forwarded-Prefix": ",".join(script_names[:2]),
            },
            # this explicitly sets the REMOTE_ADDR to be that of the last client/proxy
            # by "default"
            environ_base={"REMOTE_ADDR": remote_addrs[-1]},
        )

        num_proxies_to_expected_index = [-1, 1, 0, -1]
        # The index of the list represents num of proxies (first element for 0 proxy
        # and so on). Indeed werkzeug will take the same values as no proxies, if the
        # app expects more proxies than passed.

        i = num_proxies_to_expected_index[num_proxies]
        expected = {
            "REMOTE_ADDR": remote_addrs[i],
            "wsgi.url_scheme": wsgi_url_schemes[i],
            "SERVER_NAME": server_names[i],
            "SERVER_PORT": server_ports[i],
            "SCRIPT_NAME": script_names[i],
        }
        assert expected == res.json
