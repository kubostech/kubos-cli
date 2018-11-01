# Kubos CLI
# Copyright (C) 2017 Kubos Corporation
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

import json
import os
import release
import subprocess

this_dir = os.path.dirname(os.path.abspath(__file__))
cli_root_dir = os.path.dirname(this_dir)
module_json = os.path.join(cli_root_dir, 'module.json')


def main():
    '''
    This script updates, versions, and builds new versions of the Kubos CLI.

    How to use this script:

    To explicitly set the version of the new release, update the version to what you
    want in the module.json file. Commit and push the version update change to master. Once
    the tests pass this script will tag the repo at that new version number (that you set
    in module.json), and release the module build on github.

    If you don't care about the version number, just merge your changes to master
    of the kubos-cli repo. Once the tests pass, this will bump the version number
    and upload the module build to a github release.
    '''
    latest_tag = get_latest_tag()
    module_version = get_module_version()
    if latest_tag == module_version:
        version = bump_and_write_version(module_version)
        commit_and_push(version)
    else:
        version = module_version

    build_wheel()
    release.github_release(version)


def get_latest_tag():
    tag_str = subprocess.check_output(['git', 'tag', '--sort=-creatordate'])
    tag_list = tag_str.split('\n')
    latest = tag_list[0]
    print 'The lastest tag is: %s' % latest
    return latest


def get_module_version():
    with open(module_json, 'r') as module_file:
        data = json.loads(module_file.read())
    version = data['version']
    print 'The module.json version is: %s' % version
    return version


def bump_and_write_version(version):
    version_fields = version.split('.')

    if len(version_fields) == 4:  # Add a patch number
        # bump the version number by 1 and store it as a string
        version_fields[3] = str(int(version_fields[3]) + 1)
        version = '.'.join(version_fields)
    elif len(version_fields) == 3:  # bump the version number
        version = version + '.1'

    with open(module_json, 'r') as module_file:
        data = json.loads(module_file.read())

    data['version'] = version

    with open(module_json, 'w') as module_file:
        module_file.write(json.dumps(data,
                                     sort_keys=True,
                                     indent=4,
                                     separators=(',', ': '))
                          )
    return version


def commit_and_push(version_number):
    run_cmd('git', 'config', '--global', 'user.name',
            os.environ['GITHUB_USERNAME'])
    run_cmd('git', 'config', '--global',
            'user.email', os.environ['GITHUB_EMAIL'])
    run_cmd('git', 'add', 'module.json')
    print 'Committing the version update...'
    # we want ci to skip to prevent an infinite release cycle.
    run_cmd('git', 'commit', '-m',
            '"Bump version to %s. [ci skip]"' % version_number)

    print 'Pushing the commit to origin...'
    run_cmd('git', 'push', 'origin', 'master')  # push the commit


def build_wheel():
    print 'Building the wheel...'
    run_cmd('python', 'setup.py', 'bdist_wheel', '--universal')


def run_cmd(*args, **kwargs):
    try:
        return subprocess.check_output(args, **kwargs)
    except subprocess.CalledProcessError, e:
        print >>sys.stderr, 'Error executing command, giving up.\nError Message: %s' % e
        sys.exit(1)


if __name__ == '__main__':
    main()
