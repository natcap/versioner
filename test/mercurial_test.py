import unittest
import shutil
import subprocess
import tempfile
import os

class MercurialTest(unittest.TestCase):
    def setUp(self):
        self.repo_uri = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.repo_uri)

    def _set_up_sample_repo(self):
        """Create a sample repo with four commits and a tag.

        Returns:
            None"""
        from natcap.versioner import versioning

        def call_hg(command):
            # The subprocess docs warn that using subprocess.PIPE may result in
            # deadlock when used with subprocess.call, but it seems to work ok
            # so far!
            subprocess.call(
                command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, shell=True)

        call_hg('hg init {tempdir}'.format(
            tempdir=self.repo_uri))

        filepath = os.path.join(self.repo_uri, 'scratchfile')
        open(filepath, 'w')
        call_hg('hg add {0} -R {1}'.format(filepath, self.repo_uri))
        call_hg(('hg commit -m "initial commit" -R {0}').format(
            filepath, self.repo_uri))

        open(filepath, 'a').write('foo\n')
        call_hg(('hg commit -m "adding foo" -R {0}').format(self.repo_uri))

        open(filepath, 'a').write('bar\n')
        call_hg(('hg commit -m "adding bar" -R {0}').format(self.repo_uri))

        open(filepath, 'a').write('baz\n')
        call_hg(('hg commit -m "adding baz" -R {0}').format(self.repo_uri))

        call_hg(('hg tag 0.1 -R {tempdir}').format(tempdir=self.repo_uri))

        return versioning.HgRepo(self.repo_uri)

    def test_tag_distance(self):
        repo = self._set_up_sample_repo()
        self.assertEqual(repo.tag_distance, 1)

    def test_branch(self):
        repo = self._set_up_sample_repo()
        self.assertEqual(repo.branch, 'default')

    def test_latest_tag(self):
        repo = self._set_up_sample_repo()
        self.assertEqual(repo.latest_tag, '0.1')

    def test_node(self):
        repo = self._set_up_sample_repo()
        self.assertEqual(len(repo.node), 12)

    def test_is_archive(self):
        repo = self._set_up_sample_repo()
        self.assertEqual(repo.is_archive, False)



