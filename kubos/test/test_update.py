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

from kubos import update
from kubos.utils.constants import *


class Args():
    def __init__(self):
        self.component = None


class UpdateTest(unittest.TestCase):
    @patch('kubos.update.update_source_modules')
    def test_exec_command_update_source(self, update_source_modules):
        args = Args()
        args.component = 's'

        update.execCommand(args, None)

        update_source_modules.assert_called_with(args)

    @patch('kubos.update.update_cli')
    def test_exec_command_update_cli(self, update_cli):
        args = Args()
        args.component = 'c'

        update.execCommand(args, None)

        update_cli.assert_called()

    @patch('subprocess.check_call')
    @patch('logging.info')
    def test_update_cli_success(self, info, check_call):
        return_code = 0
        check_call.return_value = return_code

        update.update_cli()

        check_call.assert_called_with(update.INSTALL_COMMAND)
        calls = [
            call('Updating the Kubos CLI...'),
            call('Successfully updated the Kubos CLI module')
        ]
        info.assert_has_calls(calls)

    @patch('logging.error')
    @patch('subprocess.check_call')
    @patch('logging.info')
    def test_update_cli_error(self, info, check_call, error):
        return_code = -1
        check_call.return_value = return_code

        update.update_cli()

        check_call.assert_called_with(update.INSTALL_COMMAND)
        info.assert_called_with('Updating the Kubos CLI...')
        error.assert_called_with(
            'There was an issue updating the Kubos CLI module. See the above log for the error details.')

    @patch('kubos.utils.git_utils.get_tag_list')
    @patch('kubos.utils.git_utils.get_latest_tag')
    @patch('kubos.utils.git_utils.check_provided_version')
    @patch('kubos.utils.status_spinner.stop_spinner')
    @patch('kubos.utils.git_utils.clone_example_repo')
    @patch('kubos.utils.git_utils.clone_repo')
    @patch('kubos.utils.status_spinner.start_spinner')
    @patch('logging.info')
    @patch('os.chdir')
    @patch('os.path.isdir')
    def test_update_source_modules(self, isdir, chdir, info, start_spinner, clone_repo, clone_example_repo, stop_spinner, check_provided_version, get_latest_tag, get_tag_list):
        args = Args()
        set_version = 'test-set_version'
        args.set_version = set_version
        args.latest = True
        isdir.return_value = True
        spinner = 'test-spinner'
        start_spinner.return_value = spinner
        src_repo = 'test-src-repo'
        clone_repo.return_value = src_repo
        latest_tag = 'latest-tag'
        get_latest_tag.return_value = latest_tag
        tag_list = []
        get_tag_list.return_value = tag_list

        update.update_source_modules(args)

        isdir.assert_called_with(update.KUBOS_DIR)
        chdir.assert_called_with(update.KUBOS_DIR)
        info_calls = [
            call('Checking for the most recent KubOS Source...'),
            call('Setting provided release: %s' % set_version),
            call('Setting latest release: %s' % latest_tag)
        ]
        info.assert_has_calls(info_calls)
        start_spinner.assert_called()
        clone_repo.assert_called_with(
            update.KUBOS_SRC_DIR, update.KUBOS_SRC_URL)
        clone_example_repo_calls = [
            call(update.KUBOS_RT_EXAMPLE_DIR, update.KUBOS_RT_EXAMPLE_URL),
            call(update.KUBOS_LINUX_EXAMPLE_DIR,
                 update.KUBOS_LINUX_EXAMPLE_URL)
        ]
        clone_example_repo.assert_has_calls(clone_example_repo_calls)
        stop_spinner.assert_called_with(spinner)
        check_provided_version_calls = [
            call(set_version, src_repo),
            call(latest_tag, src_repo)
        ]
        check_provided_version.assert_has_calls(check_provided_version_calls)
        get_latest_tag.assert_called_with(tag_list)
        get_tag_list.assert_called_with(src_repo)


if __name__ == '__main__':
    unittest.main()
