# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
# Copyright (C) 2022-2025 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""WSGI application factory for Invenio."""

from __future__ import annotations

import warnings
from collections.abc import Callable, Iterable
from typing import Any, NotRequired, Protocol, TypeAlias, TypedDict, TypeVar

from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.middleware.proxy_fix import ProxyFix

# Define basic WSGI types
Environ: TypeAlias = dict[str, Any]
Headers: TypeAlias = list[tuple[str, str]]
ExcInfo: TypeAlias = list[Any]
StartResponse: TypeAlias = Callable[[str, Headers, ExcInfo], Iterable[bytes]]
WSGICallable: TypeAlias = Callable[[Environ, StartResponse], Iterable[bytes]]


class ProxyConfig(TypedDict, total=False):
    """Configuration for ProxyFix middleware."""

    x_for: NotRequired[int]
    x_proto: NotRequired[int]
    x_host: NotRequired[int]
    x_port: NotRequired[int]
    x_prefix: NotRequired[int]


class WSGIApplication(Protocol):
    """Protocol for WSGI applications."""

    def __call__(
        self, environ: Environ, start_response: StartResponse
    ) -> Iterable[bytes]:
        """Handle WSGI call."""
        ...

    wsgi_app: WSGICallable
    config: dict[str, Any]


def create_wsgi_factory(
    mounts_factories: dict[str, Callable[..., WSGIApplication]],
) -> Callable[[WSGIApplication], WSGICallable]:
    """Create a WSGI application factory.

    Usage example:

    .. code-block:: python

       wsgi_factory = create_wsgi_factory({'/api': create_api})

    :param mounts_factories: Dictionary of mount points per application
        factory.

    .. versionadded:: 1.0.0
    """

    def create_wsgi(app: WSGIApplication, **kwargs: Any) -> WSGICallable:
        mounts = {
            mount: factory(**kwargs).wsgi_app
            for mount, factory in mounts_factories.items()
        }
        return DispatcherMiddleware(app.wsgi_app, mounts)  # type: ignore

    return create_wsgi


def wsgi_proxyfix[T: WSGIApplication](
    factory: Callable[..., T] | None = None,
) -> Callable[[T], WSGICallable]:
    """Fix Flask environment according to ``X-Forwarded-_`` headers.

    Detailed explanation follows in the rest of the docstring.

    .. note::

       You must set ``WSGI_PROXIES`` to the correct number of proxies,
       otherwise you application is susceptible to malicious attacks.

    .. versionadded:: 1.0.0

    .. note::

       ``PROXY_CONFIG`` lets you specify the number of proxies which a HTTP
       request is traversing before reaching the Invenio application. Invenio
       will then be able to trust and therefore pick the correct headers set
       by your proxy, for example host, protocol or scheme. This is important
       to avoid any possible malicious attacks which could manipulate/inject
       headers:

       .. code-block:: python

          PROXYFIX_CONFIG = {
              x_for: 1,  # Invenio will trust only the first value of
                         # X-Forwarded-For header and ignore the rest
              x_proto: 0,  # No X-Forwarded-Proto header will be trusted
              x_host: 0,  # No X-Forwarded-Host header will be trusted
              x_port: 0,  # No X-Forwarded-Port header will be trusted
              x_prefix: 0,  # No X-Forwarded-Prefix header will be trusted
          }

       This configuration defines which HTTP headers will be taken into
       account by your application.

       For example, if you have one proxy in front of your application and you
       want your application to use the original HTTP scheme, you would set
       the following configuration:

       .. code-block:: python

          PROXYFIX_CONFIG = {
              x_proto: 1,
          }

       Which means, that the first ``X-Forwarded-Proto`` header will be taken
       into account.

    .. versionadded:: 1.2.0

    .. deprecated:: 1.2

       The ``WSGI_PROXIES`` configuration is deprecated and it will be removed,
       use ``PROXYFIX_CONFIG`` instead.
    """

    def create_wsgi(app: T) -> WSGICallable:
        wsgi_app = factory().wsgi_app if factory else app.wsgi_app
        num_proxies = app.config.get("WSGI_PROXIES")
        proxy_config: ProxyConfig | None = app.config.get("PROXYFIX_CONFIG")

        match (proxy_config, num_proxies):
            case (dict(), _):
                return ProxyFix(wsgi_app, **proxy_config)  # type: ignore
            case (None, int()):
                warnings.warn(
                    "The WSGI_PROXIES configuration is deprecated and "
                    "it will be removed, use PROXYFIX_CONFIG instead",
                    PendingDeprecationWarning,
                )
                return ProxyFix(wsgi_app, x_for=num_proxies)  # type: ignore
            case _:
                return wsgi_app

    return create_wsgi


__all__ = (
    "create_wsgi_factory",
    "wsgi_proxyfix",
    "WSGIApplication",
    "WSGICallable",
    "ProxyConfig",
)
