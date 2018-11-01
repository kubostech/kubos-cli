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
import os
import shutil
import yotta
import yotta.link
import yotta.link_target

from sets import Set
from kubos.utils.constants import *


def get_sdk_attribute(attr):
    sdk_data = json.load(open(SDK_MODULE_JSON, 'r'))
    if attr in sdk_data:
        return sdk_data[attr]
    else:
        return None


def get_module_name(path):
    if not os.path.isfile(path):
        return None
    string = open(path, 'r').read()
    data = json.loads(string)
    return data['name']


def is_module_or_target_root(entity_name):
    # Determine if the directory name is at the root of a module or target
    # The module.json and target.json file names mark the "root" of a module
    marker_names = ['module.json',
                    'target.json']
    return entity_name in marker_names


'''
The following functions are used for recursively creating links too and from the global
cache (located at /usr/local/lib/yotta_*).

`kubos update` command will link all modules
to the global cache after downloading newer kubos source.

`kubos link --all` will link all of the modules and target in the global cache into a
project.
'''


def link_entities(src, dst):
    '''
    This function is used for recursively searching subdirectories for module and target
    roots ie. where a module.json or target.json file exists once a root is found, the
    linking function is called.
    '''
    logging.disable(
        logging.WARNING)  # suppress yotta warning for linking non-required modules and targets
    for subdir in os.listdir(src):
        # loop through the subdirectories of src
        # but don't go down the rabbit hole of yotta_module symlinks
        if "yotta_modules" in subdir:
            continue
        if "yotta_targets" in subdir:
            continue
        if "build" in subdir:
            continue
        cur_dir = os.path.join(src, subdir)
        if is_module_or_target_root(subdir):
            # if we're pointing to a target.json or module.json - link the module and return
            # NOTE: This assumes there are not nested modules
            run_link(cur_dir, dst)
            return
        elif os.path.isdir(cur_dir):
            # if we're looking at a subdirectory recursively search for a module root
            link_entities(cur_dir, dst)


def run_link(src, dst):
    '''
    This is used for proxying to the yotta link and link_target commands that actually
    generate the links to or from the global cache.
    '''
    link_module = yotta.link if 'module' in src else yotta.link_target
    if dst:
        # we're linking to a project from the global cache so we need to link the module by name
        entity_name = get_module_name(src)
        path = dst
    else:
        # we're linking to the global cache, the default behavior of a None module/target name
        # is linking it to the global cache.
        entity_name = None
        path = os.path.dirname(src)
    start_dir = os.getcwd()
    os.chdir(path)
    link_args = argparse.Namespace(module_or_path=entity_name,
                                   target_or_path=entity_name,
                                   config=None,
                                   target=yotta.lib.detect.systemDefaultTarget(),
                                   save_global=True,
                                   no_install=False)
    link_module.execCommand(link_args, '')
    os.chdir(start_dir)


def purge_global_cache():
    shutil.rmtree(GLOBAL_MODULE_PATH)
    shutil.rmtree(GLOBAL_TARGET_PATH)


def link_global_cache_to_project(project):
    logging.info('Linking modules...')
    link_entities(GLOBAL_MODULE_PATH, project)
    logging.info('Linking targets...')
    link_entities(GLOBAL_TARGET_PATH, project)


def link_to_global_cache(path):
    link_entities(path, None)
    refresh_target_cache()


def get_target_lists():
    '''
    Splits rt and linux targets.
    Returns the list of kubos_rt targets and the list of linux targets.
    '''
    linux_list = []
    rt_list = []
    target_list = get_all_eligible_targets(GLOBAL_TARGET_PATH)

    # TODO: Get a better way of determining linux targets
    for target in target_list:
        if 'linux' in target:
            linux_list.append(target)
        else:
            rt_list.append(target)
    return rt_list, linux_list


def get_all_eligible_targets(path):
    '''
    Returns the list of targets which do not have dependent targets.
    Example target hierarchy:
    kubos-gcc
      |____x86-linux-native <- This is the only target we want to build
    The other targets in the hierarchy are not meant to be built against
    '''
    inherit_key = 'inherits'
    name_key = 'name'
    ineligible_set = Set()
    complete_set = Set()
    target_dir_list = os.listdir(path)

    for subdir in target_dir_list:
        json_data = get_target_json_data(path, subdir)
        if name_key in json_data:
            complete_set.add(json_data['name'])
        if inherit_key in json_data:
            # The target this current target depends on is an ineligible target
            target_dependency = json_data[inherit_key].keys()
            ineligible_set.add(*target_dependency)
    return complete_set - ineligible_set


def get_target_json_data(path, subdir):
    target_json = os.path.join(path, subdir, 'target.json')
    if os.path.isfile(target_json):
        with open(target_json, 'r') as target_file:
            json_data = json.loads(target_file.read())
            return json_data
    return None


def refresh_target_cache():
    '''
    This function stores the linux and rt targets in a cache file under the .kubos directory
    '''
    data = {}

    rt_targets, linux_targets = get_target_lists()
    data[LINUX_KEY] = linux_targets
    data[RT_KEY] = rt_targets
    with open(KUBOS_TARGET_CACHE_FILE, 'w') as target_file:
        target_file.write(json.dumps(data))


def load_target_list(platform):
    if not os.path.isdir(KUBOS_TARGET_CACHE_FILE):
        refresh_target_cache()
    with open(KUBOS_TARGET_CACHE_FILE, 'r') as json_file:
        data = json.loads(json_file.read())
    linux_targets = data[LINUX_KEY]
    rt_targets = data[RT_KEY]
    if platform == None:  # if no platform is listed in the module.json, dont restrict the target type
        return linux_targets + rt_targets
    elif platform == 'linux':
        return linux_targets
    elif platform == 'rt':
        return rt_targets


def get_project_type():
    '''
    Returns the project "platform" type: either None, 'linux', or 'rt'
    This infers the project type from its dependencies. Kubos-rt is the
    key dependency that differentiates linux and rt projects.

    A return value of None will not limit or filter any target types
    '''
    dependency_key = 'dependencies'
    valid_platforms = ['rt', 'linux']
    module_json = os.path.join(os.getcwd(), 'module.json')
    if os.path.isfile(module_json):
        with open(module_json, 'r') as module_file:
            data = json.loads(module_file.read())
        if dependency_key in data:
            deps = data[dependency_key]
            if 'kubos-rt' in deps:
                return 'rt'
            else:
                return 'linux'
        else:
            # This project doesn't have a dependencies field. This is most likely running in a unit testing context
            return None
    else:
        # There is no module.json
        return None
