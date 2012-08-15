#!/usr/bin/python

import ConfigParser
import subprocess
import select
import sys
import os
import string
import re
import csv
import locale


class Message(object):
    def __init__(self, msg_prefix, msg_number, msg_type, msg_text):
        self.msg_prefix = msg_prefix
        self.msg_number = msg_number
        self.msg_type = msg_type
        self.msg_text = msg_text

    def __str__(self):
        return "%s%s%s %s"%(self.msg_prefix, self.msg_number, self.msg_type, self.msg_text)

class Failed(Exception):
    pass

class dsmadmc(object):

    def open(self, server, user, password, logfile):
        self.server = server
        self.user = user
        self.password = password
        self.logfile = logfile

    def close(self):
        pass

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

        output = []
        cmd = [ "/usr/bin/dsmadmc", "-servername=%s"%server, "-id=%s"%user, "-password=%s"%password, "-ERRORLOGNAME=%s"%logfile, "-comma",  "-dataonly=yes", command ]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)

        reader = csv.reader(process.stdout,delimiter=",")
        for row in reader:
            iserror=False
            m = re.match("([A-Z][A-Z][A-Z])(\d\d\d\d)([IESWK]) (.*)$", row[0])
            if m is not None:
                iserror=True
                yield Message(m.group(1), m.group(2), m.group(3), m.group(4) + ",".join(row[1:]))
            if not iserror:
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


def output_results_csv(results, headers):
    writer = csv.writer(sys.stdout, delimiter=',')
    writer.writerow([h['name'] for h in headers])
    for i in results:
        if isinstance(i, Message):
            sys.stderr.write("Message: %s\n"%i)
        else:
            writer.writerow(i)

def output_results_readable(results, headers):
    locale.setlocale(locale.LC_ALL, '')

    # retrieve data
    data = []
    for i in results:
        if isinstance(i, Message):
            sys.stderr.write("Message: %s\n"%i)
        else:
            data.append(i)

    # ensure header for every column
    for row_array in data:
        while len(row_array) > len(headers):
            headers.append({ "name": "untitled", "justify": "left" })

    # caculate width's of headers
    col_width = [ len(h["name"]) for h in headers ]

    # for every row in data
    for row_array in data:
        # ensure header for every column
        while len(row_array) > len(headers):
            headers.append({ "name": "untitled", "justify": "left" })

        # for every column
        for col in range(0,len(row_array)):
            # format as required
            f = "string"
            if "format" in headers[col]:
                f = headers[col]['format']
            if f == "string":
                pass
            elif f == "integer":
                row_array[col] = locale.format(headers[col]['spec'], int(row_array[col]), grouping=True)
            elif f == "float":
                row_array[col] = locale.format(headers[col]['spec'], float(row_array[col]), grouping=True)
            else:
                raise RuntimeError("Unknown format %s"%f)

            # calculate max col width
            if col >= len(col_width):
                col_width.append(0)
            col_width[col] = max(len(row_array[col]), col_width[col])

    # output table headers
    sep = ""
    for col in range(0,len(headers)):
        sys.stdout.write(sep)
        sep = "  "
        sys.stdout.write(headers[col]['name'].ljust(col_width[col]))
    sys.stdout.write("\n")
    sep = ""
    for col in range(0,len(headers)):
        sys.stdout.write(sep)
        sep = "  "
        sys.stdout.write("-"*col_width[col])
    sys.stdout.write("\n")

    # output table body
    for row_array in data:
        sep = ""
        for col in range(0,len(row_array)):
            sys.stdout.write(sep)
            sep = "  "
            justify = "left"
            if 'justify' in headers[col]:
                justify = headers[col]['justify']
            if justify == "left":
                sys.stdout.write(row_array[col].ljust(col_width[col]))
            elif justify == "right":
                sys.stdout.write(row_array[col].rjust(col_width[col]))
            else:
                raise RuntimeError("Unknown justification %s"%justify)
        sys.stdout.write("\n")

def output_results(results, headers, output_format):
    if output_format == "csv":
        output_results_csv(results, headers)
    elif output_format == "readable":
        output_results_readable(results, headers)
    else:
        raise RuntimeError("Unknown format %s"%output_format)

if __name__=="__main__":
    if len(sys.argv) <= 2:
        raise RuntimeError("Not enough parameters")

    d = dsmadmc()
    d.auto_open(sys.argv[1])

    results = d.execute(string.join(sys.argv[2::]))
    output_results(results, [], "readable")
    d.close()

