# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio application factory."""

from __future__ import absolute_import, print_function

import logging
import os.path
import sys
import warnings

import click
import pkg_resources
from flask import Flask
from flask.cli import FlaskGroup
from flask.helpers import get_debug_flag

from .signals import app_created, app_loaded


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
    :returns: Flask application factory.

    Example of a configuration loader:

    .. code-block:: python

       def my_config_loader(app, **kwargs):
           app.config.from_module('mysite.config')
           app.config.update(**kwargs)

    .. note::

       `Invenio-Config <https://pythonhosted.org/invenio-config>`_ provides a
       factory creating default configuration loader (see
       :func:`invenio_config.utils.create_config_loader`) which is sufficient
       for most cases.

    Example of a WSGI factory:

    .. code-block:: python

       def my_wsgi_factory(app):
           return DispatcherMiddleware(app.wsgi_app, {'/api': api_app})

    .. versionadded: 1.0.0
    """
    def _create_app(**kwargs):
        app = base_app(app_name, **app_kwargs)
        app_created.send(_create_app, app=app)

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

        app_loaded.send(_create_app, app=app)

        # Replace WSGI application using factory if provided (e.g. to install
        # WSGI middleware).
        if wsgi_factory:
            app.wsgi_app = wsgi_factory(app, **kwargs)

        return app

    return _create_app


def create_cli(create_app=None):
    """Create CLI for ``inveniomanage`` command.

    :param create_app: Flask application factory.
    :returns: Click command group.

    .. versionadded: 1.0.0
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
            app = create_app(debug=get_debug_flag())
        return app

    @click.group(cls=FlaskGroup, create_app=create_cli_app)
    def cli(**params):
        """Command Line Interface for Invenio."""
        pass

    return cli


def app_loader(app, entry_points=None, modules=None):
    """Run default application loader.

    :param entry_points: List of entry points providing to Flask extensions.
    :param modules: List of Flask extensions.

    .. versionadded: 1.0.0
    """
    _loader(app, lambda ext: ext(app), entry_points=entry_points,
            modules=modules)


def blueprint_loader(app, entry_points=None, modules=None):
    """Run default blueprint loader.

    The value of any entry_point or module passed can be either an instance of
    ``flask.Blueprint`` or a callable accepting a ``flask.Flask`` application
    instance as a single argument and returning an instance of
    ``flask.Blueprint``.

    :param entry_points: List of entry points providing to Blueprints.
    :param modules: List of Blueprints.

    .. versionadded: 1.0.0
    """
    url_prefixes = app.config.get('BLUEPRINTS_URL_PREFIXES', {})

    def loader_init_func(bp_or_func):
        bp = bp_or_func(app) if callable(bp_or_func) else bp_or_func
        app.register_blueprint(bp, url_prefix=url_prefixes.get(bp.name))

    _loader(app, loader_init_func, entry_points=entry_points, modules=modules)


def converter_loader(app, entry_points=None, modules=None):
    """Run default converter loader.

    :param entry_points: List of entry points providing to Blue.
    :param modules: Map of coverters.

    .. versionadded: 1.0.0
    """
    if entry_points:
        for entry_point in entry_points:
            for ep in pkg_resources.iter_entry_points(entry_point):
                try:
                    app.url_map.converters[ep.name] = ep.load()
                except Exception:
                    app.logger.error(
                        'Failed to initialize entry point: {0}'.format(ep))
                    raise

    if modules:
        app.url_map.converters.update(**modules)


def _loader(app, init_func, entry_points=None, modules=None):
    """Run generic loader.

    Used to load and initialize entry points and modules using an custom
    initialization function.

    .. versionadded: 1.0.0
    """
    if entry_points:
        for entry_point in entry_points:
            for ep in pkg_resources.iter_entry_points(entry_point):
                try:
                    init_func(ep.load())
                except Exception:
                    app.logger.error(
                        'Failed to initialize entry point: {0}'.format(ep))
                    raise
    if modules:
        for m in modules:
            try:
                init_func(m)
            except Exception:
                app.logger.error('Failed to initialize module: {0}'.format(m))
                raise


def base_app(import_name, instance_path=None, static_folder=None,
             static_url_path='/static', template_folder='templates',
             instance_relative_config=True, app_class=Flask):
    """Invenio base application factory.

    If the instance folder does not exists, it will be created.

    :param import_name: The name of the application package.
    :param env_prefix: Environment variable prefix.
    :param instance_path: Instance path for Flask application.
    :param static_folder: Static folder path.
    :param app_class: Flask application class.
    :returns: Flask application instance.

    .. versionadded: 1.0.0
    """
    configure_warnings()

    # Create the Flask application instance
    app = app_class(
        import_name,
        instance_path=instance_path,
        instance_relative_config=instance_relative_config,
        static_folder=static_folder,
        static_url_path=static_url_path,
        template_folder=template_folder,
    )

    # Create instance path if it doesn't exists
    try:
        if instance_path and not os.path.exists(instance_path):
            os.makedirs(instance_path)
    except Exception:  # pragma: no cover
        app.logger.exception(
            'Failed to create instance folder: "{0}"'.format(instance_path)
        )

    return app


def configure_warnings():
    """Configure warnings by routing warnings to the logging system.

    It also unhides ``DeprecationWarning``.

    .. versionadded: 1.0.0
    """
    if not sys.warnoptions:
        # Route warnings through python logging
        logging.captureWarnings(True)

        # DeprecationWarning is by default hidden, hence we force the
        # 'default' behavior on deprecation warnings which is not to hide
        # errors.
        warnings.simplefilter('default', DeprecationWarning)
        warnings.simplefilter('ignore', PendingDeprecationWarning)
