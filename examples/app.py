# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Example application using Invenio-Base factories."""

# sphinxdoc-example-import-begin

import os
import sys

from invenio_base.app import create_app_factory, create_cli
from invenio_base.wsgi import create_wsgi_factory

# sphinxdoc-example-import-end


# sphinxdoc-example-config-begin
class Config(object):
    """Example configuration."""

    DEBUG = True
    SECRET_KEY = "CHANGE_ME"


def config_loader(app, **kwargs):
    """Custom config loader."""
    app.config.from_object(Config)
    app.config.update(**kwargs)


# sphinxdoc-example-config-end


# sphinxdoc-example-paths-begin
env_prefix = "APP"


def instance_path():
    """Instance path for Invenio.

    Defaults to ``<env_prefix>_INSTANCE_PATH`` or if environment variable is not
    set ``<sys.prefix>/var/<app_name>-instance``.
    """
    return os.getenv(env_prefix + "_INSTANCE_PATH") or os.path.join(
        sys.prefix, "var", "example-instance"
    )


def static_folder():
    """Static folder path.

    Defaults to ``<env_prefix>_STATIC_FOLDER`` or if environment variable is not
    set ``<sys.prefix>/var/<app_name>-instance/static``.
    """
    return os.getenv(env_prefix + "_STATIC_FOLDER") or os.path.join(
        instance_path(), "static"
    )


# sphinxdoc-example-paths-end


# sphinxdoc-example-factories-begin
create_api = create_app_factory(
    "example",
    config_loader=config_loader,
    blueprint_entry_points=["invenio_base.api_blueprints"],
    extension_entry_points=["invenio_base.api_apps"],
    converter_entry_points=["invenio_base.api_converters"],
    instance_path=instance_path,
)


create_app = create_app_factory(
    "example",
    config_loader=config_loader,
    blueprint_entry_points=["invenio_base.blueprints"],
    extension_entry_points=["invenio_base.apps"],
    converter_entry_points=["invenio_base.converters"],
    wsgi_factory=create_wsgi_factory({"/api": create_api}),
    instance_path=instance_path,
    static_folder=static_folder,
)
# sphinxdoc-example-factories-end

# sphinxdoc-example-objects-begin
app = application = create_app()
"""The application object."""
# sphinxdoc-example-objects-end
