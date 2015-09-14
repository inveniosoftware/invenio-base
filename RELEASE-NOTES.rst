=====================
 Invenio-Base v0.2.0
=====================

Invenio-Base v0.2.0 was released on September 14, 2015.

About
-----

Base package for building the Invenio application.

*This is an experimental developer preview release.*

Incompatible changes
--------------------

- Removes deprecated `demosite` command.

New features
------------

- Adds `jsoneditor` dependency to r.js settings.

Improved features
-----------------

- Replaces `select2.min` with `select2` to simplify debugging.

Bug fixes
---------

- Fixes a bug which, under certain conditions, led to wrong asset
  links when working with ASSET_DEBUG=True.

Installation
------------

   $ pip install invenio-base==0.2.0

Documentation
-------------

   http://invenio-base.readthedocs.org/en/v0.2.0

Happy hacking and thanks for flying Invenio-Base.

| Invenio Development Team
|   Email: info@invenio-software.org
|   IRC: #invenio on irc.freenode.net
|   Twitter: http://twitter.com/inveniosoftware
|   GitHub: https://github.com/inveniosoftware/invenio-base
|   URL: http://invenio-software.org
