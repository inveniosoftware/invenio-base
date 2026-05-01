# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test utilities."""

from unittest.mock import patch

from flask import Flask
from importlib_metadata import EntryPoint

from invenio_base.utils import _NO_DEDUP_GROUPS, entry_points, load_or_import_from_config, obj_or_import_string
from invenio_base.wsgi import wsgi_proxyfix


def _ep(name, value, group="invenio_base.apps"):
    return EntryPoint(name=name, group=group, value=value)


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


class TestEntryPointsDedup:
    """entry_points() must deduplicate by name and by value (first-wins)."""

    def test_unique_entries_returned_unchanged(self):
        """When all entries are unique, none should be dropped."""
        eps = [_ep("a", "pkg.a:factory"), _ep("b", "pkg.b:factory")]
        with patch("invenio_base.utils.m.entry_points", return_value=eps):
            result = entry_points("invenio_base.apps")
        assert len(result) == 2

    def test_duplicate_name_drops_second(self):
        """Two entries with the same name: only the first must survive."""
        eps = [
            _ep("myapp", "oarepo_rdm.ext:create_app"),
            _ep("myapp", "invenio_rdm_records.ext:create_app"),
        ]
        with patch("invenio_base.utils.m.entry_points", return_value=eps):
            result = entry_points("invenio_base.apps")
        assert len(result) == 1
        assert result[0].name == "myapp"
        assert result[0].value == "oarepo_rdm.ext:create_app"

    def test_duplicate_value_drops_second(self):
        """Two entries pointing to the same factory must be collapsed to one."""
        eps = [
            _ep("invenio_rdm_iiif", "invenio_rdm_records.views:create_iiif_bp"),
            _ep("invenio_iiif", "invenio_rdm_records.views:create_iiif_bp"),
        ]
        with patch("invenio_base.utils.m.entry_points", return_value=eps):
            result = entry_points("invenio_base.blueprints")
        assert len(result) == 1
        assert result[0].name == "invenio_rdm_iiif"

    def test_no_dedup_group_passes_all_through(self):
        """Groups in _NO_DEDUP_GROUPS must not be deduplicated."""
        group = next(iter(_NO_DEDUP_GROUPS))
        eps = [
            _ep("jsonschemas", "pkg_a.schemas:get_schemas", group=group),
            _ep("jsonschemas", "pkg_b.schemas:get_schemas", group=group),
        ]
        with patch("invenio_base.utils.m.entry_points", return_value=eps):
            result = entry_points(group)
        assert len(result) == 2

    def test_empty_group_returns_empty_list(self):
        """An empty group should return an empty sequence."""
        with patch("invenio_base.utils.m.entry_points", return_value=[]):
            result = entry_points("invenio_base.apps")
        assert list(result) == []
