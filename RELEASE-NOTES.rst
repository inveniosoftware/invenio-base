=====================
 Invenio-Base v0.3.0
=====================

Invenio-Base v0.3.0 was released on September 22, 2015.

About
-----

Base package for building the Invenio application.

*This is an experimental developer preview release.*

Incompatible changes
--------------------

- Disables non-core extensions for Invenio deposit and Elastic search,
  that requires Invenio-Records to be installed.
- Removes database mysql-info command.

Bug fixes
---------

- Removes dependencies on Invenio package.
- Removes calls to PluginManager consider_setuptools_entrypoints()
  removed in PyTest 2.8.0.
- Adds missing invenio_ext dependency and fixes its imports.

Installation
------------

   $ pip install invenio-base==0.3.0

Documentation
-------------

   http://invenio-base.readthedocs.org/en/v0.3.0

Happy hacking and thanks for flying Invenio-Base.

| Invenio Development Team
|   Email: info@invenio-software.org
|   IRC: #invenio on irc.freenode.net
|   Twitter: http://twitter.com/inveniosoftware
|   GitHub: https://github.com/inveniosoftware/invenio-base
|   URL: http://invenio-software.org
