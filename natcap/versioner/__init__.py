import pkg_resources
import versioning

def get_version(root='.'):
    version = versioning.get_pep440(branch=False)
    if version:
        return version
    return pkg_resources.require('natcap.versioner')[0].version


