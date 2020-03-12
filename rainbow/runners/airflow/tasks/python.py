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
import json
import os

from airflow.models import Variable
from airflow.operators.dummy_operator import DummyOperator

from rainbow.docker.python import python_image
from rainbow.runners.airflow.model import task
from rainbow.runners.airflow.operators.kubernetes_pod_operator import \
    ConfigurableKubernetesPodOperator, \
    ConfigureParallelExecutionOperator


class PythonTask(task.Task):
    """
    Python task.
    """

    def __init__(self, dag, pipeline_name, parent, config, trigger_rule):
        super().__init__(dag, pipeline_name, parent, config, trigger_rule)

        self.input_type = self.config['input_type']
        self.input_path = self.config['input_path']
        self.task_name = self.config['task']
        self.image = self.config['image']
        self.resources = self.__kubernetes_resources()
        self.env_vars = self.__env_vars()
        self.kubernetes_kwargs = self.__kubernetes_kwargs()
        self.cmds, self.arguments = self.__kubernetes_cmds_and_arguments()
        self.config_task_id = self.task_name + '_input'
        self.executors = self.__executors()

    def build(self):
        if 'source' in self.config:
            script_dir = os.path.dirname(__file__)

            python_image.build(self.config['source'], self.image, [
                os.path.join(script_dir, '../build/python/container-setup.sh'),
                os.path.join(script_dir, '../build/python/container-teardown.sh')
            ])

    def apply_task_to_dag(self):

        def create_pod_operator(task_id, task_split, image):
            return ConfigurableKubernetesPodOperator(
                task_id=task_id,
                config_task_id=self.config_task_id,
                task_split=task_split,
                image=image,
                cmds=self.cmds,
                arguments=self.arguments,
                **self.kubernetes_kwargs
            )

        config_task = None

        if self.input_type in ['static', 'task']:
            self.env_vars.update({'DATA_PIPELINE_INPUT': self.input_path})

            config_task = ConfigureParallelExecutionOperator(
                task_id=self.config_task_id,
                image=self.image,
                config_type=self.input_type,
                config_path=self.input_path,
                executors=self.executors,
                **self.kubernetes_kwargs
            )

        if self.executors == 1:
            pod_task = create_pod_operator(
                task_id=f'{self.task_name}',
                task_split=0,
                image=f'''{self.image}'''
            )

            first_task = pod_task

            if config_task:
                first_task = config_task
                first_task.set_downstream(pod_task)

            if self.parent:
                self.parent.set_downstream(first_task)

            return pod_task
        else:
            if not config_task:
                config_task = DummyOperator(
                    task_id=self.config_task_id,
                    trigger_rule=self.trigger_rule,
                    dag=self.dag
                )

            end_task = DummyOperator(
                task_id=self.task_name,
                dag=self.dag
            )

            if self.parent:
                self.parent.set_downstream(config_task)

                for i in range(self.executors):
                    split_task = create_pod_operator(
                        task_id=f'''{self.task_name}_{i}''',
                        task_split=i,
                        image=self.image
                    )

                    config_task.set_downstream(split_task)

                    split_task.set_downstream(end_task)

            return end_task

    def __executors(self):
        executors = 1
        if 'executors' in self.config:
            executors = self.config['executors']
        return executors

    def __kubernetes_cmds_and_arguments(self):
        cmds = ['/bin/bash', '-c']
        arguments = [
            f'''sh container-setup.sh && \
            {self.config['cmd']} && \
            sh container-teardown.sh {self.config['output_path']}'''
        ]
        return cmds, arguments

    def __kubernetes_kwargs(self):
        kubernetes_kwargs = {
            'namespace': Variable.get('kubernetes_namespace', default_var='default'),
            'name': self.task_name.replace('_', '-'),
            'in_cluster': Variable.get('in_kubernetes_cluster', default_var=False),
            'image_pull_policy': Variable.get('image_pull_policy', default_var='IfNotPresent'),
            'get_logs': True,
            'env_vars': self.env_vars,
            'do_xcom_push': True,
            'is_delete_operator_pod': True,
            'startup_timeout_seconds': 300,
            'image_pull_secrets': 'regcred',
            'resources': self.resources,
            'dag': self.dag
        }
        return kubernetes_kwargs

    def __env_vars(self):
        env_vars = {}
        if 'env_vars' in self.config:
            env_vars = self.config['env_vars']
        airflow_configuration_variable = Variable.get(
            f'''{self.pipeline_name}_dag_configuration''',
            default_var=None)
        if airflow_configuration_variable:
            airflow_configs = json.loads(airflow_configuration_variable)
            environment_variables_key = f'''{self.pipeline_name}_environment_variables'''
            if environment_variables_key in airflow_configs:
                env_vars = airflow_configs[environment_variables_key]
        return env_vars

    def __kubernetes_resources(self):
        resources = {}

        if 'request_cpu' in self.config:
            resources['request_cpu'] = self.config['request_cpu']
        if 'request_memory' in self.config:
            resources['request_memory'] = self.config['request_memory']
        if 'limit_cpu' in self.config:
            resources['limit_cpu'] = self.config['limit_cpu']
        if 'limit_memory' in self.config:
            resources['limit_memory'] = self.config['limit_memory']

        return resources
