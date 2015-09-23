# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2013, 2015 CERN.
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

from __future__ import print_function

import sys

from invenio_base.utils import run_py_func
from invenio_testing import InvenioTestCase


class Catcher(object):
    """Helper decorator to test raw_input."""
    ## see: http://stackoverflow.com/questions/13480632/python-stringio-selectively-place-data-into-stdin

    def __init__(self, handler):
        self.handler = handler
        self.inputs = []

    def __enter__(self):
        self.__stdin = sys.stdin
        self.__stdout = sys.stdout
        sys.stdin = self
        sys.stdout = self

    def __exit__(self, type, value, traceback):
        sys.stdin = self.__stdin
        sys.stdout = self.__stdout

    def write(self, value):
        self.__stdout.write(value)
        result = self.handler(value)
        if result is not None:
            self.inputs.append(result)

    def readline(self):
        return self.inputs.pop()

    def getvalue(self):
        return self.__stdout.getvalue()

    def truncate(self, pos):
        return self.__stdout.truncate(pos)


class InveniomanageTest(InvenioTestCase):

    def test_signals_usage(self):
        """ Test signal handling. """
        from invenio_base.scripts.database import main as db_main
        from invenio_base.signals import pre_command, post_command
        from invenio_base.manage import main, version as im_version

        def pre_handler_version(sender, *args, **kwargs):
            print('>>> pre_handler_version')

        def post_handler_version(sender, *args, **kwargs):
            print('>>> post_handler_version')

        # Bind only `inveniomanage version` command to pre/post handler.
        pre_command.connect(pre_handler_version, sender=im_version)
        post_command.connect(post_handler_version, sender=im_version)

        def pre_handler_general_test(sender, *args, **kwargs):
            print('>>> pre_handler_general')

        def post_handler_general_test(sender, *args, **kwargs):
            print('>>> post_handler_general')

        # Bind all commands to pre/post general handler.
        pre_command.connect(pre_handler_general_test)
        pre_command.connect(post_handler_general_test)

        # Expect both version and general handlers.
        out = run_py_func(main, 'inveniomanage version').out

        lines = out.split('\n')
        expected = ('>>> pre_handler_version',
                    '>>> post_handler_version',
                    '>>> pre_handler_general',
                    '>>> post_handler_general')
        for line in expected:
            self.assertTrue(line in lines,
                            "%s was not found in output %s" % (line, lines))

        # Expect only general handlers.
        out = run_py_func(db_main, 'database uri').out

        lines = out.split('\n')
        expected = ('>>> pre_handler_general',
                    '>>> post_handler_general')
        for line in expected:
            self.assertTrue(line in lines,
                            "%s was not found in output %s" % (line, lines))

        notexpected = ('>>> pre_handler_version',
                       '>>> post_handler_version')
        for line in notexpected:
            self.assertFalse(line in lines,
                             "%s was not expected in output %s" % (line, lines))
