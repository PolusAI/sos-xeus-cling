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

cpp_init_statements = r'''
#include <iostream>
#define typename(x) _Generic((x),                                                 \
         bool: "bool",                  unsigned char: "unsigned char",          \
         char: "char",                     signed char: "signed char",            \
    short int: "short int",         unsigned short int: "unsigned short int",     \
          int: "int",                     unsigned int: "unsigned int",           \
     long int: "long int",           unsigned long int: "unsigned long int",      \
long long int: "long long int", unsigned long long int: "unsigned long long int", \
        float: "float",                         double: "double",                 \
  long double: "long double",                   char *: "pointer to char",        \
       void *: "pointer to void",                int *: "pointer to int",         \
      default: "other")
'''

class sos_xeus_cling:
    supported_kernels = {'C++11': ['xeus-cling-cpp11'], 'C++14' : ['xeus-cling-cpp14'], 'C++17' : ['xeus-cling-cpp17']}
    background_color = {'C++11': '#B3BFFF', 'C++14': '#D5CCFF', 'C++17': '#EAE6FF'}
    options = {}
    cd_command = '#include <unistd.h>\nchdir("{dir}");'

    def __init__(self, sos_kernel, kernel_name='C++11'):
        self.sos_kernel = sos_kernel
        self.kernel_name = kernel_name
        self.init_statements = cpp_init_statements

    def get_vars(self, names):
        for name in names:
            var = env.sos_dict[name]
            if isinstance(var, (int, str)):
                newvar = 'int ' + name + ' = ' + repr(var)
                self.sos_kernel.run_cell(f'{newvar}', True, False,
                     on_error=f'Failed to put variable {name} to C++')

    def put_vars(self, items, to_kernel=None):
        result = {}
        for item in items:
            # item - string with variable name (in C++)
            value = self.sos_kernel.get_response('{}'.format(item), ('execute_result',))[0][1]['data']['text/plain']
            cpp_type = self.sos_kernel.get_response('typename({})'.format(item), ('execute_result',))[0][1]['data']['text/plain']
            self.sos_kernel.warn(value)
            self.sos_kernel.warn(cpp_type)

            #Convert string value to appropriate type in SoS
            integer_types = ['"int"', '"short int"', '"long int"', '"long long int"']
            real_types = ['"float"', '"double"']
            
            if cpp_type in integer_types:
                self.sos_kernel.warn('converting integer type')
                result[item] = int(value)
            elif cpp_type in real_types:
                if value[-1] == 'f':
                    value = value[:-1]
                self.sos_kernel.warn('converting real number type')
                result[item] = float(value)
            elif cpp_type == '"bool"':
                if value == 'true':
                    result[item] = True
                else:
                    result[item] = False
            else:
                self.sos_kernel.warn(f'Type {cpp_type} is not supported')
        return result
