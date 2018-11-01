# Kubos CLI
# Copyright (C) 2017 Kubos Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import mock
import os
import shutil
import sys
import tempfile
import unittest


class KubosTestCase(unittest.TestCase):
    test_arg = None  # Additional command line argument needed by any specific test cases
    test_command = None  # Not all test cases define a 'test_command'

    def setUp(self):
        '''
        To start this clears any extra command line arguments used to start
        this test. Then create a temporary directory (base_dir) and cd into
        that directory. Then start the test case.
        '''
        first_arg = sys.argv[0]
        sys.argv = [first_arg]
        self.start_dir = os.getcwd()
        self.base_dir = tempfile.mkdtemp()
        os.chdir(self.base_dir)

    def assert_default_yotta_call(self):
        '''
        This tests to ensure that the default execCommand from yotta was called
        for the specific command being tested.
        '''
        call_list = self.test_function.call_args.call_list()
        self.assertTrue(len(call_list) == 1)
        args, kwargs = call_list[0]
        arg_dict = vars(args[0])
        self.assertTrue(arg_dict['subcommand_name'] == self.test_command)

    def tearDown(self):
        '''
        cd back to the starting directory of the test, then try to remove the
        temporary created for the test case. Finally try to remove any command
        line arguments added during the test case
        '''
        os.chdir(self.start_dir)
        shutil.rmtree(self.base_dir)
        try:
            sys.argv.remove(self.test_command)
        except ValueError:
            pass
        if self.test_arg in sys.argv:  # Not all tests requrire an additional argument
            sys.argv.remove(self.test_arg)
