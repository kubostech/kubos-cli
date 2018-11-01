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
# limitations under the License.import argparse

import argparse
import kubos
import os
import tempfile
import unittest

from kubos import init
from kubos.test import utils
from kubos.utils import constants
from mock import patch
from yotta.test.cli.test_target import Test_Module_JSON  # A dummy module.json config


class KubosInitTest(utils.KubosTestCase):

    def setUp(self):
        super(KubosInitTest, self).setUp()
        self.proj_name = 'test-project'
        self.args = argparse.Namespace()
        # argparse returns proj_name as an array
        self.args.proj_name = [self.proj_name]
        self.args.linux = False
        linux_module_json = os.path.join(
            constants.KUBOS_LINUX_EXAMPLE_DIR, 'module.json')
        rt_module_json = os.path.join(
            constants.KUBOS_RT_EXAMPLE_DIR, 'module.json')

        # Set up the linux example module
        if not os.path.isdir(constants.KUBOS_LINUX_EXAMPLE_DIR):
            os.makedirs(constants.KUBOS_LINUX_EXAMPLE_DIR)
        if not os.path.isfile(linux_module_json):
            with open(linux_module_json, 'w') as mod_json:
                mod_json.write(Test_Module_JSON)

        # Set up the rt example module
        if not os.path.isdir(constants.KUBOS_RT_EXAMPLE_DIR):
            os.makedirs(constants.KUBOS_RT_EXAMPLE_DIR)
        if not os.path.isfile(rt_module_json):
            with open(rt_module_json, 'w') as mod_json:
                mod_json.write(Test_Module_JSON)

        # Set up a dummy global module and target cache
        if not os.path.isdir(constants.GLOBAL_TARGET_PATH):
            os.makedirs(constants.GLOBAL_TARGET_PATH)
        if not os.path.isdir(constants.GLOBAL_MODULE_PATH):
            os.makedirs(constants.GLOBAL_MODULE_PATH)

    def test_creates_proj_dir(self):
        self.proj_dir = os.path.join(self.base_dir, self.proj_name)
        kubos.init.execCommand(self.args, None)
        self.assertTrue(os.path.isdir(self.proj_dir))

    @patch('kubos.init.remove_unruly_rt_dependencies')
    def test_rt_init_removes_rt_toublesome_dependencies(self, remove_deps):
        # self.args already contains linux=False
        kubos.init.execCommand(self.args, None)
        remove_deps.assert_called_once()

    @patch('kubos.init.remove_unruly_rt_dependencies')
    def test_linux_init_does_not_remove_rt_toublesome_dependencies(self, remove_deps):
        self.args.linux = True
        kubos.init.execCommand(self.args, None)
        remove_deps.assert_not_called()

    def test_overwrite_existing(self):
        self.proj_name = 'test-project'
        self.proj_dir = os.path.join(self.base_dir, self.proj_name)
        with self.assertRaises(SystemExit):
            kubos.init.execCommand(self.args, None)
            # we cd into the project directory to change the module.json file in execCommand
            os.chdir(self.base_dir)
            kubos.init.execCommand(self.args, None)

    def tearDown(self):
        super(KubosInitTest, self).tearDown()


if __name__ == '__main__':
    unittest.main()
