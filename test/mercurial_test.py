import unittest
import shutil
import subprocess
import tempfile
import os
import re
import zipfile


def call_hg(command):
    """
    Make a call to the shell via ``subprocess.check_call``.

    Parameters:
        command (string): The command to issue.
        repo_dir (string): The directory where the hg repo resides.

    Returns:
        ``None``.

    Raises:
        subprocess.CalledProcessError: ``command`` exited with nonzero code.
    """
    # The subprocess docs warn that using subprocess.PIPE may result in
    # deadlock when used with subprocess.call, but it seems to work ok
    # so far!
    try:
        subprocess.check_call(
            command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as error:
        print(error.output)
        raise error


class MercurialTest(unittest.TestCase):
    def setUp(self):
        """Set up ``self.repo_path`` as a new temp folder."""
        self.repo_path = tempfile.mkdtemp()

    def tearDown(self):
        """Remove the temp folder self.repo_path."""
        shutil.rmtree(self.repo_path)

    def _set_up_sample_repo(self):
        """Create a sample repo with four commits and a tag.

        Returns:
            None"""
        from natcap.versioner import versioning

        call_hg('hg init {tempdir}'.format(
            tempdir=self.repo_path))

        filepath = os.path.join(self.repo_path, 'scratchfile')
        with open(filepath, 'a') as file_a:
            call_hg('hg add {0} -R {1}'.format(filepath, self.repo_path))
            call_hg(('hg commit -m "initial commit" -R {0}').format(
                     self.repo_path))

            file_a.write('foo\n')
            file_a.flush()
            call_hg(('hg commit -m "adding foo" -R {0}').format(self.repo_path))

            file_a.write('bar\n')
            file_a.flush()
            call_hg(('hg commit -m "adding bar" -R {0}').format(self.repo_path))

            file_a.write('baz\n')
            file_a.flush()
            call_hg(('hg commit -m "adding baz" -R {0}').format(self.repo_path))

        call_hg(('hg tag 0.1 -R {tempdir}').format(tempdir=self.repo_path))

        return versioning.HgRepo(self.repo_path)

    def test_tag_distance(self):
        """Versioner - Hg: check tag distance."""
        repo = self._set_up_sample_repo()
        self.assertEqual(repo.tag_distance, 1)

    def test_branch(self):
        """Versioner - Hg: check branch."""
        repo = self._set_up_sample_repo()
        self.assertEqual(repo.branch, 'default')

    def test_latest_tag(self):
        """Versioner - Hg: check latest tag."""
        repo = self._set_up_sample_repo()
        self.assertEqual(repo.latest_tag, '0.1')

    def test_node(self):
        """Versioner - Hg: check node."""
        repo = self._set_up_sample_repo()
        self.assertEqual(len(repo.node), 12)

    def test_is_archive(self):
        """Versioner - Hg: check whether repo is an archive."""
        repo = self._set_up_sample_repo()
        self.assertEqual(repo.is_archive, False)

    def test_build_id(self):
        """Versioner - Hg: check build ID matches regex."""
        repo = self._set_up_sample_repo()
        build_id = repo.build_id
        matches = re.findall('1:0\.1 \[[0-9a-f]{8,12}\]', build_id)
        self.assertEqual(len(matches), 1)
        self.assertEqual(build_id, matches[0])

    def test_release_version_not_at_tag(self):
        """Versioner - Hg: check release version not at a tag."""
        repo = self._set_up_sample_repo()
        self.assertIs(repo.release_version, None)

    def test_release_version_at_tag(self):
        """Versioner - Hg: check release version at a tag."""
        repo = self._set_up_sample_repo()
        call_hg('hg up -r 0.1 -R {repo}'.format(repo=self.repo_path))
        self.assertEqual(repo.release_version, '0.1')

    def test_dev_id_default(self):
        """Versioner - Hg: check dev ID matches known regex."""
        repo = self._set_up_sample_repo()
        dev_id = repo.build_dev_id()
        matches = re.findall('dev1:0\.1 \[[0-9a-f]{8,12}\]', dev_id)
        self.assertEqual(len(matches), 1)
        self.assertEqual(dev_id, matches[0])

    def test_dev_id_provided(self):
        """Versioner - Hg: check dev ID for given string matches."""
        from natcap.versioner import versioning
        repo = versioning.HgRepo('.')
        self.assertEqual(repo.build_dev_id('foo'), 'devfoo')

    def test_version_at_tag(self):
        """Versioner - Hg: check version at tag."""
        repo = self._set_up_sample_repo()
        call_hg('hg up -r 0.1 -R {repo}'.format(repo=self.repo_path))
        self.assertEqual(repo.version, '0.1')

    def test_version_not_at_tag(self):
        """Versioner - Hg: check version at untagged revision."""
        repo = self._set_up_sample_repo()
        dev_id = repo.version
        matches = re.findall('dev1:0\.1 \[[0-9a-f]{8,12}\]', dev_id)
        self.assertEqual(len(matches), 1)
        self.assertEqual(dev_id, matches[0])

    def test_pep440_at_tag(self):
        """Versioner - Hg: check PEP440 version at tag."""
        repo = self._set_up_sample_repo()
        call_hg('hg up -r 0.1 -R {repo}'.format(repo=self.repo_path))
        self.assertEqual(repo.pep440(), '0.1')

    def test_pep440_not_at_tag_no_branch_post(self):
        """Versioner - Hg: check PEP440 post-version at untagged revision."""
        repo = self._set_up_sample_repo()
        pep440_version = repo.pep440(branch=False, method='post')
        matches = re.findall('0\.1\.post1\+n[0-9a-f]{8,12}', pep440_version)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0], pep440_version)

    def test_pep440_not_at_tag_with_branch_post(self):
        """Versioner - Hg: check PEP440 post-version, no tag, with branch."""
        repo = self._set_up_sample_repo()
        pep440_version = repo.pep440(branch=True, method='post')
        matches = re.findall('0\.1\.post1\+n[0-9a-f]{8,12}-default',
                             pep440_version)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0], pep440_version)

    def test_pep440_not_at_tag_no_branch_pre(self):
        """Versioner - Hg: check PEP440 post-version, no tag, no branch."""
        repo = self._set_up_sample_repo()
        pep440_version = repo.pep440(branch=False, method='pre')
        matches = re.findall('0\.2\.pre1\+n[0-9a-f]{8,12}', pep440_version)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0], pep440_version)

    def test_pep440_not_at_tag_with_branch_pre(self):
        """Versioner - Hg: check PEP440 pre-version, no tag, with branch."""
        repo = self._set_up_sample_repo()
        pep440_version = repo.pep440(branch=True, method='pre')
        matches = re.findall('0\.2\.pre1\+n[0-9a-f]{8,12}-default',
                             pep440_version)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0], pep440_version)

    def test_vcs_version(self):
        """Versioner - Hg: check default version if PEP440."""
        import natcap.versioner
        repo = self._set_up_sample_repo()
        call_hg('hg up -r 0.1 -R {repo}'.format(repo=self.repo_path))
        version = natcap.versioner.vcs_version(self.repo_path)
        self.assertEqual(version, repo.pep440(branch=False))

    def test_vcs_version_subdir(self):
        """Versioner - Hg: check versioning works in subdir of Hg repo."""
        import natcap.versioner
        repo = self._set_up_sample_repo()

        dir_inside_repo = os.path.join(self.repo_path, 'foo', 'bar')
        os.makedirs(dir_inside_repo)

        version = natcap.versioner.vcs_version(dir_inside_repo)
        self.assertEqual(version, repo.pep440(branch=False))

    def test_create_repo_in_subdir(self):
        """Versioner - Hg: check versioning works in nested Hg repos."""
        from natcap.versioner import versioning
        repo = self._set_up_sample_repo()

        dir_inside_repo = os.path.join(self.repo_path, 'foo', 'bar')
        os.makedirs(dir_inside_repo)

        new_repo = versioning.HgRepo(dir_inside_repo)
        self.assertEqual(new_repo._repo_path, self.repo_path)

    def test_hg_get_version(self):
        """Versioner - Hg: check version OK from VCS."""
        import natcap.versioner

        self._set_up_sample_repo()
        # sys won't have a version attached to it that natcap.versioner
        # identifies.
        natcap.versioner.get_version('sys', root=self.repo_path,
                                     allow_scm=natcap.versioner.SCM_ALLOW)


