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

class sos_xeus_cling:
    supported_kernels = {'C++11': ['xeus-cling-cpp11'], 'C++14' : ['xeus-cling-cpp14'], 'C++17' : ['xeus-cling-cpp17']}
    background_color = {'C++11': '#DDA0DD', 'C++14': '#D8BFD8', 'C++17': '#E6E6FA'}
    options = {}
    cd_command = '#include <unistd.h>\nchdir("{dir}");'

    def __init__(self, sos_kernel, kernel_name='scala'):
        self.sos_kernel = sos_kernel
        self.kernel_name = kernel_name
        self.init_statements = ''

    def get_vars(self, names):
        for name in names:
            var = env.sos_dict[name]
            if isinstance(obj, (int, str)):
                newvar = 'int ' + newname + ' = ' + repr(obj)
                self.sos_kernel.run_cell(f'{newvar}', True, False,
                     on_error=f'Failed to put variable {name} to scala')

    def put_vars(self, items, to_kernel=None):
        return {}
