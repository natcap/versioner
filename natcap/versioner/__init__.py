import pkg_resources

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

    import versioning
    return versioning.get_pep440(branch=False)

