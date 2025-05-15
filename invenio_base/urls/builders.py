# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 CERN.
# Copyright (C) 2025 Northwestern University.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""InvenioUrlsBuilder.

This code is in support of providing `invenio_url_for`, the RDM supplement
to Flask's `url_for` which allows any part of the application (in the broad
sense of the term) to generate URLs even if those URLs are for views registered
in another Flask application. Other developer niceties are included.
"""

from abc import ABC, abstractmethod
from typing import Callable, Any

from flask import Flask, current_app, Blueprint
from importlib_metadata import entry_points as iter_entry_points
from werkzeug.routing import BuildError, Map, Rule, BaseConverter

from .proxies import current_app_map_adapter, other_app_map_adapter


class InvenioUrlsBuilder(ABC):
    """Interface of class in charge of producing urls."""

    @abstractmethod
    def build(self, endpoint: str, values: dict, method: str | None = None) -> str:
        """Build current or other app url."""


class NoOpInvenioUrlsBuilder(InvenioUrlsBuilder):
    """Doesn't do anything."""

    def build(self, endpoint: str, values: dict, method: str | None = None) -> str:
        """Instead of building returns empty string."""
        return ""


class InvenioAppsUrlsBuilder(InvenioUrlsBuilder):
    """Builds URLs with some knowledge of Invenio (app-rdm)."""

    def __init__(
        self,
        cfg_of_app_prefix: str,
        cfg_of_other_app_prefix: str,
        groups_of_other_app_entrypoints: dict[str, list] | list,
    ) -> None:
        """Constructor.

        The ``cfg_of_app_prefix`` and ``cfg_of_other_app_prefix`` are the names of
        config items containing the URL prefixes for both apps (e.g. ``SITE_UI_URL``
        and ``SITE_API_URL``).

        ``groups_of_other_app_entrypoints`` is expected to be either a dictionary of
        the shape ``{"blueprints": [...], "converters": [...]}``, containing the names
        of entrypoint groups.
        Alternatively the value can be a list, which will be used equivalent to
        ``{"blueprints": [...]}``.
        """
        self.cfg_of_app_prefix = cfg_of_app_prefix
        self.cfg_of_other_app_prefix = cfg_of_other_app_prefix
        self.groups_of_other_app_entrypoints = groups_of_other_app_entrypoints

    def _load_converters(
        self, app_tmp: Flask, defaults: dict[str, type[BaseConverter]] | None = None
    ) -> None:
        """Load converters in temporary app `app_tmp`.

        Prerequisite to loading blueprints.
        This doesn't use app.py's `converter_loader` to sidestep circular dependency.
        """
        # Gracefully take into account converters by supporting:
        # 1) previous interface: list of blueprints only
        if isinstance(self.groups_of_other_app_entrypoints, list):
            app_tmp.url_map.converters = defaults or {}
        # 2) new interface: dict of blueprints and converters
        else:  # assume dict and let it raise if not
            groups = self.groups_of_other_app_entrypoints.get("converters", [])
            for group in groups:
                for ep in set(iter_entry_points(group=group)):
                    try:
                        app_tmp.url_map.converters[ep.name] = ep.load()
                    except Exception:
                        app_tmp.logger.error(f"Failed to initialize entry point: {ep}")
                        raise

    def _load_blueprints(self, app_tmp: Flask) -> None:
        """Load blueprints in temporary app `app_tmp`.

        Part of loading blueprints is loading converters.
        This doesn't use app.py's `blueprint_loader` to sidestep circular dependency.
        """
        # Gracefully take into account converters by supporting:
        # 1) previous interface: list of blueprints only
        if isinstance(self.groups_of_other_app_entrypoints, list):
            groups = self.groups_of_other_app_entrypoints
        # 2) new interface: dict of blueprints and converters
        else:  # assume dict and let it raise if not
            groups = self.groups_of_other_app_entrypoints.get("blueprints", [])

        url_prefixes: dict[str, Blueprint] = app_tmp.config.get(
            "BLUEPRINTS_URL_PREFIXES", {}
        )

        def register_blueprint(
            bp_or_func: Blueprint | Callable[[Flask], Blueprint],
        ) -> None:
            bp = bp_or_func(app_tmp) if callable(bp_or_func) else bp_or_func
            app_tmp.register_blueprint(bp, url_prefix=url_prefixes.get(bp.name))

        for group in groups:
            for ep in set(iter_entry_points(group=group)):
                try:
                    register_blueprint(ep.load())
                except Exception:
                    app_tmp.logger.error(f"Failed to initialize entry point: {ep}")
                    raise

    def setup(self, app: Flask, **kwargs: Any) -> None:
        """Sets up the object for url generation.

        It does so by building an internal url_map that it will reuse.

        This is called before the application is fully setup (not in an application
        context).
        """
        # Create a tmp Flask app. This allows us to isolate any app-level side-effect
        # to it and not affect the current app. It also skips some initialization
        # since the tmp app is only needed for extraction of its final url_map.
        app_tmp = Flask("InvenioAppsUrlsBuilder")

        # The tmp Flask app needs a regular application's config and extensions
        # to load blueprints correctly. However, `app` can't be used because of
        # error handling registration by invenio_theme/views.py:create_blueprint
        # at time of writing and because it's cleaner this way.
        app_tmp.config = app.config
        app_tmp.extensions = app.extensions

        self._load_converters(app_tmp, defaults=app.url_map.converters)

        self._load_blueprints(app_tmp)

        # End goal: copy the Rules minus the view_functions (don't need them)
        self.url_map = Map(
            [Rule(r.rule, endpoint=r.endpoint) for r in app_tmp.url_map.iter_rules()],
            converters=app_tmp.url_map.converters,
        )

    def prefix(self, site_cfg: str) -> str:
        """Return site prefix."""
        return current_app.config[site_cfg].rstrip("/")  # type: ignore[no-any-return]

    def build(self, endpoint: str, values: dict, method: str | None = None) -> str:
        """Build full url of any registered endpoint with appropriate prefix.

        This is called within an application context.
        """
        # 1- Try to build url from current app
        try:
            url_adapter = current_app_map_adapter
            url_relative = url_adapter.build(  # type: ignore[attr-defined]
                endpoint, values, method=method, force_external=False
            )
            return self.prefix(self.cfg_of_app_prefix) + url_relative  # type: ignore[no-any-return]
        except BuildError:
            # The endpoint may be from the complementary blueprints
            pass

        # 2- Try to build url from complementary url_map
        url_adapter = other_app_map_adapter
        url_relative = url_adapter.build(  # type: ignore[attr-defined]
            endpoint,
            values,
            method=method,
            force_external=False,
        )
        return self.prefix(self.cfg_of_other_app_prefix) + url_relative  # type: ignore[no-any-return]


def create_invenio_apps_urls_builder_factory(
    cfg_of_app_prefix: str,
    cfg_of_other_app_prefix: str,
    groups_of_other_app_entrypoints: dict[str, list] | list[str],
) -> Callable[..., InvenioAppsUrlsBuilder]:
    """Create the factory for invenio_urls_builder that knows about dual app setup.

    This function is made with knowledge of invenio-app mechanisms as a
    convenience, but it produces a factory that produces an implementation of
    InvenioUrlsBuilder. This means invenio-app
    can swap it out easily for a different URL generator - just need to
    produce a builder that implements InvenioUrlsBuilder's interface.

    :param cfg_of_app_prefix: config for current app prefix
    :param cfg_of_other_app_prefix: config for other app prefix
    :param groups_of_other_app_entrypoints: entrypoints groups to load
                                             blueprints of other app
    """

    def _factory(app: Flask, **kwargs: Any) -> InvenioAppsUrlsBuilder:
        builder = InvenioAppsUrlsBuilder(
            cfg_of_app_prefix,
            cfg_of_other_app_prefix,
            groups_of_other_app_entrypoints,
        )
        builder.setup(app, **kwargs)
        return builder

    return _factory
