import os
from unittest import TestCase
from unittest.mock import patch, MagicMock

from airflow.models import BaseOperator

from liminal.runners.airflow.operators.operator_with_variable_resolving import OperatorWithVariableResolving


class TestKubernetesPodOperatorWithAutoImage(TestCase):
    @patch.dict(os.environ, {'env': 'myenv', 'LIMINAL_STAND_ALONE_MODE': 'True', 'nested': 'value1'})
    def test_value_from_environment_and_liminal_config(self):
        liminal_config = {'variables': {'my-image': 'my-image', 'something-value1': 'stg'}}
        operator = TestOperator(task_id='abc', field='{{env}}', expected='{{my-image}}')
        ret_val = OperatorWithVariableResolving(operator=operator,
                                                task_id='my_task',
                                                liminal_config=liminal_config).execute({})

        self.assertEqual(operator.field, 'myenv')
        self.assertEqual(ret_val, 'my-image')

    @patch.dict(os.environ, {'env': 'staging', 'LIMINAL_STAND_ALONE_MODE': 'True'})
    def test_nested_variables(self):
        liminal_config = {'variables': {'nested-the-s3-location': 'good', 'my-image': 'my-image',
                                        'something-value1': 'stg', 'env_val-staging': 'the-s3-location',
                                        'nested': 'value1'}}
        operator = TestOperator(task_id='abc', field='something-{{nested-{{env_val-{{env}}}}}}',
                                expected='{{my-image}}')

        OperatorWithVariableResolving(operator=operator,
                                      task_id='my_task',
                                      liminal_config=liminal_config).execute({})

        self.assertEqual(operator.field, 'something-good')

    @patch.dict(os.environ, {'env': 'staging', 'LIMINAL_STAND_ALONE_MODE': 'True'})
    def test_dag_run_conf_parameters(self):
        dag_run = MagicMock()
        dag_run.conf = {'nested-the-s3-location': 'good', 'my-image': 'my-image',
                        'something-value1': 'stg', 'env_val-staging': 'the-s3-location', 'nested': 'value1'}
        liminal_config = {'variables': {}}
        operator = TestOperator(task_id='abc', field='something-{{nested-{{env_val-{{env}}}}}}',
                                expected='{{my-image}}')
        OperatorWithVariableResolving(operator=operator,
                                      task_id='my_task',
                                      liminal_config=liminal_config).execute({'dag_run': dag_run})

        self.assertEqual(operator.field, 'something-good')


class TestOperator(BaseOperator):
    template_fields = ['field', 'expected']

    def __init__(self, *args, **kwargs):
        self.field = kwargs.pop('field')
        self.expected = kwargs.pop('expected')
        super(TestOperator, self).__init__(*args, **kwargs)

    def execute(self, context):
        return self.expected
