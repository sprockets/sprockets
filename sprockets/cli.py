"""
Sprockets CLI
=============
The sprockets CLI interface for running applications. Applications are meant
to be run by a controller that is managed by the sprockets CLI interface.

The sprockets CLI interface loads controller applications that are registered
using setuptools entry points.

Each controller is expected to expose at least a `main(application, args)`
method that would be invoked when starting the application. Additional, a
controller can implement a `add_cli_arguments(parser)` method that will be
invoked when setting up the command line parameters. This allows controllers
to inject configuration directives into the cli.

Applications can be a python package or module and if they are registered
to a specific controller, can be referenced by an alias.

"""
import argparse
import importlib
import logging
import string
import sys

# import logutils for Python 2.6 or logging.config for later versions
sys_version = sys.version_info
if (sys_version.major, sys_version.minor) < (2, 7):
    import logutils.dictconfig as logging_config
else:
    from logging import config as logging_config

import pkg_resources

from sprockets import __version__

DESCRIPTION = 'Available sprockets application controllers'

# Logging formatters
SYSLOG_FORMAT = ('%(levelname)s <PID %(process)d:%(processName)s> '
                 '%(name)s.%(funcName)s(): %(message)s')

VERBOSE_FORMAT = ('%(levelname) -10s %(asctime)s %(process)-6d '
                  '%(processName) -20s %(name) -20s '
                  '%(funcName) -20s L%(lineno)-6d: %(message)s')

# Base logging configuration
LOGGING = {'disable_existing_loggers': True,
           'filters': {},
           'formatters': {'syslog': {'format': SYSLOG_FORMAT},
                          'verbose': {'datefmt': '%Y-%m-%d %H:%M:%S',
                                      'format': VERBOSE_FORMAT}},
           'handlers': {'console': {'class': 'logging.StreamHandler',
                                    'formatter': 'verbose'},
                        'syslog': {'class': 'logging.handlers.SysLogHandler',
                                   'formatter': 'syslog'}},
           'incremental': False,
           'loggers': {'sprockets': {'handlers': ['console'],
                                     'level': logging.WARNING,
                                     'propagate': True}},
           'root': {'handlers': [],
                    'level': logging.CRITICAL,
                    'propagate': True},
           'version': 1}

LOGGER = logging.getLogger(__name__)


