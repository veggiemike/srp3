"""Feature module for managing checksums.

This feature records checksums for each installed file and allows the user to
verify files on demand after installation.
"""

from srp.features import *

def install_func(work):
    """gen sha of each file, update pkg manifest"""
    # FIXME: MULTI:
    pass

def uninstall_func():
    """verify, issue warning"""
    # FIXME: MULTI:
    pass

def verify_func():
    """gen sha of each file, compare with pkg manifest"""
    # FIXME: MULTI:
    pass

def commit_func():
    """update pkg manifest"""
    # FIXME: MULTI:
    pass

register_feature(
    feature_struct("checksum",
                   __doc__,
                   True,
                   install = stage_struct("checksum", install_func,
                                          ["core"], []),
                   uninstall = stage_struct("checksum", uninstall_func,
                                            [], ["core"]),
                   action = [("commit",
                              stage_struct("checksum", commit_func, [], [])),
                             ("verify",
                              stage_struct("checksum", verify_func, [], []))]))
