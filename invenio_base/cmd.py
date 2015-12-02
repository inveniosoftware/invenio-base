# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization or
# submit itself to any jurisdiction.

"""Application bootstraping."""

from __future__ import absolute_import, print_function

import click
from cookiecutter.main import cookiecutter
from pkg_resources import resource_filename, working_set


@click.group()
def instance():
    """Instance commands."""


@instance.command('create')
@click.argument('name')
def create(name):
    """Create a new Invenio instance from template."""
    path = resource_filename(__name__, "cookiecutter-invenio-base")

    result = cookiecutter(path, no_input=True,
                          extra_context={
                              "site_name": name,
                              "secret_key": generate_secret_key()
                          })
    click.secho("Created instance...", fg="green")
    return result


@instance.command('entrypoints')
@click.option(
    '-e', '--entry-point', default=None, metavar='ENTRY_POINT',
    help='Entry point group name (e.g. invenio_base.apps)')
def list_entrypoints(entry_point):
    """List defined entry points."""
    found_entry_points = {}
    for dist in working_set:
        entry_map = dist.get_entry_map()
        for group_name, entry_points in entry_map.items():
            # Filter entry points
            if entry_point is None and \
               not group_name.startswith('invenio'):
                continue
            if entry_point is not None and \
               entry_point != group_name:
                continue

            # Store entry points.
            if group_name not in found_entry_points:
                found_entry_points[group_name] = []
            for ep in entry_points.values():
                found_entry_points[group_name].append(str(ep))

    for ep_group in sorted(found_entry_points.keys()):
        click.secho("{0}".format(ep_group), fg='green')
        for ep in sorted(found_entry_points[ep_group]):
            click.echo("  {0}".format(ep))


def generate_secret_key():
    """Generate secret key."""
    import string
    import random

    rng = random.SystemRandom()
    return ''.join(
        rng.choice(string.ascii_letters + string.digits)
        for dummy in range(0, 256)
    )
