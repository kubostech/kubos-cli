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
import json
import logging
import sys
import subprocess
import shutil
import os

from yotta.options import parser

from kubos.utils import git_utils, \
    sdk_utils, \
    status_spinner
from kubos.utils.constants import *

KUBOS_CLI_REPO_URL = 'git+https://github.com/kubos/kubos-cli'
INSTALL_COMMAND = ['sudo', 'pip', 'install', '--upgrade', KUBOS_CLI_REPO_URL]


def addOptions(parser):
    parser.add_argument('set_version', nargs='?', default=None,
                        help='Specify a version of the kubos source to use.')
    parser.add_argument('-l', '--latest', action='store_true', default=False,
                        help='Default to the most recent release of Kubos modules')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-s', '--source',  dest='component', action='store_const',
                       const='s', default=False, help='Update only the source Kubos modules')
    group.add_argument('-c', '--cli',     dest='component', action='store_const',
                       const='c', default=False, help='Update the Kubos CLI.')
    group.add_argument('-a', '--all',     dest='component', action='store_const', const='a',
                       default=False, help='Update both the Kubos source modules and the Kubos CLI')
    group.add_argument('-t', '--tab-completion', dest='component', action='store_const',
                       const='t', default=False, help='Update the tab completion definitions')
    # The default behavior is to only update the source modules.
    parser.set_defaults(component='s')


def execCommand(args, following_args):
    if args.component == 'a' or args.component == 's':
        update_source_modules(args)
    # TODO: I don't think this a check can ever be reached
    if args.component == 'a' or args.component == 'c':
        update_cli()
    if args.component == 't':
        update_tab_completions()


def update_cli():
    logging.info('Updating the Kubos CLI...')
    return_code = subprocess.check_call(INSTALL_COMMAND)
    if return_code == 0:
        logging.info('Successfully updated the Kubos CLI module')
    else:
        # The subprocess stdout/stderr is printed to the console. Any errors that occur will be visible there.
        logging.error(
            'There was an issue updating the Kubos CLI module. See the above log for the error details.')


def update_source_modules(args):
    if not os.path.isdir(KUBOS_DIR):
        os.makedirs(KUBOS_DIR)
    os.chdir(KUBOS_DIR)
    logging.info('Checking for the most recent KubOS Source...')
    spinner = status_spinner.start_spinner()
    src_repo = git_utils.clone_repo(KUBOS_SRC_DIR, KUBOS_SRC_URL)
    git_utils.clone_example_repo(KUBOS_RT_EXAMPLE_DIR, KUBOS_RT_EXAMPLE_URL)
    git_utils.clone_example_repo(
        KUBOS_LINUX_EXAMPLE_DIR, KUBOS_LINUX_EXAMPLE_URL)
    status_spinner.stop_spinner(spinner)
    set_version = args.set_version
    if set_version:
        logging.info('Setting provided release: %s' % set_version)
        git_utils.check_provided_version(set_version, src_repo)
    if args.latest:
        latest_tag = git_utils.get_latest_tag(git_utils.get_tag_list(src_repo))
        logging.info('Setting latest release: %s' % latest_tag)
        git_utils.check_provided_version(latest_tag, src_repo)


def update_tab_completions():
    logging.info("Setting up kubos tab completions...")
    if os.path.isdir(COMPLETION_LINK_DEST):
        # shutil.copytree requires the dest to not exist
        shutil.rmtree(COMPLETION_LINK_DEST)
    try:
        shutil.copytree(COMPLETION_RESOURCE_DIR, COMPLETION_LINK_DEST)
    except OSError:
        logging.info('The link %s to %s already exists.' %
                     (COMPLETION_RESOURCE_DIR, COMPLETION_LINK_DEST))

    completion_file = os.path.join(COMPLETION_LINK_DEST, 'kubos_completion')
    shell = os.environ['SHELL'] if 'SHELL' in os.environ else None
    username = os.environ['USER'] if 'USER' in os.environ else None
    if 'bash' not in shell:
        logging.warning(
            'Currently Bash is the only officially supported shell for tab completions.')
        logging.warning(
            "If you want to manually continue source the %s file to configure the kubos completions via the complete command." % completion_file)
        logging.warning(
            "Beware: This is not supported and there is no guarantee this will actually work with your current shell: %s" % shell)
        sys.exit(1)
    if username != 'vagrant':  # this is done during the vagrant provisioning
        logging.info(
            "If this is your first time setting up tab completion you will need to add the following line to your bash startup file of choice (.bashrc, .profile, etc")
        logging.info("source %s" % completion_file)
