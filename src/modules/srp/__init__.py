"""The toplevel srp module.

This module contains all the python back-end code for the Source Ruckus
Packager.  Importing it will automatically include all submodules.
"""

__all__ = ["config", "features", "notes", "cli"]

for x in __all__:
    __import__(".".join([__name__, x]))
