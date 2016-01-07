import unittest

class GenericVCSTest(unittest.TestCase):
    def test_is_archive(self):
        from natcap.versioner import versioning
        repo = versioning.VCSQuerier('.')
        self.assertFalse(repo.is_archive)

    def test_tag_distance(self):
        from natcap.versioner import versioning
        repo = versioning.VCSQuerier('.')
        with self.assertRaises(NotImplementedError):
            repo.tag_distance

    def test_build_id(self):
        from natcap.versioner import versioning
        repo = versioning.VCSQuerier('.')
        with self.assertRaises(NotImplementedError):
            repo.build_id

    def test_latest_tag(self):
        from natcap.versioner import versioning
        repo = versioning.VCSQuerier('.')
        with self.assertRaises(NotImplementedError):
            repo.latest_tag

    def test_branch(self):
        from natcap.versioner import versioning
        repo = versioning.VCSQuerier('.')
        with self.assertRaises(NotImplementedError):
            repo.branch

    def test_vcs_version_error_raise(self):
        import natcap.versioner
        with self.assertRaises(natcap.versioner.VersionNotFound):
            natcap.versioner.vcs_version(
                '/', on_error=natcap.versioner.ERROR_RAISE)

    def test_vcs_version_error_return(self):
        import natcap.versioner
        # This will return an error string instead of a version, but that's ok
        # because we told it to return via ERROR_RETURN
        natcap.versioner.vcs_version(
            '/', on_error=natcap.versioner.ERROR_RETURN)
