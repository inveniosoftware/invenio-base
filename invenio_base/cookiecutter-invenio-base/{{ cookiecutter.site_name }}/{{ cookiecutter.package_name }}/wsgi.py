# -*- coding: utf-8 -*-

"""{{ cookiecutter.site_name }} Invenio WSGI application."""

from __future__ import absolute_import, print_function

from .factory import create_app

application = create_app()
