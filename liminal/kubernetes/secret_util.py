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

import base64
import logging
import os
import sys
from pathlib import Path
from time import sleep

from kubernetes import client, config, shutil
from kubernetes.client import V1Secret

# noinspection PyBroadException
try:
    config.load_kube_config()
except Exception:
    msg = "Kubernetes is not running\n"
    sys.stdout.write(f"INFO: {msg}")

_LOG = logging.getLogger('volume_util')
_LOCAL_VOLUMES = set()
_kubernetes = client.CoreV1Api()


def get_secret_configs(liminal_config, base_dir):
    secrets_config = liminal_config.get('secrets', [])

    for volume_config in secrets_config:
        if 'secret' in volume_config and 'local_path_file' not in volume_config:
            secret_path = f"{os.getcwd()}/credentials-{volume_config['secret']}.txt"
            shutil.copyfile(f"{os.path.dirname(os.path.abspath(__file__))}/license.txt", secret_path)
            open(secret_path, 'a').close()
            volume_config['local_path_file'] = secret_path
    return secrets_config


def create_local_secrets(liminal_config, base_dir):
    secrets_config = get_secret_configs(liminal_config, base_dir)

    for secret_config in secrets_config:
        logging.info(f'Creating local kubernetes secret if needed: {secret_config}')
        create_secret(secret_config)


def create_secret(conf, namespace='default') -> None:
    name = conf['secret']

    _LOG.info(f'Requested secret {name}')

    if name not in _LOCAL_VOLUMES:
        _create_secret(namespace, conf, name)
        sleep(5)

        _LOCAL_VOLUMES.add(name)


def _create_secret(namespace, conf, name):
    _LOG.info(f'Creating kubernetes secret {name} with spec {conf}')

    _kubernetes.create_namespaced_secret(
        namespace,
        V1Secret(
            api_version='v1',
            kind='Secret',
            metadata={
                'name': name,
                'labels': {"apache/incubator-liminal": "liminal.apache.org"},
            },
            data={
                'credentials': base64.b64encode(
                    Path(os.path.expanduser(conf['local_path_file'])).read_text().encode('ascii')
                ).decode('ascii')
            },
        ),
    )


def delete_local_secrets(liminal_config, base_dir):
    secrets_config = get_secret_configs(liminal_config, base_dir)

    for secret_config in secrets_config:
        logging.info(f'Delete local secret if needed: {secret_config}')
        delete_local_secret(secret_config)


def delete_local_secret(name, namespace='default'):
    matching_secrets = _kubernetes.list_namespaced_secret(namespace, field_selector=f'metadata.name={name}').to_dict()[
        'items'
    ]

    if len(matching_secrets) > 0:
        _LOG.info(f'Deleting secret {name}')
        _kubernetes.delete_namespaced_secret(name, namespace)

    if name in _LOCAL_VOLUMES:
        _LOCAL_VOLUMES.remove(name)
