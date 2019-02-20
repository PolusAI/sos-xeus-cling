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
import sys

def homogeneous_type(seq):
    iseq = iter(seq)
    first_type = type(next(iseq))
    if first_type in (int, float):
        return True if all(isinstance(x, (int, float)) for x in iseq) else False
    else:
        return True if all(isinstance(x, first_type) for x in iseq) else False

#Include helper functions header and set std::cout rounding to a maximum length for double and float accuracy (https://stackoverflow.com/a/554780/6357726)
cpp_init_statements = f'#include "{os.path.split(__file__)[0]}/utils.hpp"\nstd::cout.precision(std::numeric_limits<double>::digits10 + 1);'

def stitch_cell_output(response):
    return ''.join([stream[1]['text'] for stream in response ])

def _sos_to_cpp_type(obj):
    ''' Returns corresponding C++ data type string for provided Python object '''
    if isinstance(obj, (int, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64, bool, np.bool_)):
        if isinstance(obj, (bool, np.bool_)):
            return 'bool', 'true' if obj==True else 'false'
        elif obj >= -2147483648 and obj <= 2147483647:
            return 'int', repr(obj)
        elif obj >= -9223372036854775808 and obj <= 9223372036854775807:
            return 'long int', repr(obj)
        else:
            return -1, None #Integer is out of bounds
    elif isinstance(obj, (float, np.float16, np.float32, np.float64)):
        if (obj >= -3.40282e+38 and obj <= -1.17549e-38) or (obj >= 1.17549e-38 and obj <= 3.40282e+38):
            return 'float', repr(obj)
        elif (obj >= -1.79769e+308 and obj <= -2.22507e-308) or (obj >= 2.22507e-308 and obj <= 1.79769e+308):
            return 'double', repr(obj)
        else:
            return -1, None
    elif isinstance(obj, np.longdouble):
        if (obj >= -1.18973e+4932 and obj <= -3.3621e-4932) or (obj >= 3.3621e-4932 and obj <= 1.18973e+4932):
            return 'long double', repr(obj)
    elif isinstance(obj, str):
        return 'std::string', '"'+obj+'"'
    
    else:
        return -1, None

def _cpp_scalar_to_sos(cpp_type, value):
    #Convert string value to appropriate type in SoS
    integer_types = ['"int"', '"short"', '"long"', '"long long"']
    real_types = ['"float"', '"double"']
    if cpp_type in integer_types:
        # self.sos_kernel.warn('converting integer type')
        return int(value)
    elif cpp_type in real_types:
        if value[-1] == 'f':
            value = value[:-1]
        # self.sos_kernel.warn('converting real number type')
        return float(value)
    elif cpp_type == '"long double"':
        # self.sos_kernel.warn('converting long double number type')
        return np.longdouble(value)
    elif cpp_type == '"char"':
        # self.sos_kernel.warn('converting char type')
        return value
    elif cpp_type.startswith('"std::__cxx11::basic_string') or cpp_type.startswith('"xtl::xbasic_fixed_string'):
        return value
    elif cpp_type in ['"bool"', '"std::_Bit_reference"']:
        if value == '1':
            return True
        else:
            return False

