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

from copy import deepcopy
from unittest import TestCase, mock
from unittest.mock import MagicMock

import boto3
from airflow.contrib.hooks.emr_hook import EmrHook
from airflow.contrib.operators.emr_add_steps_operator import EmrAddStepsOperator
from airflow.contrib.sensors.emr_step_sensor import EmrStepSensor
from moto import mock_emr

from liminal.runners.airflow import DummyDag
from liminal.runners.airflow.executors.emr import EMRExecutor
from liminal.runners.airflow.tasks import hadoop
from tests.util import dag_test_utils


@mock_emr
class TestEMRExecutorTask(TestCase):
    """
    Test EMRExecutor task
    """

    def setUp(self) -> None:
        self.run_job_flow_args = dict(
            Instances={
                "InstanceCount": 1,
                "KeepJobFlowAliveWhenNoSteps": True,
                "MasterInstanceType": "c3.medium",
                "Placement": {"AvailabilityZone": "us-east-1"},
                "SlaveInstanceType": "c3.xlarge",
            },
            JobFlowRole="EMR_EC2_DefaultRole",
            LogUri="s3://liminal/log",
            Name="test-emr-cluster",
            ServiceRole="EMR_DefaultRole",
            VisibleToAllUsers=True
        )

        self.client = boto3.client("emr", region_name="us-east-1")

        args = deepcopy(self.run_job_flow_args)

        self.cluster_id = self.client.run_job_flow(**args)["JobFlowId"]

        self.dag = dag_test_utils.create_dag()
        self.dag.context = DummyDag(dag_id=self.dag.dag_id, task_id="").context
        self.executor_name = 'test-emr-cluster'
        executor_config = {
            'executor': self.executor_name,
            'cluster_name': self.executor_name,
            'aws_conn_id': 'us-east-1',
            'type': 'emr',
            'properties': {
                'ActionOnFailure': 'CONTINUE'
            }

        }
        self.hadoop_task = MagicMock(spec=hadoop.HadoopTask)
        self.hadoop_task.get_runnable_command.return_value = ['spark-submit', 'test', 'params',
                                                              '--param']
        self.hadoop_task.task_id = 'spark-task'
        self.hadoop_task.dag = self.dag
        self.hadoop_task.trigger_rule = 'all_done'
        self.hadoop_task.parent = None

        self.emr = EMRExecutor(
            self.executor_name,
            liminal_config={},
            executor_config=executor_config
        )

    def test_apply_task_to_dag(self):
        self.emr.apply_task_to_dag(task=self.hadoop_task)

        self.assertEqual(len(self.dag.tasks), 2)

        self.assertIsInstance(self.dag.tasks[0], EmrAddStepsOperator)
        self.assertIsInstance(self.dag.tasks[1], EmrStepSensor)

    @mock.patch.object(EmrHook, 'get_conn')
    def test_add_step(self, mock_emr_hook_get_conn):
        aws_region = 'us-east-1'
        mock_emr_hook_get_conn.return_value = boto3.client(
            'emr',
            region_name=aws_region
        )

        self.emr.apply_task_to_dag(task=self.hadoop_task)

        emr_add_step_task = self.dag.tasks[0]

        self.assertIsInstance(emr_add_step_task, EmrAddStepsOperator)

        step_id = emr_add_step_task.execute(self.dag.context)[0]

        desc_step = self.client.describe_step(
            ClusterId=self.cluster_id,
            StepId=step_id
        )['Step']

        self.assertEqual(desc_step['Config'],
                         {'Jar': 'command-runner.jar',
                          'Properties': {},
                          'Args': ['spark-submit', 'test', 'params', '--param']
                          })

        self.assertEqual(desc_step['Name'], 'spark-task')

        self.assertEqual(desc_step['ActionOnFailure'], 'CONTINUE')

    def test_watch_step(self):
        self.emr.apply_task_to_dag(task=self.hadoop_task, parents=[])

        emr_watch_step_task = self.dag.tasks[1]

        self.assertIsInstance(emr_watch_step_task, EmrStepSensor)

        # todo - elaborate tests
