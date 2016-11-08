from setuptools import setup

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='natcap.versioner',
    description="PEP440-compliant Git and hg versioning",
    long_description=readme + '\n\n' + history,
    maintainer='James Douglass',
    maintainer_email='jdouglass@stanford.edu',
    url='https://bitbucket.org/jdouglass/versioner',
    namespace_packages=['natcap'],
    packages=[
        'natcap',
        'natcap.versioner',
    ],
    natcap_version='natcap/versioner/version.py',
    license='BSD',
    entry_points="""
        [distutils.setup_keywords]
        natcap_version = natcap.versioner.utils:distutils_keyword
    """,
    zip_safe=True,
    keywords='hg mercurial git versioning natcap',
    test_suite='nose.collector',
    install_requires=['six'],
    classifiers=[
        'Intended Audience :: Developers',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Version Control',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: BSD License',
    ]
)
