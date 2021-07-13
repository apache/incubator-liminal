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
import logging
import os
from abc import ABC
from typing import Dict

from liminal.core import environment
from liminal.runners.airflow.config import standalone_variable_backend
from liminal.runners.airflow.config.standalone_variable_backend import get_variable
from liminal.runners.airflow.model import task

_LOG = logging.getLogger(__name__)
ENV = 'env'
DEFAULT = 'default'
OUTPUT_PATH = 'OUTPUT_PATH'
OUTPUT_DESTINATION_PATH = 'OUTPUT_DESTINATION_PATH'


class ContainerTask(task.Task, ABC):
    """
    K8S Containerable task
    """

    def __init__(self, task_id, dag, parent, trigger_rule, liminal_config, pipeline_config,
                 task_config):
        super().__init__(task_id, dag, parent, trigger_rule, liminal_config,
                         pipeline_config, task_config)
        env = standalone_variable_backend.get_variable(ENV, DEFAULT)
        self.env_vars = self.__env_vars(env)
        self.image = self.task_config['image']
        self.mounts = self.task_config.get('mounts', [])
        self.cmds, self.arguments = self._kubernetes_cmds_and_arguments(
            self.env_vars.get(OUTPUT_PATH),
            self.env_vars.get(OUTPUT_DESTINATION_PATH)
        )

    def _kubernetes_cmds_and_arguments(self, output_path, output_destination_path):
        cmds = ['/bin/sh', '-c']

        arguments = [
            self.task_config['cmd']
        ]

        return cmds, arguments

    @staticmethod
    def __get_local_env_params_from_env_file():
        env_file = f'{environment.get_liminal_home()}/env'
        if os.path.isfile(env_file):
            _LOG.info(f'found env file at {env_file}')
            result = {}
            with open(env_file) as f:
                lines = f.readlines()
                for line in lines:
                    if line and line.strip() and line.strip()[0:1] != '#':
                        parts = line.strip().split('=')
                        if len(parts) == 2:
                            result[parts[0]] = parts[1]
            return result
        else:
            return {}

    def __env_vars(self, env) -> Dict:
        env_vars = dict(self.task_config['env_vars']) if 'env_vars' in self.task_config else {}
        env_vars.update(self.__get_local_env_params_from_env_file())
        airflow_configuration_variable = get_variable(
            f'''{self.pipeline_config['pipeline']}_dag_configuration''',
            default_val=None
        )

        if airflow_configuration_variable:
            airflow_configs = json.loads(airflow_configuration_variable)
            environment_variables_key = f"{self.pipeline_config['pipeline']}_environment_variables"
            if environment_variables_key in airflow_configs:
                env_vars = airflow_configs[environment_variables_key]

        if ENV not in env_vars:
            env_vars[ENV] = env

        env_vars[OUTPUT_PATH] = self.task_config[
            OUTPUT_PATH
        ] if OUTPUT_PATH in self.task_config else '/tmp/s3_mount'

        if 'output_destination_path' in self.task_config:
            env_vars[OUTPUT_DESTINATION_PATH] = self.task_config[
                'output_destination_path'
            ]
        return dict([(k, str(v)) for k, v in env_vars.items()])
