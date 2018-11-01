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

import os
from pkg_resources import resource_filename

KUBOS_SRC_URL = 'https://github.com/kubos/kubos'
KUBOS_RT_EXAMPLE_URL = 'https://github.com/kubos/kubos-rt-example'
KUBOS_LINUX_EXAMPLE_URL = 'https://github.com/kubos/kubos-linux-example'

HOME_DIR = os.path.expanduser('~')
KUBOS_DIR = os.path.join(HOME_DIR, '.kubos')
KUBOS_SRC_DIR = os.path.join(KUBOS_DIR, 'kubos')
KUBOS_RT_EXAMPLE_DIR = os.path.join(KUBOS_DIR, 'rt-example')
KUBOS_LINUX_EXAMPLE_DIR = os.path.join(KUBOS_DIR, 'linux-example')

KUBOS_GIT_DIR = os.path.join(KUBOS_SRC_DIR, '.git')
KUBOS_VERSION_FILE = os.path.join(KUBOS_DIR, 'version.txt')
KUBOS_TARGET_CACHE_FILE = os.path.join(KUBOS_DIR, 'targets.json')

KUBOS_RESOURCE_DIR = os.path.join(resource_filename(__name__, ''), '..')
SDK_MODULE_JSON = os.path.join(KUBOS_RESOURCE_DIR, 'module.json')
GLOBAL_TARGET_PATH = os.path.join('/', 'usr', 'local', 'lib', 'yotta_targets')
GLOBAL_MODULE_PATH = os.path.join('/', 'usr', 'local', 'lib', 'yotta_modules')

LINUX_KEY = 'linux-targets'
RT_KEY = 'rt-targets'

COMPLETION_RESOURCE_DIR = os.path.join(KUBOS_RESOURCE_DIR, 'completion')
COMPLETION_SCRIPT = os.path.join(
    COMPLETION_RESOURCE_DIR, 'kubos_completion.bash')
COMPLETION_OPTIONS_FILE = os.path.join(COMPLETION_RESOURCE_DIR, 'options.json')
COMPLETION_PYTHON_FILE = os.path.join(COMPLETION_RESOURCE_DIR, 'completion.py')

COMPLETION_LINK_DEST = os.path.join(KUBOS_DIR, 'completion')

SHOW_NUMBER_CD_VERSIONS = 0
