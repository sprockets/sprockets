"""
Sprockets
=========
A loosely coupled framework built on top of Tornado. Take what you need to
build awesome applications.

"""
version_info = (0, 0, 0)
__version__ = '.'.join(str(v) for v in version_info)

import logging

# Ensure there is a NullHandler for logging
try:
    from logging import NullHandler
except ImportError:
    # Not available in Python 2.6
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass
