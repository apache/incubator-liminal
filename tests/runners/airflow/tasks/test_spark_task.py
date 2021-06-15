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
from unittest import TestCase

from liminal.runners.airflow import DummyDag
from liminal.runners.airflow.tasks.spark import SparkTask


class TestSparkTask(TestCase):
    """
    Test Spark Task
    """

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
                '--query': "select * from dlk_visitor_funnel_dwh_staging.fact_events where unified_Date_prt >= "
                           "'{{yesterday_ds}}'",
                '--output': 'mytable'
            }
        }

        expected = ['spark-submit', '--master', 'yarn', '--class', 'org.apache.liminal.MySparkApp', '--conf',
                    'spark.driver.memory=1g', '--conf', 'spark.driver.maxResultSize=1g', '--conf',
                    'spark.yarn.executor.memoryOverhead=500M', 'my_app.py',
                    '--query',
                    "select * from dlk_visitor_funnel_dwh_staging.fact_events where unified_Date_prt >="
                    " '{{yesterday_ds}}'",
                    '--output', 'mytable']

        actual = SparkTask(
            'my_spark_task',
            DummyDag('dag-id', 'my_spark_task'),
            [],
            trigger_rule='all_success',
            liminal_config={},
            pipeline_config={},
            task_config=task_config
        ).get_runnable_command()

        self.assertEqual(actual, expected)

    def test_missing_spark_arguments(self):
        task_config = {
            'application_source': 'my_app.py',
            'application_arguments': {
                '--query': "select * from dlk_visitor_funnel_dwh_staging.fact_events where unified_Date_prt >= "
                           "'{{yesterday_ds}}'",
                '--output': 'mytable'
            }
        }

        expected = ['spark-submit', 'my_app.py',
                    '--query',
                    "select * from dlk_visitor_funnel_dwh_staging.fact_events where unified_Date_prt >="
                    " '{{yesterday_ds}}'",
                    '--output', 'mytable']

        actual = SparkTask(
            'my_spark_task',
            DummyDag('dag-id', 'my_spark_task'),
            [],
            trigger_rule='all_success',
            liminal_config={},
            pipeline_config={},
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
                '--query': "select * from dlk_visitor_funnel_dwh_staging.fact_events where unified_Date_prt >= "
                           "'{{yesterday_ds}}'",
                '--output': 'mytable'
            }
        }

        expected = ['spark-submit',
                    '--class',
                    'org.apache.liminal.MySparkApp',
                    '--conf',
                    'spark.driver.memory=1g',
                    '--conf',
                    'spark.driver.maxResultSize=1g',
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
            pipeline_config={},
            task_config=task_config
        ).get_runnable_command()

        self.assertEqual(actual, expected)
