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
import os
import unittest
from mock import patch, MagicMock, call
from pip.utils import get_installed_version

from kubos import link


class LinkTest(unittest.TestCase):
    def test_add_options(self):
        parser = MagicMock()
        parser.add_argument = MagicMock()
        link.addOptions(parser)
        calls = [
            call('-a', '--all', action='store_true', default=False,
                 help='Link all modules (and targets) from the global cache into the local project.'),
            call('module_or_path', default=None, nargs='?',
                 help='Link a globally installed (or globally linked) module into ' +
                 'the current module\'s dependencies. If ommited, globally ' +
                 'link the current module.'),
        ]
        parser.add_argument.assert_has_calls(calls)

    @patch('yotta.link.execCommand')
    def test_calls_yotta_link(self, yotta_link):
        class Args():
            def __init__(self):
                self.all = False
        args = Args()
        following_args = {'random-following-arg': 'random'}

        link.execCommand(args, following_args)

        yotta_link.assert_called_with(args, following_args)

    @patch('kubos.link.link_global_cache_to_project')
    def test_calls_global_cache(self, link_global_cache_to_project):
        class Args():
            def __init__(self):
                self.all = True
        args = Args()
        following_args = {'random-following-arg': 'random'}

        link.execCommand(args, following_args)

        link_global_cache_to_project.assert_called_with(os.getcwd())


if __name__ == '__main__':
    unittest.main()
