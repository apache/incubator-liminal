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

import os
from unittest import TestCase
from unittest.mock import patch, MagicMock

from airflow.models import BaseOperator

from liminal.runners.airflow.operators.operator_with_variable_resolving import OperatorWithVariableResolving


class TestKubernetesPodOperatorWithAutoImage(TestCase):
    @patch.dict(os.environ, {'env': 'myenv', 'LIMINAL_STAND_ALONE_MODE': 'True', 'nested': 'value1'})
    def test_value_from_environment_and_liminal_config(self):
        variables = {'my-image': 'my-image', 'something-value1': 'stg'}
        operator = TestOperator(task_id='abc', field='{{env}}', expected='{{my-image}}')
        ret_val = OperatorWithVariableResolving(
            dag=None, operator=operator, task_id='my_task', task_config={}, variables=variables
        ).execute({})

        self.assertEqual(operator.field, 'myenv')
        self.assertEqual(ret_val, 'my-image')

    @patch.dict(os.environ, {'env': 'myenv', 'LIMINAL_STAND_ALONE_MODE': 'True', 'nested': 'value1'})
    def test_value_from_task_variables(self):
        variables = {'my-image': 'my-image', 'my_dict_var': {'env': 'myenv2'}}
        operator = TestOperator(task_id='abc', field='{{env}}', expected='{{my-image}}')
        ret_val = OperatorWithVariableResolving(
            dag=None,
            operator=operator,
            task_id='my_task',
            task_config={'variables': 'my_dict_var'},
            variables=variables,
        ).execute({})

        self.assertEqual(operator.field, 'myenv2')
        self.assertEqual(ret_val, 'my-image')

    @patch.dict(os.environ, {'env': 'myenv', 'LIMINAL_STAND_ALONE_MODE': 'True', 'nested': 'value1'})
    def test_value_from_inline_task_variables(self):
        variables = {'my-image': 'my-image'}
        operator = TestOperator(task_id='abc', field='{{env}}', expected='{{my-image}}')
        ret_val = OperatorWithVariableResolving(
            dag=None,
            operator=operator,
            task_id='my_task',
            task_config={'variables': {'env': 'myenv2'}},
            variables=variables,
        ).execute({})

        self.assertEqual(operator.field, 'myenv2')
        self.assertEqual(ret_val, 'my-image')

    @patch.dict(os.environ, {'env': 'staging', 'LIMINAL_STAND_ALONE_MODE': 'True'})
    def test_nested_variables(self):
        variables = {
            'nested-the-s3-location': 'good',
            'my-image': 'my-image',
            'something-value1': 'stg',
            'env_val-staging': 'the-s3-location',
            'nested': 'value1',
        }
        operator = TestOperator(
            task_id='abc', field='something-{{nested-{{env_val-{{env}}}}}}', expected='{{my-image}}'
        )

        OperatorWithVariableResolving(
            dag=None, operator=operator, task_id='my_task', task_config={}, variables=variables
        ).execute({})

        self.assertEqual(operator.field, 'something-good')

    @patch.dict(os.environ, {'env': 'staging', 'LIMINAL_STAND_ALONE_MODE': 'True'})
    def test_dag_run_conf_parameters(self):
        dag_run = MagicMock()
        dag_run.conf = {
            'nested-the-s3-location': 'good',
            'my-image': 'my-image',
            'something-value1': 'stg',
            'env_val-staging': 'the-s3-location',
            'nested': 'value1',
        }
        operator = TestOperator(
            task_id='abc', field='something-{{nested-{{env_val-{{env}}}}}}', expected='{{my-image}}'
        )
        OperatorWithVariableResolving(
            dag=None, operator=operator, task_id='my_task', task_config={}, variables={}
        ).execute({'dag_run': dag_run})

        self.assertEqual(operator.field, 'something-good')

    @patch.dict(os.environ, {'env': 'staging', 'LIMINAL_STAND_ALONE_MODE': 'True'})
    def test_duplicated_params(self):
        dag_run = MagicMock()
        dag_run.conf = {
            'nested-the-s3-location': 'good',
            'my-image': 'my-image',
            'something-value1': 'stg',
            'env_val-staging': 'the-s3-location',
            'nested': 'value1',
        }
        operator = TestOperator(
            task_id='abc',
            field='something-{{nested-{{env_val-{{env}}}}}}-' '{{nested-{{env_val-{{env}}}}}}',
            expected='{{my-image}}',
        )
        OperatorWithVariableResolving(
            dag=None, operator=operator, task_id='my_task', task_config={}, variables={}
        ).execute({'dag_run': dag_run})

        self.assertEqual(operator.field, 'something-good-good')

        operator = TestOperator(task_id='abc', field='something-{{env}} {{env}}', expected='{{my-image}}')
        OperatorWithVariableResolving(
            dag=None, operator=operator, task_id='my_task', task_config={}, variables={}
        ).execute({'dag_run': dag_run})

        self.assertEqual(operator.field, 'something-staging staging')

        dag_run.conf = {'var1': '{{var2}}', 'var2': 'bla', 'my-image': 'my-image'}
        operator = TestOperator(task_id='abc', field='{{ var1 }}', expected='{{my-image}}')
        OperatorWithVariableResolving(
            dag=None, operator=operator, task_id='my_task', task_config={}, variables={}
        ).execute({'dag_run': dag_run})

        self.assertEqual(operator.field, 'bla')

    @patch.dict(os.environ, {'env': 'staging', 'LIMINAL_STAND_ALONE_MODE': 'True'})
    def test_non_existing_param(self):
        dag_run = MagicMock()
        dag_run.conf = {'var1': '{{var2}}', 'var2': 'bla'}
        operator = TestOperator(task_id='abc', field='{{myimage}}', expected='{{myimage}}')
        OperatorWithVariableResolving(
            dag=None, operator=operator, task_id='my_task', task_config={}, variables={}
        ).execute({'dag_run': dag_run})

        self.assertEqual(operator.field, '')


class BaseTestOperator(BaseOperator):
    def execute(self, context):
        raise NotImplementedError()

    def __init__(self, field, expected, *args, **kwargs):
        self.field = field
        self.expected = expected
        super().__init__(*args, **kwargs)


class TestOperator(BaseTestOperator):
    def __init__(self, *args, **kwargs):
        super(TestOperator, self).__init__(*args, **kwargs)

    def execute(self, context):
        return self.expected
