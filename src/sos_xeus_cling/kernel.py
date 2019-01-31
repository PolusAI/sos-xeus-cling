#!/usr/bin/env python3
#
# Copyright (c) Konstantin Taletskiy
# Distributed under the terms of the MIT License.

import os
import pandas as pd
from tempfile import TemporaryDirectory
from textwrap import dedent
from sos.utils import short_repr, env
from collections import Sequence
from IPython.core.error import UsageError
import re

# C++    length (n)    Python
# <C++ type>    0    <Python type>
def _xeus_declare_variable(obj, newname):
    if isinstance(obj, (int, str)):
        return 'int ' + newname + ' = ' + repr(obj)
    else:
        return ''

class sos_xeus_cling:
    background_color = '#9400D3'
    supported_kernels = {'C++11': ['xeus-cling-cpp11'], 'C++14' : ['xeus-cling-cpp14'], 'C++17' : ['xeus-cling-cpp17']}
    options = {}
    cd_command = '#include <unistd.h>\nchdir("{dir}");'

    def __init__(self, sos_kernel, kernel_name='scala'):
        self.sos_kernel = sos_kernel
        self.kernel_name = kernel_name
        self.init_statements = ''

    def get_vars(self, names):
        pass

    def put_vars(self, items, to_kernel=None):
        return {}
