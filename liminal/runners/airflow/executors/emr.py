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

from airflow.providers.amazon.aws.operators.emr_add_steps import EmrAddStepsOperator
from airflow.providers.amazon.aws.sensors.emr_step import EmrStepSensor

from liminal.runners.airflow.model import executor
from liminal.runners.airflow.tasks import hadoop


class EMRExecutor(executor.Executor):
    """
    Executes a EMR steps
    """

    supported_task_types = [hadoop.HadoopTask]

    def __init__(self, executor_id, liminal_config, executor_config):
        super().__init__(executor_id, liminal_config, executor_config)
        self.aws_conn_id = self.executor_config.get('aws_conn_id', 'aws_default')
        self.cluster_states = self.executor_config.get('cluster_state', ['RUNNING', 'WAITING'])
        self.job_flow_id = self.executor_config.get('cluster_id', None)
        self.job_flow_name = self.executor_config.get('cluster_name', None)

    def _apply_executor_task_to_dag(self, **kwargs):
        task = kwargs['task']
        parent = task.parent

        self._validate_task_type(task)

        # assuming emr already exists
        add_step = executor.add_variables_to_operator(
            EmrAddStepsOperator(
                task_id=f'{task.task_id}_add_step',
                job_flow_id=self.job_flow_id,
                job_flow_name=self.job_flow_name,
                aws_conn_id=self.aws_conn_id,
                steps=self.__generate_emr_step(task.task_id,
                                               [str(x) for x in task.get_runnable_command()]),
                cluster_states=self.cluster_states,
            ),
            task
        )

        if task.parent:
            parent.set_downstream(add_step)

        emr_sensor_step = executor.add_variables_to_operator(
            EmrStepSensor(
                task_id=f'{task.task_id}_watch_step',
                job_flow_id="{{ task_instance.xcom_pull('" + add_step.task_id +
                            "', key='job_flow_id') }}",
                step_id="{{ task_instance.xcom_pull('" + add_step.task_id +
                        "', key='return_value')[0] }}",
                aws_conn_id=self.aws_conn_id
            ),
            task
        )

        add_step.set_downstream(emr_sensor_step)

        return emr_sensor_step

    def __generate_emr_step(self, task_id, args):
        return [
            {
                'Name': task_id,
                **self.executor_config.get('properties', {}),
                'HadoopJarStep': {
                    'Jar': 'command-runner.jar',
                    'Args': args
                }
            }
        ]
