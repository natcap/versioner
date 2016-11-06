import unittest


class GenericVCSTest(unittest.TestCase):
    def test_is_archive(self):
        """Versioner: test when a repo is not an archive."""
        from natcap.versioner import versioning
        repo = versioning.VCSQuerier('.')
        self.assertFalse(repo.is_archive)

    def test_tag_distance(self):
        """Versioner: check NotImplementedError on tag_distance."""
        from natcap.versioner import versioning
        repo = versioning.VCSQuerier('.')
        with self.assertRaises(NotImplementedError):
            repo.tag_distance

    def test_build_id(self):
        """Versioner: check NotImplementedError on build_id."""
        from natcap.versioner import versioning
        repo = versioning.VCSQuerier('.')
        with self.assertRaises(NotImplementedError):
            repo.build_id

    def test_latest_tag(self):
        """Versioner: check NotImplementedError on latest_tag."""
        from natcap.versioner import versioning
        repo = versioning.VCSQuerier('.')
        with self.assertRaises(NotImplementedError):
            repo.latest_tag

    def test_branch(self):
        """Versioner: check NotImplementedError on branch."""
        from natcap.versioner import versioning
        repo = versioning.VCSQuerier('.')
        with self.assertRaises(NotImplementedError):
            repo.branch

    def test_vcs_version_error_raise(self):
        """Versioner: check error raised as expected when requested."""
        import natcap.versioner
        with self.assertRaises(natcap.versioner.VersionNotFound):
            natcap.versioner.vcs_version(
                '/', on_error=natcap.versioner.ERROR_RAISE)

    def test_vcs_version_error_return(self):
        """Versioner: check error returned as expected when requested."""
        import natcap.versioner
        # This will return an error string instead of a version, but that's ok
        # because we told it to return via ERROR_RETURN
        error_string = natcap.versioner.vcs_version(
            '/', on_error=natcap.versioner.ERROR_RETURN)
        self.assertTrue(len(error_string) != 0)

    def test_node_version_error_raise(self):
        """Versioner: check NotImplementedError on node."""
        from natcap.versioner import versioning
        repo = versioning.VCSQuerier('.')
        with self.assertRaises(NotImplementedError):
            repo.node
