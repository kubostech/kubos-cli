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

import kubos
import mock
import sys
import unittest
import yotta.build

from kubos.test.utils import KubosTestCase


class KubosBuildTest(KubosTestCase):
    '''
    Since the kubos build command proxies to the default yotta implementation
    this test only looks to make sure that the yotta implementation is called.
    There's a separate yotta unit test to test the build functionality.
    '''

    def setUp(self):
        super(KubosBuildTest, self).setUp()
        self.test_function = mock.MagicMock()
        yotta.build.execCommand = self.test_function
        self.test_command = 'build'
        sys.argv.append(self.test_command)

    def test_build(self):
        kubos.main()
        self.assert_default_yotta_call()

    def tearDown(self):
        super(KubosBuildTest, self).tearDown()


if __name__ == '__main__':
    unittest.main()
