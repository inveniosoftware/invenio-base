# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Unit tests for the inveniomanage script."""

from __future__ import absolute_import

from flask import escape, url_for

from mock import patch

from invenio_testing import InvenioTestCase


class FlashMessageSecurityTest(InvenioTestCase):
    """Test base views."""

    @property
    def config(self):
        # add the test flask application to loaded packages
        cfg = super(FlashMessageSecurityTest, self).config
        cfg['PACKAGES'] = [
            'test_apps.flash_msg',
            'invenio_base',
        ]
        return cfg

    @patch('webassets.ext.jinja2.AssetsExtension._render_assets')
    def test_flash_message_escaping(self, _render_assets):
        """Test that flash messages are escaped by default."""
        _render_assets.return_value = '/ping'

        flash_contexts = ['', 'info', 'danger', 'error', 'warning', 'success']
        safe_flash_contexts = [context + '(html_safe)' for context in
                               flash_contexts]

        message = 'this is an <script>alert(1)</script>'
        escaped_message = str(escape('<script>alert(1)</script>'))

        for context in flash_contexts:
            # test non safe contexts
            response = self.client.get(url_for('flash_msg.index', message=message,
                                               context=context))
            self.assertTrue(escaped_message in response.data,
                            'flash message should have been escaped for ' +
                            'context "{0}"'.format(context))

        for context in safe_flash_contexts:
            # test safe contexts
            response = self.client.get(url_for('flash_msg.index', message=message,
                                               context=context))
            self.assertTrue(message in response.data,
                            'flash message should not have been escaped for ' +
                            'context "{0}"'.format(context))
