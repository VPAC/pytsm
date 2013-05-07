pydsm
=====

python dsm bridge

##Authors
Brian May had the idea and wrote most of it.
Andrew Spiers turned it into a library.

##License
GPL3. Read the file LICENSE

##Installation on Debian Wheezy
Prerequisites:  

* mksh (korn shell)
* The IBM Tivoli client packages. IBM provide rpms only.
* a config file ~/.pydsm/pydsm.conf It should have the following syntax:   


    [main]
    default_server: $DEFAULT_SERVER


    [$DEFAULT_SERVER]  
    user: $USER  
    password: $PASSWORD  


You need to setup Tivoli's dsm.opt and dsm.sys files to point to your Tivoli 
server. These should be installed when you install the IBM Tivoli client packages. If
not, look for dsm.opt.smp and dsm.sys.smp.

