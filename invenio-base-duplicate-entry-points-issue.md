# Bug: Duplicate entry points in Python 3.10+ cause Flask blueprint name collision errors

## Summary

When two packages register the same entry point name in a group (e.g. `invenio_base.apps`,
`invenio_base.blueprints`, `invenio_base.api_blueprints`), Python 3.10+'s
`importlib.metadata.entry_points` returns **both** entries. `invenio_base.utils.entry_points`
does not deduplicate them, so both are loaded. The result is either:

- the same blueprint registered twice, raising
  `AssertionError: A blueprint's name collision occurred between …`, or
- two different blueprints with the same `name` attribute (when two entry points
  point to the same factory), raising Flask's "different blueprint" error.

This is a regression from `pkg_resources`, where first-wins deduplication was implicit.

## Affected version

`invenio-base` 2.4.0

## Context

`oarepo-rdm` is designed to override selected `invenio-rdm-records` blueprints and apps by
declaring entry points with the same names under `invenio_base.apps`,
`invenio_base.blueprints`, and `invenio_base.api_blueprints`. Under `pkg_resources` this worked
because `pkg_resources` returned only the first matching entry by name. Under Python 3.10+
`importlib.metadata` returns every entry with that name across all installed packages, so both the
override and the original are loaded.

## Steps to reproduce

1. Install both `oarepo-rdm` and `invenio-rdm-records`.
2. Start an InvenioRDM application with `flask run` or `invenio run`.
3. Observe `AssertionError: A blueprint's name collision occurred between ...`.

## Root cause

`invenio_base/utils.py::entry_points` returns the raw result of
`importlib.metadata.entry_points(group=group)` without deduplication. On Python 3.10+ this
includes every registered entry for the group across all installed packages, including same-name
entries from different packages.

Several callers in `invenio_base` and `invenio_config` each import this function directly, so
fixing it at the source (`utils.py`) covers all call sites:

- `invenio_base.app` (app and blueprint loaders)
- `invenio_base.urls.builders` (blueprint loader)
- `invenio_config.entrypoint` (config module loader)

## Proposed fix

Deduplicate the returned entry points in `entry_points()` itself using a first-wins strategy:

1. **Name deduplication**: skip any entry whose name has already been seen.
2. **Value deduplication**: skip any entry whose value (the dotted-path factory string) has
   already been seen, even under a different name.  This catches the case where two entry points
   with different names point to the same factory: loading it twice creates two Flask blueprints
   with identical `name` attributes, which triggers a different collision error.

Groups where aggregation of same-name entries from multiple packages is intentional
(`invenio_jsonschemas.schemas`, `invenio_records.jsonresolver`) are exempt from deduplication.

## Workaround (applied in frozen_testing)

`patches.py` monkey-patches `invenio_base.utils.entry_points` and every direct import of
it in `invenio_base.app`, `invenio_base.urls.builders`, and `invenio_config.entrypoint`
with a wrapper that performs the same deduplication logic.
