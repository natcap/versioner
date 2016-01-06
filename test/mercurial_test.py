import unittest
import shutil
import subprocess
import tempfile
import os
import re
import zipfile


def call_hg(command):
    # The subprocess docs warn that using subprocess.PIPE may result in
    # deadlock when used with subprocess.call, but it seems to work ok
    # so far!
    subprocess.call(
        command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, shell=True)


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

    def test_build_id(self):
        repo = self._set_up_sample_repo()
        build_id = repo.build_id
        matches = re.findall('1:0\.1 \[[0-9a-f]{8,12}\]', build_id)
        self.assertEqual(len(matches), 1)
        self.assertEqual(build_id, matches[0])

    def test_release_version_not_at_tag(self):
        repo = self._set_up_sample_repo()
        self.assertIs(repo.release_version, None)

    def test_release_version_at_tag(self):
        repo = self._set_up_sample_repo()
        call_hg('hg up -r 0.1 -R {repo}'.format(repo=self.repo_uri))
        self.assertEqual(repo.release_version, '0.1')

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


class MercurialArchiveTest(MercurialTest):
    def _set_up_sample_repo(self, archive_rev=None):
        from natcap.versioner import versioning
        repo = MercurialTest._set_up_sample_repo(self)
        if archive_rev is None:
            archive_rev = 'tip'
        call_hg('hg archive -R {repo} -r {rev} --type=zip archive.zip'.format(
            repo=self.repo_uri, rev=archive_rev))

        archive = zipfile.ZipFile('archive.zip')
        archive.extractall(path=self.repo_uri)
        archive.close()

        archive_path = os.path.join(self.repo_uri, 'archive')
        repo = versioning.HgArchive(archive_path)
        return repo

    def test_is_archive(self):
        repo = self._set_up_sample_repo()
        self.assertEqual(repo.is_archive, True)

    def test_release_version_at_tag(self):
        repo = self._set_up_sample_repo(archive_rev='0.1')
        self.assertEqual(repo.release_version, '0.1')
