# ----------------------------------------------------------------------------
# Copyright (c) 2016--, taxster development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------

from setuptools import setup, find_packages

from taxster import __version__

setup(
    name="taxster",
    version=__version__,
    packages=find_packages(),
    install_requires=['pandas'],
    author="Greg Caporaso",
    author_email="gregcaporaso@gmail.com",
    description="Functionality for working with taxonomy data.",
    license="BSD",
    keywords="microbiome taxonomy",
    url="http://www.qiime.org",
)
