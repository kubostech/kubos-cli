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
import hashlib
import json
import os
import requests
import sys
import threading
import time
import uuid

from appdirs import AppDirs
from pip.utils import get_installed_version

from kubos.utils.sdk_utils import get_sdk_attribute


def load_config():
    return _config_class()


def load_sdk_version():
    return get_installed_version('kubos-sdk')


class KubosSDKConfig(object):
    json_template = '{"TableName" : "AnalyticsTest", "Item": {"Timestamp" : %s, "UUID" : "%s"}}'

    def __init__(self):
        self.appdirs = AppDirs('kubos')
        self.config_path = os.path.join(
            self.appdirs.user_config_dir, 'kubos-cli.json')
        self.sdk_version = load_sdk_version()
        self.load_config()
        #thread = threading.Thread(target=self.ping)
        # thread.start()

    def load_config(self):
        self.config = {}
        if os.path.isfile(self.config_path):
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)

    def save_config(self):
        if not os.path.isdir(self.appdirs.user_config_dir):
            os.makedirs(self.appdirs.user_config_dir)

        with open(self.config_path, 'w') as f:
            f.write(json.dumps(self.config))

    def ping(self):
        if 'uuid' in self.config:
            uid = self.config['uuid']
        else:
            uid = uuid.uuid4().hex  # uuid4 generates a completely random uuid
            self.config['uuid'] = uid
            self.save_config()
        data = self.json_template % (time.time(), uid)
        try:
            # This URL needs to be changed to the production DynamoDB endpoint
            requests.post(
                "https://drvpjfu9ci.execute-api.us-east-1.amazonaws.com/prod/AnalyticsTest", data=data)
        except:
            pass


_config_class = KubosSDKConfig
