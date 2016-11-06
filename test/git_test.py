import os
import shutil
import subprocess
import tempfile
import unittest
import re


def call_git(command, repo_dir):
    """
    Make a call to the shell via ``subprocess.check_call``.

    Parameters:
        command (string): The command to issue.
        repo_dir (string): The directory where the git repo resides.

    Returns:
        ``None``.

    Raises:
        subprocess.CalledProcessError: ``command`` exited with nonzero code.
    """
    # The subprocess docs warn that using subprocess.PIPE may result in
    # deadlock when used with subprocess.call, but it seems to work ok
    # so far!
    subprocess.check_call(
        command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, shell=True, cwd=repo_dir)


class GitTest(unittest.TestCase):
    def setUp(self):
        """Set up ``self.repo_uri`` as a new temp folder."""
        self.repo_uri = tempfile.mkdtemp()

    def tearDown(self):
        """Remove the temp folder self.repo_uri."""
        shutil.rmtree(self.repo_uri)

    def _set_up_sample_repo(self, tag=True):
        """Create a sample repo with four commits and (optionally) a tag.

        ``self.repo_uri`` is used as the repository location.

        All changes are made to the file ``<self.repo_uri>/scratchfile``

        A few git configuration options are assumed for ease of testing on CI
        machines, where the currently executing user may not have this
        configured:

            * ``user.name`` is set to ``Example Name``
            * ``user.email`` is set to ``name@example.com``

        Parameters:
            tag=True (bool): whether to include a tag in the repo.  If
                ``True``, the 4th commit will be tagged with ``0.1``.

        Returns:
            None"""
        from natcap.versioner import versioning

        call_git('git init {tempdir}'.format(
            tempdir=self.repo_uri), self.repo_uri)

        call_git('git checkout -B master', self.repo_uri)

        git_commit = (
            'git '
            '-c user.name="Example Name" '
            '-c user.email="name@example.com" '
            'commit -a -m "{message}"')

        filepath = os.path.join(self.repo_uri, 'scratchfile')
        with open(filepath, 'w') as scratchfile:
            call_git('git add {0}'.format(filepath), self.repo_uri)
            call_git(git_commit.format(message="initial commit"), self.repo_uri)

            scratchfile.write('foo\n')
            scratchfile.flush()
            call_git(git_commit.format(message="adding foo"), self.repo_uri)

            scratchfile.write('bar\n')
            scratchfile.flush()
            call_git(git_commit.format(message="adding bar"), self.repo_uri)

            scratchfile.write('baz\n')
            scratchfile.flush()
            call_git(git_commit.format(message="adding baz"), self.repo_uri)

            if tag:
                call_git('git tag 0.1', self.repo_uri)

            scratchfile.write('example\n')
            scratchfile.flush()
            call_git(git_commit.format(message="adding example"), self.repo_uri)

        return versioning.GitRepo(self.repo_uri)

    def test_tag_distance(self):
        """Versioner - Git: Check tag distance."""
        repo = self._set_up_sample_repo()
        self.assertEqual(repo.tag_distance, 1)

    def test_branch(self):
        """Versioner - Git: Check branch name."""
        repo = self._set_up_sample_repo()
        self.assertEqual(repo.branch, 'master')

    def test_latest_tag(self):
        """Versioner - Git: Check latest tag."""
        repo = self._set_up_sample_repo()
        self.assertEqual(repo.latest_tag, '0.1')

    def test_node(self):
        """Versioner - Git: check latest node ID."""
        repo = self._set_up_sample_repo()
        self.assertEqual(len(repo.node), 8)

    def test_is_archive(self):
        """Versioner - Git: check whether repo is an archive."""
        repo = self._set_up_sample_repo()
        self.assertEqual(repo.is_archive, False)

    def test_build_id(self):
        """Versioner - Git: check build ID matches known regex."""
        repo = self._set_up_sample_repo()
        build_id = repo.build_id
        matches = re.findall('1:0\.1 \[[0-9a-f]{8,12}\]', build_id)
        self.assertEqual(len(matches), 1)
        self.assertEqual(build_id, matches[0])

    def test_dev_id_default(self):
        """Versioner - Git: check dev build ID matches known regex."""
        repo = self._set_up_sample_repo()
        dev_id = repo.build_dev_id()
        matches = re.findall('dev1:0\.1 \[[0-9a-f]{8,12}\]', dev_id)
        self.assertEqual(len(matches), 1)
        self.assertEqual(dev_id, matches[0])

    def test_dev_id_provided(self):
        """Versioner - Git: check dev build ID of known string."""
        from natcap.versioner import versioning
        repo = versioning.HgRepo('.')
        self.assertEqual(repo.build_dev_id('foo'), 'devfoo')

    def test_release_version_at_tag(self):
        """Versioner - Git: check version at tag."""
        repo = self._set_up_sample_repo()
        call_git('git checkout 0.1', self.repo_uri)
        self.assertEqual(repo.version, '0.1')

    def test_release_version_not_at_tag(self):
        """Versioner - Git: check version not at tag."""
        repo = self._set_up_sample_repo()
        dev_id = repo.version
        matches = re.findall('dev1:0\.1 \[[0-9a-f]{8,12}\]', dev_id)
        self.assertEqual(len(matches), 1)
        self.assertEqual(dev_id, matches[0])

    def test_vcs_version(self):
        """Versioner - Git: check PEP440 version from VCS."""
        import natcap.versioner
        repo = self._set_up_sample_repo()
        call_git('git checkout 0.1', self.repo_uri)
        version = natcap.versioner.vcs_version(self.repo_uri)
        self.assertEqual(version, repo.pep440(branch=False))

    def test_vcs_version_no_tag(self):
        """Versioner - Git: check PEP440 version from VCS without a tag."""
        import natcap.versioner
        self._set_up_sample_repo(tag=False)
        version = natcap.versioner.vcs_version(self.repo_uri)
        matches = re.findall('null\.post5\+n[0-9a-f]{8,12}', version)
        self.assertEqual(len(matches), 1, version)
        self.assertEqual(version, matches[0])

    def test_git_no_branches(self):
        """Versioner - Git: check error raised when no branches exist."""
        from natcap.versioner import versioning

        # A newly initialized repo has no commits.  A repo with no commits has
        # no branches.
        call_git('git init {tempdir}'.format(
            tempdir=self.repo_uri), self.repo_uri)

        repo = versioning.GitRepo(self.repo_uri)
        with self.assertRaises(IOError):
            repo.branch

    def test_git_vcs_version(self):
        """Versioner - Git: check fallback to SCM."""
        import natcap.versioner

        self._set_up_sample_repo()
        # sys won't have a version attached to it that natcap.versioner
        # identifies.
        natcap.versioner.get_version('sys', root=self.repo_uri,
                                     allow_scm=natcap.versioner.SCM_ALLOW)
