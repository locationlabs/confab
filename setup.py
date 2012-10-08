#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='confab',
      version='0.2',
      description='Configuration management with Fabric and Jinja2.',
      author='Location Labs',
      author_email='info@locationlabs.com',
      url='http://github.com/locationlabs/confab',
      license='Apache2',
      packages=find_packages(exclude=['*.tests']),
      namespace_packages=[
        'confab'
        ],
      setup_requires=[
        'nose>=1.0'
        ],
      install_requires=[
        'Fabric>=1.4',
        'Jinja2>=2.4',
        'python-magic'
        ],
      test_suite = 'confab.tests',
      entry_points={
        'console_scripts': [
            'confab = confab.main:main',
            ]
        },
      )

