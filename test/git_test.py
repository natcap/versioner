import os
import shutil
import subprocess
import tempfile
import unittest
import re

def call_git(command, repo_dir):
    # The subprocess docs warn that using subprocess.PIPE may result in
    # deadlock when used with subprocess.call, but it seems to work ok
    # so far!
    subprocess.call(
        command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, shell=True, cwd=repo_dir)

class GitTest(unittest.TestCase):
    def setUp(self):
        self.repo_uri = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.repo_uri)

    def _set_up_sample_repo(self):
        """Create a sample repo with four commits and a tag.

        Returns:
            None"""
        from natcap.versioner import versioning

        call_git('git init {tempdir}'.format(
            tempdir=self.repo_uri), self.repo_uri)

        call_git('git checkout -B master', self.repo_uri)

        filepath = os.path.join(self.repo_uri, 'scratchfile')
        open(filepath, 'w')
        call_git('git add {0}'.format(filepath), self.repo_uri)
        call_git(('git commit -a -m "initial commit"'), self.repo_uri)

        open(filepath, 'a').write('foo\n')
        call_git('git commit -a -m "adding foo"', self.repo_uri)

        open(filepath, 'a').write('bar\n')
        call_git('git commit -a -m "adding bar"', self.repo_uri)

        open(filepath, 'a').write('baz\n')
        call_git('git commit -a -m "adding baz"', self.repo_uri)

        call_git('git tag 0.1', self.repo_uri)

        open(filepath, 'a').write('example\n')
        call_git('git commit -a -m "adding example"', self.repo_uri)

        return versioning.GitRepo(self.repo_uri)

    def test_tag_distance(self):
        repo = self._set_up_sample_repo()
        self.assertEqual(repo.tag_distance, 1)

    def test_branch(self):
        repo = self._set_up_sample_repo()
        self.assertEqual(repo.branch, 'master')

    def test_latest_tag(self):
        repo = self._set_up_sample_repo()
        self.assertEqual(repo.latest_tag, '0.1')

    def test_node(self):
        repo = self._set_up_sample_repo()
        self.assertEqual(len(repo.node), 8)

    def test_is_archive(self):
        repo = self._set_up_sample_repo()
        self.assertEqual(repo.is_archive, False)

    def test_build_id(self):
        repo = self._set_up_sample_repo()
        build_id = repo.build_id
        matches = re.findall('1:0\.1 \[[0-9a-f]{8,12}\]', build_id)
        self.assertEqual(len(matches), 1)
        self.assertEqual(build_id, matches[0])

    def test_dev_id_default(self):
        repo = self._set_up_sample_repo()
        dev_id = repo.build_dev_id()
        matches = re.findall('dev1:0\.1 \[[0-9a-f]{8,12}\]', dev_id)
        self.assertEqual(len(matches), 1)
        self.assertEqual(dev_id, matches[0])

    def test_dev_id_provided(self):
        from natcap.versioner import versioning
        repo = versioning.HgRepo('.')
        self.assertEqual(repo.build_dev_id('foo'), 'devfoo')

    def test_release_version_at_tag(self):
        repo = self._set_up_sample_repo()
        call_git('git checkout 0.1', self.repo_uri)
        self.assertEqual(repo.version, '0.1')

    def test_release_version_not_at_tag(self):
        repo = self._set_up_sample_repo()
        dev_id = repo.version
        matches = re.findall('dev1:0\.1 \[[0-9a-f]{8,12}\]', dev_id)
        self.assertEqual(len(matches), 1)
        self.assertEqual(dev_id, matches[0])

    def test_vcs_version(self):
        import natcap.versioner
        repo = self._set_up_sample_repo()
        call_git('git checkout 0.1', self.repo_uri)
        version = natcap.versioner.vcs_version(self.repo_uri)
        self.assertEqual(version, repo.pep440(branch=False))
