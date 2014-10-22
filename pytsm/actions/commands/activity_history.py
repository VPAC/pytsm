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

        parser.add_argument('--node', dest="node",
                            help='Name of node')
        parser.add_argument('--activity', dest="activity",
                            choices=["backup", "restore", "expiration"],
                            help='Activity')

    def handle_tsm(self, args, f, d):
        f.output_head("Activity History")

        conditions = []
        cargs = ()
        if args.activity is not None:
            conditions.append("activity=%s")
            cargs = cargs + (args.activity.upper(), )
        if args.node is not None:
            conditions.append("entity=%s")
            cargs = cargs + (args.node.upper(), )

        if len(conditions) > 0:
            condition = "where " + " and ".join(conditions)
        else:
            condition = ""

        results = d.execute(
            """select
entity as "Node",
activity as "Activity",
date(start_time) as "Start Date",
time(start_time) as "Start Time",
date(end_time) as "End Date",
time(end_time) as "End Time",
TIMESTAMPDIFF(2,CHAR(end_time-start_time))/60.0 as "Min",
bytes/1024.0/1024.0 as "Total_MiB",
case
    when TIMESTAMPDIFF(2,CHAR(end_time-start_time)) >0
    then bytes/TIMESTAMPDIFF(2,CHAR(end_time-start_time))/1024.0/1024.0
    else cast(0 as decimal(6,1))
    end as "MiB/Sec",
case
    when examined >0
    then affected*100.0/examined
    else cast(0 as decimal(6,1))
    end as "Volatility_%%"
from summary """ + condition + " order by 2,3", cargs)

        headers = [
            {"name": "Node", },
            {"name": "Activity", },
            {"name": "Start Date", },
            {"name": "Start Time", },
            {"name": "End Date", },
            {"name": "End Time", },
            {"name": "Minutes",    "justify": "right",
                "format": "float", "spec": "%0.1f"},
            {"name": "MiB",        "justify": "right",
                "format": "float", "spec": "%0.1f"},
            {"name": "MiB/Sec",    "justify": "right",
                "format": "float", "spec": "%0.1f"},
            {"name": "Volatility", "justify": "right",
                "format": "float", "spec": "%0.1f"},
        ]
        f.output_results(results, headers)

        d.close()

        f.output_tail()
