# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Base utilities."""

from flask import current_app
from werkzeug.utils import import_string


def obj_or_import_string(value, default=None):
    """Import string or return object.

    :params value: Import path or class object to instantiate.
    :params default: Default object to return if the import fails.
    :returns: The imported object.
    """
    if isinstance(value, str):
        return import_string(value)
    elif value:
        return value
    return default


def load_or_import_from_config(key, app=None, default=None):
    """Load or import value from the application config.

    :params key: Configuration key.
    :params app: Flask application (by default ``flask.current_app``).
    :params default: Default object to return if the import fails
        (by default ``None``).
    :returns: The loaded value.
    """
    app = app or current_app
    value = app.config.get(key)
    return obj_or_import_string(value, default=default)
