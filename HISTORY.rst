.. :changelog:

0.4.0
=====
* Removing dependency on ``pyyaml``.
* Adding ``__version__`` attribute to ``natcap.versioner``.

0.3.3
=====
* Tests now have full coverage of the package.
* Git repositories without branches are now correctly handled.
* Errors encountered in calls to ``hg`` and ``git`` command-line applications
  will cause ``subprocess.CalledProcessError`` to be raised.

0.3.2
=====
* Setting setuptools ``zip_safe=True``.  After a review of the module, it
  appears that no functionality within ``natcap.versioner`` requires access to
  resources within the package via the filesystem.

0.3.1
=====
* Restoring support for installation as egg (0.3.0 lacked this).
* Minor stylistic changes for PEP8 and PEP257

0.3.0
=====
* Adding support for git.
* Added tests for core versioning functionality.

0.2.4
=====
* Allowing get_version() to allow fallback to SCM only when allowed by user
  input.  Defaults to only allowing fallback in non-frozen environments (e.g. a
  source tree).  ``natcap.versioner.VersionNotFound`` will be raised if the version
  string cannot be loaded normally or SCM is disallowed.
* If a version string cannot be parsed by vcs_version(),
  ``natcap.versioner.VersionNotFound`` will optionally be raised.

0.2.3
=====
* Turning setuptools zip_safe flag to False.  When this and natcap.invest have their zip_safe
  flags all as False, the packages happily install side-by-side as individual eggs.

0.2.2
=====
* Fixes an issue where a development version is returned when the user is at a tag.  The 
  version is now correctly reported as just the tag.

0.2.1
=====
* Version files are now properly imported.  This fixes an issue with users unable to fetch
  version strings from within frozen environments that are outside of a source tree.

0.2.0
=====
* API Change: version is now parsed from setup.py using ``natcap.versioner.parse_version()``.
* Allowing the version to be correctly fetched from PKG-INFO from egg/distribution metadata even when the package has not already been built.

0.1.4
=====
* Attempting to get the utils module to import correctly.

0.1.3
=====
* Allowing version string to be written to a package file.

0.1.2
=====
* Default version scheme is dvcs-based post-release now. but can also do a pre-release.

0.1.1
=====
* Fixes installation issues where certain files needed for setup.py were missing from the source distribution.

0.1.0
=====
* Initial public release.
