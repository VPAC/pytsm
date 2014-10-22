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

import pytsm
import argparse


class BaseCommand(object):
    help = 'Please shoot the messenger.'

    def execute(self, prog, command, args):
        parser = argparse.ArgumentParser(
            description=self.help,
            prog="%s %s" % (prog, command))
        self.add_arguments(parser)

        args = parser.parse_args(args)
        self.handle(args)

    def add_arguments(self, parser):
        pass

    def handle(self, args):
        raise NotImplementedError()


class TsmCommand(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--server', dest="server",
            help='TSM server to connect to')
        parser.add_argument(
            '--format', dest="format",
            choices=["readable", "csv", "html"], default="readable",
            help='format to use when displaying results')

    def handle(self, args):
        f = pytsm.get_formatter(args.format)

        d = pytsm.dsmadmc()
        d.auto_open(args.server)

        self.handle_tsm(args, f, d)
