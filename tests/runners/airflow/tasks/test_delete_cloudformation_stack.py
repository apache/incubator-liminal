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

from datetime import datetime
from unittest import TestCase
from unittest.mock import MagicMock

from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import BranchPythonOperator
from airflow.utils.trigger_rule import TriggerRule
from moto import mock_cloudformation

from liminal.runners.airflow.operators.cloudformation import (
    CloudFormationDeleteStackOperator,
    CloudFormationDeleteStackSensor,
)
from liminal.runners.airflow.operators.operator_with_variable_resolving import (
    OperatorWithVariableResolving,
)
from liminal.runners.airflow.tasks.delete_cloudformation_stack import (
    DeleteCloudFormationStackTask,
)
from tests.util import dag_test_utils


# noinspection DuplicatedCode
@mock_cloudformation
class TestDeleteCloudFormationStackTask(TestCase):
    """
    Test DeleteCloudFormationStackTask
    """

    def setUp(self) -> None:
        self.dag = dag_test_utils.create_dag()
        self.dag.context = {
            'ti': self.dag,
            'ts': datetime.now().timestamp(),
            'execution_date': datetime.now().timestamp(),
        }
        self.dag.get_dagrun = MagicMock()

        self.cluster_name = "liminal-cluster-for-tests"

        self.delete_cloudformation_task = DeleteCloudFormationStackTask(
            'delete-emr',
            self.dag,
            [],
            trigger_rule='all_success',
            liminal_config={},
            pipeline_config={},
            task_config={'stack_name': self.cluster_name},
        )

        self.delete_cloudformation_task.apply_task_to_dag()

    def test_apply_task_to_dag(self):
        self.assertEqual(len(self.dag.tasks), 4)

        self.assertIsInstance(self.dag.tasks[0], BranchPythonOperator)
        self.assertIsInstance(self.dag.tasks[1], OperatorWithVariableResolving)
        self.assertIsInstance(self.dag.tasks[1].operator_delegate, CloudFormationDeleteStackOperator)
        self.assertIsInstance(self.dag.tasks[2], OperatorWithVariableResolving)
        self.assertIsInstance(self.dag.tasks[2].operator_delegate, CloudFormationDeleteStackSensor)
        self.assertIsInstance(self.dag.tasks[3], DummyOperator)

    def test_check_dags_queued_task(self):
        self.dag.get_num_active_runs = MagicMock()

        self.dag.get_num_active_runs.return_value = 2
        check_dags_queued_task = self.dag.tasks[0]
        self.assertEqual(check_dags_queued_task.trigger_rule, TriggerRule.ALL_DONE)

        self.assertEqual(check_dags_queued_task.python_callable(), f'delete-end-delete-emr')

        self.dag.get_num_active_runs.return_value = 1

        self.assertEqual(check_dags_queued_task.python_callable(), f'delete-cloudformation-delete-emr')
