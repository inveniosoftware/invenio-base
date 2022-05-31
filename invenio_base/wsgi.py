# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""WSGI application factory for Invenio."""

import warnings

# They were moved in the same version so they can be in one try/except
try:
    from werkzeug.middleware.dispatcher import DispatcherMiddleware
    from werkzeug.middleware.proxy_fix import ProxyFix

    WERKZEUG_GTE_014 = False
except ImportError:
    from werkzeug.contrib.fixers import ProxyFix
    from werkzeug.wsgi import DispatcherMiddleware

    WERKZEUG_GTE_014 = True


def create_wsgi_factory(mounts_factories):
    """Create a WSGI application factory.

    Usage example:

    .. code-block:: python

       wsgi_factory = create_wsgi_factory({'/api': create_api})

    :param mounts_factories: Dictionary of mount points per application
        factory.

    .. versionadded:: 1.0.0
    """

    def create_wsgi(app, **kwargs):
        mounts = {
            mount: factory(**kwargs) for mount, factory in mounts_factories.items()
        }
        return DispatcherMiddleware(app.wsgi_app, mounts)

    return create_wsgi


def wsgi_proxyfix(factory=None):
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

    def create_wsgi(app, **kwargs):
        wsgi_app = factory(app, **kwargs) if factory else app.wsgi_app
        num_proxies = app.config.get("WSGI_PROXIES")
        proxy_config = app.config.get("PROXYFIX_CONFIG")
        if proxy_config and not WERKZEUG_GTE_014:
            return ProxyFix(wsgi_app, **proxy_config)
        elif num_proxies:
            warnings.warn(
                "The WSGI_PROXIES configuration is deprecated and "
                "it will be removed, use PROXYFIX_CONFIG instead",
                PendingDeprecationWarning,
            )
            if WERKZEUG_GTE_014:
                return ProxyFix(wsgi_app, num_proxies=num_proxies)
            else:
                return ProxyFix(wsgi_app, x_for=num_proxies)
        return wsgi_app

    return create_wsgi
