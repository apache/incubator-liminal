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

from airflow.operators.dummy import DummyOperator
from airflow.operators.python import BranchPythonOperator
from flatdict import FlatDict

from liminal.runners.airflow.operators.cloudformation import (
    CloudFormationCreateStackOperator,
    CloudFormationCreateStackSensor,
    CloudFormationHook,
)
from liminal.runners.airflow.operators.operator_with_variable_resolving import (
    OperatorWithVariableResolving,
)
from liminal.runners.airflow.tasks import airflow


class CreateCloudFormationStackTask(airflow.AirflowTask):
    """
    Creates cloud_formation stack.
    """

    def __init__(
        self, task_id, dag, parent, trigger_rule, liminal_config, pipeline_config, task_config, variables=None
    ):
        super().__init__(task_id, dag, parent, trigger_rule, liminal_config, pipeline_config, task_config, variables)
        self.stack_name = task_config['stack_name']

    def apply_task_to_dag(self):
        check_cloudformation_stack_exists_task = self._add_variables_to_operator(
            BranchPythonOperator(
                templates_dict={'stack_name': self.stack_name},
                task_id=f'is-cloudformation-{self.task_id}-running',
                python_callable=self.__cloudformation_stack_running_branch,
                provide_context=True,
            )
        )

        create_cloudformation_stack_task = self._add_variables_to_operator(
            CloudFormationCreateStackOperator(
                task_id=f'create-cloudformation-{self.task_id}', params={**self.__reformatted_params()}
            )
        )

        create_stack_sensor_task = self._add_variables_to_operator(
            CloudFormationCreateStackSensor(
                task_id=f'cloudformation-watch-{self.task_id}-create',
                stack_name=self.stack_name,
            )
        )

        stack_creation_end_task = DummyOperator(
            task_id=f'creation-end-{self.task_id}', trigger_rule='all_done', dag=self.dag
        )

        if self.parent:
            self.parent.set_downstream(check_cloudformation_stack_exists_task)

        create_stack_sensor_task.set_downstream(stack_creation_end_task)
        create_cloudformation_stack_task.set_downstream(create_stack_sensor_task)
        check_cloudformation_stack_exists_task.set_downstream(create_cloudformation_stack_task)
        check_cloudformation_stack_exists_task.set_downstream(stack_creation_end_task)

        return stack_creation_end_task

    def __cloudformation_stack_running_branch(self, stack_name):
        cloudformation = CloudFormationHook().get_conn()
        try:
            stack_status = cloudformation.describe_stacks(StackName=stack_name)['Stacks'][0]['StackStatus']
            if stack_status in ['CREATE_COMPLETE', 'DELETE_FAILED']:
                print(f'Stack {stack_name} is running')
                return f'creation-end-{self.task_id}'
            else:
                print(f'Stack {stack_name} is not running')
        except Exception as e:
            if 'does not exist' in str(e):
                print(f'Stack {stack_name} does not exist')
                return f'create-cloudformation-{self.task_id}'
            else:
                raise e

        return f'create-cloudformation-{self.task_id}'

    # noinspection PyUnusedLocal
    def __reformatted_params(self, **kwargs):
        return {
            'StackName': self.stack_name,
            **self.task_config['properties'],
            'Parameters': [
                {'ParameterKey': x, 'ParameterValue': str(y)}
                for (x, y) in FlatDict(self.task_config['properties']['Parameters']).items()
            ],
        }
