# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

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
    SECRET_KEY = 'CHANGE_ME'


def config_loader(app, **kwargs):
    """Custom config loader."""
    app.config.from_object(Config)
    app.config.update(**kwargs)
# sphinxdoc-example-config-end

# sphinxdoc-example-paths-begin
env_prefix = 'APP'

instance_path = os.getenv(env_prefix + '_INSTANCE_PATH') or \
    os.path.join(sys.prefix, 'var', 'example-instance')
"""Instance path for Invenio.

Defaults to ``<env_prefix>_INSTANCE_PATH`` or if environment variable is not
set ``<sys.prefix>/var/<app_name>-instance``.
"""

static_folder = os.getenv(env_prefix + '_STATIC_FOLDER') or \
    os.path.join(instance_path, 'static')
"""Static folder path.

Defaults to ``<env_prefix>_STATIC_FOLDER`` or if environment variable is not
set ``<sys.prefix>/var/<app_name>-instance/static``.
"""
# sphinxdoc-example-paths-end

# sphinxdoc-example-factories-begin
create_api = create_app_factory(
    'example',
    config_loader=config_loader,
    blueprint_entry_points=['invenio_base.api_blueprints'],
    extension_entry_points=['invenio_base.api_apps'],
    converter_entry_points=['invenio_base.api_converters'],
    instance_path=instance_path,
)


create_app = create_app_factory(
    'example',
    config_loader=config_loader,
    blueprint_entry_points=['invenio_base.blueprints'],
    extension_entry_points=['invenio_base.apps'],
    converter_entry_points=['invenio_base.converters'],
    wsgi_factory=create_wsgi_factory({'/api': create_api}),
    instance_path=instance_path,
    static_folder=static_folder,
)
# sphinxdoc-example-factories-end

# sphinxdoc-example-objects-begin
app = application = create_app()
"""The application object."""
# sphinxdoc-example-objects-end
