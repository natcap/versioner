import os
import pkg_resources
import traceback

def get_version(package, root='.'):
    """
    Get the version string for the target package.

    If `package` is not available for import, check the root for git or hg.

    Parameters:
        package (string): The package name to check for (e.g. 'natcap.invest')
        root='.' (string): The path to the directory to check for a DVCS repository.

    Returns:
        A DVCS-aware versioning string.
    """
    try:
        return pkg_resources.require(package)[0].version
    except pkg_resources.DistributionNotFound:
        pass

    return vcs_version(root)

def vcs_version(root='.'):
    """
    Get the version string from your VCS.

    Parameters:
        root='.' (string): The root directory to search for vcs information.
            This should be the path to the repository root.
    """
    import versioning
    cwd = os.getcwd()
    try:
        os.chdir(root)
        version = versioning.get_pep440(branch=False)
    except:
        traceback.print_exc()
        version = 'UNKNOWN'
    finally:
        os.chdir(cwd)

    return version

