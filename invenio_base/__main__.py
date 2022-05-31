# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Command Line Interface for Invenio."""

from .app import create_cli

cli = create_cli()

if __name__ == "__main__":  # pragma: no cover
    cli()
