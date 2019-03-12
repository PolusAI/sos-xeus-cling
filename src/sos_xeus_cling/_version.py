#!/usr/bin/env python3
#
# Copyright (c) Konstantin Taletskiy
# Distributed under the terms of the MIT License.

import sys

__all__ = ['__version__']

_py_ver = sys.version_info
if _py_ver.major == 2 or (_py_ver.major == 3 and (_py_ver.minor, _py_ver.micro) < (4, 0)):
    raise SystemError('SOS requires Python 3.4 or higher. Please upgrade your Python {}.{}.{}.'
        .format(_py_ver.major, _py_ver.minor, _py_ver.micro))

__sos_version__ = '1.0'

# version of the sos-xeus-cling module
__version__ = '0.1.0'
