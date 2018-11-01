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

import unittest
from mock import patch, MagicMock, call, mock_open
from pip.utils import get_installed_version

from kubos import target
from kubos.utils.constants import *

test_global_target = 'test-global-target'


class Args():
    def __init__(self):
        self.set_target = None
        self.target = None
        self.list = None
        self.plain = []


class TargetTest(unittest.TestCase):
    @patch('kubos.target.show_target')
    def test_shows_target_by_default(self, show_target):
        args = Args()

        target.execCommand(args, None)

        show_target.assert_called_with(None)

    @patch('kubos.target.print_target_list')
    def test_prints_target_list(self, print_target_list):
        args = Args()
        args.list = True

        target.execCommand(args, None)

        print_target_list.assert_called()

    @patch('yotta.target.execCommand')
    @patch('argparse.Namespace')
    @patch('logging.info')
    @patch('kubos.target.get_target_list')
    def test_sets_the_target(self, get_target_list, info, namespace, execCommand):
        new_target = 'test-target'
        new_target_args = Args()
        get_target_list.return_value = [new_target]
        namespace.return_value = new_target_args

        target.set_target(new_target)

        calls = [
            call('Setting Target: %s' % new_target.split('@')[0]),
            call('Target Successfully Set to: %s' % new_target)
        ]
        get_target_list.assert_called()
        info.assert_has_calls(calls)
        namespace.assert_called_with(target_or_path=new_target, config=None, target=new_target,
                                     set_target=new_target, save_global=False, no_install=False)
        execCommand.assert_called_with(new_target_args, '')

    @patch('sys.exit')
    @patch('kubos.target.print_target_list')
    @patch('logging.error')
    @patch('logging.info')
    @patch('kubos.target.get_target_list')
    def test_displays_error_when_invalid_target(self, get_target_list, info, error, print_target_list, sysexit):
        new_target = 'test-target'
        get_target_list.return_value = []

        target.set_target(new_target)

        get_target_list.assert_called()
        info.assert_called_with('Setting Target: %s' %
                                new_target.split('@')[0])
        error.assert_called_with(
            'Requested target %s not available.' % new_target)
        print_target_list.assert_called()
        sysexit.assert_called_with(1)

    @patch('logging.info')
    @patch('kubos.target.load_target_list')
    @patch('kubos.target.get_project_type')
    def test_prints_target_list(self, get_project_type, load_target_list, info):
        project_type = 'project-type'
        get_project_type.return_value = project_type
        target_test = 'test-target'
        target_list = [target_test]
        load_target_list.return_value = target_list

        target.print_target_list()

        get_project_type.assert_called()
        load_target_list.assert_called_with(project_type)
        calls = [
            call('Available targets are:\n'),
            call(target_test)
        ]
        info.assert_has_calls(calls)

    @patch('kubos.target.open', mock_open(read_data='{"name": "test"}'), create=True)
    @patch('os.path.join')
    @patch('kubos.target.GLOBAL_TARGET_PATH', test_global_target)
    @patch('os.listdir')
    def test_get_target_list(self, listdir, join):
        subdir = 'test-subdir'
        target_list = [subdir]
        listdir.return_value = target_list
        target_json = 'test-json-file'
        join.return_value = target_json

        available_list = target.get_target_list()
        self.assertEqual(available_list, ['test'])

        listdir.assert_called_with(test_global_target)
        join.assert_called_with(test_global_target, subdir, 'target.json')


if __name__ == '__main__':
    unittest.main()
