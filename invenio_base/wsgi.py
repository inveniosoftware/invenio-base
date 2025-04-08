# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
# Copyright (C) 2022-2025 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""WSGI application factory for Invenio."""

import warnings
from typing import Any, Callable, Dict, Optional, Protocol, TypeVar, cast, ParamSpec

try:
    from werkzeug.middleware.dispatcher import DispatcherMiddleware
    from werkzeug.middleware.proxy_fix import ProxyFix

    WERKZEUG_GTE_014 = True
except ImportError:
    from werkzeug.contrib.fixers import ProxyFix
    from werkzeug.wsgi import DispatcherMiddleware

    WERKZEUG_GTE_014 = False

from invenio_base.utils import obj_or_import_string

# Define type parameters
P = ParamSpec("P")  # For function parameters
T = TypeVar("T", bound="WSGIApplication")  # For WSGI applications

# Define types for WSGI applications
Environ = Dict[str, Any]
StartResponse = Callable[[str, list[tuple[str, str]]], Callable[[], bytes]]
WSGICallable = Callable[[Environ, StartResponse], list[bytes]]


class WSGIApplication(Protocol):
    """Protocol for WSGI applications."""

    def __call__(
        self, environ: Environ, start_response: StartResponse
    ) -> list[bytes]: ...

    wsgi_app: WSGICallable
    config: Dict[str, Any]


def create_wsgi_factory(
    mounts_factories: Dict[str, Callable[P, WSGIApplication]],
) -> Callable[[WSGIApplication, P], WSGICallable]:
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
            mount: factory(**kwargs) for mount, factory in mounts_factories.items()
        }
        return cast(WSGICallable, DispatcherMiddleware(app.wsgi_app, mounts))

    return create_wsgi


def wsgi_proxyfix(
    factory: Optional[Callable[P, T]] = None,
) -> Callable[[T, P], WSGICallable]:
    """Fix Flask environment according to ``X-Forwarded-_`` headers.

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

    def create_wsgi(app: T, **kwargs: Any) -> WSGICallable:
        wsgi_app = factory(**kwargs) if factory else app.wsgi_app
        num_proxies = app.config.get("WSGI_PROXIES")
        proxy_config = app.config.get("PROXYFIX_CONFIG")
        if proxy_config and WERKZEUG_GTE_014:
            return cast(WSGICallable, ProxyFix(wsgi_app, **proxy_config))
        elif num_proxies:
            warnings.warn(
                "The WSGI_PROXIES configuration is deprecated and "
                "it will be removed, use PROXYFIX_CONFIG instead",
                PendingDeprecationWarning,
            )
            if WERKZEUG_GTE_014:
                return cast(WSGICallable, ProxyFix(wsgi_app, x_for=num_proxies))
            else:
                return cast(WSGICallable, ProxyFix(wsgi_app, num_proxies=num_proxies))
        return cast(WSGICallable, wsgi_app)

    return create_wsgi


__all__ = (
    "create_wsgi_factory",
    "wsgi_proxyfix",
    "WSGIApplication",
    "WSGICallable",
)
