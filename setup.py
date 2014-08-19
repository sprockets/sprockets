from setuptools import setup
import os

requirements = ['tornado']
tests_require = ['coverage', 'coveralls', 'mock', 'nose']

# Requirements for Python 2.6
(major, minor, rev) = platform.python_version_tuple()
if float('%s.%s' % (major, minor)) < 2.7:
    requirements.append('argparse')
    requirements.append('logutils')
    tests_require.append('unittest2')


setup(name='sprockets',
      version='0.1.0',
      description=('A modular, loosely coupled micro-framework built on top '
                   'of Tornado simplifying the creation of web applications '
                   'and RabbitMQ workers'),
      entry_points={'console_scripts': ['sprockets=sprockets:main']}
      maintainer='Gavin M. Roy',
      maintainer_email='gavinr@aweber.com',
      url='https://github.com/sprockets/sprockets',
      install_requires=requirements,
      license=open('LICENSE').read(),
      package_data={'': ['LICENSE', 'README.md']},
      packages=['sprockets'],
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: No Input/Output (Daemon)',
                   'Framework :: Tornado',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 2.6',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.2',
                   'Programming Language :: Python :: 3.3',
                   'Programming Language :: Python :: 3.4',
                   'Programming Language :: Python :: Implementation :: CPython',
                   'Programming Language :: Python :: Implementation :: PyPy',
                   'Topic :: Internet :: WWW/HTTP',
                   'Topic :: Software Development :: Libraries',
                   'Topic :: Software Development :: Libraries :: Python Modules'],
      test_suite='nose.collector',
      tests_require=tests_require,
      zip_safe=True)
