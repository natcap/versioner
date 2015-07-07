"""setup.py module for natcap.invest

InVEST - Integrated Valuation of Ecosystem Services and Tradeoffs

Common functionality provided by setup.py:
    build_sphinx

For other commands, try `python setup.py --help-commands`
"""

import imp

from setuptools import setup

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')
LICENSE = open('LICENSE.txt').read()

def load_version():
    """
    Load the version string.

    If we're in a source tree, load the version from the invest __init__ file.
    If we're in an installed version of invest use the __version__ attribute.
    """
    try:
        import natcap.versioner as versioner
    except ImportError:
        versioner = imp.load_source('natcap.versioner', 'natcap/versioner/__init__.py')
    return versioner.__version__

setup(
    name='natcap.versioner',
    description="Versioning for DVCS for natcap projects",
    long_description=readme + '\n\n' + history,
    maintainer='James Douglass',
    maintainer_email='jdouglass@stanford.edu',
    url='https://bitbucket.org/natcap/versioner',
    namespace_packages=['natcap'],
    packages=[
        'natcap',
        'natcap.versioner',
    ],
    version=load_version(),
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
    ]
)
