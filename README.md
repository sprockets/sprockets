Sprockets
=========
A loosely coupled framework built on top of Tornado. Take what you need to build
awesome applications.

CLI Usage
---------

    usage: sprockets [-h] [-l] [-d] [-s] [-v] [--version]
                     {http,amqp} ... application
    
    positional arguments:
      {http,amqp}      Available sprockets application controllers
        http           HTTP Application Controller
        amqp           RabbitMQ Worker Controller
      application      The sprockets app to run
    
    optional arguments:
      -h, --help       show this help message and exit
      -l, --list       List installed sprockets apps
      -d, --daemonize  Fork into a background process
      -s, --syslog     Log to syslog
      -v, --verbose    Verbose logging output
      --version        show program's version number and exit
