#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import pickle
import time
import glob

import os

MOUNT_PATH = os.environ.get('MOUNT_PATH', '/mnt/gettingstartedvol')
PRODUCTION = 'production'
CANDIDATE = 'candidate'

_ONE_HOUR = 60 * 60

class ModelStore:

    def __init__(self, env):
        self.env = env
        self._latest_model = None
        self._latest_version = None
        self._last_check = time.time()

    def load_latest_model(self, force=False):
        if not self._latest_model or time.time() - self._last_check > _ONE_HOUR or force:
            self._latest_model, self._latest_version = self._download_latest_model()

        return self._latest_model, self._latest_version

    def save_model(self, model, version):
        key = 'model.p'
        path = f'{MOUNT_PATH}/{self.env}/{version}'

        os.makedirs(f'{path}', exist_ok=True)
        pickle.dump(model, open(f'{path}/{key}', "wb"))

    def _download_latest_model(self):
        objects = (glob.glob(f'{MOUNT_PATH}/{self.env}/**/*'))
        models = list(reversed(sorted([obj for obj in objects if obj.endswith('.p')])))
        latest_key = models[0]
        version = latest_key.rsplit('/')[-2]
        print(f'Loading model version {version}')
        return pickle.load(open(latest_key, 'rb')), version
