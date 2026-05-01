# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2020 CERN.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Base utilities."""

import importlib.metadata as m
from sys import version_info

from flask import current_app
from werkzeug.utils import import_string


# Groups where multiple packages intentionally register entries under the same
# name (e.g. each package contributes its own schema files).  Deduplication
# must be skipped for these groups so that no contribution is silently dropped.
_NO_DEDUP_GROUPS = frozenset(
    [
        "invenio_jsonschemas.schemas",
        "invenio_records.jsonresolver",
    ]
)


def entry_points(group):
    """Entry points, deduplicated by name and value (first-wins).

    In Python 3.10+ ``importlib.metadata.entry_points`` returns *all*
    registered entries for a group, including duplicates introduced when two
    packages register the same name (e.g. a downstream package overriding an
    upstream one).  Without deduplication, ``invenio_base`` loads both entries:
    the override fires once, the original fires a second time, and Flask raises
    a blueprint-name collision error.

    Deduplication is applied in two passes:

    * **Name deduplication** (first-wins): if two entries share a name, only
      the first is kept.  This covers the common override pattern.
    * **Value deduplication** (first-wins): if two entries with *different*
      names point to the same factory (same ``ep.value``), only the first is
      kept.  Loading the same factory twice would produce two Flask blueprints
      with identical ``name`` attributes, which triggers a different collision
      error.

    Groups listed in ``_NO_DEDUP_GROUPS`` are exempt because their entries are
    aggregated across many packages on purpose.
    """
    if version_info < (3, 10):
        eps = m.entry_points()
        # the only reason to add this check is to simplify the tests! the tests
        # are implemented against python >=3.10 which uses the group keyword.
        # since we drop python3.9 soon, this should work!
        # in the tests there is a line which patches the return value of
        # importlib.metadata.entry_points with a list. this works for
        # python>=3.10 but not for 3.9
        # the return value of .get can contain duplicates. the simplest way to
        # remove is the set() call, to still return a list, list() is called on
        # set()
        if isinstance(eps, dict):
            eps = list(set(eps.get(group, [])))
    else:
        eps = m.entry_points(group=group)

    if group in _NO_DEDUP_GROUPS:
        return eps

    seen_names: set[str] = set()
    seen_values: set[str] = set()
    deduped = []
    for ep in eps:
        if ep.name not in seen_names and ep.value not in seen_values:
            seen_names.add(ep.name)
            seen_values.add(ep.value)
            deduped.append(ep)
    return deduped


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
