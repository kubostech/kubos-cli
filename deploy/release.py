# Kubos CLI
# Copyright (C) 2017 Kubos Corporation
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''
This script is a REST API client for creating github releases for the kubos-cli
repo
'''

import json
import os
import requests
import sys

from uritemplate import URITemplate, expand

release_endpoint = 'https://api.github.com/repos/kubos/kubos-cli/releases'

try:
    token = os.environ['GITHUB_TOKEN']
except KeyError:
    print 'Error the environment variable "GITHUB_TOKEN" is not set. Aborting..'
    sys.exit(1)

auth = ('username', token)


def create_release(version):
    '''
    Create a new tag/release in the kubos-cli repo

    This function returns the URI template for uploading a release asset
    '''
    headers = {
        'Content-type': 'application/json',
        'Accept': 'application/json'
    }

    data = {
        'tag_name': version,
        'target_commitish': 'master',
        'name': version,
        'body': '',
                'draft': False,
                'prerelease': False
    }

    res = requests.post(release_endpoint, auth=auth,
                        headers=headers, data=json.dumps(data))
    res.raise_for_status()
    return res.json()['upload_url']


def upload_wheel(version, uri_template):
    '''
    upload the module wheel as a release asset
    '''
    print 'Uploading the wheel build...'
    headers = {
        'Content-type': 'application/octet-stream',
        'Accept': 'application/json'
    }

    template = URITemplate(uri_template)
    wheel_path = get_wheel_file_path()
    wheel_file = os.path.basename(wheel_path)
    url = template.expand(name=wheel_file, label=wheel_file)
    files = {'files': open(wheel_path, 'rb')}
    res = requests.post(url, auth=auth, files=files)


def get_wheel_file_path():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(this_dir, '..', 'dist')
    if os.path.isdir(dist_dir):
        for _file in os.listdir(dist_dir):
            # Running in a CD environment, there will only be a single wheel build in the dist/ folder
            if _file.endswith('.whl'):
                return os.path.join(dist_dir, _file)
    print 'Unable to find the wheel build under directory %s.. Aborting.' % dist_dir
    sys.exit(1)


def github_release(version):
    uri_template = create_release(version)
    upload_wheel(version, uri_template)
