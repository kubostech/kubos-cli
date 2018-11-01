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

from kubos import use
from kubos.utils.constants import *


class Args():
    def __init__(self):
        self.set_version = None
        self.branch = None


class UseTest(unittest.TestCase):
    @patch('kubos.utils.sdk_utils.link_to_global_cache')
    @patch('kubos.utils.sdk_utils.purge_global_cache')
    @patch('kubos.utils.git_utils.checkout_and_update_version')
    @patch('kubos.utils.git_utils.get_repo')
    def test_exec_command_with_branch(self, get_repo, checkout_and_update_version, purge_global_cache, link_to_global_cache):
        args = Args()
        branch = 'test-branch'
        args.branch = branch

        kubos_repo = 'test-repo'
        get_repo.return_value = kubos_repo

        use.execCommand(args, None)

        get_repo.assert_called_with(KUBOS_SRC_DIR)
        checkout_and_update_version.assert_called_with(branch, kubos_repo)
        purge_global_cache.assert_called()
        link_to_global_cache.assert_called_with(KUBOS_SRC_DIR)

    @patch('kubos.utils.sdk_utils.link_to_global_cache')
    @patch('kubos.utils.sdk_utils.purge_global_cache')
    @patch('kubos.utils.git_utils.check_provided_version')
    @patch('kubos.utils.git_utils.get_repo')
    def test_exec_command_with_version(self, get_repo, check_provided_version, purge_global_cache, link_to_global_cache):
        args = Args()
        version = 'test-version'
        args.set_version = version

        kubos_repo = 'test-repo'
        get_repo.return_value = kubos_repo

        use.execCommand(args, None)

        get_repo.assert_called_with(KUBOS_SRC_DIR)
        check_provided_version.assert_called_with(version, kubos_repo)
        purge_global_cache.assert_called()
        link_to_global_cache.assert_called_with(KUBOS_SRC_DIR)


if __name__ == '__main__':
    unittest.main()
