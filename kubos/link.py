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

from yotta import link
from yotta.options import parser

from kubos.utils.sdk_utils import *
from kubos.init import remove_unruly_rt_dependencies


def addOptions(parser):
    parser.add_argument('-a', '--all', action='store_true', default=False,
                        help='Link all modules (and targets) from the global cache into the local project.')
    parser.add_argument('module_or_path', default=None, nargs='?',
                        help='Link a globally installed (or globally linked) module into ' +
                        'the current module\'s dependencies. If ommited, globally ' +
                        'link the current module.'
                        )


def execCommand(args, following_args):
    '''
    Defining a specific `kubos link` command allows the CLI to "bulk" link all of the global targets
    and modules into a project in one step. This is useful for instances where either new kubos modules
    are added after a Kubos update, or for projects that were cloned from github rather than created
    with the CLI `init` command.

    If the -a or --all argument is not provided this command proxies to the default yotta command
    implementation.
    '''

    arg_dict = vars(args)
    if arg_dict['all']:
        link_global_cache_to_project(os.getcwd())
        proj_type = get_project_type()
        if proj_type == 'rt':
            remove_unruly_rt_dependencies()
    else:
        # pass in the args argparse.Namespace object - not the dictionary from above
        link.execCommand(args, following_args)
