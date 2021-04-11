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

import unittest
from unittest import TestCase

from liminal.runners.airflow.tasks import job_end
from tests.util import dag_test_utils


# noinspection DuplicatedCode
class TestJobEndTask(TestCase):

    def test_apply_task_to_dag(self):
        dag = dag_test_utils.create_dag()

        task0 = job_end.JobEndTask(
            task_id='job_end',
            dag=dag,
            pipeline_config={'pipeline': 'my_end_pipeline'},
            task_config={},
            parent=None,
            trigger_rule='all_done',
            liminal_config={'metrics': {'namespace': 'EndJobNameSpace', 'backends': ['cloudwatch']}}
        )
        task0.apply_task_to_dag()

        self.assertEqual(len(dag.tasks), 1)
        dag_task0 = dag.tasks[0]

        self.assertEqual(dag_task0.namespace, 'EndJobNameSpace')
        self.assertEqual(dag_task0.backends, ['cloudwatch'])

        self.assertEqual(dag_task0.task_id, 'end')

    def test_apply_task_to_dag_missing_metrics(self):
        conf = {'pipeline': 'my_pipeline'}
        dag = dag_test_utils.create_dag()

        task0 = job_end.JobEndTask(task_id="job_end", dag=dag,
                                   pipeline_config={'pipeline': 'my_end_pipeline'}, liminal_config=conf, parent=None,
                                   trigger_rule='all_done', task_config={})
        task0.apply_task_to_dag()

        self.assertEqual(len(dag.tasks), 1)
        dag_task0 = dag.tasks[0]

        self.assertEqual(dag_task0.namespace, '')
        self.assertEqual(dag_task0.backends, [])
        self.assertEqual(dag_task0.trigger_rule, 'all_done')

    def test_apply_task_to_dag_with_partial_configuration(self):
        dag = dag_test_utils.create_dag()

        task0 = job_end.JobEndTask(task_id="job_enc",
                                   dag=dag,
                                   liminal_config={'metrics': {'namespace': 'EndJobNameSpace'}},
                                   pipeline_config={'pipeline': 'my_end_pipeline'},
                                   task_config={},
                                   parent=None,
                                   trigger_rule='all_done')
        task0.apply_task_to_dag()

        self.assertEqual(len(dag.tasks), 1)
        dag_task0 = dag.tasks[0]

        self.assertEqual(dag_task0.namespace, 'EndJobNameSpace')
        self.assertEqual(dag_task0.backends, [])
        self.assertEqual(dag_task0.trigger_rule, 'all_done')


if __name__ == '__main__':
    unittest.main()
