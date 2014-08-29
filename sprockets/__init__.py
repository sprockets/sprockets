"""
Sprockets
=========
A loosely coupled framework built on top of Tornado. Take what you need to
build awesome applications.

"""
version_info = (0, 1, 1)
__version__ = '.'.join(str(v) for v in version_info)

import logging

__import__('pkg_resources').declare_namespace(__name__)

# Ensure there is a NullHandler for logging
try:
    from logging import NullHandler
except ImportError:
    # Not available in Python 2.6
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass
