from setuptools import setup

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')
LICENSE = open('LICENSE.txt').read()

setup(
    name='natcap.versioner',
    description="Git and hg versioning for natcap projects",
    long_description=readme + '\n\n' + history,
    maintainer='James Douglass',
    maintainer_email='jdouglass@stanford.edu',
    url='https://bitbucket.org/jdouglass/versioner',
    namespace_packages=['natcap'],
    install_requires=[
        'pyyaml'
    ],
    packages=[
        'natcap',
        'natcap.versioner',
    ],
    version='0.4.0',
    license=LICENSE,
    entry_points="""
        [distutils.setup_keywords]
        natcap_version = natcap.versioner.utils:distutils_keyword
    """,
    zip_safe=True,
    keywords='hg mercurial git versioning natcap',
    test_suite='nose.collector',
    classifiers=[
        'Intended Audience :: Developers',
        'Development Status :: 2 - Pre-Alpha',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2 :: Only',
    ]
)
