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

import logging
import os
import tempfile
import unittest
from unittest import TestCase

from liminal.build import liminal_apps_builder
from liminal.kubernetes import volume_util
from liminal.runners.airflow import DummyDag
from liminal.runners.airflow.executors.kubernetes import KubernetesPodExecutor
from liminal.runners.airflow.tasks import python
from tests.util import dag_test_utils


class TestPythonTask(TestCase):
    _VOLUME_NAME = 'myvol1'

    def setUp(self) -> None:
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

        liminal_apps_builder.build_liminal_apps(
            os.path.join(os.path.dirname(__file__), '../liminal'))

    def test_apply_task_to_dag(self):
        dag = dag_test_utils.create_dag()

        task0 = self.__create_python_task(dag,
                                          'my_input_task',
                                          None,
                                          'my_python_task_img',
                                          'python -u write_inputs.py',
                                          env_vars={
                                              'NUM_FILES': 10,
                                              'NUM_SPLITS': 3
                                          })
        task0.apply_task_to_dag()

        task1 = self.__create_python_task(dag,
                                          'my_output_task',
                                          dag.tasks[0],
                                          'my_parallelized_python_task_img',
                                          'python -u write_outputs.py',
                                          executors=3)
        task1.apply_task_to_dag()

        for task in dag.tasks:
            print(f'Executing task {task.task_id}')
            task.execute(DummyDag('my_dag', task.task_id).context)

        inputs_dir = os.path.join(self.temp_dir, 'inputs')
        outputs_dir = os.path.join(self.temp_dir, 'outputs')

        self.assertListEqual(sorted(os.listdir(self.temp_dir)), sorted(['outputs', 'inputs']))

        inputs_dir_contents = sorted(os.listdir(inputs_dir))

        self.assertListEqual(inputs_dir_contents, ['0', '1', '2'])

        self.assertListEqual(sorted(os.listdir(os.path.join(inputs_dir, '0'))),
                             ['input0.json', 'input3.json', 'input6.json', 'input9.json'])

        self.assertListEqual(sorted(os.listdir(os.path.join(inputs_dir, '1'))),
                             ['input1.json', 'input4.json', 'input7.json'])

        self.assertListEqual(sorted(os.listdir(os.path.join(inputs_dir, '2'))),
                             ['input2.json', 'input5.json', 'input8.json'])

        self.assertListEqual(sorted(os.listdir(outputs_dir)),
                             ['output0.txt', 'output1.txt',
                              'output2.txt', 'output3.txt',
                              'output4.txt', 'output5.txt',
                              'output6.txt', 'output7.txt',
                              'output8.txt', 'output9.txt'])

        for filename in os.listdir(outputs_dir):
            with open(os.path.join(outputs_dir, filename)) as f:
                expected_file_content = filename.replace('output', 'myval').replace('.txt', '')
                self.assertEqual(f.read(), expected_file_content)

    def __create_python_task(self,
                             dag,
                             task_id,
                             parent,
                             image,
                             cmd,
                             env_vars=None,
                             executors=None):
        self.liminal_config['executors'] = [
            {
                'executor': 'k8s',
                'type': 'kubernetes',
            }
        ]
        task_config = {
            'task': task_id,
            'cmd': cmd,
            'image': image,
            'env_vars': env_vars if env_vars is not None else {},
            'mounts': [
                {
                    'mount': 'mymount',
                    'volume': self._VOLUME_NAME,
                    'path': '/mnt/vol1'
                }
            ]
        }

        if executors:
            task_config['executors'] = executors

        return python.PythonTask(
            task_id=task_id,
            dag=dag,
            liminal_config={
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
                ]},
            pipeline_config={
                'pipeline': 'my_pipeline'
            },
            task_config=task_config,
            parent=parent,
            trigger_rule='all_success',
            executor=KubernetesPodExecutor(
                task_id='k8s',
                liminal_config=self.liminal_config,
                executor_config={
                    'executor': 'k8s',
                    'name': 'mypod'
                }
            ))


if __name__ == '__main__':
    unittest.main()
