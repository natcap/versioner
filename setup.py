"""setup.py module for natcap.invest

InVEST - Integrated Valuation of Ecosystem Services and Tradeoffs

Common functionality provided by setup.py:
    build_sphinx

For other commands, try `python setup.py --help-commands`
"""

import os
import imp

from setuptools.command.sdist import sdist as _sdist
from setuptools import setup

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')
LICENSE = open('LICENSE.txt').read()


class CustomSdist(_sdist):
    """Custom source distribution builder.  Builds a source distribution via the
    distutils sdist command, but then writes the version information to
    the temp source tree before everything is archived for distribution."""
    def make_release_tree(self, base_dir, files):
        _sdist.make_release_tree(self, base_dir, files)

        version = self.distribution.version
        if not version:
            from natcap.versioner import get_version
            version = get_version('natcap.versioner')

        temp_setupfile = os.path.join(base_dir, 'setup.py')
        with open(temp_setupfile, 'a') as setup_fp:
            setup_fp.write('__version__ = version\n')

setup(
    name='natcap.versioner',
    description="Versioning for DVCS for natcap projects",
    long_description=readme + '\n\n' + history,
    maintainer='James Douglass',
    maintainer_email='jdouglass@stanford.edu',
    url='https://bitbucket.org/natcap/versioner',
    namespace_packages=['natcap'],
    install_requires=[
        'pyyaml'
    ],
    packages=[
        'natcap',
        'natcap.versioner',
    ],
    version='0.1.3',
    license=LICENSE,
    zip_safe=True,
    keywords='hg mercurial git versioning natcap',
    classifiers=[
        'Intended Audience :: Developers',
        'Development Status :: 5 - Production/Stable',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2 :: Only',
    ],
    cmdclass={'sdist': CustomSdist}
)
