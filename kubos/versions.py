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

import logging
import sys
import os

from packaging import version
from yotta.options import parser

from kubos.utils import git_utils
from kubos.utils.constants import *


def addOptions(parser):
    parser.add_argument('-a', '--all-versions', dest='filter',
                        action='store_false', default=True, help='Show all available versions')


def execCommand(args, following_args):
    if not os.path.isdir(KUBOS_SRC_DIR):
        logging.info(
            'No versions are locally available. Please run `kubos update` to pull all of the available source versions.')
        return 1
    repo = git_utils.get_repo(KUBOS_SRC_DIR)
    tag_list = git_utils.get_tag_list(repo)
    latest = git_utils.get_latest_tag(tag_list)
    logging.info('Available versions are:')
    git_utils.print_tag_list(tag_list, filter=args.filter)
    logging.info('The most recent release is: %s' % latest)
