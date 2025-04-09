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
from typing import Any, cast

import click
import importlib_metadata
from flask import current_app
from flask.cli import with_appcontext
from importlib_metadata import EntryPoint
from pkg_resources import working_set
from typing_extensions import Protocol


class SecretKeyMigrator(Protocol):
    """Type definition for secret key migration functions."""

    def __call__(self, **kwargs: Any) -> None:
        """Call the migrator with keyword arguments."""
        ...


@click.group()  # type: ignore[misc]
def instance() -> None:
    """Instance commands."""


@instance.command("entrypoints")  # type: ignore[misc]
@click.option(  # type: ignore[misc]
    "-e",
    "--entry-point",
    default=None,
    metavar="ENTRY_POINT",
    help="Entry point group name (e.g. invenio_base.apps)",
)
def list_entrypoints(entry_point: str | None = None) -> None:
    """List defined entry points."""
    found_entry_points: dict[str, list[str]] = {}
    for dist in working_set:
        # for dist in importlib_metadata.distributions:
        entry_map = dist.get_entry_map()
        for group_name, entry_points in entry_map.items():
            # Filter entry points
            if entry_point is None and not group_name.startswith("invenio"):
                continue
            if entry_point is not None and entry_point != group_name:
                continue

            # Store entry points.
            if group_name not in found_entry_points:
                found_entry_points[group_name] = []
            # Convert the entry point to string before appending
            for _, ep_value in entry_points.items():
                found_entry_points[group_name].append(str(ep_value))

    for ep_group in sorted(found_entry_points.keys()):
        click.secho(f"{ep_group}", fg="green")
        for ep in sorted(found_entry_points[ep_group]):
            click.echo(f"  {ep}")


@instance.command("migrate-secret-key")  # type: ignore[misc]
@click.option("--old-key", required=True)  # type: ignore[misc]
@with_appcontext  # type: ignore[misc]
def migrate_secret_key(old_key: str) -> None:
    """Call entry points exposed for the SECRET_KEY change."""
    if (
        "SECRET_KEY" not in current_app.config
        or current_app.config["SECRET_KEY"] is None
    ):
        raise click.ClickException("SECRET_KEY is not set in the configuration.")

    migrators: list[SecretKeyMigrator] = []
    for ep in set(importlib_metadata.entry_points().get("invenio_base.secret_key", [])):  # type: ignore[attr-defined]
        try:
            migrators.append(cast(SecretKeyMigrator, ep.load()))
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


def generate_secret_key() -> str:
    """Generate secret key."""
    import random
    import string

    rng = random.SystemRandom()
    return "".join(
        rng.choice(string.ascii_letters + string.digits) for dummy in range(0, 256)
    )
