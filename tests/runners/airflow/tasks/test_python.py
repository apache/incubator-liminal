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

import docker

from rainbow.runners.airflow.operators.kubernetes_pod_operator import \
    ConfigurableKubernetesPodOperator
from rainbow.runners.airflow.tasks import python
from tests.util import dag_test_utils


class TestPythonTask(TestCase):

    def test_apply_task_to_dag(self):
        # TODO: elaborate tests
        dag = dag_test_utils.create_dag()

        task_id = 'my_task'

        config = self.__create_conf(task_id)

        task0 = python.PythonTask(dag, 'my_pipeline', None, config, 'all_success')
        task0.apply_task_to_dag()

        self.assertEqual(len(dag.tasks), 1)
        dag_task0 = dag.tasks[0]

        self.assertIsInstance(dag_task0, ConfigurableKubernetesPodOperator)
        self.assertEqual(dag_task0.task_id, task_id)

    def test_build(self):
        config = self.__create_conf('my_task')

        task0 = python.PythonTask(None, None, None, config, None)
        task0.build()

        # TODO: elaborate test of image, validate input/output
        image_name = config['image']

        docker_client = docker.from_env()
        docker_client.images.get(image_name)
        container_log = docker_client.containers.run(image_name, "python hello_world.py")
        docker_client.close()

        self.assertEqual("b'Hello world!\\n'", str(container_log))

    @staticmethod
    def __create_conf(task_id):
        return {
            'task': task_id,
            'cmd': 'foo bar',
            'image': 'my_image',
            'source': 'tests/runners/airflow/tasks/hello_world',
            'input_type': 'my_input_type',
            'input_path': 'my_input',
            'output_path': '/my_output.json'
        }


if __name__ == '__main__':
    unittest.main()
