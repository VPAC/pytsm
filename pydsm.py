#!/usr/bin/python

import ConfigParser
import subprocess
import sys
import os
import string
import re
import csv
import locale
import texttable
import copy

def _default_message_handler(msg_prefix, msg_number, msg_type, msg_text):
    sys.stderr.write("%s%s%s %s\n"%(msg_prefix, msg_number, msg_type, msg_text))

class Failed(Exception):
    pass

class dsmadmc(object):

    def __init__(self):
        self.message_handler = _default_message_handler

    def open(self, server, user, password, logfile):
        self.server = server
        self.user = user
        self.password = password
        self.logfile = logfile

    def close(self):
        pass

    def set_message_handler(self, message_handler):
        self.message_handler = message_handler

    def _message(self, msg_prefix, msg_number, msg_type, msg_text):
        self.message_handler(msg_prefix, msg_number, msg_type, msg_text)

    def auto_open(self, server):
        configfile = os.path.join(os.getenv('HOME'),'.pydsm','pydsm.conf')
        logfile=os.path.join(os.getenv('HOME'),'.pydsm','dsmerror.log')
        config = ConfigParser.RawConfigParser()
        config.read(configfile)
        if server is None:
            server = config.get("main", 'default_server')
        user = config.get(server, 'user')
        password = config.get(server, 'password')
        self.open(server, user, password, logfile)

    def execute(self, command, args=None):
        server = self.server
        user = self.user
        password = self.password
        logfile = self.logfile

        if args is not None:
            command = command % self.literal(args)

        cmd = [ "/usr/bin/dsmadmc", "-servername=%s"%server, "-id=%s"%user, "-password=%s"%password, "-ERRORLOGNAME=%s"%logfile, "-comma",  "-dataonly=yes", command ]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)

        reader = csv.reader(process.stdout,delimiter=",")
        for row in reader:
            is_msg=False
            m = re.match("([A-Z][A-Z][A-Z])(\d\d\d\d)([IESWK]) (.*)$", row[0])
            if m is not None:
                is_msg=True
                self._message(m.group(1), m.group(2), m.group(3), m.group(4) + ",".join(row[1:]))
            if not is_msg:
                yield row

        retcode = process.wait()
        if retcode:
            cmd[3] = "-password=XXXXXXXXXX" #don't put the password on stderr
            cmd_str=" ".join(cmd)
            raise Failed("Command '%s' returned non-zero exit status %d\n" % (cmd_str, retcode))

    def literal(self, o):
        result_array = []
        for v in o:
            v = str(v)
            v = v.replace("'", "\\'")
            result_array.append("'" + v + "'")
        return tuple(result_array)


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
                headers.append({ "name": "untitled", "justify": "left" })

        # for every row in results
        for row_array in results:
            # ensure header for every column
            while len(row_array) > len(headers):
                headers.append({ "name": "untitled", "justify": "left" })

            # for every column
            for col in range(0,len(row_array)):
                # format as required
                f = "string"
                if "format" in headers[col]:
                    f = headers[col]['format']
                if f == "integer":
                    row_array[col] = locale.format(headers[col]['spec'], int(row_array[col]), grouping=True)
                elif f == "float":
                    row_array[col] = locale.format(headers[col]['spec'], float(row_array[col]), grouping=True)

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
                raise RuntimeError("Unknown justification %s"%justify)
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
                    raise RuntimeError("Unknown justification %s"%justify)
                self.output.write("<td align='%s'>" % justify)
                self.output.write(d)
                self.output.write("</td>")
            self.output.write("</tr>\n")
        self.output.write("</table>\n")

    def output_head(self, title):
        self.output.write('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">')
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
                raise RuntimeError("Unknown justification %s"%justify)

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
                raise RuntimeError("Unknown format %s"%f)

        table.set_cols_align(col_align)
        table.set_cols_dtype(col_dtype)
        table.header([ h["name"] for h in headers ])
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
        raise RuntimeError("Unknown format %s"%output_format)

if __name__=="__main__":
    if len(sys.argv) < 1:
      raise RuntimeError("Usage: specify a tivoli command.")

    configfile = os.path.join(os.getenv('HOME'),'.pydsm','pydsm.conf')
    config = ConfigParser.RawConfigParser()
    config.read(configfile)
    server = config.get("main", 'default_server')

    d = dsmadmc()
    d.auto_open(server)

    f = get_formatter(output_format="readable")

    results = d.execute(string.join(sys.argv[1::]))
    f.output_head(string.join(sys.argv[1::]))
    f.output_results(results, [])
    d.close()
    f.output_tail()

