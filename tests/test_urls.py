# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 CERN.
# Copyright (C) 2025 Northwestern University.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from unittest.mock import patch

from flask import Blueprint, url_for
from importlib_metadata import EntryPoint
from werkzeug.routing import BuildError, Map, Rule

from invenio_base import invenio_url_for
from invenio_base.app import create_app_factory
from invenio_base.urls.builders import (
    InvenioUrlsBuilder,
    create_invenio_apps_urls_builder_factory,
)


class UrlsBuilderForTest(InvenioUrlsBuilder):
    """Test urls builder."""

    def __init__(self):
        """Constructor."""
        self.url_map = Map(
            [
                Rule("/foo", endpoint="endpoint_foo_of_other_app"),
            ]
        )
        self.url_adapter = self.url_map.bind("")

    def build(self, endpoint, values, method=None):
        """Build url for any registered blueprints."""
        try:
            return url_for(endpoint, **values, _method=method, _external=True)
        except BuildError:
            url_relative = self.url_adapter.build(
                endpoint,
                values,
                method=method,
            )
            return "https://example.org/api" + url_relative


def factory_for_test(app, **kwargs):
    """Returns a test urls builder."""
    return UrlsBuilderForTest()


def test_generic_setup_of_invenio_url_for():
    """This simply tests overall integration/interfaces.

    The tests after this one actually test the specific implementation that will be
    used for InvenioRDM.
    """

    def _config_loader(app, **kwargs):
        app.config["SERVER_NAME"] = "example.org"
        app.config["PREFERRED_URL_SCHEME"] = "https"

    create_app = create_app_factory(
        "test", urls_builder_factory=factory_for_test, config_loader=_config_loader
    )
    app = create_app()
    app.add_url_rule("/foo", endpoint="endpoint_foo_of_this_app")

    assert app._urls_builder
    with app.app_context():
        # Both current and other app URLs can be generated
        assert "https://example.org/foo" == invenio_url_for("endpoint_foo_of_this_app")
        assert "https://example.org/api/foo" == invenio_url_for(
            "endpoint_foo_of_other_app"
        )
    # even in request context the full external URL is returned
    with app.test_request_context():
        assert "https://example.org/foo" == invenio_url_for("endpoint_foo_of_this_app")
        assert "https://example.org/api/foo" == invenio_url_for(
            "endpoint_foo_of_other_app"
        )


# InvenioAppsUrlsBuilder tests


class MockEntryPoint(EntryPoint):
    """Mocking of entrypoint."""

    def load(self):
        """Mock load entry point."""
        if self.name == "fail":
            raise Exception("Fail")
        return self.name


class MockBlueprintEntryPoint:  # EntryPoint by any other name
    """Mocking of entrypoint for blueprints.

    Not inheriting from Entrypoint because they are immutable.
    """

    def __init__(self, name, rule_endpoint_tuples):
        """Constructor."""
        self.name = name
        self.rule_endpoint_tuples = rule_endpoint_tuples

    def load(self):
        """Mock load entry point."""
        bp = Blueprint(self.name, __name__)
        for rule, endpoint in self.rule_endpoint_tuples:
            bp.add_url_rule(rule, endpoint=endpoint)
        return bp


def _mock_iter_entry_points(group=None):
    data = {
        "invenio_base.blueprints": [
            MockBlueprintEntryPoint(
                "ui_blueprint", [("/foo", "endpoint_foo_of_ui_app")]
            ),
        ],
        "invenio_base.api_blueprints": [
            MockBlueprintEntryPoint(
                "api_blueprint", [("/foo", "endpoint_foo_of_api_app")]
            ),
        ],
    }
    names = data.keys() if group is None else [group]
    for key in names:
        for entry_point in data[key]:
            yield entry_point


def _config_loader(app, **kwargs):
    app.config["SITE_UI_URL"] = "https://example.org"
    app.config["SITE_API_URL"] = "https://example.org/api"


@patch("invenio_base.app.iter_entry_points", _mock_iter_entry_points)
@patch("invenio_base.urls.builders.iter_entry_points", _mock_iter_entry_points)
def test_invenio_apps_urls_builder_w_ui_as_this_app():

    create_app = create_app_factory(
        "test",
        blueprint_entry_points=["invenio_base.blueprints"],
        config_loader=_config_loader,
        urls_builder_factory=create_invenio_apps_urls_builder_factory(
            "SITE_UI_URL", "SITE_API_URL", ["invenio_base.api_blueprints"]
        ),
    )
    app = create_app()

    with app.app_context():
        # test for endpoint of main app
        assert "https://example.org/foo" == invenio_url_for(
            "ui_blueprint.endpoint_foo_of_ui_app"
        )
        # test for endpoint of other app
        assert "https://example.org/api/foo" == invenio_url_for(
            "api_blueprint.endpoint_foo_of_api_app"
        )
