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
#define typename(x) _Generic((x),                                                 \
         bool: "_Bool",                  unsigned char: "unsigned char",          \
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
    background_color = {'C++11': '#DDA0DD', 'C++14': '#D8BFD8', 'C++17': '#E6E6FA'}
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
        # self.sos_kernel.warn(
                # f'Debug')
        result = {}
        for item in items:
            # item - string with variable name (in C++)
            response = self.sos_kernel.get_response('{}'.format(item), ('execute_result',))[0][1]['data']['text/plain']
            result[item] = response
            # self.sos_kernel.warn("%i" % result[item])

            cpp_type = self.sos_kernel.get_response('typename({})'.format(item), ('execute_result',))[0][1]['data']['text/plain']
            # self.sos_kernel.warn("%s" % cpp_type)

            #Convert string to appropriate type in SoS

            # cpp_type = self.sos_kernel.get_response('typename({})'.format(item), ('stream',), name=('stdout',))[0][1]
            # self.sos_kernel.warn("%s" % cpp_type)
            # if cpp_type == 'int':
                # print(cpp_type)
                # print(item)
                # response = self.sos_kernel.get_response('{}'.format(item), ('stream',))[0][1]
                # expr = response['text']
                # result[item] = eval(expr)
            # print(cpp_type)
            # self.sos_kernel.warn(
                # f'Variable of type: is passed to SoS kernel')
        # print(result)
        return result
