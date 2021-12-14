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

import copy
import datetime
import logging
import os

from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import (
    KubernetesPodOperator,
)
from kubernetes.client import V1Volume, V1VolumeMount
from kubernetes.client import models as k8s

from liminal.core.util import env_util
from liminal.runners.airflow.config.standalone_variable_backend import get_variable
from liminal.runners.airflow.model import executor
from liminal.runners.airflow.tasks import containerable
from liminal.runners.airflow.tasks.containerable import ContainerTask

_LOG = logging.getLogger(__name__)


class KubernetesPodExecutor(executor.Executor):
    """
    Kubernetes pod executor
    """

    supported_task_types = [containerable.ContainerTask]

    def __init__(self, task_id, liminal_config, executor_config):
        super().__init__(task_id, liminal_config, executor_config)

        self.task_name = self.executor_config['executor']
        self.volumes = self._volumes()

    def _apply_executor_task_to_dag(self, **kwargs):
        task = kwargs['task']
        parent = task.parent

        self._validate_task_type(task)

        pod_task = executor.add_variables_to_operator(
            KubernetesPodOperator(trigger_rule=task.trigger_rule, **self.__kubernetes_kwargs(task)), task
        )

        if parent:
            parent.set_downstream(pod_task)

        return pod_task

    def _volumes(self):
        volumes_config = self.liminal_config.get('volumes', [])
        volumes = []
        for volume_config in volumes_config:
            name = volume_config['volume']
            claim_name = volume_config.get('claim_name')
            if not claim_name and 'local' in volume_config:
                claim_name = f'{name}-pvc'
            volume = V1Volume(name=name, persistent_volume_claim={'claimName': claim_name})
            volumes.append(volume)
        return volumes

    def __kubernetes_kwargs(self, task: ContainerTask):
        config = copy.deepcopy(self.executor_config)
        kubernetes_kwargs = {
            'task_id': task.task_id,
            'image': task.image,
            'arguments': task.arguments,
            'namespace': os.environ.get('AIRFLOW__KUBERNETES__NAMESPACE', 'default'),
            'name': task.task_id.replace('_', '-'),
            'in_cluster': os.environ.get('AIRFLOW__KUBERNETES__IN_CLUSTER', False),
            'image_pull_policy': get_variable('image_pull_policy', default_val='IfNotPresent'),
            'get_logs': config.pop('get_logs', True),
            'is_delete_operator_pod': config.pop('is_delete_operator_pod', True),
            'startup_timeout_seconds': config.pop('startup_timeout_seconds', 1200),
            'env_vars': [k8s.V1EnvVar(name=x, value=v) for x, v in task.env_vars.items()],
            'do_xcom_push': task.task_config.get('do_xcom_push', False),
            'image_pull_secrets': config.pop('image_pull_secrets', 'regcred'),
            'volumes': self.volumes,
            'config_file': os.environ.get('AIRFLOW__KUBERNETES__CONFIG_FILE'),
            'cluster_context': os.environ.get('AIRFLOW__KUBERNETES__CLUSTER_CONTEXT', None),
            'cmds': task.cmds,
            'volume_mounts': [
                V1VolumeMount(
                    name=mount['volume'],
                    mount_path=mount['path'],
                    sub_path=mount.get('sub_path'),
                    read_only=mount.get('read_only', False),
                )
                for mount in task.mounts
            ],
        }

        config.pop('in_cluster', None)
        config.pop('volumes', None)
        config.pop('volume_mounts', None)
        config.pop('executor', None)
        config.pop('type', None)

        kubernetes_kwargs.update(config)

        if env_util.is_running_on_jenkins():
            kubernetes_kwargs['affinity'] = self.__jenkins_kubernetes_affinity()
            kubernetes_kwargs['namespace'] = 'jenkins'

        if not task.dag:
            kubernetes_kwargs.update(
                {
                    'start_date': datetime.datetime(1970, 1, 1),
                }
            )

        return kubernetes_kwargs

    @staticmethod
    def __jenkins_kubernetes_affinity():
        return {
            "podAffinity": {
                "requiredDuringSchedulingIgnoredDuringExecution": [
                    {
                        "labelSelector": {
                            "matchExpressions": [{"key": "liminal", "operator": "In", "values": ["unittest"]}]
                        },
                        "namespaces": ["jenkins"],
                        "topologyKey": "kubernetes.io/hostname",
                    }
                ]
            }
        }
