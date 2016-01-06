import unittest

class VCSQuerierTest(unittest.TestCase):
    def test_is_archive(self):
        from natcap.versioner import versioning
        repo = versioning.VCSQuerier('.')
        with self.assertRaises(NotImplementedError):
            repo.is_archive

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
