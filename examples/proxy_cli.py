# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from typing import Dict, Union
import click
from invenio_base.wsgi import ProxyConfig


def validate_proxy_config(config: Dict[str, Union[int, str]]) -> ProxyConfig:
    """Check if proxy counts are valid integers.

    Bug prevention:
    - catches string inputs like 'all' or 'none' that could break things
    - stops negative numbers that would mess up proxy counting
    - prevents typos in config keys
    """
    valid_keys = {"x_for", "x_proto", "x_host", "x_port", "x_prefix"}
    invalid_keys = set(config.keys()) - valid_keys
    if invalid_keys:
        raise ValueError(f"Invalid proxy keys: {invalid_keys}")

    # Convert and validate values
    result = {}
    for key, value in config.items():
        try:
            num_value = int(value) if isinstance(value, str) else value
            if not isinstance(num_value, int):
                raise ValueError(f"{key} must be an integer")
            if num_value < 0:
                raise ValueError(f"{key} cannot be negative")
            result[key] = num_value
        except ValueError as e:
            raise ValueError(f"Invalid value for {key}: {value}. {str(e)}")

    return ProxyConfig(**result)


@click.command()
@click.option("--x-for", help="Nr of X-Forwarded-For headers to trust")
@click.option("--x-proto", help="Nr of X-Forwarded-Proto headers to trust")
@click.option("--x-host", help="Nr of X-Forwarded-Host headers to trust")
@click.option("--x-port", help="Nr of X-Forwarded-Port headers to trust")
@click.option("--x-prefix", help="Nr of X-Forwarded-Prefix headers to trust")
def configure_proxy(
    x_for: str, x_proto: str, x_host: str, x_port: str, x_prefix: str
) -> None:
    """Configure trusted proxy counts with type safety.

    Prevents three common proxy configuration mistakes:
    - using strings like 'all' instead of numbers
    - using negative numbers for proxy counts
    - mistyping configuration keys

    These mistakes could cause security issues if not caught early.

    Usage:
        python proxy_cli.py --x-for 1 --x-proto 2 --x-host 1 --x-port 1 --x-prefix 1

    Bad examples:
        python proxy_cli.py --x-for -1     # negative numbers
        python proxy_cli.py --x-for all    # strings
        python proxy_cli.py --x-bad 1      # any config keys
    """
    config = {}
    if x_for is not None:
        config["x_for"] = x_for
    if x_proto is not None:
        config["x_proto"] = x_proto
    if x_host is not None:
        config["x_host"] = x_host
    if x_port is not None:
        config["x_port"] = x_port
    if x_prefix is not None:
        config["x_prefix"] = x_prefix

    try:
        proxy_config = validate_proxy_config(config)
        click.echo(f"Valid proxy configuration: {proxy_config}")
    except ValueError as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    configure_proxy()
