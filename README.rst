pytsm
=====

Contains python TSM bindings.

Authors
-------
Brian May
Andrew Spiers

License
-------
GPL3. Read the file LICENSE

Installation
------------
Prerequisites:

* The IBM Tivoli client packages. IBM provide rpms only. For Debian packages,
  see https://github.com/VPAC/tivsm/
* You need to setup Tivoli's dsm.opt and dsm.sys files to point to your Tivoli
  server. These should be installed when you install the IBM Tivoli client
  packages. If not, look for dsm.opt.smp and dsm.sys.smp.
* a config file ``~/.pydsm/pydsm.conf`` It should have the following syntax::

    [main]
    default_server: $DEFAULT_SERVER


    [$DEFAULT_SERVER]
    user: $USER
    password: $PASSWORD

Status
------
The API is not final and subject to change and break without notice.
