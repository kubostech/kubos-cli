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

import argparse
import sys
import os
import json
import yotta.lib.globalconf as globalconf

from yotta import target
from yotta.options import parser

from kubos.utils.constants import GLOBAL_TARGET_PATH
from kubos.utils.sdk_utils import *


def addOptions(parser):
    proj_type = get_project_type()
    choices = load_target_list(proj_type)
    parser.add_argument('set_target', nargs='?', default=None, choices=choices,
                        help='Set a new target board or display the current target')
    parser.add_argument('-l', '--list', action='store_true',
                        default=False, help='List all of the available target names')


def execCommand(args, following_args):
    args = vars(args)
    # Confusingly the set_target key is the target the user wants to set, no the currently set target
    target = args['set_target']
    # this is either the currently set target or the default x86-linux-native target
    default_target = args['target']
    if args['list']:
        print_target_list()
    elif target != None:
        set_target(target)
    else:
        show_target(default_target)


def show_target(default_target):
    current_target = default_target
    if current_target:
        target_args = argparse.Namespace(plain=False,
                                         set_target=None,
                                         target=default_target)
        target.displayCurrentTarget(target_args)
    else:
        logging.warning('No target currently set')
        logging.info(
            'Use the "kubos target <target name>" command to set a target')
        print_target_list()


def set_target(new_target):
    available_target_list = get_target_list()
    logging.info('Setting Target: %s' % new_target.split('@')[0])

    if new_target in available_target_list:
        new_target_args = argparse.Namespace(target_or_path=new_target,
                                             config=None,
                                             target=new_target,
                                             set_target=new_target,
                                             save_global=False,
                                             no_install=False)
        target.execCommand(new_target_args, '')
        logging.info('Target Successfully Set to: %s' % new_target)
    else:
        if new_target != '':
            logging.error('Requested target %s not available.' % new_target)
            print_target_list()
            sys.exit(1)


def print_target_list():
    proj_type = get_project_type()
    target_list = load_target_list(proj_type)
    logging.info('Available targets are:\n')
    for _target in target_list:
        logging.info(_target)


def get_target_list():
    target_list = os.listdir(GLOBAL_TARGET_PATH)
    available_target_list = []

    for subdir in target_list:
        target_json = os.path.join(GLOBAL_TARGET_PATH, subdir, 'target.json')
        with open(target_json, 'r') as json_file:
            data = json.load(json_file)
            available_target_list.append(data['name'])
    return available_target_list
