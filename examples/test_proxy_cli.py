# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

import pytest
from click.testing import CliRunner
from proxy_cli import configure_proxy, validate_proxy_config


def test_validate_proxy_config():
    """Make sure proxy validation catches common mistakes."""
    # valid nput works
    assert validate_proxy_config({"x_for": "1", "x_proto": "2"})

    # typos in config keys fail
    with pytest.raises(ValueError) as exc:
        validate_proxy_config({"bad_key": "1"})
    assert "Invalid proxy keys" in str(exc.value)

    # random strings fail
    with pytest.raises(ValueError) as exc:
        validate_proxy_config({"x_for": "abc"})
    assert "Invalid value for x_for" in str(exc.value)

    # negative numbers fail
    with pytest.raises(ValueError) as exc:
        validate_proxy_config({"x_for": "-1"})
    assert "cannot be negative" in str(exc.value)


def test_cli_interface():
    """Check if CLI handles inputs correctly."""
    runner = CliRunner()

    # valid input works
    result = runner.invoke(configure_proxy, ["--x-for", "1", "--x-proto", "2"])
    assert result.exit_code == 0
    assert "Valid proxy configuration" in result.output

    # strings fail
    result = runner.invoke(configure_proxy, ["--x-for", "abc"])
    assert result.exit_code != 0
    assert "Invalid value for x_for" in result.output

    # negative numbers fail
    result = runner.invoke(configure_proxy, ["--x-for", "-1"])
    assert result.exit_code != 0
    assert "cannot be negative" in result.output
