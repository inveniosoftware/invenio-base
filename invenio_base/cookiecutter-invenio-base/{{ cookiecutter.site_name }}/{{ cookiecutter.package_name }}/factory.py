# -*- coding: utf-8 -*-

"""Mysite Invenio API application."""

from invenio_base.app import create_app_factory
from invenio_base.wsgi import create_wsgi_factory
from invenio_config import create_conf_loader

from . import config

env_prefix = 'APP'

conf_loader = create_conf_loader(config=config, env_prefix=env_prefix)

create_api = create_app_factory(
    '{{ cookiecutter.site_name }}',
    env_prefix=env_prefix,
    conf_loader=conf_loader,
    bp_entry_point='invenio_base.api_blueprints',
    ext_entry_point='invenio_base.api_apps',
)


create_app = create_app_factory(
    '{{ cookiecutter.site_name }}',
    env_prefix=env_prefix,
    conf_loader=conf_loader,
    bp_entry_point='invenio_base.blueprints',
    ext_entry_point='invenio_base.apps',
    wsgi_factory=create_wsgi_factory({'/api': create_api})
)
