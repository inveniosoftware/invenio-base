# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2012, 2013, 2014, 2015 CERN.
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

"""Invenio application loader.

The ``inveniomanage`` command
-----------------------------
Invenio-Base installs the ``inveniomanage`` command. By default only three
subcommands are available:

.. code-block:: console

   $ inveniomanage --help
   Usage: inveniomanage [OPTIONS] COMMAND [ARGS]...

     Command Line Interface for Invenio.

   Options:
     -a, --app TEXT        The application to run
     --debug / --no-debug  Enable or disable debug mode.
     --help                Show this message and exit.

   Commands:
     run              Runs a development server.
     shell            Runs a shell in the app context.
     instance create  Create a new project from template.


The ``run`` and ``shell`` commands only works if you have specified the
``--app`` option or the ``FLASK_APP`` environment variable. See
`Flask <http://flask.pocoo.org/docs/dev/cli/>`_ documentation for further
information.


Starting a new project
~~~~~~~~~~~~~~~~~~~~~~
The ``instance create`` subcommand helps you bootstrap a minimal Invenio
application:

.. code-block:: console

   $ inveniomanage instance create mysite
   $ find mysite


You can run the newly created site using the provided ``manage.py`` script:

.. code-block:: console

   $ cd mysite
   $ python manage.py run
"""

from __future__ import absolute_import, print_function

from .app import create_app_factory, create_cli
from .version import __version__
from .wsgi import create_wsgi_factory

__all__ = (
    '__version__',
    'create_app_factory',
    'create_cli',
    'create_wsgi_factory',
)
