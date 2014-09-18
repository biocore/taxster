#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------
# Copyright (c) 2014, The Taxster Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------

import os
from setuptools import setup
from setuptools.extension import Extension
from glob import glob

try:
    import numpy as np
except ImportError:
    raise ImportError("numpy must be installed prior to installing taxster")

# Hack to prevent stupid "TypeError: 'NoneType' object is not callable" error
# in multiprocessing/util.py _exit_function when running `python
# setup.py test` (see
# http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html),
# borrowed from https://github.com/getsentry/sentry/blob/master/setup.py
for m in ('multiprocessing', 'logging'):
    try:
        __import__(m)
    except ImportError:
        pass

__author__ = "Austin Richardson, Greg Caporaso and Daniel McDonald"
__copyright__ = "Copyright 2014, The Taxster Development Team"
__credits__ = ["Austin Richarson", "Greg Caporaso", "Daniel McDonald"]
__license__ = "BSD"
__version__ = "0.0.1"
__maintainer__ = "Daniel McDonald"
__email__ = "mcdonadt@colorado.edu"

long_description = """Assigning taxons you've never heard of"""

classes = """
    Development Status :: 4 - Beta
    License :: OSI Approved :: BSD License
    Topic :: Scientific/Engineering :: Bio-Informatics
    Topic :: Software Development :: Libraries :: Python Modules
    Programming Language :: Python
    Programming Language :: Python :: 2.7
    Programming Language :: Python :: Implementation :: CPython
    Operating System :: OS Independent
    Operating System :: POSIX :: Linux
    Operating System :: MacOS :: MacOS X
"""
classifiers = [s.strip() for s in classes.split('\n') if s]


setup(name='taxster',
      version=__version__,
      description='taxster',
      long_description=long_description,
      license=__license__,
      author=__maintainer__,
      author_email=__email__,
      maintainer=__maintainer__,
      maintainer_email=__email__,
      url='',
      test_suite='nose.collector',
      packages=['taxster'],
      include_dirs=[np.get_include()],
      scripts=glob('scripts/*'),
      install_requires=["numpy >= 1.8.2",
                        "future",
                        "scipy >= 0.14.0",
                        "scikit-learn == 0.15.1",
                        "scikit-bio == 0.2.0"],
      extras_require={'test': ["nose >= 0.10.1", "pep8", "flake8"],
                      'doc': ["Sphinx >= 1.2.2"]},
      classifiers=classifiers
      )
