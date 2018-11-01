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

import git
import logging
import packaging.version
import re
import os
import sys

from kubos.utils import sdk_utils
from kubos.utils.constants import *


def get_repo(path):
    repo = git.Repo(path)
    return repo


def get_tag_list(repo):
    tags = repo.tags
    tag_list = []
    for tag in tags:
        tag_list.insert(0, tag.name)
    return tag_list


def filter_cd_generated_tags(display_num, tag_list):
    '''
    cd_generated_versions are the auto generated releases from the CD configuration. With
    every merge to master of the kubos repo one of these release tags is generated.

    ga_release_versions are manually created, more significant (general availability) releases that should have higher levels
    of stability than cd_generated_version releases will.

    This function filters only the most recent display_num number of cd_generated_versions from tag_list.
    '''
    filtered_tags = []
    ga_release_version = re.compile('v?\d+\.\d+\.\d+')
    cd_generated_version = re.compile('v?\d+\.\d+\.\d+\.\d+')
    for tag in tag_list:
        if cd_generated_version.match(tag):
            if display_num <= 0:
                continue
            filtered_tags.append(tag)
            display_num = display_num - 1
        elif ga_release_version.match(tag):
            filtered_tags.append(tag)
    return filtered_tags


def print_tag_list(tag_list, filter=True):
    active_version = get_active_kubos_version()

    if filter:  # filter the CD Generated versions
        tag_list = filter_cd_generated_tags(SHOW_NUMBER_CD_VERSIONS, tag_list)

    for tag in tag_list:
        if tag == active_version:
            tag = tag + ' *'
        logging.info(tag)


def get_latest_tag(tag_list):
    latest_tag = '0.0.0'  # Set to a dummy tag that will be less than any other valid tag
    for tag in tag_list:
        if packaging.version.parse(tag) > packaging.version.parse(latest_tag):
            latest_tag = tag
    return latest_tag


def fetch_tags(repo):
    origin = repo.remotes.origin
    # Tags mark new KubOS releases
    logging.info('Checking for newer releases...')
    origin.fetch()


def checkout_and_update_version(ref, repo):
    # Tags follow the v?X.X.X convention
    tag_expr = re.compile('v?\d+\.\d+\.\d+\.*')
    is_tag = tag_expr.match(ref)
    logging.info("Checking out '%s'" % ref)
    if not is_tag:
        logging.warning(
            'Kubos branches are not guaranteed to be stable. Proceed with caution.')
    try:
        repo.git.checkout(ref)
        # only set the version file for kubos source checkouts, not for example checkouts
        if repo.git_dir == os.path.join(KUBOS_SRC_DIR, '.git'):
            update_version_file(ref)
    except:
        logging.error('There was an error checking out branch "%s"' % ref)
        logging.debug('The error details are: %s' % sys.exc_info()[0])


def update_version_file(version):
    with open(KUBOS_VERSION_FILE, 'w') as version_file:
        version_file.write(version)


def clone_example_repo(repo_dir, repo_url):
    '''
    For the example repos (kubos-rt-example, kubos-linux-example) we
    simply checkout the latest version, rather than making the user
    specify a specific version of the example repo.
    '''
    repo = clone_repo(repo_dir, repo_url)
    tag_list = get_tag_list(repo)
    latest_tag = get_latest_tag(tag_list)
    checkout_and_update_version(latest_tag, repo)


def clone_repo(repo_dir, repo_url):
    try:
        if not os.path.isdir(repo_dir):
            repo = git.Repo.clone_from(repo_url, repo_dir)
            logging.info('Successfully cloned repo: %s' % repo_url)
        else:
            repo = git.Repo(repo_dir)
            logging.info('Repo %s already exists' % repo_url)
        fetch_tags(repo)
        # Link the modules/targets from the kubos repo to the default, Global location
        sdk_utils.link_to_global_cache(KUBOS_SRC_DIR)
        return repo
    except git.exc.GitCommandError as e:
        logging.error(
            'Error: there was an error accessing the remote git repository...')
        logging.debug('The specific error is: \n\n %s' % e)


def get_active_kubos_version():
    if os.path.isfile(KUBOS_VERSION_FILE):
        return open(KUBOS_VERSION_FILE).read()
    else:
        return None


def set_active_kubos_version(set_tag, repo):
    origin = repo.remotes.origin
    tag_list = get_tag_list(repo)
    found = False
    for tag in tag_list:
        if tag == set_tag:
            checkout_and_update_version(tag, repo)
            found = True
            break
    if not found:
        logging.error(
            'The requested version "%s" is not an available version.' % set_tag)
        logging.info('Available versions are: ')
        print_tag_list(tag_list)
        sys.exit(1)


def check_provided_version(requested_version, repo):
    # the repo paramenter allows this function to be used for the example project as well
    active_version = get_active_kubos_version()
    if requested_version == active_version:
        logging.info(
            'The requested version: %s is already active. There\'s nothing to do..' % requested_version)
        return
    set_active_kubos_version(requested_version, repo)
    if active_version:
        logging.info('Deactivating Kubos source version: %s' % active_version)
    logging.info('Activating Kubos source version %s' % requested_version)
