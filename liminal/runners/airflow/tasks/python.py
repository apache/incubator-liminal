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
from typing import Optional

from airflow.kubernetes.volume import Volume
from airflow.kubernetes.volume_mount import VolumeMount
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.operators.dummy_operator import DummyOperator

from liminal.runners.airflow.config.standalone_variable_backend import get_variable
from liminal.runners.airflow.model import task

_LOG = logging.getLogger(__name__)


class PythonTask(task.Task):
    """
    Python task.
    """

    def __init__(self, dag, liminal_config, pipeline_config, task_config, parent, trigger_rule):
        super().__init__(dag, liminal_config, pipeline_config, task_config, parent, trigger_rule)
        self.task_name = self.task_config['task']
        self.image = self.task_config['image']
        self.volumes = self._volumes()
        self.mounts = self.task_config.get('mounts', [])
        self.resources = self.__kubernetes_resources()
        self.env_vars = self.__env_vars()
        self.kubernetes_kwargs = self.__kubernetes_kwargs()
        self.cmds, self.arguments = self.__kubernetes_cmds_and_arguments()
        self.executors = self.__executors()

    def apply_task_to_dag(self):
        if self.executors == 1:
            return self.__apply_task_to_dag_single_executor()
        else:
            return self.__apply_task_to_dag_multiple_executors()

    def _volumes(self):
        volumes_config = self.liminal_config.get('volumes', [])
        volumes = []
        for volume_config in volumes_config:
            name = volume_config['volume']
            volume = Volume(
                name=name,
                configs={
                    'persistentVolumeClaim': {
                        'claimName': f"{name}-pvc"
                    }
                }
            )
            volumes.append(volume)
        return volumes

    def __apply_task_to_dag_multiple_executors(self):
        start_task = DummyOperator(
            task_id=f'{self.task_name}_parallelize',
            trigger_rule=self.trigger_rule,
            dag=self.dag
        )

        end_task = DummyOperator(
            task_id=self.task_name,
            dag=self.dag
        )

        if self.parent:
            self.parent.set_downstream(start_task)

            for i in range(self.executors):
                split_task = self.__create_pod_operator(
                    image=self.image,
                    task_id=i
                )

                start_task.set_downstream(split_task)

                split_task.set_downstream(end_task)

        return end_task

    def __create_pod_operator(self, image: str, task_id: Optional[int] = None):
        env_vars = self.env_vars

        if task_id is not None:
            env_vars = self.env_vars.copy()
            env_vars['LIMINAL_SPLIT_ID'] = str(task_id)
            env_vars['LIMINAL_NUM_SPLITS'] = str(self.executors)

        return KubernetesPodOperator(
            task_id=f'{self.task_name}_{task_id}' if task_id is not None else self.task_name,
            image=image,
            cmds=self.cmds,
            arguments=self.arguments,
            env_vars=env_vars,
            **self.kubernetes_kwargs
        )

    def __apply_task_to_dag_single_executor(self):
        pod_task = self.__create_pod_operator(image=f'''{self.image}''')

        first_task = pod_task

        if self.parent:
            self.parent.set_downstream(first_task)

        return pod_task

    def __executors(self) -> int:
        executors = 1

        if 'executors' in self.task_config:
            executors = self.task_config['executors']

        return executors

    def __kubernetes_cmds_and_arguments(self):
        cmds = ['/bin/bash', '-c']
        arguments = [self.task_config['cmd']]
        return cmds, arguments

    def __kubernetes_kwargs(self):
        kubernetes_kwargs = {
            'namespace': get_variable('kubernetes_namespace', default_val='default'),
            'name': self.task_name.replace('_', '-'),
            'in_cluster': get_variable('in_kubernetes_cluster', default_val=False),
            'image_pull_policy': get_variable('image_pull_policy', default_val='IfNotPresent'),
            'get_logs': True,
            'is_delete_operator_pod': True,
            'startup_timeout_seconds': 300,
            'image_pull_secrets': 'regcred',
            'resources': self.resources,
            'dag': self.dag,
            'volumes': self.volumes,
            'volume_mounts': [
                VolumeMount(mount['volume'],
                            mount['path'],
                            mount.get('sub_path'),
                            mount.get('read_only', False))
                for mount
                in self.mounts
            ]
        }
        return kubernetes_kwargs

    def __env_vars(self):
        return dict([(k, str(v)) for k, v in self.task_config.get('env_vars', {}).items()])

    def __kubernetes_resources(self):
        resources = {}

        if 'request_cpu' in self.task_config:
            resources['request_cpu'] = self.task_config['request_cpu']
        if 'request_memory' in self.task_config:
            resources['request_memory'] = self.task_config['request_memory']
        if 'limit_cpu' in self.task_config:
            resources['limit_cpu'] = self.task_config['limit_cpu']
        if 'limit_memory' in self.task_config:
            resources['limit_memory'] = self.task_config['limit_memory']

        return resources
