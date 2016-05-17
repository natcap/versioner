Consistent versioning for NatCap Projects
=========================================

This package provides a consistent versioning scheme for projects of the
Natural Capital Project (http://naturalcapitalproject.org).

Versioning Scheme
=================

How a version string is formatted: ::

    If we are at a tag:
        version = {tag}
    else:
        version = {tag}.post{N}+r{nodeid|short}

    If there are no tags:
        {tag} = 'null'


Examples:

 * **Version string** = ``3.4.5``

   * Meaning: This version of this tool was built from the tag ``3.4.5``.

   * You can update to this revision by calling ``hg update -r 3.4.5``

 * **Version string =** ``3.4.5.post35+r788a29c99234``

   * Meaning: This version of this tool was built from a revision where:

     * The latest tag was ``3.4.5``

     * The latest commit on this branch is ``35`` commits beyond the latest tag.

     * The latest commit has a shortened node ID of ``788a29c99234``

   * You can update to this revision by calling ``hg update -r 788a29c99234``



Installation
============

**Via pip:** ``pip install natcap.versioner``

**Via setup.py:** ``python setup.py install``

.. note ::
    If you install ``natcap.versioner`` via pip or via setup.py, dependencies
    should install automatically.


Dependencies
============

To install dependency: ::

     pip install setuptools


Usage In Your Project
=====================

To use this project, you'll need to edit two files: ``setup.py`` and ``__init__.py``.


**In your ``setup.py``**

Adding these lines to your ``setup.py`` allows the DVCS information to be
fetched from ``git`` or ``hg`` and recorded in the package metadata.

::

    from setuptools import setup
    import natcap.versioner

    setup(
        name='example_project',
        ...
        version=natcap.versioner.parse_version()
        natcap_version='example_project/version.py',
    )


**In your package's ``__init__.py``** 

Adding these lines to your package's ``__init__.py`` file will allow the package
version to be fetched from the package metadata.

::

    # Let's assume your package name is still 'example_project'
    import natcap.versioner
    __version__ = natcap.versioner.get_version('example_project')

Support
=======

If something doesn't work, it's probably broken!
Please submit an issue via the issue tracker, send James an email
or stop by if you're in the office and I'll try to fix it!

Tests
=====

To run the suite of tests: ::

    $ python setup.py nosetests

Note that ``hg`` and ``git`` must be available as executables on the command-line.
