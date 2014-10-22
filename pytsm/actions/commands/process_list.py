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
    help = "Display Process List"

    def handle_tsm(self, args, f, d):
        f.output_head("Process List")

        results = d.execute(
            """select
process_num,
process,
date(start_time) as "Start Date",
time(start_time) as "Start Time",
TIMESTAMPDIFF(2,CHAR(current_timestamp-start_time))/60.0 as "Min",
bytes_processed/1024/1024 as "Total_MiB",
case
    when TIMESTAMPDIFF(2,CHAR(current_timestamp-start_time)) >0
    then bytes_processed/TIMESTAMPDIFF(2,CHAR(current_timestamp-start_time))
        /1024.0/1024.0
    else cast(0 as decimal(6,1))
    end as "MiB/Sec"
from processes
""")

        headers = [
            {"name": "PID", },
            {"name": "Process", },
            {"name": "Start Date", },
            {"name": "Start Time", },
            {"name": "Minutes", "justify": "right",
                "format": "float", "spec": "%0.1f"},
            {"name": "MiB",     "justify": "right",
                "format": "float", "spec": "%0.1f"},
            {"name": "MiB/Sec", "justify": "right",
                "format": "float", "spec": "%0.1f"},
        ]
        f.output_results(results, headers)

        d.close()

        f.output_tail()
