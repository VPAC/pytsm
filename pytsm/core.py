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

import ConfigParser
import subprocess
import sys
import os
import re
import csv


def _default_message_handler(msg_prefix, msg_number, msg_type, msg_text):
    sys.stderr.write("%s%s%s %s\n" %
                     (msg_prefix, msg_number, msg_type, msg_text))


class Failed(Exception):
    pass

blacklist_msg_numbers = {
    '2034',  # ANR2034E SELECT: No match found using this criteria.
    '8001',  # ANS8001I Return code 11
}


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
        configfile = os.path.join(os.getenv('HOME'), '.pytsm', 'pytsm.conf')
        logfile = os.path.join(os.getenv('HOME'), '.pytsm', 'dsmerror.log')
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

        cmd = [
            "/usr/bin/dsmadmc",
            "-servername=%s" % server,
            "-id=%s" % user,
            "-password=%s" % password,
            "-ERRORLOGNAME=%s" % logfile,
            "-comma",  "-dataonly=yes", command]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)

        reader = csv.reader(process.stdout, delimiter=str(","))
        for row in reader:
            m = re.match("([A-Z][A-Z][A-Z])(\d\d\d\d)([IESWK]) (.*)$", row[0])
            if m is not None:
                if m.group(2) not in blacklist_msg_numbers:
                    self._message(
                        m.group(1), m.group(2), m.group(3),
                        m.group(4) + ",".join(row[1:]))
            else:
                yield row

        retcode = process.wait()
        if retcode and retcode != 11:
            cmd[3] = "-password=XXXXXXXXXX"  # don't put the password on stderr
            cmd_str = " ".join(cmd)
            raise Failed(
                "Command '%s' returned non-zero exit status %d\n"
                % (cmd_str, retcode))

    def literal(self, o):
        result_array = []
        for v in o:
            v = str(v)
            v = v.replace("'", "\\'")
            result_array.append("'" + v + "'")
        return tuple(result_array)
