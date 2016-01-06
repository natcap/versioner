import subprocess
import logging
import platform
import collections
import shutil
import os
import tempfile
import atexit
import yaml


LOGGER = logging.getLogger('natcap.invest.versioning')
LOGGER.setLevel(logging.ERROR)


class VCSQuerier(object):
    def __init__(self, repo_path):
        self._repo_path = repo_path

    def _run_command(self, cmd):
        """Run a subprocess.Popen command.  This function is intended for internal
        use only and ensures a certain degree of uniformity across the various
        subprocess calls made in this module.

        cmd - a python string to be executed in the shell.

        Returns a python bytestring of the output of the input command."""
        p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return p.stdout.read().replace('\n', '')

    @property
    def is_archive(self):
        raise NotImplementedError

    @property
    def tag_distance(self):
        raise NotImplementedError

    @property
    def build_id(self):
        raise NotImplementedError

    @property
    def latest_tag(self):
        raise NotImplementedError

    @property
    def branch(self):
        raise NotImplementedError

    @property
    def release_version(self):
        """This function gets the release version.  Returns either the latest tag
        (if we're on a release tag) or None, if we're on a dev changeset."""
        if self.tag_distance == 0:
            return self.latest_tag
        return None

    @property
    def version(self):
        """This function gets the module's version string.  This will be either the
        dev build ID (if we're on a dev build) or the current tag if we're on a
        known tag.  Either way, the return type is a string."""
        release_version = self.release_version
        if release_version == None:
            return self.build_dev_id(self.build_id)
        return release_version

    def build_dev_id(self, build_id=None):
        """This function builds the dev version string.  Returns a string."""
        if build_id is None:
            build_id = self.build_id
        return 'dev%s' % (build_id)


class HgArchive(VCSQuerier):
    shortnode_len = 12

    @property
    def build_id(self):
        attrs = _get_archive_attrs(self._repo_path)
        return '{latesttagdistance}:{latesttag} [{node}]'.format(
            latesttagdistance=attrs['latesttagdistance'],
            latesttag=attrs['latesttag'],
            node=attrs['node'][:self.shortnode_len],
        )

    @property
    def tag_distance(self):
        try:
            return _get_archive_attrs(self._repo_path)['latesttagdistance']
        except KeyError:
            # This happens when we are at a tag.
            return 0

    @property
    def latest_tag(self):
        attrs = _get_archive_attrs(self._repo_path)
        try:
            return unicode(attrs['latesttag'])
        except KeyError:
            # This happens when we are at a tag.
            return unicode(attrs['tag'])

    @property
    def branch(self):
        return _get_archive_attrs(self._repo_path)['branch']

    @property
    def node(self):
        return _get_archive_attrs(self._repo_path)['node'][:self.shortnode_len]

    @property
    def is_archive(self):
        if os.path.exists(os.path.join(self._repo_path, '.hg_archival.txt')):
            return True
        return False


class HgRepo(VCSQuerier):
    def _log_template(self, template_string):
        hg_call = 'hg log -R %s -r . --config ui.report_untrusted=False'
        cmd = (hg_call + ' --template="%s"') % (self._repo_path,
                                                template_string)
        return self._run_command(cmd)

    @property
    def build_id(self):
        """Call mercurial with a template argument to get the build ID.  Returns a
        python bytestring."""
        return self._log_template('{latesttagdistance}:{latesttag} '
                                  '[{node|short}]')

    @property
    def tag_distance(self):
        """Call mercurial with a template argument to get the distance to the latest
        tag.  Returns an int."""
        return int(self._log_template('{latesttagdistance}'))

    @property
    def latest_tag(self):
        """Call mercurial with a template argument to get the latest tag.  Returns a
        python bytestring."""
        return self._log_template('{latesttag}')

    @property
    def branch(self):
        """Get the current branch from hg."""
        return self._log_template('{branch}')

    @property
    def node(self):
        return self._log_template('{node|short}')

    @property
    def is_archive(self):
        if os.path.exists('.hg_archival.txt'):
            return True
        return False


class GitRepo(VCSQuerier):
    def __init__(self):
        VCSQuerier.__init__(self)
        self._tag_distance = None
        self._latest_tag = None
        self._commit_hash = None

    @property
    def branch(self):
        branch_cmd = 'git branch'
        current_branches = self._run_command(branch_cmd)
        for line in current_branches.split('\n'):
            if line.startswith('* '):
                return line.strip()[2:]
        raise IOError('Could not detect current branch')

    def _describe_current_rev(self):
        self._tag_distance = None
        self._latest_tag = None
        self._commit_hash = None

        data = self._run_command('git describe --tags')
        current_branch = self.branch

        # assume that the tag has no dashes in it
        if data == 'heads/%s' % current_branch:
            # when there are no tags
            self._latest_tag = 'null'

            num_commits_cmd = 'git rev-list %s --count' % current_branch
            self._tag_distance = self._run_command(num_commits_cmd)

            commit_hash_cmd = 'git log -1 --pretty="format:%h"'
            self._commit_hash = self._run_command(commit_hash_cmd)
        elif '-' not in data:
            # then we're at a tag
            self._latest_tag = str(data)
            self._tag_distance = 0

            commit_hash_cmd = 'git log -1 --pretty="format:%h"'
            self._commit_hash = self._run_command(commit_hash_cmd)
        else:
            # we're not at a tag, so data has the format:
            # data = tagname-tagdistange-commit_hash
            tagname, tag_dist, _commit_hash = data.split('-')
            self._tag_distance = int(tag_dist)
            self._latest_tag = tagname
            self._commit_hash = self.node

    @property
    def build_id(self):
        self._describe_current_rev()
        return "%s:%s [%s]" % (self._tag_distance, self._latest_tag,
            self._commit_hash)

    @property
    def tag_distance(self):
        self._describe_current_rev()
        return self._tag_distance

    @property
    def latest_tag(self):
        self._describe_current_rev()
        return self._latest_tag

    @property
    def node(self):
        return self._run_command('git rev-parse HEAD').strip()[:8]

    @property
    def is_archive(self):
        # Archives are a mercurial feature.
        return False


