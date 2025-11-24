# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 CERN.
# Copyright (C) 2025 Northwestern University.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Urls helpers.

Really just there to put invenio_url_for definition in a way that circumvents
circular import.
"""

from flask import current_app


def invenio_url_for(
    endpoint,
    *,
    _method=None,
    _anchor=None,
    **values,
):
    """A URL generator for the Invenio reality.

    This function can build full (external) URLs for the current app and for setup
    endpoints. For maximum flexibility it leaves most of the work to the instance of
    `InvenioUrlsBuilder` (`current_app._urls_builder`) created at Flask app creation.
    This solves the problem of generating URLs for a Flask app when inside
    another Flask app.

    Because of this and to simplify things, `invenio_url_for` only generates
    external URLs (with scheme and server name configured by the instance of
    `InvenioUrlsBuilder`). This makes its interface slightly different
    than `url_for`'s. However, invenio_url_for strives to be compatible with `url_for`'s
    interface in all other ways (e.g., _anchor, _method ...).
    """

    return current_app._urls_builder.build(
        endpoint,
        values,
        method=_method,
        anchor=_anchor,
    )
