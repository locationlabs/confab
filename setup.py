#!/usr/bin/env python

import os
from setuptools import setup, find_packages

# Workaround for running "setup.py test"
# See: http://bugs.python.org/issue15881
try:
    import multiprocessing  # noqa
except ImportError:
    pass

__version__ = '1.4'

# Jenkins will replace __build__ with a unique value.
__build__ = ''

here = os.path.abspath(os.path.dirname(__file__))

try:
    with open(os.path.join(here, 'README.rst')) as f:
        README = f.read()
    with open(os.path.join(here, 'CHANGES.rst')) as f:
        CHANGES = f.read()
except:
    README = ''
    CHANGES = ''

setup(name='confab',
      version=__version__ + __build__,
      description='Configuration management with Fabric and Jinja2.',
      long_description=README + '\n\n' + CHANGES,
      author='Location Labs',
      author_email='info@locationlabs.com',
      url='http://github.com/locationlabs/confab',
      license='Apache2',
      packages=find_packages(exclude=['*.tests']),
      setup_requires=[
          'nose>=1.0'
      ],
      install_requires=[
          'Fabric>=1.4',
          'Jinja2>=2.4',
          'python-magic',
          'gusset==1.2',
      ],
      tests_require=[
          'mock==1.0.1'
      ],
      test_suite='confab.tests',
      entry_points={
          'console_scripts': [
              'confab = confab.main:main',
              'confab-show = confab.diagnostics:main',
          ]
      },
      )
