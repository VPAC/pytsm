# Copyright 2012-2014 VPAC
#
# This file is part of pytsm.
#
# pytsm is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pytsm is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pytsm.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import importlib
import sys
import codecs
import locale


def load_command(name):
    assert not name.startswith("_")
    assert name.find(".") == -1
    mod = importlib.import_module('pytsm.actions.commands.' + name)
    return mod.Command


def command_line(argv=None):
    if sys.version_info < (3, 0):
        # for python2 we need to use correct encoding when writing to stdout
        encoding = locale.getpreferredencoding()
        Writer = codecs.getwriter(encoding)
        sys.stdout = Writer(sys.stdout)

    if argv is None:
        argv = sys.argv

    try:
        command = argv[1]
    except IndexError:
        command = "help"

    args = argv[2:]

    try:
        klass = load_command(command)
    except ImportError:
        print("Unknown command %s." % command, file=sys.stderr)
        return 255

    obj = klass()
    rc = obj.execute(argv[0], command, args)
    return rc
