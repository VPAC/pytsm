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

from ..base import TsmCommand


class Command(TsmCommand):
    help = "Display TSM backup usage"

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)

        parser.add_argument(
            '--node', dest="node",
            help='Name of node')

    def handle_tsm(self, args, f, d):
        f.output_head("Usage")

        conditions = []
        cargs = ()
        if args.node is not None:
            conditions.append("node_name=%s")
            cargs = cargs + (args.node.upper(), )

        if len(conditions) > 0:
            condition = "where " + " and ".join(conditions)
        else:
            condition = ""

        results = d.execute(
            "SELECT node_name, sum(logical_mb), sum(physical_mb), "
            "sum(physical_mb)-sum(logical_mb) "
            "FROM occupancy " + condition + " "
            "GROUP BY node_name", cargs)

        headers = [
            {"name": "Node", },
            {"name": "Logical (MiB)",  "justify": "right",
             "format": "float", "spec": "%0.1f"},
            {"name": "Physical (MiB)", "justify": "right",
             "format": "float", "spec": "%0.1f"},
            {"name": "Overhead (MiB)", "justify": "right",
             "format": "float", "spec": "%0.1f"},
        ]

        f.output_results(results, headers)

        d.close()

        f.output_tail()
