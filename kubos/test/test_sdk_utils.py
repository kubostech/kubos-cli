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

import json
import kubos
import mock
import os
import sys
import unittest

from yotta.test.cli.util import Test_Trivial_Lib
from yotta.test.cli.test_target import Test_Module_JSON
from yotta import link, link_target

from kubos.utils import sdk_utils
from kubos.test.utils import KubosTestCase

from sets import Set


class KubosSdkUtilsTest(KubosTestCase):

    def setUp(self):
        super(KubosSdkUtilsTest, self).setUp()
        '''
        Make the following directory structure to test the recursive module/target discovery function
        .../base_dir
               |____ dir_a
               |        |____ module.json
               |____ dir_b
               |         |____ dir_c
               |                  |____ target.json
               |____ dir_d
        '''
        self.dir_a = os.path.join(self.base_dir, 'dir_a')
        self.dir_b = os.path.join(self.base_dir, 'dir_b')
        self.dir_c = os.path.join(self.dir_b, 'dir_c')
        self.dir_d = os.path.join(self.base_dir, 'dir_d')
        self.module_json = os.path.join(self.dir_a, 'module.json')
        self.target_json = os.path.join(self.dir_c, 'target.json')

        os.makedirs(self.dir_a)
        os.makedirs(self.dir_b)
        os.makedirs(self.dir_c)
        os.makedirs(self.dir_d)

        with open(self.module_json, 'w') as module_file:
            module_file.write(Test_Module_JSON)
        with open(self.target_json, 'w') as target_file:
            target_file.write(Test_Module_JSON)

    @mock.patch('yotta.link.execCommand', mock.MagicMock())
    @mock.patch('yotta.link_target.execCommand', mock.MagicMock())
    def test_link_target_to_proj(self):
        json_data = json.loads(Test_Module_JSON)
        expected_args = {'save_global': True,
                         'module_or_path': json_data['name'],
                         'target': 'x86-linux-native,*',
                         'no_install': False,
                         'target_or_path': json_data['name'],
                         'config': None}
        # Link the module to an arbitrary location
        sdk_utils.run_link(self.module_json, self.dir_a)
        link.execCommand.assert_called()
        link_target.execCommand.assert_not_called()
        args, kwargs = link.execCommand.call_args[0]
        self.assertEqual(expected_args, vars(args))

    @mock.patch('yotta.link.execCommand', mock.MagicMock())
    @mock.patch('yotta.link_target.execCommand', mock.MagicMock())
    def test_link_local_to_global_cache(self):
        expected_args = {'save_global': True,
                         'module_or_path': None,
                         'target': 'x86-linux-native,*',
                         'no_install': False,
                         'target_or_path': None,
                         'config': None}
        # link test target to the "global cache" of targets
        sdk_utils.run_link(self.target_json, None)
        link.execCommand.assert_not_called()
        link_target.execCommand.assert_called_once()
        args, kwargs = link_target.execCommand.call_args[0]
        self.assertEqual(expected_args, vars(args))

    @mock.patch('kubos.utils.sdk_utils.run_link', mock.MagicMock())
    def test_link_entities_discovery(self):
        sys.argv.append('link')
        sdk_utils.link_entities(self.base_dir, None)
        self.assertEqual(sdk_utils.run_link.call_count, 2)
        call_list = sdk_utils.run_link.call_args_list
        expected_args = [self.module_json, self.target_json]
        idx = 0
        for call in call_list:
            args, kwargs = call[0]
            self.assertTrue(args in expected_args)
            idx = idx + 1

    def test_get_all_eligible_targets(self):
        '''
        setup target hierarchy:

        target_a
        |_target_b
          |_target_c

        target_c should be the only target that is an eligible target
        '''

        inherit_json = '{"name" : "%s", "inherits" : {"%s" : "Fake repo url"}}'
        no_inherit_json = '{"name": "%s"}'
        expected_targets = Set(['target_c'])
        target_json = 'target.json'

        with open(os.path.join(self.dir_a, target_json), 'w') as target_file:
            target_file.write(no_inherit_json % 'target_a')
            print os.path.join(self.dir_a, target_json)
        with open(os.path.join(self.dir_b, target_json), 'w') as target_file:
            target_file.write(inherit_json % ('target_b', 'target_a'))
        with open(os.path.join(self.dir_d, target_json), 'w') as target_file:
            target_file.write(inherit_json % ('target_c', 'target_b'))

        # Now the actual testing bits
        targets = sdk_utils.get_all_eligible_targets(self.base_dir)
        self.assertEqual(targets, expected_targets)

    def tearDown(self):
        super(KubosSdkUtilsTest, self).tearDown()


if __name__ == '__main__':
    unittest.main()
