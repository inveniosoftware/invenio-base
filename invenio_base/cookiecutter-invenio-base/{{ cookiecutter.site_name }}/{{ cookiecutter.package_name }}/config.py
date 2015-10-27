# -*- coding: utf-8 -*-

"""{{ cookiecutter.site_name }} base Invenio configuration."""

from __future__ import absolute_import, print_function


# Identity function for string extraction
def _(x):
    return x

# Default language and timezone
BABEL_DEFAULT_LANGUAGE = 'en'
BABEL_DEFAULT_TIMEZONE = 'Europe/Zurich'
I18N_LANGUAGES = [
]

BASE_TEMPLATE = "invenio_theme/page.html"

SECRET_KEY = "{{cookiecutter.secret_key }}"

# Theme
THEME_SITENAME = _("{{ cookiecutter.site_name }}")
