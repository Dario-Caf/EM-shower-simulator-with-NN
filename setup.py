from setuptools import setup, find_packages

from EM_shower_simulator.__version__ import *

_LICENSE = 'GNU General Public License v3'
_PACKAGES = find_packages(exclude='Tests')
_CLASSIFIERS = [
    'License :: OSI Approved :: '
    'GNU General Public License v3',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: C++',
    'Intended Audience :: Science/Research',
    'Topic :: Scientific computation',
    'Development Status :: Beta']
_SCRIPTS = []

with open('requirements.txt', 'r') as f:
    _DEPENDENCIES = f.read().splitlines()

_KWARGS = dict(name=PACKAGE_NAME,
               version=TAG,
               author=AUTHOR,
               description=DESCRIPTION,
               license=_LICENSE,
               packages=_PACKAGES,
               include_package_data=True,
               url=URL,
               classifiers=_CLASSIFIERS,
               scripts=_SCRIPTS,
               install_requires=_DEPENDENCIES)


setup(**_KWARGS)
