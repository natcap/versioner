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

        subprocess.call('hg init {tempdir}'.format(
            tempdir=self.repo_uri), shell=True)

        cwd = os.getcwd()
        filepath = os.path.join(self.repo_uri, 'scratchfile')

        open(filepath, 'w')
        subprocess.call('hg add {0} -R {1}'.format(filepath, self.repo_uri),
                shell=True)
        subprocess.call(('hg commit -m "initial commit" -R '
                '{0}').format(filepath, self.repo_uri), shell=True)

        open(filepath, 'a').write('foo\n')
        subprocess.call(('hg commit -m "adding foo" -R '
                '{0}').format(self.repo_uri), shell=True)

        open(filepath, 'a').write('bar\n')
        subprocess.call(('hg commit -m "adding bar" -R '
            '{0}').format(self.repo_uri), shell=True)

        open(filepath, 'a').write('baz\n')
        subprocess.call(('hg commit -m "adding baz" -R '
            '{0}').format(self.repo_uri), shell=True)

        subprocess.call(('hg tag 0.1 -R '
            '{tempdir}').format(tempdir=self.repo_uri), shell=True)

        return versioning.HgRepo(self.repo_uri)

    def test_tag_distance(self):
        repo = self._set_up_sample_repo()

        self.assertEqual(repo.tag_distance, 1)




