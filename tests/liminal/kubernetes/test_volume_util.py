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

import sys
import unittest

from kubernetes import config
from liminal.kubernetes import volume_util

try:
    config.load_kube_config()
except Exception:
    msg = "Kubernetes is not running\n"
    sys.stdout.write(f"INFO: {msg}")


class TestKubernetesVolume(unittest.TestCase):
    def setUp(self) -> None:
        self.config = {
            'volumes': [
                {
                    'volume': 'gettingstartedvol-test',
                    'claim_name': 'gettingstartedvol-test-pvc',
                    'local': {'path': '.'},
                }
            ]
        }

    def test_volume_config(self):
        volumes_config = volume_util.get_volume_configs(self.config, ".")
        self.assertEqual(str(self.config['volumes'][0]), str(volumes_config[0]))

    def test_create_volume(self):
        self._delete_volumes()
        self._create_volumes()
        matching_volumes = volume_util._list_persistent_volumes(self.config['volumes'][0]['volume'])
        self.assertTrue(
            self.config['volumes'][0]['volume'] in matching_volumes[0]['metadata']['name'],
            self.config['volumes'][0]['claim_name'] in matching_volumes[0]['spec']['claim_ref']['name'],
        )

    def test_delete_volume(self):
        self._create_volumes()
        self._delete_volumes()
        matching_volumes = volume_util._list_persistent_volumes(self.config['volumes'][0]['volume'])
        self.assertEqual([], matching_volumes)

    def _create_volumes(self):
        volume_util.create_local_volumes(self.config, ".")

    def _delete_volumes(self):
        volume_util.delete_local_volumes(self.config, ".")
