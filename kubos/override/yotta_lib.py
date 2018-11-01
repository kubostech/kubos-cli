# Kubos SDK
# Copyright (C) 2016 Kubos Corporation
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

'''
This file deals with modifying all of the necessary functions in yotta/lib that
are required for removing certain yotta functionality. Remove some of yotta's
features, specficially the use of the yotta registry, allow it to be much more
convenient to use in the Kubos-cli.
'''

import yotta.lib.access
from reimplemented_modules import access, cmakegen, component, detect


def exec_override():
    yotta.lib.access = access
    yotta.lib.detect = detect
    yotta.lib.cmakegen = cmakegen
    yotta.lib.component = component
