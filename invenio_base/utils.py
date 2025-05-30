# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2020 CERN.
# Copyright (C) 2025 Graz University of Technology.

#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Base utilities."""
from fractions import Fraction
from typing import TypeAlias, TypeVar, cast

from flask import Flask, current_app
from werkzeug.utils import import_string

# The classes from the standard library `numbers` module are not suitable for
# type checking (https://github.com/python/mypy/issues/3186).
Real: TypeAlias = int | float | Fraction


def obj_or_import_string[T](
    value: str | T | None, default: T | None = None
) -> T | None:
    """Import string or return object.

    :params value: Import path or class object to instantiate.
    :params default: Default object to return if the import fails.
    :returns: The imported object.
    """
    if isinstance(value, str):
        return cast(T, import_string(value))
    elif value:
        return value
    return default


def load_or_import_from_config[T](
    key: str, app: Flask | None = None, default: T | None = None
) -> T | None:
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
