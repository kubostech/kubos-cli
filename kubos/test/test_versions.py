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
from mock import patch, MagicMock, call
from pip.utils import get_installed_version

from kubos import versions
from kubos.utils.constants import *


class VersionsTest(unittest.TestCase):
    @patch('kubos.utils.git_utils.print_tag_list')
    @patch('kubos.utils.git_utils.get_latest_tag')
    @patch('kubos.utils.git_utils.get_tag_list')
    @patch('kubos.utils.git_utils.get_repo')
    @patch('logging.info')
    def test_exec_command(self, info, get_repo, get_tag_list, get_latest_tag, print_tag_list):
        filterArg = 'test-filter'

        class Args():
            def __init__(self):
                self.filter = filterArg
        args = Args()

        repo = 'test-report'
        latest = 'test-latest'
        tag_list = 'test-taglist'
        get_repo.return_value = repo
        get_tag_list.return_value = tag_list
        get_latest_tag.return_value = latest

        versions.execCommand(args, None)

        get_repo.assert_called_with(KUBOS_SRC_DIR)
        get_tag_list.assert_called_with(repo)
        get_latest_tag.assert_called_with(tag_list)
        print_tag_list.assert_called_with(tag_list, filter=filterArg)
        calls = [
            call('Available versions are:'),
            call('The most recent release is: %s' % latest)
        ]
        info.assert_has_calls(calls)

    @patch('kubos.versions.KUBOS_SRC_DIR', '')
    @patch('logging.info')
    def test_exec_command_with_no_directory(self, info):
        versions.execCommand(None, None)

        info.assert_called_with(
            'No versions are locally available. Please run `kubos update` to pull all of the available source versions.')


if __name__ == '__main__':
    unittest.main()