class MercurialArchiveTest(MercurialTest):
    def _set_up_sample_repo(self, archive_rev=None):
        """Create an Hg archive of a repo.

        Parameters:
            archive_rev=None (string or None): the revision to archive.
                If None, the latest revision of the repo will be used.

        Returns:
            ``natcap.versioner.versioning.HgArchive`` instance.
        """
        from natcap.versioner import versioning
        repo = MercurialTest._set_up_sample_repo(self)
        if archive_rev is None:
            archive_rev = 'tip'
        call_hg('hg archive -R {repo} -r {rev} --type=zip archive.zip'.format(
            repo=self.repo_path, rev=archive_rev))

        archive = zipfile.ZipFile('archive.zip')
        archive.extractall(path=self.repo_path)
        archive.close()

        self.archive_path = os.path.join(self.repo_path, 'archive')
        repo = versioning.HgArchive(self.archive_path)
        return repo

    def test_is_archive(self):
        """Versioner - Hg Archive: check is_archive."""
        repo = self._set_up_sample_repo()
        self.assertEqual(repo.is_archive, True)

    def test_release_version_at_tag(self):
        """Versioner - Hg Archive: check release version at tag."""
        repo = self._set_up_sample_repo(archive_rev='0.1')
        self.assertEqual(repo.release_version, '0.1')

    def test_version_at_tag(self):
        """Versioner - Hg Archive: check version at tag."""
        repo = self._set_up_sample_repo(archive_rev='0.1')
        self.assertEqual(repo.version, '0.1')

    def test_pep440_at_tag(self):
        """Versioner - Hg Archive: check PEP440 version at tag."""
        repo = self._set_up_sample_repo(archive_rev='0.1')
        self.assertEqual(repo.pep440(), '0.1')

    def test_vcs_version(self):
        """Versioner - Hg Archive: check vcs_version at tag."""
        import natcap.versioner
        repo = self._set_up_sample_repo('0.1')
        version = natcap.versioner.vcs_version(self.archive_path)
        self.assertEqual(version, repo.pep440(branch=False))
