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
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import BranchPythonOperator
from airflow.utils.trigger_rule import TriggerRule

from liminal.runners.airflow.operators.cloudformation import CloudFormationDeleteStackOperator, \
    CloudFormationDeleteStackSensor
from liminal.runners.airflow.tasks import airflow


class DeleteCloudFormationStackTask(airflow.AirflowTask):
    """
    Deletes cloud_formation stack.
    """

    def __init__(self, task_id, dag, parent, trigger_rule, liminal_config, pipeline_config,
                 task_config):
        super().__init__(task_id, dag, parent, trigger_rule, liminal_config,
                         pipeline_config, task_config)
        self.stack_name = task_config['stack_name']

    def apply_task_to_dag(self):
        check_dags_queued_task = BranchPythonOperator(
            task_id=f'{self.task_id}-is-dag-queue-empty',
            python_callable=self.__queued_dag_runs_exists,
            provide_context=True,
            trigger_rule=TriggerRule.ALL_DONE,
            dag=self.dag
        )

        delete_stack_task = CloudFormationDeleteStackOperator(
            task_id=f'delete-cloudformation-{self.task_id}',
            params={'StackName': self.stack_name},
            dag=self.dag
        )

        delete_stack_sensor = CloudFormationDeleteStackSensor(
            task_id=f'cloudformation-watch-{self.task_id}-delete',
            stack_name=self.stack_name,
            dag=self.dag
        )

        stack_delete_end_task = DummyOperator(
            task_id=f'delete-end-{self.task_id}',
            dag=self.dag
        )

        if self.parent:
            self.parent.set_downstream(check_dags_queued_task)

        check_dags_queued_task.set_downstream(stack_delete_end_task)
        check_dags_queued_task.set_downstream(delete_stack_task)
        delete_stack_task.set_downstream(delete_stack_sensor)
        delete_stack_sensor.set_downstream(stack_delete_end_task)

        return stack_delete_end_task

    # noinspection PyUnusedLocal
    def __queued_dag_runs_exists(self, **kwargs):
        if self.dag.get_num_active_runs() > 1:
            return f'delete-end-{self.task_id}'
        else:
            return f'delete-cloudformation-{self.task_id}'
