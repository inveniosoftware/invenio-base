# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization or
# submit itself to any jurisdiction.

"""Invenio application factory."""

from __future__ import absolute_import, print_function

import logging
import os.path
import sys
import warnings

import click
import pkg_resources
from flask import Flask
from flask_cli import FlaskCLI, FlaskGroup

from .cmd import instance


def create_app_factory(app_name, config_loader=None,
                       extension_entry_points=None, extensions=None,
                       blueprint_entry_points=None, blueprints=None,
                       converter_entry_points=None, converters=None,
                       wsgi_factory=None, **app_kwargs):
    """Create a Flask application factory.

    The application factory will load Flask extensions and blueprints specified
    using both entry points and directly in the arguments. Loading order of
    entry points are not guaranteed and can happen in any order.

    :param app_name: Flask application name.
    :param config_loader: Callable which will be invoked on application
        creation in order to load the Flask configuration. See example below.
    :param extension_entry_points: List of entry points, which specifies Flask
        extensions that will be initialized only by passing in the Flask
        application object
    :param extensions: List of Flask extensions that can be initialized only by
        passing in the Flask application object.
    :param blueprint_entry_points: List of entry points, which specifies
        Blueprints that will be registered on the Flask application.
    :param blueprints: List of Blueprints that will be registered on the
        Flask application.
    :param converter_entry_points: List of entry points, which specifies
        Werkzeug URL map converters that will be added to
        ``app.url_map.converters``.
    :param converters: Map of Werkzeug URL map converter classes that will
        be added to ``app.url_map.converters``.
    :param wsgi_factory: A callable that will be passed the Flask application
        object in order to overwrite the default WSGI application (e.g. to
        install ``DispatcherMiddleware``).
    :param app_kwargs: Keyword arguments passed to :py:meth:`base_app`.
    :return: Flask application factory.

    Example of a configuration loader:

    .. code-block:: python

       def my_config_loader(app, **kwargs):
           app.config.from_module('mysite.config')
           app.config.update(**kwargs)

    Note that Invenio-Config provides a default configuration loader which is
    sufficient for most cases.

    Example of a WSGI factory:

    .. code-block:: python

       def my_wsgi_factory(app):
           return DispatcherMiddleware(app.wsgi_app, {'/api': api_app})

    """
    def _create_app(**kwargs):
        app = base_app(app_name, **app_kwargs)

        debug = kwargs.get('debug')
        if debug is not None:
            app.debug = debug

        # Load configuration
        if config_loader:
            config_loader(app, **kwargs)

        # Load URL converters.
        converter_loader(
            app,
            entry_points=converter_entry_points,
            modules=converters,
        )

        # Load application based on entrypoints.
        app_loader(
            app,
            entry_points=extension_entry_points,
            modules=extensions,
        )

        # Load blueprints
        blueprint_loader(
            app,
            entry_points=blueprint_entry_points,
            modules=blueprints,
        )

        # Replace WSGI application using factory if provided (e.g. to install
        # WSGI middleware).
        if wsgi_factory:
            app.wsgi_app = wsgi_factory(app, **kwargs)

        return app

    return _create_app


def create_cli(create_app=None):
    """Create CLI for ``inveniomanage`` command.

    :param create_app: Flask application factory.
    :return: Click command group.
    """
    def create_cli_app(info):
        """Application factory for CLI app.

        Internal function for creating the CLI. When invoked via
        ``inveniomanage`` FLASK_APP must be set.
        """
        if create_app is None:
            # Fallback to normal Flask behavior
            info.create_app = None
            app = info.load_app()
        else:
            app = create_app(debug=info.debug)
        return app

    @click.group(cls=FlaskGroup, create_app=create_cli_app,
                 add_app_option=True)
    def cli(**params):
        """Command Line Interface for Invenio."""
        pass

    # Add command for startin new Invenio instances.
    cli.add_command(instance)

    return cli


def app_loader(app, entry_points=None, modules=None):
    """Default application loader.

    :param entry_points: List of entry points providing to Flask extensions.
    :param modules: List of Flask extensions.
    """
    _loader(app, lambda ext: ext(app), entry_points=entry_points,
            modules=modules)


def blueprint_loader(app, entry_points=None, modules=None):
    """Default blueprint loader.

    :param entry_points: List of entry points providing to Blueprints.
    :param modules: List of Blueprints.
    """
    url_prefixes = app.config.get('BLUEPRINTS_URL_PREFIXES', {})
    _loader(app, lambda bp: app.register_blueprint(
        bp, url_prefix=url_prefixes.get(bp.name)
    ), entry_points=entry_points, modules=modules)


def converter_loader(app, entry_points=None, modules=None):
    """Default converter loader.

    :param entry_points: List of entry points providing to Blue.
    :param modules: Map of coverters.
    """
    if entry_points:
        for entry_point in entry_points:
            for ep in pkg_resources.iter_entry_points(entry_point):
                try:
                    app.url_map.converters[ep.name] = ep.load()
                except Exception:
                    app.logger.error(
                        "Failed to initialize entry point: {0}".format(ep))
                    raise

    if modules:
        app.url_map.converters.update(**modules)


def _loader(app, init_func, entry_points=None, modules=None):
    """Generic loader.

    Used to load and initialize entry points and modules using an custom
    initialization function.
    """
    if entry_points:
        for entry_point in entry_points:
            for ep in pkg_resources.iter_entry_points(entry_point):
                try:
                    init_func(ep.load())
                except Exception:
                    app.logger.error(
                        "Failed to initialize entry point: {0}".format(ep))
                    raise
    if modules:
        for m in modules:
            try:
                init_func(m)
            except Exception:
                app.logger.error("Failed to initialize module: {0}".format(m))
                raise


def base_app(import_name, instance_path=None, static_folder=None,
             static_url_path='/static', template_folder='templates',
             instance_relative_config=True):
    """Invenio base application factory.

    If the instance folder does not exists, it will be created.

    :param import_name: The name of the application package.
    :param env_prefix: Environment variable prefix.
    :param instance_path: Instance path for Flask application.
    :param static_folder: Static folder path.
    :return: Flask application instance.
    """
    configure_warnings()

    # Create the Flask application instance
    app = Flask(
        import_name,
        instance_path=instance_path,
        instance_relative_config=instance_relative_config,
        static_folder=static_folder,
        static_url_path=static_url_path,
        template_folder=template_folder,
    )
    # Ensure we have Click available for Flask <1.0
    FlaskCLI(app)

    # Create instance path if it doesn't exists
    try:
        if not os.path.exists(instance_path):
            os.makedirs(instance_path)
    except Exception:  # pragma: no cover
        app.logger.exception(
            "Failed to create instance folder: '{0}'".format(instance_path)
        )

    return app


def configure_warnings():
    """Configure warnings by routing warnings to the logging system.

    It also unhides ``DeprecationWarning``.
    """
    if not sys.warnoptions:
        # Route warnings through python logging
        logging.captureWarnings(True)

        # DeprecationWarning is by default hidden, hence we force the
        # "default" behavior on deprecation warnings which is not to hide
        # errors.
        warnings.simplefilter("default", DeprecationWarning)
