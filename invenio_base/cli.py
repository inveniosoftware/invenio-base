# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
# Copyright (C) 2022 RERO.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Application bootstraping."""

from importlib.metadata import distributions

import click
from flask import current_app
from flask.cli import with_appcontext

from .utils import entry_points


@click.group()
def instance():
    """Instance commands."""


@instance.command("entrypoints")
@click.option(
    "-e",
    "--entry-point",
    default=None,
    metavar="ENTRY_POINT",
    help="Entry point group name (e.g. invenio_base.apps)",
)
def list_entrypoints(entry_point):
    """List defined entry points."""
    found_entry_points = {}

    for dist in distributions():
        for ep in dist.entry_points:
            group_name = ep.group

            # Filter entry points
            if entry_point is None and not group_name.startswith("invenio"):
                continue
            if entry_point is not None and entry_point != group_name:
                continue

            # Store entry points.
            if group_name not in found_entry_points:
                found_entry_points[group_name] = []

            found_entry_points[group_name].append(ep)

    for ep_group in sorted(found_entry_points.keys()):
        click.secho(f"{ep_group}", fg="green")
        for ep in sorted(found_entry_points[ep_group]):
            click.echo(f"  {ep.name} = {ep.value}")


@instance.command("migrate-secret-key")
@click.option("--old-key", required=True)
@with_appcontext
def migrate_secret_key(old_key):
    """Call entry points exposed for the SECRET_KEY change."""
    if (
        "SECRET_KEY" not in current_app.config
        or current_app.config["SECRET_KEY"] is None
    ):
        raise click.ClickException("SECRET_KEY is not set in the configuration.")

    migrators = []
    for ep in entry_points("invenio_base.secret_key"):
        try:
            migrators.append(ep.load())
        except Exception:
            raise click.ClickException(f"Failed to initialize entry point: {ep}")

    if migrators:
        for m in migrators:
            try:
                m(old_key=old_key)
            except Exception:
                raise click.ClickException(
                    f"Failed to perform migration of secret key {old_key}"
                )
        click.secho("Successfully changed secret key.", fg="green")
    else:
        raise click.ClickException(
            f"Failed to perform migration of secret key {old_key}"
        )


def generate_secret_key():
    """Generate secret key."""
    import random
    import string

    rng = random.SystemRandom()
    return "".join(
        rng.choice(string.ascii_letters + string.digits) for dummy in range(0, 256)
    )
