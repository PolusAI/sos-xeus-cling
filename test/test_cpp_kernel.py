#!/usr/bin/env javascript
#
# Copyright (c) Konstantin Taletskiy
# Distributed under the terms of the MIT License.

import os
import unittest
from ipykernel.tests.utils import assemble_output, execute, wait_for_idle
from sos_notebook.test_utils import sos_kernel, get_result, get_display_data, clear_channels
from time import sleep

class TestCppKernel(unittest.TestCase):

    def setUp(self):
        self.olddir = os.getcwd()
        if os.path.dirname(__file__):
            os.chdir(os.path.dirname(__file__))

    def tearDown(self):
        os.chdir(self.olddir)

    def testPythonToCppScalars(self):
        with sos_kernel() as kc:
            iopub = kc.iopub_channel
            execute(kc=kc, code = '''
                import numpy as np
                int1 = 10
                int2 = 1000000000000000000
                int4 = np.intc(20)
                float1 = 0.1
                float2 = 1e+50
                float3 = np.longdouble("1e+1000")
                string1 = 'abc'
                bool1 = True
                ''')
            wait_for_idle(kc)

            execute(kc=kc, code='%use C++14')
            wait_for_idle(kc)

            execute(kc=kc, code='%get int1 int2 int4 float1 float2 float3 string1 bool1')
            wait_for_idle(kc)

            #Test int1
            execute(kc=kc, code='std::cout << int1;')
            stdout, _ = assemble_output(iopub)
            self.assertEqual(stdout.strip(),'10')

            #Test int2
            execute(kc=kc, code='std::cout << int2;')
            stdout, _ = assemble_output(iopub)
            self.assertEqual(stdout.strip(),'1000000000000000000')

            #Test int4
            execute(kc=kc, code='std::cout << int4;')
            stdout, _ = assemble_output(iopub)
            self.assertEqual(stdout.strip(),'20')

            #Test float1
            execute(kc=kc, code='std::cout << float1;')
            stdout, _ = assemble_output(iopub)
            self.assertEqual(stdout.strip()[:3],'0.1')

            #Test float2
            execute(kc=kc, code='std::cout << float2;')
            stdout, _ = assemble_output(iopub)
            self.assertEqual(stdout.strip(),'1e+50')

            #Test float3
            execute(kc=kc, code='std::cout << float3;')
            stdout, _ = assemble_output(iopub)
            self.assertEqual(stdout.strip(),'inf')

            #Test string1
            execute(kc=kc, code='std::cout << string1;')
            stdout, _ = assemble_output(iopub)
            self.assertEqual(stdout.strip(),'abc')

            #Test bool1
            execute(kc=kc, code='std::cout << (bool1?"true":"false");')
            stdout, _ = assemble_output(iopub)
            self.assertEqual(stdout.strip(),'true')

            execute(kc=kc, code="%use sos")
            wait_for_idle(kc)

    def testPythonToCppDataframe(self):
        with sos_kernel() as kc:
            iopub = kc.iopub_channel
            execute(kc=kc, code = '''
                import numpy as np
                import pandas as pd
                dataframe = pd.DataFrame(np.random.randn(1000,4), columns=list('ABCD'))
                ''')

            wait_for_idle(kc)
            execute(kc=kc, code='%use C++14')
            wait_for_idle(kc)
            execute(kc=kc, code='%get dataframe')
            wait_for_idle(kc)

            execute(kc=kc, code='std::cout << dataframe.size();')
            stdout, _ = assemble_output(iopub)
            self.assertEqual(stdout.strip(),'4000')

            execute(kc=kc, code="%use sos")
            wait_for_idle(kc)

    def testCpptoPythonScalars(self):
        with sos_kernel() as kc:
            iopub = kc.iopub_channel

            execute(kc=kc, code='%use C++14')
            wait_for_idle(kc)
            execute(kc=kc, code='''
                int i = 1;
                short int si = 32;
                long int li = 2000000000;
                long long int lli = 2000000000000000000;
                float f = 0.1f;
                double d = 1e+300;
                long double ld = 1e+1000L;
                bool b = true;
                char c = '*';
                std::map<int, int> m = {{1,2},{2,3}};
                std::map<std::string, float> m2 = {{"Alice", -1.0f},{"Bob", 1.0f}};
                std::map<std::string, bool> m3 = {{"Alice", true},{"Bob", false}};
                std::vector<int> v = {1,2,3,4,5};
                std::vector<bool> v2 = {true,false,true,false,true};
                std::vector<std::string> v3 = {"q","w","e","r","t","y"};
                xt::xarray<double> arr
                      {{1.1, 2.2, 3.3},
                       {4.4, 5.5, 6.6},
                       {7.7, 8.8, 9.9}};          
                xt::xarray<std::string> arr2
                      {{"1.1", "2.2", "a"},
                       {"4.4", "5.5", "6.6"},
                       {"7.7", "8.8", "9.9"}};
                ''')
            wait_for_idle(kc)
            execute(kc=kc, code='%put i si li lli f d ld b c m m2 m3 v v2 v3 arr arr2')
            wait_for_idle(kc)
            execute(kc=kc, code='%use sos')
            wait_for_idle(kc)

            execute(kc=kc, code='print(i)')
            stdout, _ = assemble_output(iopub)
            self.assertEqual(stdout.strip(),'1')

            execute(kc=kc, code='print(si)')
            stdout, _ = assemble_output(iopub)
            self.assertEqual(stdout.strip(),'32')

            execute(kc=kc, code='print(lli)')
            stdout, _ = assemble_output(iopub)
            self.assertEqual(stdout.strip(),'2000000000000000000')

            execute(kc=kc, code='print(f)')
            stdout, _ = assemble_output(iopub)
            self.assertEqual(stdout.strip()[:10],'0.10000000')

            execute(kc=kc, code='print(d)')
            stdout, _ = assemble_output(iopub)
            self.assertEqual(stdout.strip(),'1e+300')

            execute(kc=kc, code='print(ld)')
            stdout, _ = assemble_output(iopub)
            self.assertEqual(stdout.strip(),'1e+1000')

            execute(kc=kc, code='print(b)')
            stdout, _ = assemble_output(iopub)
            self.assertEqual(stdout.strip(),'True')

            execute(kc=kc, code='print(c)')
            stdout, _ = assemble_output(iopub)
            self.assertEqual(stdout.strip(),'*')

            execute(kc=kc, code='print(m[2])')
            stdout, _ = assemble_output(iopub)
            self.assertEqual(stdout.strip(),'3')

            execute(kc=kc, code='print(m2["Alice"])')
            stdout, _ = assemble_output(iopub)
            self.assertEqual(stdout.strip(),'-1.0')

            execute(kc=kc, code='print(m3["Bob"])')
            stdout, _ = assemble_output(iopub)
            self.assertEqual(stdout.strip(),'False')

            execute(kc=kc, code='print(v)')
            stdout, _ = assemble_output(iopub)
            self.assertEqual(stdout.strip(),'[1 2 3 4 5]')

            execute(kc=kc, code='print(sum(v2))')
            stdout, _ = assemble_output(iopub)
            self.assertEqual(stdout.strip(),'3')

            execute(kc=kc, code='print("".join(v3))')
            stdout, _ = assemble_output(iopub)
            self.assertEqual(stdout.strip(),'qwerty')

            execute(kc=kc, code='print(arr[1,1])')
            stdout, _ = assemble_output(iopub)
            self.assertEqual(stdout.strip(),'5.5')

            execute(kc=kc, code='print(arr2[0,2])')
            stdout, _ = assemble_output(iopub)
            self.assertEqual(stdout.strip(),'a')

if __name__ == '__main__':
    unittest.main()