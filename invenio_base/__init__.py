# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio application loader.

Quickstart
----------
Invenio-Base is taking advantage of advanced patterns for building Flask
application. It assumes you already have understanding of
`patterns for Flask <http://flask.pocoo.org/docs/dev/patterns/>`_.

Dependencies
~~~~~~~~~~~~
First we need to install and import dependencies:

.. code-block:: console

   $ mkvirtualenv example
   (example)$ pip install invenio-base

Now you can create new file ``app.py`` with following imports:

.. include:: ../examples/app.py
   :start-after: # sphinxdoc-example-import-begin
   :end-before: # sphinxdoc-example-import-end
   :literal:

Configuration
~~~~~~~~~~~~~
Tell the application factory how to load configuration by creating
``config_loader`` function that accepts an application instance:

.. include:: ../examples/app.py
   :start-after: # sphinxdoc-example-config-begin
   :end-before: # sphinxdoc-example-config-end
   :literal:

The recommended way is to use `Invenio-Config
<https://invenio-config.readthedocs.io/>`_ that provides a default
configuration loader :func:`invenio_config.utils.create_config_loader` which is
sufficient for most cases:

.. code-block:: python

   from invenio_config import create_config_loader
   config_loader = create_config_loader(config=Config, env_prefix='APP')

In the next step you should set an absolute path for the *instance folder* in
order to load configuration files and other data from deployment specific
location. The instance folder is also perfect place for dropping static files
if you do not serve them from CDN:

.. include:: ../examples/app.py
   :start-after: # sphinxdoc-example-paths-begin
   :end-before: # sphinxdoc-example-paths-end
   :literal:

In our example the variables are read from environment variables first with the
purpose that they can be easily changed without modifying code for various
deployment usecases.

Combining Applications
~~~~~~~~~~~~~~~~~~~~~~
It is highly recommendended to separate Invenio UI and REST applications then
different exception handlers, URL converters and session management can be
installed on each application instance. You can even install your own WSGI
application side by side with Invenio ones.

Invenio packages provide apps (extensions), blueprints, and URL converters via
entry points ``invenio_base.[api_]<apps,blueprints,converters>``. You can
specify multiple entry point groups for each application factory (e.g.
``myservice.blueprints``):

.. include:: ../examples/app.py
   :start-after: # sphinxdoc-example-factories-begin
   :end-before: # sphinxdoc-example-factories-end
   :literal:

You provide instances of your own apps, blueprints, or URL converters directly
to the factory:

.. code-block:: python

   from flask import Blueprint

   blueprint = Blueprint('example', __name__)

   @blueprint.route('/')
   def index():
       return 'Hello from Example application.'

    create_app = create_app_factory(
        'example',
        blueprints=[blueprint],
        # other parameters as shown in previous example
    )

Running
~~~~~~~
To run you application you need to first instantiate the application object:

.. include:: ../examples/app.py
   :start-after: # sphinxdoc-example-objects-begin
   :end-before: # sphinxdoc-example-objects-end
   :literal:

Then you need to tell the **``flask``** command where is your file located
by setting environment variable ``FLASK_APP=app.py``:

.. code-block:: console

   $ export FLASK_APP=app.py
   $ flask run

If you prefer to make your own executable script then you can use following
pattern:

.. code-block:: python

   from invenio_base.app import create_cli

   cli = create_cli(create_app=create_app)

   if __name__ == '__main__':
       cli()

Do not worry, you do not have to write all this by yourself. Follow next steps
and use ``inveniomanage`` command that generates the scaffold code for you.

The ``inveniomanage`` command
-----------------------------
Invenio-Base installs the ``inveniomanage`` command. By default only three
subcommands are available:

.. code-block:: console

   $ inveniomanage --help
   Usage: inveniomanage [OPTIONS] COMMAND [ARGS]...

     Command Line Interface for Invenio.

   Options:
     -a, --app TEXT        The application to run.
     --debug / --no-debug  Enable or disable debug mode.
     --help                Show this message and exit.

   Commands:
     run              Run development server.
     shell            Run shell in the app context.

The ``run`` and ``shell`` commands only works if you have specified the
``--app`` option or the ``FLASK_APP`` environment variable. See
`Flask <http://flask.pocoo.org/docs/dev/cli/>`_ documentation for further
information.


Listing all entrypoints of an Invenio instance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The ``instance entrypoints`` subcommand helps you list all entrypoints of your
Invenio application:

.. code-block:: console

   $ inveniomanage instance entrypoints

The output of the command will be in the below format:

.. code-block:: console

   <entrypoint_group_name>
     <entrypoint>


You can also restrict the output of the command to list all entrypoints for a
specific entrypoint group by passing the name via the `-e` option:

.. code-block:: console

   $ inveniomanage instance entrypoints -e <entrypoint_group_name>

For further details about the available options run the `help` command:

.. code-block:: console

   $ inveniomanage instance entrypoints --help
   ...


Migrating the application's old secret key
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The ``instance migrate_secret_key`` subcommand helps you migrate your
application's old secret key:

.. code-block:: console

   $ inveniomanage instance migrate_secret_key --old-key <old_key>

The purpose of this command is to provide the administrator the capability to
change the Invenio application's secret_key and migrate that change in all
database's EncryptedType properties through an entrypoint group called
`invenio_base.secret_key'`. There you can specify your migration function that
will receive the old secret_key that can be used to decrypt the old properties
and encrypt them again with the application's new secret_key.

You can register your migration function as shown below in your package's
entrypoints in the setup.py:

.. code-block:: console

   entrypoints= {
       'invenio_base.secret_key': [
           '<entrypoint_name> = <entrypoint_function>'
       ]
   }

Also you can see an example of use in `invenio_oauthclient
<https://github.com/inveniosoftware/invenio-oauthclient>`_
package's setup.py.

.. note::
 You should change your application's `secret_key` in the config before calling
 the migration command.

For further details about the available options run the `help` command:

.. code-block:: console

   $ inveniomanage instance migrate_secret_key --help
   ...
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
