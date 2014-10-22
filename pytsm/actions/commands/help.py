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

import os
import pkgutil

from .. import load_command
from ..base import BaseCommand

from .. import commands as namespace


class Command(BaseCommand):
    help = "List all supported commands."

    def handle(self, args):
        path = os.path.dirname(namespace.__file__)
        for _, name, _ in pkgutil.iter_modules([path]):
            klass = load_command(name)
            print("%24s  %s" % (name, klass.help))
