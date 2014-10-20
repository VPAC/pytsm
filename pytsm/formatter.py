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

import copy
import csv
import locale
import sys

from . import texttable


class formatter(object):

    def __init__(self, output=sys.stdout):
        self.output = output

    def output_head(self, title):
        self.output.write("# ")
        self.output.write(title)
        self.output.write("\n\n")

    def output_tail(self):
        pass

    def output_header(self, line):
        self.output.write("\n\n## ")
        self.output.write(line)
        self.output.write("\n\n")

    def output_text(self, line):
        self.output.write(line)
        self.output.write("\n")

    def format_results(self, results, headers):

        # copy data
        results = copy.deepcopy(list(results))
        headers = copy.deepcopy(headers)

        # ensure header for every column
        for row_array in results:
            while len(row_array) > len(headers):
                headers.append({"name": "untitled", "justify": "left"})

        # for every row in results
        for row_array in results:
            # ensure header for every column
            while len(row_array) > len(headers):
                headers.append({"name": "untitled", "justify": "left"})

            # for every column
            for col in range(0, len(row_array)):
                # format as required
                f = "string"
                if "format" in headers[col]:
                    f = headers[col]['format']
                if f == "integer":
                    row_array[col] = locale.format(
                        headers[col]['spec'],
                        int(row_array[col]), grouping=True)
                elif f == "float":
                    row_array[col] = locale.format(
                        headers[col]['spec'],
                        float(row_array[col]), grouping=True)

        return results, headers


class formatter_csv(formatter):

    def output_results(self, results, headers):
        writer = csv.writer(self.output, delimiter=',')
        writer.writerow([h['name'] for h in headers])
        for row in results:
            writer.writerow(row)


class formatter_html(formatter):

    def output_results(self, results, headers):
        results, headers = self.format_results(results, headers)

        self.output.write("<table border='1'>\n<tr>")
        for h in headers:
            justify = "left"
            if 'justify' in h:
                justify = h['justify']
            if justify == "left":
                pass
            elif justify == "right":
                pass
            else:
                raise RuntimeError("Unknown justification %s" % justify)
            self.output.write("<th align='%s'>" % justify)
            self.output.write(h['name'])
            self.output.write("</th>")
        self.output.write("</tr>\n")

        for row in results:
            self.output.write("<tr>")
            for d, h in zip(row, headers):
                justify = "left"
                if 'justify' in h:
                    justify = h['justify']
                if justify == "left":
                    pass
                elif justify == "right":
                    pass
                else:
                    raise RuntimeError("Unknown justification %s" % justify)
                self.output.write("<td align='%s'>" % justify)
                self.output.write(d)
                self.output.write("</td>")
            self.output.write("</tr>\n")
        self.output.write("</table>\n")

    def output_head(self, title):
        self.output.write(
            '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" '
            '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">')
        self.output.write('<html><head><title>')
        self.output.write(title)
        self.output.write('</title></head><body><h1>')
        self.output.write(title)
        self.output.write('</h1>')
        self.output.write("\n\n")

    def output_tail(self):
        self.output.write('</body>\n')

    def output_header(self, line):
        self.output.write("<h2>")
        self.output.write(line)
        self.output.write("</h2>\n")

    def output_text(self, line):
        self.output.write("<p>")
        self.output.write(line)
        self.output.write("</p>\n")


class formatter_readable(formatter):

    def output_results(self, results, headers):
        locale.setlocale(locale.LC_ALL, '')

        results, headers = self.format_results(results, headers)

        col_align = []
        col_dtype = []
        table = texttable.Texttable(max_width=130)
        table.set_deco(texttable.Texttable.HEADER | texttable.Texttable.VLINES)
        for h in headers:
            justify = "left"
            if 'justify' in h:
                justify = h['justify']
            if justify == "left":
                col_align.append("l")
            elif justify == "right":
                col_align.append("r")
            else:
                raise RuntimeError("Unknown justification %s" % justify)

            f = "auto"
            if "format" in h:
                f = h['format']
            if f == "string":
                col_dtype.append('t')
            elif f == "integer":
                col_dtype.append('t')
            elif f == "float":
                col_dtype.append('t')
            elif f == "auto":
                col_dtype.append('auto')
            else:
                raise RuntimeError("Unknown format %s" % f)

        table.set_cols_align(col_align)
        table.set_cols_dtype(col_dtype)
        table.header([h["name"] for h in headers])
        table.add_rows(results, header=False)
        self.output.write(table.draw())
        self.output.write("\n")


def get_formatter(output_format, *args, **kwargs):
    if output_format == "csv":
        return formatter_csv(*args, **kwargs)
    elif output_format == "html":
        return formatter_html(*args, **kwargs)
    elif output_format == "readable":
        return formatter_readable(*args, **kwargs)
    else:
        raise RuntimeError("Unknown format %s" % output_format)
