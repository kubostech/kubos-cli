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
This file is an altered copy of yotta/lib/detect.py
Our specific changes alter the default yotta target
and change it to the x86-linux-native instead of
the x86-platform-native target which doesn't exist
in the kubos-cli context
'''

# standard library modules, , ,
import platform
import sys

# settings, , load and save settings, internal
from yotta.lib import settings


def defaultTarget(ignore_set_target=False):
    set_target = settings.getProperty('build', 'target')
    if set_target:
        return set_target
    else:
        return kubosDefaultTarget()


def kubosDefaultTarget():
    return 'x86-linux-native,*'


def systemDefaultTarget():
    return kubosDefaultTarget()
