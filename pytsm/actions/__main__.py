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
import sys
import codecs
import locale
from . import command_line

if __name__ == "__main__":
    if sys.version_info < (3, 0):
        # for python2 we need to use correct encoding when writing to stdout
        encoding = locale.getpreferredencoding()
        Writer = codecs.getwriter(encoding)
        sys.stdout = Writer(sys.stdout)

    rc = command_line(sys.argv)
    sys.exit(rc)