class CLI(object):
    """The core Sprockets CLI application providing argument parsing and
    logic for starting a controller.

    The package or module for an application is passed into

    """

    CONTROLLERS = 'sprockets.controller'

    def __init__(self):
        self._controllers = self._get_controllers()
        self._arg_parser = argparse.ArgumentParser()
        self._add_cli_args()
        self._args = self._arg_parser.parse_args()

    def run(self):
        """Evaluate the command line arguments, performing the appropriate
        actions so the application can be started.

        """
        # The list command prevents any other processing of args
        if self._args.list:
            self._print_installed_apps(self._args.controller)
            sys.exit(0)

        # If app is not specified at this point, raise an error
        if not self._args.application:
            sys.stderr.write('\nerror: application not specified\n\n')
            self._arg_parser.print_help()
            sys.exit(-1)

        # If it's a registered app reference by name, get the module name
        app_module = self._get_application_module(self._args.controller,
                                                  self._args.application)

        # Configure logging based upon the flags
        self._configure_logging(app_module,
                                self._args.verbose,
                                self._args.syslog)

        # Try and run the controller
        try:
            self._controllers[self._args.controller].main(app_module,
                                                          self._args)
        except TypeError as error:
            sys.stderr.write('error: could not start the %s controller for %s'
                             ': %s\n\n' % (self._args.controller,
                                           app_module,
                                           str(error)))
            sys.exit(-1)

    def _add_cli_args(self):
        """Add the cli arguments to the argument parser."""

        # Optional cli arguments
        self._arg_parser.add_argument('-l', '--list',
                                      action='store_true',
                                      help='List installed sprockets apps')

        self._arg_parser.add_argument('-s', '--syslog',
                                      action='store_true',
                                      help='Log to syslog')

        self._arg_parser.add_argument('-v', '--verbose',
                                      action='count',
                                      help=('Verbose logging output, use -vv '
                                            'for DEBUG level logging'))

        self._arg_parser.add_argument('--version',
                                      action='version',
                                      version='sprockets v%s ' % __version__)

        # Controller sub-parser
        subparsers = self._arg_parser.add_subparsers(dest='controller',
                                                          help=DESCRIPTION)

        # Iterate through the controllers and add their cli arguments
        for key in self._controllers:
            help_text = self._get_controller_help(key)
            sub_parser = subparsers.add_parser(key, help=help_text)
            try:
                self._controllers[key].add_cli_arguments(sub_parser)
            except AttributeError:
                LOGGER.debug('%s missing add_cli_arguments()', key)

        # The application argument
        self._arg_parser.add_argument('application',
                                      action="store",
                                      help='The sprockets app to run')

    @staticmethod
    def _configure_logging(application, verbosity=0, syslog=False):
        """Configure logging for the application, setting the appropriate
        verbosity and adding syslog if it's enabled.

        :param str application: The application module/package name
        :param int verbosity: 1 == INFO, 2 == DEBUG
        :param bool syslog: Enable the syslog handler

        """
        # Create a new copy of the logging config that will be modified
        config = dict(LOGGING)

        # Increase the logging verbosity
        if verbosity == 1:
            config['loggers']['sprockets']['level'] = logging.INFO
        elif verbosity == 2:
            config['loggers']['sprockets']['level'] = logging.DEBUG

        # Add syslog if it's enabled
        if syslog:
            config['loggers']['sprockets']['handlers'].append('syslog')

        # Copy the sprockets logger to the application
        config['loggers'][application] = dict(config['loggers']['sprockets'])

        # Configure logging
        logging_config.dictConfig(config)

    def _get_application_module(self, controller, application):
        """Return the module for an application. If it's a entry-point
        registered application name, return the module name from the entry
        points data. If not, the passed in application name is returned.

        :param str controller: The controller type
        :param str application: The application name or module
        :rtype: str

        """
        for pkg in self._get_applications(controller):
            if pkg.name == application:
                return pkg.module_name
        return application

    @staticmethod
    def _get_applications(controller):
        """Return a list of application names for the given controller type
        that have registered themselves as sprockets applications.

        :param str controller: The type of controller for the applications
        :rtype: list

        """
        group_name = 'sprockets.%s.app' % controller
        return pkg_resources.iter_entry_points(group=group_name)

    @staticmethod
    def _get_argument_parser():
        """Return an instance of the argument parser.

        :return: argparse.ArgumentParser

        """
        return argparse.ArgumentParser()

    def _get_controllers(self):
        """Iterate through the installed controller entry points and import
        the module and assign the handle to the CLI._controllers dict.

        :return: dict

        """
        controllers = dict()
        for pkg in pkg_resources.iter_entry_points(group=self.CONTROLLERS):
            LOGGER.debug('Loading %s controller', pkg.name)
            controllers[pkg.name] = importlib.import_module(pkg.module_name)
        return controllers

    def _get_controller_help(self, controller):
        """Return the value of the HELP attribute for a controller that should
        describe the functionality of the controller.

        :rtype: str|None

        """
        if hasattr(self._controllers[controller], 'HELP'):
            return self._controllers[controller].HELP
        return None

    def _print_installed_apps(self, controller):
        """Print out a list of installed sprockets applications

        :param str controller: The name of the controller to get apps for
        """
        print('\nInstalled Sprockets %s Apps\n' % controller.upper())
        print("{0:<25} {1:>25}".format('Name', 'Module'))
        print(string.ljust('', 51, '-'))
        for app in self._get_applications(controller):
            print('{0:<25} {1:>25}'.format(app.name, '(%s)' % app.module_name))
        print('')


def main():
    """Main application runner"""
    cli = CLI()
    cli.run()
