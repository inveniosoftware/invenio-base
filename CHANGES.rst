..
    This file is part of Invenio.
    Copyright (C) 2015-2024 CERN.
    Copyright (C) 2025 Graz University of Technology.

    Invenio is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

Changes
=======

Version 2.3.2 (released 2025-07-01)

- fix: python3.9 can contain duplicates

Version 2.3.1 (released 2025-06-28)

- fix: use standard importlib.metadata

Version 2.3.0 (released 2025-06-27)

- fix: pkg_resources DeprecationWarning
- fix: click breaking changes

Version 2.2.0 (released 2025-04-25)

- urls: support converters in create_invenio_apps_urls_builder_factory

Version 2.1.0 (released 2025-04-17)

- Add invenio_url_for (and related mechanisms) to generate cross-app URLs

Version 2.0.0 (released 2024-11-19)

- setup: set flask,werkzeug min version
- jws: move functionality from itsdangerous
- setup: remove upper pins

Version 1.4.0 (released 2024-01-29)

- app: add configurable gc.freeze() call
- setup: pin watchdog

Version 1.3.0 (released 2023-06-23)

- Adds finalize_app_entry_points to overcome ``before_(app_)_first_request``
  deprecation in Flask>=2.3.0

Version 1.2.15 (released 2023-05-02)

- Pins Werkzeug<2.3.0 due to removed deprecations (for example ``Authoriation`` headers
  parsing issues).

Version 1.2.14 (released 2023-04-26)

- Pins Flask<2.3.0 due to removed deprecations (for example
  `before_(app_)first_request`).

Version 1.2.11 (released 2022-03-29)

- Adds a compatibility layer for Werkzeug v2.1.

Version 1.2.10 (released 2022-03-29)

- Adds support for Flask v2.1

Version 1.2.9 (released 2022-02-22)

- Fixes issue with duplicate entry points during tests due to pytest
  modifying the sys.path.

Version 1.2.8 (released 2022-02-21)

- Lowered Python requirement to v3.6 to avoid breaking builds.

Version 1.2.7 (released 2022-02-21)

- Fixed minimal test dependencies and limited itsdangerous to <2.1

Version 1.2.6 (released 2022-02-18)

- Added importlib-resources/importlib-metadata packages to replace usage of
  pkg_resources.

- Updated package to use a purely declarative package definition.

- Removed __future__ imports and usage of six library.

Version 1.2.5 (released 2021-10-18)

- Unpin Flask <2.0 and Werkzeug <2.0.

Version 1.2.4 (released 2021-05-12)

- Pins Flask <2.0 and Werkzeug <2.0 due to incompatibilities in the newly
  released versions.

Version 1.2.3 (released 2020-05-11)

- Adds support for passing ``root_path`` to the base Flask application factory.

Version 1.2.2 (released 2020-03-05)

- Adds ``six`` dependency.
- Adds the ``obj_or_import_string`` and ``load_or_import_from_config`` common
  utility functions for general re-use throughout other Invenio modules.

Version 1.2.1 (released 2020-03-02)

- Bumps Flask minimum version to v1.0.4.
- Removes ``invenio instance create`` command and ``cokiecutter`` dependency.

Version 1.2.0 (released 2019-08-28)

- Adds support to trust new proxy headers through the ``PROXYFIX_CONFIG``
  configuration variable. For more information see the
  `full documentation <api.html#invenio_base.wsgi.wsgi_proxyfix>`_.

- Deprecates the usage of ``WSGI_PROXIES`` configuration which only supports
  ``X-Forwarded-For`` headers.

Version 1.1.0 (released 2019-07-29)

- Add support for allowing instance path and static folder to be callables
  which are evaluated before being passed to the Flask application class. This
  fixes an issue in pytest-invenio and Invenio-App in which a global instance
  path was only evaluated once.

- Fixes deprecation warnings from Werkzeug.

Version 1.0.2 (released 2018-12-14)

Version 1.0.1 (released 2018-05-25)

- Added support for blueprint factory functions in the
  ``invenio_base.blueprints`` and the ``invenio_base.api_blueprints`` entry
  point groups. In addition to specifying an import path to an already created
  blueprint, you can now specify an import path of a blueprint factory function
  with the signature create_blueprint(app), that will create and return a
  blueprint. This allows moving dynamic blueprint creation from the extension
  initialization phase to the blueprint registration phase.

Version 1.0.0 (released 2018-03-23)

- Initial public release.