class sos_xeus_cling:
    background_color = {'C++11': '#B3BFFF', 'C++14': '#D5CCFF', 'C++17': '#EAE6FF'}
    supported_kernels = {'C++11': ['xeus-cling-cpp11'], 'C++14' : ['xeus-cling-cpp14'], 'C++17' : ['xeus-cling-cpp17']}
    options = {}
    cd_command = '#include <unistd.h>\nchdir("{dir}");'

    def __init__(self, sos_kernel, kernel_name='C++11'):
        self.sos_kernel = sos_kernel
        self.kernel_name = kernel_name
        self.init_statements = cpp_init_statements

    def insistent_get_response(self, command, stream):
        response = self.sos_kernel.get_response(command, stream)
        while response==[]:
            response = self.sos_kernel.get_response(command, stream)

        return response


    def _Cpp_declare_command_string(self, name, obj):
        #Check if object is scalar
        if isinstance(obj, (int, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64, float, np.float16, np.float32, np.float64, np.longdouble, str, bool, np.bool_)):
            #do scalar declaration
            obj_type, obj_val = _sos_to_cpp_type(obj)
            if not obj_type == -1:
                return f'{obj_type} {name} = {obj_val};'
            else:
                return None
        elif isinstance(obj, (Sequence, np.ndarray, dict, pd.core.frame.DataFrame)):
            #do vector things
            if len(obj) == 0:
                #TODO: how to deal with an empty array?
                return ''
            else:
                if isinstance(obj, dict): #convert Python dict to C++'s std::map
                    keys = obj.keys()
                    values = obj.values()
                    if homogeneous_type(keys) and homogeneous_type(values):
                        dict_value = '{ ' + ', '.join([f'{{{ _sos_to_cpp_type(d[0])[1] }, { _sos_to_cpp_type(d[1])[1] }}}' for d in obj.items()])  + ' }'
                        return f'std::map<{_sos_to_cpp_type(next(iter(keys)))[0]}, {_sos_to_cpp_type(next(iter(values)))[0]}> {name} = {dict_value};'
                    else:
                        return None
                elif isinstance(obj, Sequence):
                    if homogeneous_type(obj):
                        seq_value = '{ ' + ', '.join([_sos_to_cpp_type(s)[1] for s in obj]) + ' }'
                        return f'std::vector<{ _sos_to_cpp_type(next(iter(obj)))[0] }> {name} = {seq_value};'
                    else:
                        return None
                elif isinstance(obj, np.ndarray):
                    ndarr_value = '{ ' + ', '.join([_sos_to_cpp_type(s)[1] for s in obj.flatten()]) + ' }'
                    ndarr_shape = '{ ' + ','.join([str(i) for i in obj.shape]) + ' }'
                    return f'xt::xarray<{ _sos_to_cpp_type(obj.flat[0])[0] }> {name} = {ndarr_value}; {name}.reshape({ndarr_shape})'
                elif isinstance(obj, pd.core.frame.DataFrame):
                    df_cols = '{ ' + ','.join([_sos_to_cpp_type(j)[1] for j in obj.columns.tolist()]) + ' }'
                    df_rows = '{ ' + ','.join([_sos_to_cpp_type(i)[1] for i in obj.index.values]) + ' }'
                    df_type = _sos_to_cpp_type(obj.values.flatten()[0])[0]
                    df_flat_list = '{ ' + ', '.join([_sos_to_cpp_type(s)[1] for s in obj.values.flatten()]) + ' }'
                    df_shape = '{ ' + ','.join([str(i) for i in obj.values.shape]) + ' }'
                    return f'xt::xarray<{df_type}> {name}_data = {df_flat_list}; {name}_data.reshape({df_shape}); auto {name}_x_axis = xf::axis({df_rows}); auto {name}_y_axis = xf::axis({df_cols}); auto {name}_coord = xf::coordinate({{{{"x", {name}_x_axis}}, {{"y", {name}_y_axis}}}}); auto {name}_dim = xf::dimension({{"x", "y"}}); auto {name} = xf::variable({name}_data,{name}_coord,{name}_dim);'
        else:
            #unsupported type
            return None

    def get_vars(self, names):
        for name in names:
            # self.sos_kernel.warn(name)
            cpp_repr = self._Cpp_declare_command_string(name, env.sos_dict[name])
            # self.sos_kernel.warn(cpp_repr)
            if not cpp_repr==None:
                self.sos_kernel.run_cell(cpp_repr, True, False,
                 on_error=f'Failed to put variable {name} to C++')

    def put_vars(self, names, to_kernel=None):
        result = {}
        for name in names:
            # name - string with variable name (in C++)
            cpp_type = self.insistent_get_response(f'type({name})', ('execute_result',))[0][1]['data']['text/plain']

            if cpp_type in ('"int"', '"short"', '"long"', '"long long"', '"float"', '"double"', '"long double"', '"char"', '"bool"', '"std::_Bit_reference"', '"std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >"'):
                #do scalar conversion
                value = self.insistent_get_response(f'std::cout<<{name};', ('stream',))[0][1]['text']
                result[name] = _cpp_scalar_to_sos(cpp_type, value)

            elif cpp_type.startswith('"std::map'):
                #convert map to a dict of strings
                value = '{' + self.insistent_get_response(f'for (auto it={name}.begin(); it!={name}.end(); ++it) std::cout << "\\"" << it->first << "\\":\\"" << it->second << "\\",";', ('stream',))[0][1]['text'] + '}'
                temp_dict = dict(eval(value))
                #convert string to appropriate Python types
                key_cpp_type = self.insistent_get_response(f'type({name}.begin()->first)', ('execute_result',))[0][1]['data']['text/plain']
                val_cpp_type = self.insistent_get_response(f'type({name}.begin()->second)', ('execute_result',))[0][1]['data']['text/plain']
                result[name] = dict({_cpp_scalar_to_sos(key_cpp_type, key) : _cpp_scalar_to_sos(val_cpp_type, val) for (key, val) in temp_dict.items()})

            elif cpp_type.startswith('"std::vector'):
                #convert std::vector to array of strings which hold variable values
                flat_list = '[' + self.insistent_get_response(f'for(auto it={name}.begin(); it!={name}.end(); ++it) std::cout << "\\"" << *it << "\\",";', ('stream',))[0][1]['text'] + ']'
                el_type = self.insistent_get_response(f'type(*{name}.begin())', ('execute_result',))[0][1]['data']['text/plain']
                result[name] = np.array([_cpp_scalar_to_sos(el_type, el) for el in eval(flat_list)])

            elif cpp_type.startswith('"xt::xarray_container') or cpp_type.startswith('"xt::xfunction'):
                #convert xarray
                # flat_array = eval(self.sos_kernel.get_response(f'std::cout<<xt::flatten({name});', ('stream',))[0][1]['text'].replace('{','[').replace('}',']'))
                flat_list = '[' + self.insistent_get_response(f'for(auto it={name}.begin(); it!={name}.end(); ++it) std::cout << "\\"" << *it << "\\",";', ('stream',))[0][1]['text'] + ']'
                # self.sos_kernel.warn(eval(flat_list))
                shape = eval('(' + self.insistent_get_response(f'for (auto& el : {name}.shape()) {{std::cout << el << ", "; }}', ('stream',))[0][1]['text'] + ')')  #https://github.com/QuantStack/xtensor/issues/1247
                el_type = self.insistent_get_response(f'type(*{name}.begin())', ('execute_result',))[0][1]['data']['text/plain']
                result[name] = np.array([_cpp_scalar_to_sos(el_type, el) for el in eval(flat_list)]).reshape(shape)

            elif cpp_type.startswith('"xf::xvariable_container'):
                #convert xframe to pd.dataframe
                flat_list = eval( '[' + stitch_cell_output(self.insistent_get_response(f'for(auto it={name}.data().begin(); it!={name}.data().end(); ++it) std::cout << "\\"" << *it << "\\",";', ('stream',))) + ']' )
                shape = eval('(' + stitch_cell_output(self.insistent_get_response(f'for (auto& el : {name}.shape()) {{std::cout << el << ", "; }}', ('stream',))) + ')')
                el_type = self.insistent_get_response(f'type(*{name}.data().begin())', ('execute_result',))[0][1]['data']['text/plain']
                column_labels = eval('[' + stitch_cell_output( self.insistent_get_response(f'print_dataframe_indices({name},1)', ('stream',)) ) + ']')
                row_labels = eval('[' + stitch_cell_output( self.insistent_get_response(f'print_dataframe_indices({name},0)', ('stream',)) ) + ']')
                result[name] = pd.DataFrame(np.array([_cpp_scalar_to_sos(el_type, el) for el in flat_list]).reshape(shape), columns=column_labels, index=row_labels )

            else:
                self.sos_kernel.warn(f'Type {cpp_type} is not supported')
        return result
