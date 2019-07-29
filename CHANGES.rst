..
    This file is part of Invenio.
    Copyright (C) 2015-2018 CERN.

    Invenio is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

Changes
=======

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
