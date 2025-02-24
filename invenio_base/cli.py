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

import click
import importlib_metadata
from flask import current_app
from flask.cli import with_appcontext
from pkg_resources import working_set


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
            for ep in entry_points.values():
                found_entry_points[group_name].append(str(ep))

    for ep_group in sorted(found_entry_points.keys()):
        click.secho(f"{ep_group}", fg="green")
        for ep in sorted(found_entry_points[ep_group]):
            click.echo(f"  {ep}")


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
    for ep in set(importlib_metadata.entry_points().get("invenio_base.secret_key", [])):
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


def create_args(subcommand, subcommand_args):
    """Create args"""
    click_params = {param.name: param for param in subcommand.params}

    args = []
    kwargs = {}

    for param_name, param_type in click_params.items():
        if isinstance(param_type, click.Option):
            print(f"create_args is option")
        elif isinstance(param_type, click.Argument):
            print(f"create_args is argument")
            kwargs[param_name] = subcommand_args[0]
        print(
            f"create_args param_type: {param_type}, param_name: {param_name}, subcommand_args: {subcommand_args}"
        )

    print(f"create_args kwargs: {kwargs}, positional_args: {args}")
    return args, kwargs


@click.command()
@click.argument("commands", type=str, required=True)
@click.pass_context
@with_appcontext
def apply(ctx, commands):
    """Apply group."""
    parsed_commands = [cmd.strip() for cmd in commands.split("&&") if cmd.strip()]

    for cmd in parsed_commands:
        parts = cmd.split()
        group_name = parts[0]
        args = parts[1:]

        try:
            group_cmd = ctx.parent.command.commands[group_name]
        except KeyError:
            click.echo(f"Unknown group: {group_name}", err=True)
            continue

        if not isinstance(group_cmd, click.Group):
            click.echo(f"Group cmd: {group_cmd} is not of type click.Group", err=True)
            continue

        if len(args) == 0:
            click.echo("Args must be greater then 0", err=True)
            continue

        try:
            subcommand_name = args[0]
            subcommand_args = args[1:]

            subcommand = group_cmd.commands[subcommand_name]

            args, kwargs = create_args(subcommand, subcommand_args)
            ctx.invoke(subcommand, *args, **kwargs)
        except KeyError:
            click.echo(
                f"Unknown subcommand: {subcommand_name} for {group_name}", err=True
            )
