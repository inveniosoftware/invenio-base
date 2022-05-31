# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Signals for application creation."""

from blinker import Namespace

_signals = Namespace()

app_created = _signals.signal("app-created")
"""Signal sent when the base Flask application have been created.

Parameters:
- ``sender`` - the application factory function.
- ``app`` - the Flask application instance.

Example receiver:

.. code-block:: python

   def receiver(sender, app=None, **kwargs):
       # ...
"""

app_loaded = _signals.signal("app-loaded")
"""Signal sent when the Flask application have been fully loaded.

Parameters:
- ``sender`` - the application factory function.
- ``app`` - the Flask application instance.

Example receiver:

.. code-block:: python

   def receiver(sender, app=None, **kwargs):
       # ...
"""
