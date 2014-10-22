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
    help = "List volumes"

    def handle_tsm(self, args, f, d):
        volumes = {}
        results = d.execute(
            "select VOLUME_NAME,LIBRARY_NAME,STATUS,LAST_USE from LIBVOLUMES")
        for r in results:
            v = r[0]
            if v in volumes:
                raise RuntimeError("volume %s found multiple times" % v)
            volumes[v] = r

        d.close()

        results = d.execute(
            "select VOLUME_NAME,STGPOOL_NAME,EST_CAPACITY_MB,PCT_UTILIZED,"
            "EST_CAPACITY_MB*PCT_UTILIZED/100,STATUS "
            "from volumes "
            "order by VOLUME_NAME")
        inlib_array = []
        notinlib_array = []
        known_volumes = {}
        for r in results:
            v = r[0]
            if v in known_volumes:
                raise RuntimeError("volume %s found multiple times" % v)
            known_volumes[v] = r
            if v in volumes:
                inlib_array.append(r + volumes[v][1:])
            else:
                notinlib_array.append(r)

        f.output_header("NOT IN LIBRARY")

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
        ]
        f.output_results(notinlib_array, headers)

        f.output_header("IN LIBRARY ASSIGNED")

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
            {"name": "Library", },
            {"name": "Status", },
            {"name": "Usage", },
        ]
        f.output_results(inlib_array, headers)

        f.output_header("IN LIBRARY NOT ASSIGNED")

        result_array = []
        for _, r in volumes.items():
            v = r[0]
            if v not in known_volumes:
                result_array.append(r)

        headers = [
            {"name": "Volume", },
            {"name": "Library", },
            {"name": "Status", },
            {"name": "Usage", },
        ]
        f.output_results(result_array, headers)

        f.output_tail()
