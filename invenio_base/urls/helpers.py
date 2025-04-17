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
    # _anchor = None,  # TODO
    _method=None,
    **values,
):
    """A URL generator for the Invenio reality.

    This function can build full (external) URLs for the current app and for setup
    endpoints. For maximum flexibility it leaves most of the work to `invenio_urls`
    and instance of `InvenioUrlsBuilder` setup and assigned at Flask app creation.
    This solves the problem of generating URLs for a Flask app when inside
    another Flask app.

    Because of this and to simplify things, `invenio_url_for` only generates
    external URLs (with scheme and server name configured by the instance of
    `InvenioUrlsBuilder`). This makes its interface slightly different
    than `url_for`'s.
    """

    return current_app._urls_builder.build(
        endpoint,
        values,
        method=_method,
        # _anchor=_anchor,  # TODO
    )
