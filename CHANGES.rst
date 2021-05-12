..
    This file is part of Invenio.
    Copyright (C) 2015-2018 CERN.

    Invenio is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

Changes
=======

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