def _temporary_filename():
    """Returns a temporary filename using mkstemp. The file is deleted
        on exit using the atexit register.  This function was migrated from
        the invest-3 raster_utils file, rev 11354:1029bd49a77a.

        returns a unique temporary filename"""

    file_handle, path = tempfile.mkstemp()
    os.close(file_handle)

    def remove_file(path):
        """Function to remove a file and handle exceptions to register
            in atexit"""
        try:
            os.remove(path)
        except OSError:
            # This happens if the file didn't exist, which is okay because
            # maybe we deleted it in a function
            pass

    atexit.register(remove_file, path)
    return path


def get_py_arch():
    """This function gets the python architecture string.  Returns a string."""
    return platform.architecture()[0]


def get_release_version():
    """This function gets the release version.  Returns either the latest tag
    (if we're on a release tag) or None, if we're on a dev changeset."""
    if get_tag_distance() == 0:
        return get_latest_tag()
    return None


def version():
    """This function gets the module's version string.  This will be either the
    dev build ID (if we're on a dev build) or the current tag if we're on a
    known tag.  Either way, the return type is a string."""
    release_version = get_release_version()
    if release_version is None:
        return build_dev_id(get_build_id())
    return release_version


def build_dev_id(build_id=None):
    """This function builds the dev version string.  Returns a string."""
    if build_id is None:
        build_id = get_build_id()
    return 'dev%s' % (build_id)


def get_architecture_string():
    """Return a string representing the operating system and the python
    architecture on which this python installation is operating (which may be
    different than the native processor architecture.."""
    return '%s%s' % (platform.system().lower(),
                     platform.architecture()[0][0:2])


def get_version_from_hg():
    """Get the version from mercurial.  If we're on a tag, return that.
    Otherwise, build the dev id and return that instead."""
    # TODO: Test that Hg exists before getting this information.
    if get_tag_distance() == 0:
        return get_latest_tag()
    else:
        return build_dev_id()


def _increment_tag(version_string):
    split_string = version_string.split('.dev')

    if len(split_string) == 1:
        # When the version string is just the tag, we return the tag
        return version_string
    else:
        # increment the minor version number and not the update num.
        tag = split_string[0].split('.')

        # If there's never been a tag, assume 0.0.0 was the tag at rev 0.
        if len(tag) == 1 and tag[0] in ['null', 'None']:
            tag = ['0', '0', '0']

        tag[-2] = str(int(tag[-2]) + 1)
        tag[-1] = '0'
        return '.'.join(tag) + '.dev' + split_string[1]


def get_pep440(branch=True, method='post'):
    """
    Build a PEP440-compliant version.  Returns a string.

    Parameters:
        branch=True (boolean): Whether to include the name of the current
            branch in the version string
        method='post' (string): One of ['post', 'pre'].  If 'post', the
            version string will br formatted as a post-release.  If 'pre',
            the version string will be formetted as a pre-release.

    Returns:
        The string version number.
    """
    assert method in ['pre', 'post'], 'Versioning method %s not valid' % method

    template_string = "%(latesttag)s.%(method)s%(tagdist)s+n%(node)s"
    if branch is True:
        template_string += "-%(branch)s"

    if os.path.exists('.hg'):
        repo = HgRepo()
    else:
        repo = GitRepo()

    if repo.is_archive:
        data = {
            'tagdist': _get_archive_attr('latesttagdistance'),
            'latesttag': _get_archive_attr('latesttag'),
            'node': _get_archive_attr('node')[:8],
            'branch': _get_archive_attr('branch'),
            'method': method,
        }
    else:
        data = {
            'tagdist': repo.tag_distance,
            'latesttag': repo.latest_tag,
            'node': repo.node,
            'branch': repo.branch,
            'method': method,
        }

    version_string = template_string % data

    # If we're at a tag, return the tag only
    if int(data['tagdist']) == 0:
        return "{latesttag}".format(**data)

    if method == 'pre':
        return _increment_tag(version_string)
    return version_string


def _get_archive_attrs(archive_path):
    """
    If we're in an hg archive, there will be a file '.hg_archival.txt' in the
    repo root.  If this is the case, we can fetch relevant build information
    from this file that we might normally be able to get directly from hg.

    Parameters:
        attr (string): The archive attr to fetch.  One of
        "repo"|"node"|"branch"|"latesttag"|"latesttagdistance"|"changessincelatesttag"
        archive_path (string): The path to the mercurial archive.
            The .hg_archival.txt file must exist right inside this directory.

    Returns:
        A dict of the attributes within the .hg_archival file.

    Raises:
        IOError when the .hg_archival.txt file cannot be found.
        KeyError when `attr` is not in .hg_archival.txt
    """
    return yaml.safe_load(open(os.path.join(archive_path, '.hg_archival.txt')))
