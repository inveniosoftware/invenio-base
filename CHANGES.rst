..
    This file is part of Invenio.
    Copyright (C) 2015, 2016 CERN.

    Invenio is free software; you can redistribute it
    and/or modify it under the terms of the GNU General Public License as
    published by the Free Software Foundation; either version 2 of the
    License, or (at your option) any later version.

    Invenio is distributed in the hope that it will be
    useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Invenio; if not, write to the
    Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
    MA 02111-1307, USA.

    In applying this license, CERN does not
    waive the privileges and immunities granted to it by virtue of its status
    as an Intergovernmental Organization or submit itself to any jurisdiction.

Changes
=======

Version 1.0.0a10 (released 2016-05-13)
----------------=---------------------

- Initial refactoring for Invenio 3 compatible packages.


Version 0.3.1 (released 2015-10-06)
-----------------------------------

Bug fixes
~~~~~~~~~

- Corrects the d3.js library path.

Version 0.3.0 (released 2015-09-22)
-----------------------------------

Incompatible changes
~~~~~~~~~~~~~~~~~~~~

- Disables non-core extensions for Invenio deposit and Elastic search,
  that requires Invenio-Records to be installed.
- Removes database mysql-info command.

Bug fixes
~~~~~~~~~

- Removes dependencies on Invenio package.
- Removes calls to PluginManager consider_setuptools_entrypoints()
  removed in PyTest 2.8.0.
- Adds missing invenio_ext dependency and fixes its imports.

Version 0.2.1 (released 2015-09-14)
-----------------------------------

Bug fixes
~~~~~~~~~

- Amends legacy imports and mentions of `invenio.base` module.
- Removes dependency on JSONAlchemy in `database` command.

Version 0.2.0 (released 2015-09-14)
-----------------------------------

Incompatible changes
~~~~~~~~~~~~~~~~~~~~

- Removes deprecated `demosite` command.

New features
~~~~~~~~~~~~

- Adds `jsoneditor` dependency to r.js settings.

Improved features
~~~~~~~~~~~~~~~~~

- Replaces `select2.min` with `select2` to simplify debugging.

Bug fixes
~~~~~~~~~

- Fixes a bug which, under certain conditions, led to wrong asset
  links when working with ASSET_DEBUG=True.

Version 0.1.0 (released 2015-09-09)
-----------------------------------

- Initial public release.
