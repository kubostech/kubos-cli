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

from kubos import version


class VersionTest(unittest.TestCase):
    def test_add_options(self):
        parser = MagicMock()
        parser.add_argument = MagicMock()
        version.addOptions(parser)
        parser.add_argument.assert_called_with('-l', '--list', action='store_true',
                                               default=False, help='List all of the locally available KubOS source versions')

    @patch('kubos.utils.git_utils.get_active_kubos_version')
    @patch('logging.info')
    def test_exec_command(self, info, get_active_kubos_version):
        kubos_version = get_installed_version('kubos-cli')
        get_active_kubos_version.return_value = kubos_version

        version.execCommand(None, None)

        get_active_kubos_version.assert_called()
        calls = [
            call('Kubos-CLI version    : %s' %
                 'v' + get_installed_version('kubos-cli')),
            call('Kubos Source version : %s' % kubos_version)
        ]
        info.assert_has_calls(calls)

    @patch('kubos.utils.git_utils.print_tag_list')
    @patch('kubos.utils.git_utils.get_tag_list')
    @patch('kubos.utils.git_utils.get_repo')
    @patch('kubos.utils.git_utils.get_active_kubos_version')
    @patch('logging.info')
    def test_exec_command_with_no_version_and_directory(self, info, get_active_kubos_version, get_repo, get_tag_list, print_tag_list):
        kubos_version = ''
        get_active_kubos_version.return_value = kubos_version

        version.execCommand(None, None)

        get_repo.assert_called()
        get_tag_list.assert_called()
        print_tag_list.assert_called()
        calls = [
            call('Kubos-CLI version    : %s' %
                 'v' + get_installed_version('kubos-cli')),
            call('Kubos Source version : %s' % kubos_version),
            call('There\'s not an active Kubos source version..'),
            call('The available versions are:'),
            call('Please run kubos use <version> (with one of the above versions)' +
                 'to checkout a version of the source before working with a project.')
        ]
        info.assert_has_calls(calls)

    @patch('kubos.version.KUBOS_SRC_DIR', '')
    @patch('kubos.utils.git_utils.get_active_kubos_version')
    @patch('logging.info')
    def test_exec_command_with_no_version_and_no_directory(self, info, get_active_kubos_version):
        kubos_version = ''
        get_active_kubos_version.return_value = kubos_version

        version.execCommand(None, None)

        calls = [
            call('Kubos-CLI version    : %s' %
                 'v' + get_installed_version('kubos-cli')),
            call('Kubos Source version : %s' % kubos_version),
            call('There are not any local versions of the kubos source currently.'),
            call('Please run `kubos update` to pull the kubos source before running `kubos version` again')
        ]
        info.assert_has_calls(calls)


if __name__ == '__main__':
    unittest.main()
