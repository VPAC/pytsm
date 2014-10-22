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
    help = "Display TSM backup history"

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)

        group = parser.add_mutually_exclusive_group()
        group.add_argument('--node', dest="node",
                           help='Name of node')
        group.add_argument('--stgpool', dest="stgpool",
                           help='Storage pool to list')

    def handle_tsm(self, args, f, d):
        f.output_head("Node STG Per Filespace")

        if args.node is not None:
            condition = "where node_name=%s"
            cargs = (args.node.upper(), )
        elif args.stgpool is not None:
            condition = "where stgpool_name=%s"
            cargs = (args.stgpool, )
        else:
            condition = ""
            cargs = None

        results = d.execute(
            "SELECT node_name, filespace_name, stgpool_name, logical_mb "
            "AS \"Total MB\" FROM occupancy %s "
            "ORDER BY node_name, filespace_name, stgpool_name"
            % condition, cargs)

        headers = [
            {"name": "Node", },
            {"name": "Filespace", },
            {"name": "STG Pool", },
            {"name": "Used (MiB)", "justify": "right",
             "format": "float", "spec": "%0.2f"},
        ]
        f.output_results(results, headers)

        d.close()

        f.output_tail()
