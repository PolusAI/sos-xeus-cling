#!/usr/bin/env python3
#
# Copyright (c) Konstantin Taletskiy
# Distributed under the terms of the MIT License.

import os
import numpy as np
import pandas as pd
from tempfile import TemporaryDirectory
from textwrap import dedent
from sos.utils import short_repr, env
from collections import Sequence
from IPython.core.error import UsageError
import re

def homogeneous_type(seq):
    iseq = iter(seq)
    first_type = type(next(iseq))
    if first_type in (int, float):
        return True if all(isinstance(x, (int, float)) for x in iseq) else False
    else:
        return True if all(isinstance(x, first_type) for x in iseq) else False

cpp_init_statements = f'#include "{os.path.split(__file__)[0]}/utils.hpp"'

def _sos_to_cpp_type(obj):
    ''' Returns corresponding C++ data type string for provided Python object '''
    if isinstance(obj, (int, np.intc)):
        if obj >= -2147483648 and obj <= 2147483647:
            return 'int' #{name} = {repr(obj)};'
        elif obj >= -9223372036854775808 and obj <= 9223372036854775807:
            return 'long int' #{name} = {repr(obj)};'
        else:
            return -1 #Integer is out of bounds
    elif isinstance(obj, float):
        if (obj >= -3.40282e+38 and obj <= -1.17549e-38) or (obj >= 1.17549e-38 and obj <= 3.40282e+38):
            return 'float' #{name} = {repr(obj)};'
        elif (obj >= -1.79769e+308 and obj <= -2.22507e-308) or (obj >= 2.22507e-308 and obj <= 1.79769e+308):
            return 'double' #{name} = {repr(obj)};'
        else:
            return -1
    elif isinstance(obj, np.longdouble):
        if (obj >= -1.18973e+4932 and obj <= -3.3621e-4932) or (obj >= 3.3621e-4932 and obj <= 1.18973e+4932):
            return 'long double' #{name} = {repr(obj)}L;'
    elif isinstance(obj, str):
        return 'std::string'
    elif isinstance(obj, bool):
        return 'bool'
    else:
        return -1

class sos_xeus_cling:
    supported_kernels = {'C++11': ['xeus-cling-cpp11'], 'C++14' : ['xeus-cling-cpp14'], 'C++17' : ['xeus-cling-cpp17']}
    background_color = {'C++11': '#B3BFFF', 'C++14': '#D5CCFF', 'C++17': '#EAE6FF'}
    options = {}
    cd_command = '#include <unistd.h>\nchdir("{dir}");'

    def __init__(self, sos_kernel, kernel_name='C++11'):
        self.sos_kernel = sos_kernel
        self.kernel_name = kernel_name
        self.init_statements = cpp_init_statements

    def _Cpp_declare_command_string(self, name, obj):
        #Check if object is scalar
        if isinstance(obj, (Sequence, np.ndarray, dict, pd.core.frame.DataFrame)) and not isinstance(obj, str):
            #do vector things
            if len(obj) == 0:
                #TODO: how to deal with an empty array?
                return ''
            else:
                if isinstance(obj, dict): #convert Python dict to C++'s std::map
                    keys = obj.keys()
                    values = obj.values()
                    if homogeneous_type(keys) and homogeneous_type(values):
                        return f'std::map<{_sos_to_cpp_type(next(iter(keys)))}, {_sos_to_cpp_type(next(iter(values)))}> {name};'
                    else:
                        return None
                else:
                    return _sos_to_cpp_type(obj)
        else:
            #do scalar declaration
            obj_type = _sos_to_cpp_type(obj)
            if not obj_type == -1:
                return f'{obj_type} {name} = {repr(obj)};'
            else:
                return None

    def get_vars(self, names):
        for name in names:
            # self.sos_kernel.warn(name)
            cpp_repr = self._Cpp_declare_command_string(name, env.sos_dict[name])
            self.sos_kernel.warn(cpp_repr)
            if not cpp_repr==None:
                self.sos_kernel.run_cell(cpp_repr, True, False,
                 on_error=f'Failed to put variable {name} to C++')

    def put_vars(self, items, to_kernel=None):
        result = {}
        for item in items:
            # item - string with variable name (in C++)
            value = self.sos_kernel.get_response('std::cout<<{};'.format(item), ('stream',))[0][1]['text']
            cpp_type = self.sos_kernel.get_response(f'type({item})', ('execute_result',))[0][1]['data']['text/plain']
            self.sos_kernel.warn(value)
            self.sos_kernel.warn(cpp_type)

            #Convert string value to appropriate type in SoS
            integer_types = ['"int"', '"short"', '"long"', '"long long"']
            real_types = ['"float"', '"double"']
            if cpp_type in integer_types:
                self.sos_kernel.warn('converting integer type')
                result[item] = int(value)
            elif cpp_type in real_types:
                if value[-1] == 'f':
                    value = value[:-1]
                self.sos_kernel.warn('converting real number type')
                result[item] = float(value)
            elif cpp_type == '"long double"':
                self.sos_kernel.warn('converting long double number type')
                result[item] = np.longdouble(value)
            elif cpp_type == '"char"':
                self.sos_kernel.warn('converting char type')
                result[item] = value
            elif cpp_type == '"bool"':
                if value == 'true':
                    result[item] = True
                else:
                    result[item] = False
            else:
                self.sos_kernel.warn(f'Type {cpp_type} is not supported')
        return result
