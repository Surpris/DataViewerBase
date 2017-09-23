#-*- coding: utf-8 -*-

try:
    __DATAVIEWERBASE_SETUP__
except NameError:
    __DATAVIEWERBASE_SETUP__ = False

if __DATAVIEWERBASE_SETUP__:
    import sys as _sys
    _sys.stderr.write('Running from general source directory.\n')
    del _sys
else:
    from . import core
    from . import gui
    from . import anatools
