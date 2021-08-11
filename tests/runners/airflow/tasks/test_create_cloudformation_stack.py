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
from unittest import TestCase, mock
from unittest.mock import MagicMock

from airflow.operators.dummy import DummyOperator
from airflow.operators.python import BranchPythonOperator
from moto import mock_cloudformation

from liminal.runners.airflow.executors import airflow
from liminal.runners.airflow.operators.cloudformation import CloudFormationCreateStackOperator, \
    CloudFormationCreateStackSensor, CloudFormationHook
from liminal.runners.airflow.operators.operator_with_variable_resolving import OperatorWithVariableResolving
from liminal.runners.airflow.tasks.create_cloudformation_stack import CreateCloudFormationStackTask
from tests.util import dag_test_utils


# noinspection DuplicatedCode
@mock_cloudformation
class TestCreateCloudFormationStackTask(TestCase):
    """
    Test CreateCloudFormationStackTask
    """

    def setUp(self) -> None:
        self.dag = dag_test_utils.create_dag()
        self.dag.context = {
            'ti': self.dag,
            'ts': datetime.now().timestamp(),
            'execution_date': datetime.now().timestamp()
        }
        self.dag.get_dagrun = MagicMock()

        self.cluster_name = "liminal-cluster-for-tests"
        self.config = {
            'task': 'create_emr',
            'type': 'create_cloudformation_stack',
            'description': 'create emr',
            'stack_name': self.cluster_name,
            'properties': {
                'OnFailure': 'DO_NOTHING',
                'TimeoutInMinutes': 25,
                'Capabilities': ['CAPABILITY_NAMED_IAM'],
                'TemplateURL': 'https://s3.amazonaws.com/liminal-tests/emr_cluster_creation.yml',
                'Parameters': {
                    'Environment': 'Staging',
                    'OwnerTeam': 'liminal-team',
                    'Tenancy': 'Ephemeral',
                    'MasterServerCount': '1',
                    'CoreServerCount': '1',
                    'EmrApplicationRelease': '5.28',
                    'InstanceTypeMaster': 'm5.xlarge',
                    'InstanceTypeCore': 'm5.xlarge'
                }
            }
        }

        self.create_cloudformation_task = \
            CreateCloudFormationStackTask(
                self.config['task'],
                self.dag,
                [],
                trigger_rule='all_success',
                liminal_config={},
                pipeline_config={},
                task_config=self.config
            )

        airflow.AirflowExecutor("airflow-executor", {}, {}).apply_task_to_dag(
            task=self.create_cloudformation_task)

    def test_apply_task_to_dag(self):
        self.assertEqual(len(self.dag.tasks), 4)

        self.assertIsInstance(self.dag.tasks[0], OperatorWithVariableResolving)
        self.assertIsInstance(self.dag.tasks[0].operator_delegate, BranchPythonOperator)
        self.assertIsInstance(self.dag.tasks[1], OperatorWithVariableResolving)
        self.assertIsInstance(self.dag.tasks[1].operator_delegate, CloudFormationCreateStackOperator)
        self.assertIsInstance(self.dag.tasks[2], OperatorWithVariableResolving)
        self.assertIsInstance(self.dag.tasks[2].operator_delegate, CloudFormationCreateStackSensor)
        self.assertIsInstance(self.dag.tasks[3], DummyOperator)

    def test_cloudformation_does_not_exist(self):
        with mock.patch.object(CloudFormationHook, 'get_conn') as mock_conn:
            mock_cf_conn = MagicMock()
            mock_cf_conn.describe_stacks.return_value.raiseError.side_effect = Exception()

            mock_conn.return_value = mock_cf_conn
            is_cloudformation_exists = self.dag.tasks[0].operator_delegate

            print(is_cloudformation_exists)
            self.assertEqual(
                is_cloudformation_exists.python_callable(stack_name=self.cluster_name),
                'create-cloudformation-create_emr')

    def test_cloudformation_exist_and_running(self):
        is_cloudformation_exists = self.dag.tasks[0].operator_delegate

        for status in ['CREATE_COMPLETE', 'DELETE_FAILED']:
            with mock.patch.object(CloudFormationHook, 'get_conn') as mock_conn:
                mock_cloudformation_conn = MagicMock()
                mock_cloudformation_conn.describe_stacks.return_value = {
                    'Stacks': [
                        {
                            'StackStatus': status
                        }
                    ]
                }

                mock_conn.return_value = mock_cloudformation_conn

                self.assertEqual(
                    is_cloudformation_exists.python_callable(stack_name=self.cluster_name),
                    'creation-end-create_emr')

    def test_cloudformation_exists_and_not_running(self):
        is_cloudformation_exists = self.dag.tasks[0].operator_delegate

        for status in ['DELETED']:
            with mock.patch.object(CloudFormationHook, 'get_conn') as mock_conn:
                mock_cloudformation_conn = MagicMock()
                mock_cloudformation_conn.describe_stacks.return_value = {
                    'Stacks': [
                        {
                            'StackStatus': status
                        }
                    ]
                }

                mock_conn.return_value = mock_cloudformation_conn

                self.assertEqual(
                    is_cloudformation_exists.python_callable(stack_name=self.cluster_name),
                    'create-cloudformation-create_emr')

    def test_cloudformation_create_stack_operator_task(self):
        create_cloudformation_stack = self.dag.tasks[1]
        self.assertEqual(create_cloudformation_stack.task_id, 'create-cloudformation-create_emr')
