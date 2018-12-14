..
    This file is part of Invenio.
    Copyright (C) 2015-2018 CERN.

    Invenio is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

Changes
=======

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
