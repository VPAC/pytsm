#!/usr/bin/python

import ConfigParser
import subprocess
import select
import sys
import os
import string

debug = False


def runcommand(user,password,logfile,*arguments):
  """
Accept 4 or more strings, the first two being username and password, the third
being a writeable file that dsmadmc can log errors to, and the others being
arguments to pass to dsmadmc.
  """
  output = []
  cmd = [ "/usr/bin/dsmadmc", "-id=%s"%user, "-password=%s"%password, "-ERRORLOGNAME=%s"%logfile, "-comma",  string.join(arguments) ]
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
#      sys.exit(retcode)
  return output,retcode


if __name__=="__main__":
  configfile=os.path.join(os.getenv('HOME'),'pydsm','pydsm.conf')
  logfile=os.path.join(os.getenv('HOME'),'pydsm','dsmerror.log')
  config = ConfigParser.RawConfigParser()
  config.read(configfile)

  user = config.get('main', 'user')
  password = config.get('main', 'password')

  if len(sys.argv) <= 1:
    raise RuntimeError("Not enough parameters")
  else:
    dsmresponse = runcommand(user,password,logfile,string.join(sys.argv[1::]))
    for i in dsmresponse[0]:
      sys.stdout.write(i)
    sys.exit(dsmresponse[1])

