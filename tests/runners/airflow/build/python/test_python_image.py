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

import docker

from rainbow.build.python.python_image import PythonImage


class TestPythonImage(TestCase):

    def test_build(self):
        config = self.__create_conf('my_task')

        image_name = config['image']

        PythonImage().build('tests/runners/airflow/rainbow', 'hello_world', image_name)

        # TODO: elaborate test of image, validate input/output

        docker_client = docker.from_env()
        docker_client.images.get(image_name)

        cmd = 'export RAINBOW_INPUT="{}" && ' + \
              'sh container-setup.sh && ' + \
              'python hello_world.py && ' + \
              'sh container-teardown.sh'
        cmds = ['/bin/bash', '-c', cmd]

        container_log = docker_client.containers.run(image_name, cmds)

        docker_client.close()

        self.assertEqual("b'Hello world!\\n\\n{}\\n'", str(container_log))

    @staticmethod
    def __create_conf(task_id):
        return {
            'task': task_id,
            'cmd': 'foo bar',
            'image': 'rainbow_image',
            'source': 'tests/runners/airflow/rainbow/hello_world',
            'input_type': 'my_input_type',
            'input_path': 'my_input',
            'output_path': '/my_output.json'
        }
