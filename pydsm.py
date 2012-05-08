#!/usr/bin/python

import ConfigParser
import subprocess
import select
import sys
import os
import string

debug = True


def runcommand(user,password,*arguments):
  """
  Accept 3 or more strings, the first two being username and password, the others being arguments to pass to dsmadmc.
  """
  output = []
  cmd = [ "/usr/bin/dsmadmc", "-id=%s"%user, "-password=%s"%password, "-comma",  string.join(arguments) ]
  process = subprocess.Popen(cmd, stdout=subprocess.PIPE)

  state="prefix"
  for line in process.stdout:
      if debug: print "%s[[%s]]"%(state,line.rstrip())

      if state=="prefix":
          # ANS8000I Server command: 'query mount'
          if line[0:9] == "ANS8000I ":
              state="content"
      elif state=="content":
          # ANR2034E QUERY MOUNT: No match found using this criteria.
          if line[0:9] == "ANR2034E ":
              pass
          elif line == "\n":
              state="blankline"
          else:
              #sys.stdout.write(line)
              output.append(line)
      elif state=="blankline":
          # ANS8002I Highest return code was 0.
          if line[0:9] == "ANS8002I ":
              state="postfix"
          else:
              #sys.stdout.write("\n")
              output.append(line)
              state="content"
      elif state=="postfix":
          pass
      else:
          raise RuntimeError('Unknown state %s'%state)

  retcode = process.wait()
  if retcode:
      sys.stderr.write("Command '%s' returned non-zero exit status %d\n" % (" ".join(cmd), retcode))
      sys.exit(retcode)
  return output


if __name__=="__main__":
  config = ConfigParser.RawConfigParser()
  config.read('/root/pydsm/pydsm.conf')

  user = config.get('main', 'user')
  password = config.get('main', 'password')

  if len(sys.argv) <= 1:
    raise RuntimeError("Not enough parameters")
  else:
    lines = runcommand(user,password,string.join(sys.argv[1::]))
    for i in lines:
      sys.stdout.write(i)
    sys.exit(0)

