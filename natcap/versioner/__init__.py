import pkg_resources
import versioning

def get_version(package, root='.'):
    try:
        return pkg_resources.require(package)[0].version
    except pkg_resources.DistributionNotFound:
        pass

    return versioning.get_pep440(branch=False)


