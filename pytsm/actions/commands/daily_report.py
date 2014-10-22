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
from __future__ import print_function

import datetime
import pytsm
import re
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import sys
import subprocess
import email.mime.text
import email.mime.multipart

from ..base import BaseCommand


class dual_writer(object):

    def __init__(self):
        self.plain_string = StringIO()
        self.plain = pytsm.get_formatter('readable', output=self.plain_string)
        self.html_string = StringIO()
        self.html = pytsm.get_formatter('html', output=self.html_string)

    def output_head(self, title):
        self.plain.output_head(title)
        self.html.output_head(title)

    def output_tail(self):
        self.plain.output_tail()
        self.html.output_tail()

    def output_header(self, line):
        self.plain.output_header(line)
        self.html.output_header(line)

    def output_text(self, line):
        self.plain.output_text(line)
        self.html.output_text(line)

    def output_results(self, results, headers):
        results = list(results)
        self.plain.output_results(results, headers)
        self.html.output_results(results, headers)

    def close(self):
        self.plain_string.close()
        self.html_string.close()


class Command(BaseCommand):
    help = "List all supported commands."

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)

        parser.add_argument('--server', dest="server",
                            help='TSM server to connect to')
        parser.add_argument('--date', dest="date",
                            help='Date of report')
        parser.add_argument('--start', dest="start_time", required=True,
                            help='Start time of report')
        parser.add_argument('--stop', dest="stop_time",
                            help='Stop time of report')
        parser.add_argument('--sender', dest="sender", required=True,
                            help='Sender email address')
        parser.add_argument('--email', dest="email", required=True,
                            help='Destination email address')
        parser.add_argument("--debug",
                            help="write email to stdout instead of sending it",
                            action="store_true")

    def handle(self, args):
        class dummy(object):
            pass
        errors = dummy()
        errors.events = False
        errors.actlog = False

        today = datetime.datetime.now().date()
        yesterday = today - datetime.timedelta(1)

        (hh, mm) = args.start_time.split(":")
        start_time = datetime.time(int(hh), int(mm))

        if args.stop_time is None:
            stop_time = start_time
        else:
            (hh, mm) = args.stop_time.split(":")
            stop_time = datetime.time(int(hh), int(mm))

        if args.date is None:
            start = datetime.datetime.combine(yesterday, start_time)
        else:
            dt = datetime.datetime.strptime(args.date, "%Y-%m-%d").date()
            start = datetime.datetime.combine(dt, start_time)
        stop = datetime.datetime.combine(
            start + datetime.timedelta(days=1), stop_time)

        f = dual_writer()

        def message_handler(msg_prefix, msg_number, msg_type, msg_text):
            f.output_text(
                "%s%s%s %s" % (msg_prefix, msg_number, msg_type, msg_text))

        d = pytsm.dsmadmc()
        d.set_message_handler(message_handler)
        d.auto_open(args.server)

        f.output_head("TSM summary from %s to %s" % (start, stop))

        # ---------------  EVENTS -------------------

        f.output_header("events")

        results = d.execute(
            """select
            date(SCHEDULED_START),
            time(SCHEDULED_START),
            time(ACTUAL_START),
            time(COMPLETED),
            DOMAIN_NAME,
            SCHEDULE_NAME,
            NODE_NAME,
            STATUS,
            RESULT
        from events
        where SCHEDULED_START >= %s and SCHEDULED_START < %s
        order by SCHEDULED_START
        """, (start, stop))

        headers = [
            {"name": "Date", },
            {"name": "Scheduled", },
            {"name": "Start", },
            {"name": "Completed", },
            {"name": "Domain", },
            {"name": "Schedule", },
            {"name": "Node", },
            {"name": "Status"},
            {"name": "Result"},
        ]

        def check_events(results):
            for r in results:
                if r[7] != "Completed":
                    errors.events = True
                if r[8] == "0" or r[8] == "":
                    r[8] = "OK"
                elif r[8] == "4":
                    r[8] = "Missed Files"
                elif r[8] == "8":
                    r[8] = "Warnings"
                elif r[8] == "12":
                    r[8] = "Errors"
                else:
                    r[8] = "Failed (%s)" % r[8]
                yield r

        try:
            f.output_results(check_events(results), headers)
        except pytsm.Failed:
            f.output_text("Errors getting results.")

        # ---------------  SUMMARY -------------------

        for activity in [
                'BACKUP', 'RESTORE', 'ARCHIVE', 'RETRIEVE', 'STGPOOL BACKUP',
                'FULL_DBBACKUP', 'MIGRATION', 'RECLAMATION', 'MOVE DATA']:
            f.output_header("summary %s" % activity)

            results = d.execute(
                """select
    entity as "Node",
    activity as "Activity",
    date(start_time) as "Start Date",
    time(start_time) as "Start Time",
    date(end_time) as "End Date",
    time(end_time) as "End Time",
    TIMESTAMPDIFF(2,CHAR(end_time-start_time))/60.0 as "Min",
    bytes/1024/1024 as "Total_MiB",
    case
        when TIMESTAMPDIFF(2,CHAR(end_time-start_time)) >0
        then bytes/TIMESTAMPDIFF(2,CHAR(end_time-start_time))/1024.0/1024.0
        else 0
        end as "MiB/Sec",
    case
        when examined >0
        then affected/examined*100
        else 0
        end as "Volatility_%%"
from summary
where START_TIME >= %s and START_TIME < %s and activity=%s
order by START_TIME
""", (start, stop, activity))

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

            try:
                f.output_results(results, headers)
            except pytsm.Failed:
                f.output_text("Errors getting results.")

        # ---------------  ACTLOG -------------------

        f.output_header("actlog")

        results = d.execute(
            """select
    date(DATE_TIME),
    time(DATE_TIME),
    NODENAME,
    MESSAGE
from actlog
where DATE_TIME >= %s and DATE_TIME < %s
    and ( SEVERITY='E' or SEVERITY='S' )
    and (MSGNO!=2034 and MSGNO!=1701 and MSGNO!=944)
order by DATE_TIME
""", (start, stop))

        headers = [
            {"name": "Date", },
            {"name": "Time", },
            {"name": "Node", },
            {"name": "Message", },
        ]

        try:
            for r in results:
                errors.actlog = True
                m = re.match(
                    "(ANE4018E Error processing) "
                    "'(/nfs/user[12]/[a-z0-9]+/[^/]+/).*(/[^/]+/[^/]*)': "
                    "(file name too long \(SESSION: [0-9]+\))", r[3])
                if m is not None:
                    r[3] = "%s '%s...%s': %s" % (
                        m.group(1), m.group(2), m.group(3), m.group(4))
                f.output_text(
                    "%s, %s, %s, %s" %
                    (r[0], r[1], r[2], r[3]))
        except pytsm.Failed:
            f.output_text("Errors getting results.")

        # ---------------  USAGE -------------------

        if args.date is None:
            f.output_header("usage")

            results = d.execute(
                "SELECT node_name, sum(logical_mb), sum(physical_mb), "
                "sum(physical_mb)-sum(logical_mb) "
                "FROM occupancy "
                "GROUP BY node_name")

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

        # ---------------  ERRORS -------------------
        f.output_header("errors")

        needs_attention = False

        if errors.events:
            f.output_text("Errors in events")
            needs_attention = True

        if errors.actlog:
            f.output_text("Errors in activity log")

        d.close()
        f.output_tail()

        # ---------------  Send E-MAIL -------------------
        if args.debug:
            sys.stdout.write(f.plain_string.getvalue())
            sys.stdout.write(f.html_string.getvalue())
            f.close()
        else:
            msg = email.mime.multipart.MIMEMultipart('alternative')
            msg.attach(email.mime.text.MIMEText(
                f.plain_string.getvalue(), "plain", _charset="utf8"))
            msg.attach(email.mime.text.MIMEText(
                f.html_string.getvalue(), "html", _charset="utf8"))
            f.close()

            subject = "TSM Operational Report - TSM, Daily Report"
            if needs_attention:
                subject += " - Needs Attention"
            else:
                subject += " -  Running Smoothly"
            msg['Subject'] = subject

            msg['From'] = args.sender
            msg['To'] = args.email

            p = subprocess.Popen(
                ["/usr/sbin/sendmail", "-t"], stdin=subprocess.PIPE)
            p.communicate(msg.as_string())
