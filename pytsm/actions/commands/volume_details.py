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
    help = "List abbreviated contents of TSM volume"

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)

        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--stgpool', dest="stgpool",
                           help='Storage pool to list')
        group.add_argument('--volume', dest="volume",
                           help='Name of volume')

    def handle_tsm(self, args, f, d):
        if args.volume is not None:
            condition = "where volume_name=%s"
            cargs = (args.volume,)
        elif args.stgpool is not None:
            condition = "where stgpool_name=%s"
            cargs = (args.stgpool,)
        else:
            condition = ""
            cargs = None

        volumes = {}
        results = d.execute(
            "select volume_name,STGPOOL_NAME,EST_CAPACITY_MB,PCT_UTILIZED,"
            "EST_CAPACITY_MB*PCT_UTILIZED/100,STATUS "
            "from volumes %s" % condition, cargs)
        for row in results:
            v = row[0]
            if v in volumes:
                raise RuntimeError("volume %s found multiple times" % v)
            volumes[v] = row

        results = d.execute(
            "select volume_name, node_name, filespace_name "
            "from volumeusage %s "
            "order by volume_name, node_name, filespace_name"
            % condition, cargs)

        headers = [
            {"name": "Volume", },
            {"name": "STG Pool", },
            {"name": "Capacity (MiB)", "justify": "right",
             "format": "float", "spec": "%0.1f"},
            {"name": "Utilized (%)",   "justify": "right",
             "format": "float", "spec": "%0.1f"},
            {"name": "Utilized (MiB)", "justify": "right",
             "format": "float", "spec": "%0.1f"},
            {"name": "Status", },
            {"name": "Node", },
            {"name": "Filespace", },
        ]

        def process_results(results):
            for row in results:
                volume = row[0]
                row = row[0:1] + volumes[volume][1:] + row[1:]
                yield row

        f.output_results(process_results(results), headers)

        d.close()

        f.output_tail()
