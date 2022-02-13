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

import logging
import os
import sys
from time import sleep

from kubernetes import client, config
from kubernetes.client import V1PersistentVolume, V1PersistentVolumeClaim

# noinspection PyBroadException
try:
    config.load_kube_config()
except Exception:
    msg = "Kubernetes is not running\n"
    sys.stdout.write(f"INFO: {msg}")

_LOG = logging.getLogger('volume_util')
_LOCAL_VOLUMES = set()
_kubernetes = client.CoreV1Api()


def get_volume_configs(liminal_config, base_dir):
    volumes_config = liminal_config.get('volumes', [])

    for volume_config in volumes_config:
        if 'local' in volume_config:
            path = volume_config['local']['path']
            if path.startswith(".."):
                path = os.path.join(base_dir, path)
            if path.startswith("."):
                path = os.path.join(base_dir, path[1:])
            volume_config['local']['path'] = path
    return volumes_config


def create_local_volumes(liminal_config, base_dir):
    volumes_config = get_volume_configs(liminal_config, base_dir)

    for volume_config in volumes_config:
        logging.info(f'Creating local kubernetes volume if needed: {volume_config}')
        create_local_volume(volume_config)


def create_local_volume(conf, namespace='default') -> None:
    name = conf['volume']

    _LOG.info(f'Requested volume {name}')

    if name not in _LOCAL_VOLUMES:
        matching_volumes = _kubernetes.list_persistent_volume(field_selector=f'metadata.name={name}').to_dict()[
            'items'
        ]

        while len(matching_volumes) == 0:
            _create_local_volume(conf, name)
            sleep(5)
            matching_volumes = _kubernetes.list_persistent_volume(field_selector=f'metadata.name={name}').to_dict()[
                'items'
            ]

        pvc_name = conf.get('claim_name', f'{name}-pvc')

        matching_claims = _kubernetes.list_persistent_volume_claim_for_all_namespaces(
            field_selector=f'metadata.name={pvc_name}'
        ).to_dict()['items']

        while len(matching_claims) == 0:
            _create_persistent_volume_claim(pvc_name, name, namespace)
            sleep(5)
            matching_claims = _kubernetes.list_persistent_volume_claim_for_all_namespaces(
                field_selector=f'metadata.name={pvc_name}'
            ).to_dict()['items']

        _LOCAL_VOLUMES.add(name)


def delete_local_volumes(liminal_config, base_dir):
    volumes_config = get_volume_configs(liminal_config, base_dir)

    for volume_config in volumes_config:
        logging.info(f'Delete local kubernetes volume if needed: {volume_config}')
        delete_local_volume(volume_config['volume'])


def delete_local_volume(name, namespace='default'):
    pvc_name = f'{name}-pvc'

    matching_claims = _list_persistent_volume_claims(pvc_name)

    if len(matching_claims) > 0:
        _LOG.info(f'Deleting persistent volume claim {pvc_name}')
        _kubernetes.delete_namespaced_persistent_volume_claim(pvc_name, namespace)

    while len(matching_claims) > 0:
        matching_claims = _list_persistent_volume_claims(pvc_name)

    matching_volumes = _list_persistent_volumes(name)

    if len(matching_volumes) > 0:
        _LOG.info(f'Deleting persistent volume {name}')
        _kubernetes.delete_persistent_volume(name)

    while len(matching_volumes) > 0:
        matching_volumes = _list_persistent_volumes(name)

    if name in _LOCAL_VOLUMES:
        _LOCAL_VOLUMES.remove(name)


def _list_persistent_volume_claims(name):
    return _kubernetes.list_persistent_volume_claim_for_all_namespaces(
        field_selector=f'metadata.name={name}'
    ).to_dict()['items']


def _list_persistent_volumes(name):
    return _kubernetes.list_persistent_volume(field_selector=f'metadata.name={name}').to_dict()['items']


def _create_persistent_volume_claim(pvc_name, volume_name, namespace):
    _LOG.info(f'Creating persistent volume claim {pvc_name} with volume {volume_name}')
    spec = {
        'volumeName': volume_name,
        'volumeMode': 'Filesystem',
        'storageClassName': 'local-storage',
        'accessModes': ['ReadWriteOnce'],
        'resources': {'requests': {'storage': '100Gi'}},
    }

    _kubernetes.create_namespaced_persistent_volume_claim(
        namespace,
        V1PersistentVolumeClaim(
            api_version='v1', kind='PersistentVolumeClaim', metadata={'name': pvc_name}, spec=spec
        ),
    )


def _create_local_volume(conf, name):
    _LOG.info(f'Creating persistent volume {name} with spec {conf}')
    spec = {
        'capacity': {'storage': '100Gi'},
        'volumeMode': 'Filesystem',
        'accessModes': ['ReadWriteOnce'],
        'persistentVolumeReclaimPolicy': 'Retain',
        'storageClassName': 'local-storage',
        'nodeAffinity': {
            'required': {
                'nodeSelectorTerms': [
                    {'matchExpressions': [{'key': 'kubernetes.io/hostname', 'operator': 'NotIn', 'values': ['']}]}
                ]
            }
        },
    }

    spec.update(conf)

    _kubernetes.create_persistent_volume(
        V1PersistentVolume(api_version='v1', kind='PersistentVolume', metadata={'name': name}, spec=spec)
    )
