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

import datetime
import logging
import os

from airflow.kubernetes.volume import Volume
from airflow.kubernetes.volume_mount import VolumeMount

from liminal.runners.airflow.config.standalone_variable_backend import get_variable
from liminal.runners.airflow.model import executor
from liminal.runners.airflow.operators.kubernetes_pod_operator_with_auto_image import \
    KubernetesPodOperatorWithAutoImage
from liminal.runners.airflow.operators.operator_with_variable_resolving import \
    OperatorWithVariableResolving
from liminal.runners.airflow.tasks import containerable
from liminal.runners.airflow.tasks.containerable import ContainerTask

_LOG = logging.getLogger(__name__)


class KubernetesPodExecutor(executor.Executor):
    """
    Kubernetes pod executor
    """

    def __init__(self, task_id,
                 liminal_config, executor_config):
        super().__init__(task_id,
                         liminal_config, executor_config)

        self.task_name = self.executor_config['executor']
        self.volumes = self._volumes()
        self.resources = self.__kubernetes_resources()

    def apply_task_to_dag(self, **kwargs):
        task = kwargs['task']

        self.__validate_task_type(task)

        parent = kwargs.get('parent', task.parent)

        pod_task = KubernetesPodOperatorWithAutoImage(
            task_id=task.task_id,
            image=task.image,
            cmds=task.cmds,
            arguments=task.arguments,
            **self.__kubernetes_kwargs(task),
        )

        wrapper_task = OperatorWithVariableResolving(task_id=task.task_id,
                                                     dag=task.dag,
                                                     operator=pod_task,
                                                     trigger_rule=task.trigger_rule,
                                                     liminal_config=self.liminal_config)

        if parent:
            parent.set_downstream(wrapper_task)

        return wrapper_task

    def _volumes(self):
        volumes_config = self.liminal_config.get('volumes', [])
        volumes = []
        for volume_config in volumes_config:
            name = volume_config['volume']
            if os.getenv('POD_NAMESPACE') == "jenkins":
                claimName = 'jenkins-mvn-cache'
            else:
                claimName = f"{name}-pvc"

            volume = Volume(
                name=name,
                configs={
                    'persistentVolumeClaim': {
                        'claimName': f"{claimName}"
                    }
                }
            )
            volumes.append(volume)
        return volumes

    def __kubernetes_kwargs(self, task: ContainerTask):
        kubernetes_kwargs = {
            'namespace': get_variable('kubernetes_namespace', default_val='default'),
            'name': task.task_id.replace('_', '-'),
            'in_cluster': get_variable('in_kubernetes_cluster', default_val=False),
            'image_pull_policy': get_variable('image_pull_policy', default_val='IfNotPresent'),
            'get_logs': True,
            'is_delete_operator_pod': True,
            'startup_timeout_seconds': 1200,
            'env_vars': task.env_vars,
            'do_xcom_push': task.task_config.get('do_xcom_push', False),
            'image_pull_secrets': 'regcred',
            'resources': self.resources,
            'volumes': self.volumes,
            'volume_mounts': [
                VolumeMount(mount['volume'],
                            mount['path'],
                            mount.get('sub_path'),
                            mount.get('read_only', False))
                for mount
                in task.mounts
            ]
        }

        if os.getenv('POD_NAMESPACE') == "jenkins":
            kubernetes_kwargs['affinity'] = self.__kubernetes_affinity()
            kubernetes_kwargs['namespace'] = 'jenkins'

        if not task.dag:
            kubernetes_kwargs.update({
                'start_date': datetime.datetime(1970, 1, 1),
            })
        return kubernetes_kwargs

    @staticmethod
    def __validate_task_type(task):
        assert isinstance(task, containerable.ContainerTask), \
            'supported task types: [containerable]'

    def __kubernetes_resources(self):
        resources = {}
        if 'request_cpu' in self.executor_config:
            resources['request_cpu'] = self.executor_config['request_cpu']
        if 'request_memory' in self.executor_config:
            resources['request_memory'] = self.executor_config['request_memory']
        if 'limit_cpu' in self.executor_config:
            resources['limit_cpu'] = self.executor_config['limit_cpu']
        if 'limit_memory' in self.executor_config:
            resources['limit_memory'] = self.executor_config['limit_memory']

        return resources

    @staticmethod
    def __kubernetes_affinity():
        return {
            "podAffinity": {
                "requiredDuringSchedulingIgnoredDuringExecution": [
                    {
                        "labelSelector": {
                            "matchExpressions": [
                                {
                                    "key": "liminal",
                                    "operator": "In",
                                    "values": [
                                        "unittest"
                                    ]
                                }
                            ]
                        },
                        "namespaces": [
                            "jenkins"
                        ],
                        "topologyKey": "kubernetes.io/hostname"
                    }
                ]
            }
        }
