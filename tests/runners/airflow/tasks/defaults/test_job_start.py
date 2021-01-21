# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from unittest import TestCase

from liminal.runners.airflow.tasks.defaults import job_start
from tests.util import dag_test_utils


# noinspection DuplicatedCode
class TestJobStartTask(TestCase):

    def test_apply_task_to_dag(self):
        dag = dag_test_utils.create_dag()

        task0 = job_start.JobStartTask(
            dag,
            {'metrics': {'namespace': 'StartJobNameSpace', 'backends': ['cloudwatch']}},
            {'pipeline': 'my_start_pipeline'},
            {},
            None,
            'all_success'
        )
        task0.apply_task_to_dag()

        self.assertEqual(len(dag.tasks), 1)
        dag_task0 = dag.tasks[0]

        self.assertEqual(dag_task0.namespace, 'StartJobNameSpace')
        self.assertEqual(dag_task0.backends, ['cloudwatch'])

        self.assertEqual(dag_task0.task_id, 'start')

    def test_apply_task_to_dag_missing_metrics(self):
        conf = {'pipeline': 'my_pipeline'}

        dag = dag_test_utils.create_dag()

        task0 = job_start.JobStartTask(dag,
                                       {},
                                       {'pipeline': 'my_end_pipeline'},
                                       conf,
                                       None,
                                       'all_success')
        task0.apply_task_to_dag()

        self.assertEqual(len(dag.tasks), 1)
        dag_task0 = dag.tasks[0]

        self.assertEqual(dag_task0.namespace, '')
        self.assertEqual(dag_task0.backends, [])
        self.assertEqual(dag_task0.trigger_rule, 'all_success')

    def test_apply_task_to_dag_with_partial_configuration(self):
        dag = dag_test_utils.create_dag()

        task0 = job_start.JobStartTask(dag,
                                       {'metrics': {'namespace': 'StartJobNameSpace'}},
                                       {'pipeline': 'my_start_pipeline'},
                                       {},
                                       None,
                                       'all_success')
        task0.apply_task_to_dag()

        self.assertEqual(len(dag.tasks), 1)
        dag_task0 = dag.tasks[0]

        self.assertEqual(dag_task0.namespace, 'StartJobNameSpace')
        self.assertEqual(dag_task0.backends, [])


if __name__ == '__main__':
    unittest.main()
