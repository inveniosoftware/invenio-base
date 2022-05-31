# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2018 CERN.
# Copyright (C) 2022 RERO.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test signals."""

from invenio_base.app import create_app_factory
from invenio_base.signals import app_created, app_loaded


def test_create_app_factory():
    """Test signals sending."""
    calls = {"created": 0, "loaded": 0}
    create_app = create_app_factory("test")

    def _receiver(name):
        def _inner(sender, app=None):
            calls[name] += 1
            calls[f"{name}_app"] = app

        return _inner

    app_created.connect(_receiver("created"), sender=create_app, weak=False)
    app_loaded.connect(_receiver("loaded"), sender=create_app, weak=False)

    assert callable(create_app)

    app = create_app()
    assert calls["created"] == 1
    assert calls["loaded"] == 1
    assert calls["created_app"] is app
    assert calls["loaded_app"] is app
