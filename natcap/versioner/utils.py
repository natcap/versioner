from __future__ import absolute_import
from . import parse_version
import os

VERSION_FILE_TEMPLATE = """
# coding: utf-8
# file generated by natcap.versioner
version = {version!r}
"""


def distutils_keyword(dist, keyword, value):
    """
    This is called when the user provides a `natcap_version` keyword in their
    setup.py:setup().
    """

    if not value:
        # If the user didn't use our keyword
        return

    new_version = parse_version()
    dist.metadata.version = new_version

    # Assume the value is the file to write to.
    out_file = os.path.join('.', value)
    with open(out_file, 'w') as version_file:
        version_file.write(
            VERSION_FILE_TEMPLATE.format(version=new_version))
