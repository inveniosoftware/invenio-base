# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 CERN.
# Copyright (C) 2025 Northwestern University.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Proxies."""

from flask import current_app, g
from werkzeug.local import LocalProxy

# The following 2 proxies were created to mimic how Flask caches the MapAdapter object
# on the application or request.
# See https://github.com/pallets/flask/blob/main/src/flask/app.py#L1085.
# The hope is that this cuts down on cost of generating
# each link (especially for search API responses)


def other_bind():
    """Cache MapAdapter for non-current app's url_map.

    Usage of this proxy can only be done after `current_app._urls_builder.url_map`
    has been set.
    """
    if "other_app_map_adapter" not in g:
        g.other_app_map_adapter = current_app._urls_builder.url_map.bind("")
    return g.other_app_map_adapter


other_app_map_adapter = LocalProxy(other_bind)


def current_bind():
    """Cache MapAdapter for current app's url_map."""
    if "current_app_map_adapter" not in g:
        g.current_app_map_adapter = current_app.url_map.bind("")
    return g.current_app_map_adapter


current_app_map_adapter = LocalProxy(current_bind)
