#!/usr/bin/env javascript
#
# Copyright (c) Konstantin Taletskiy
# Distributed under the terms of the MIT License.

import os
import unittest
from ipykernel.tests.utils import assemble_output, execute, wait_for_idle
from sos_notebook.test_utils import sos_kernel, get_result, get_display_data, clear_channels

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
            clear_channels(iopub)
            execute(kc=kc, code='%use C++14')
            wait_for_idle(kc)
            execute(kc=kc, code='%get int1 int2 int4 float1')
            wait_for_idle(kc)

            #Test int1
            execute(kc=kc, code='std::cout << int1;')
            stdout, _ = assemble_output(iopub)
            self.assertEqual(stdout.strip(),'10')

            # #Test int2
            # execute(kc=kc, code='std::cout << int2;')
            # stdout, _ = assemble_output(iopub)
            # self.assertEqual(stdout.strip(),'1000000000000000000')

            # #Test int4
            # execute(kc=kc, code='std::cout << int4;')
            # stdout, _ = assemble_output(iopub)
            # self.assertEqual(stdout.strip(),'20')


            execute(kc=kc, code="%use sos")
            wait_for_idle(kc)



if __name__ == '__main__':
    unittest.main()