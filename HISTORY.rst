.. :changelog:

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
