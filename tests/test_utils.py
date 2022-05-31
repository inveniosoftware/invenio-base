# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test utilities."""

from flask import Flask

from invenio_base.utils import load_or_import_from_config, obj_or_import_string
from invenio_base.wsgi import wsgi_proxyfix


def test_obj_or_import_string():
    """Test object or string import utility function."""
    assert obj_or_import_string(wsgi_proxyfix) == wsgi_proxyfix
    assert obj_or_import_string(None, default=wsgi_proxyfix) == wsgi_proxyfix
    assert obj_or_import_string("invenio_base.wsgi.wsgi_proxyfix") == wsgi_proxyfix


def test_load_or_import_from_config():
    """Test load or import from config utility function."""
    app = Flask("testapp")
    app.config["OBJ_KEY"] = wsgi_proxyfix
    app.config["PATH_KEY"] = "invenio_base.wsgi.wsgi_proxyfix"

    with app.app_context():
        assert load_or_import_from_config("OBJ_KEY") == wsgi_proxyfix
        assert load_or_import_from_config("PATH_KEY") == wsgi_proxyfix
        assert (
            load_or_import_from_config("MISSING_KEY", default=wsgi_proxyfix)
            == wsgi_proxyfix
        )
