import sys
import unittest


class GetVersionTest(unittest.TestCase):
    @staticmethod
    def setup_fake_module(package, module, version_str):
        """Set up mock package structure.

        This method creates the appropriate objects and falsified import logic
        to allow for python's import statements and importlib to be able to
        load the appropriate versioning information.

        For example, if ``package = 'foo'`` and ``module = 'bar'``, there
        will be two new attributes in ``sys.modules``: ``foo`` and
        ``foo.bar``.  ``foo.bar`` will contain a ``version`` attribute that is
        the value of the ``version`` parameter to this method.

        Parameters:
            package (string): The name of the package that will contain the
                version module.
            module (string): The name of the module to which version info
                will be written.
            version_str (string): The version string.

        Returns:
            None.
        """
        class SampleVersionModule(object):
            version = version_str

        full_modname = '.'.join([package, module])

        for name in [package, full_modname]:
            if name in sys.modules:
                raise KeyError(
                    '{mod} already exists in sys.modules'.format(name))

        sys.modules[package] = object()
        sys.modules[full_modname] = SampleVersionModule()

    @staticmethod
    def clean_fake_module(package):
        """Remove all packages from sys.modules that match ``package``.

        ``package`` is assumed to have been set up in ``setup_fake_module()``.

        Parameters:
            package (string): The package name to clean.

        Returns:
            None.
        """
        for modname in list(sys.modules.keys()):
            if modname.startswith(package):
                del sys.modules[modname]

    def test_get_version_from_version_module(self):
        import natcap.versioner

        pkgname = '_foo'
        version = '0.0.1'
        try:
            GetVersionTest.setup_fake_module(pkgname, 'version', version)

            self.assertEqual(
                natcap.versioner.get_version(
                    pkgname, allow_scm=natcap.versioner.SCM_DISALLOW),
                version)
        finally:
            GetVersionTest.clean_fake_module(pkgname)

    def test_get_version_from_nonversion_module(self):
        import natcap.versioner

        pkgname = '_foo'
        version = '0.0.1'
        try:
            GetVersionTest.setup_fake_module(pkgname, 'bar', version)

            self.assertEqual(
                natcap.versioner.get_version(
                    pkgname, ver_module='bar',
                    allow_scm=natcap.versioner.SCM_DISALLOW),
                version)
        finally:
            GetVersionTest.clean_fake_module(pkgname)

    def test_disallowed_scm(self):
        import natcap.versioner
        with self.assertRaises(natcap.versioner.VersionNotFound):
            natcap.versioner.get_version('_foo', root='/')

    def test_pyinstaller_frozen(self):
        import natcap.versioner

        if hasattr(sys, 'frozen'):
            remove_frozen = False
        else:
            remove_frozen = True
            sys.frozen = True

        try:
            with self.assertRaises(natcap.versioner.VersionNotFound):
                natcap.versioner.get_version(
                    '_foo', root='/', allow_scm=natcap.versioner.SCM_ALLOW)
        finally:
            if remove_frozen:
                del sys.frozen
