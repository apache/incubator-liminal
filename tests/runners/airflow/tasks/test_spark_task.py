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
import tempfile
from unittest import TestCase

from liminal.build import liminal_apps_builder
from liminal.kubernetes import volume_util
from liminal.runners.airflow import DummyDag
from liminal.runners.airflow.executors.kubernetes import KubernetesPodExecutor
from liminal.runners.airflow.tasks.spark import SparkTask
from tests.util import dag_test_utils


class TestSparkTask(TestCase):
    """
    Test Spark Task
    """

    _VOLUME_NAME = 'myvol1'

    def test_spark_on_k8s(self):
        volume_util.delete_local_volume(self._VOLUME_NAME)
        os.environ['TMPDIR'] = '/tmp'
        self.temp_dir = tempfile.mkdtemp()
        self.liminal_config = {
            'volumes': [
                {
                    'volume': self._VOLUME_NAME,
                    'local': {
                        'path': self.temp_dir.replace(
                            "/var/folders",
                            "/private/var/folders"
                        )
                    }
                }
            ]
        }
        volume_util.create_local_volumes(self.liminal_config, None)

        # build spark image
        liminal_apps_builder.build_liminal_apps(
            os.path.join(os.path.dirname(__file__), '../../apps/test_spark_app'))

        outputs_dir = os.path.join(self.temp_dir, 'outputs')

        task_config = {
            'task': "my_spark_task",
            'image': "my_spark_image",
            'application_source': 'wordcount.py',
            'application_arguments': ['words.txt', '/mnt/vol1/outputs/'],
            'env_vars': {},
            'mounts': [
                {
                    'mount': 'mymount',
                    'volume': self._VOLUME_NAME,
                    'path': '/mnt/vol1'
                }
            ]
        }

        dag = dag_test_utils.create_dag()

        task1 = SparkTask(
            task_id="my_spark_task",
            dag=dag,
            liminal_config=self.liminal_config,
            pipeline_config={
                'pipeline': 'my_pipeline'
            },
            task_config=task_config,
            parent=None,
            trigger_rule='all_success')

        executor = KubernetesPodExecutor(
            task_id='k8s',
            liminal_config=self.liminal_config,
            executor_config={
                'executor': 'k8s',
                'name': 'mypod'
            }
        )
        executor.apply_task_to_dag(task=task1)

        for task in dag.tasks:
            print(f'Executing task {task.task_id}')
            task.execute(DummyDag('my_dag', task.task_id).context)

        expected_output = '{"word":"my","count":1}\n' \
                          '{"word":"first","count":1}\n' \
                          '{"word":"liminal","count":1}\n' \
                          '{"word":"spark","count":1}\n' \
                          '{"word":"task","count":1}\n'.split("\n")

        actual = ''
        for filename in os.listdir(outputs_dir):
            if filename.endswith(".json"):
                with open(os.path.join(outputs_dir, filename)) as f:
                    actual = f.read()

        self.assertEqual(actual.split("\n"), expected_output)


def test_get_runnable_command(self):
    task_config = {
        'application_source': 'my_app.py',
        'master': 'yarn',
        'class': 'org.apache.liminal.MySparkApp',
        'conf': {
            'spark.driver.memory': '1g',
            'spark.driver.maxResultSize': '1g',
            'spark.yarn.executor.memoryOverhead': '500M'
        },
        'application_arguments': {
            '--query': "select * from "
                       "dlk_visitor_funnel_dwh_staging.fact_events where unified_Date_prt >= "
                       "'{{yesterday_ds}}'",
            '--output': 'mytable'
        }
    }

    expected = ['spark-submit',
                '--master',
                'yarn',
                '--class',
                'org.apache.liminal.MySparkApp',
                '--conf',
                'spark.driver.maxResultSize=1g', '--conf', 'spark.driver.memory=1g', '--conf',
                'spark.yarn.executor.memoryOverhead=500M', 'my_app.py',
                '--query',
                "select * from dlk_visitor_funnel_dwh_staging.fact_events where "
                "unified_Date_prt >= '{{yesterday_ds}}'",
                '--output', 'mytable']

    actual = SparkTask(
        'my_spark_task',
        DummyDag('dag-id', 'my_spark_task'),
        [],
        trigger_rule='all_success',
        liminal_config={},
        pipeline_config={'pipeline': 'pipeline'},
        task_config=task_config
    ).get_runnable_command()

    self.assertEqual(actual, expected)


def test_missing_spark_arguments(self):
    task_config = {
        'application_source': 'my_app.py',
        'application_arguments': {
            '--query': "select * from dlk_visitor_funnel_dwh_staging.fact_events where"
                       " unified_Date_prt >= '{{yesterday_ds}}'",
            '--output': 'mytable'
        }
    }

    expected = ['spark-submit', 'my_app.py',
                '--query',
                "select * from dlk_visitor_funnel_dwh_staging.fact_events where "
                "unified_Date_prt >= '{{yesterday_ds}}'",
                '--output', 'mytable']

    actual = SparkTask(
        'my_spark_task',
        DummyDag('dag-id', 'my_spark_task'),
        [],
        trigger_rule='all_success',
        liminal_config={},
        pipeline_config={'pipeline': 'pipeline'},
        task_config=task_config
    ).get_runnable_command()

    self.assertEqual(actual, expected)


def test_partially_missing_spark_arguments(self):
    task_config = {
        'application_source': 'my_app.py',
        'class': 'org.apache.liminal.MySparkApp',
        'conf': {
            'spark.driver.memory': '1g',
            'spark.driver.maxResultSize': '1g',
            'spark.yarn.executor.memoryOverhead': '500M'
        },
        'application_arguments': {
            '--query': "select * from dlk_visitor_funnel_dwh_staging.fact_events where "
                       "unified_Date_prt >= '{{yesterday_ds}}'",
            '--output': 'mytable'
        }
    }

    expected = ['spark-submit',
                '--class',
                'org.apache.liminal.MySparkApp',
                '--conf',
                'spark.driver.maxResultSize=1g',
                '--conf',
                'spark.driver.memory=1g',
                '--conf',
                'spark.yarn.executor.memoryOverhead=500M',
                'my_app.py',
                '--query',
                'select * from dlk_visitor_funnel_dwh_staging.fact_events where '
                "unified_Date_prt >= '{{yesterday_ds}}'",
                '--output',
                'mytable']

    actual = SparkTask(
        'my_spark_task',
        DummyDag('dag-id', 'my_spark_task'),
        [],
        trigger_rule='all_success',
        liminal_config={},
        pipeline_config={'pipeline': 'pipeline'},
        task_config=task_config
    ).get_runnable_command()

    print(actual)

    self.assertEqual(actual, expected)
