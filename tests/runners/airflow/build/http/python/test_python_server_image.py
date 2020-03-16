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

import threading
import time
import unittest
import urllib.request
from unittest import TestCase

import docker

from rainbow.build.http.python.python_server_image import PythonServerImageBuilder


class TestPythonServer(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.docker_client = docker.from_env()
        self.config = self.__create_conf('my_task')
        self.image_name = self.config['image']
        self.__remove_containers()

    def tearDown(self) -> None:
        self.__remove_containers()
        self.docker_client.close()

    def test_build_python_server(self):
        builder = PythonServerImageBuilder(config=self.config,
                                           base_path='tests/runners/airflow/rainbow',
                                           relative_source_path='myserver',
                                           tag=self.image_name)

        builder.build()

        thread = threading.Thread(target=self.__run_container, args=[self.image_name])
        thread.daemon = True
        thread.start()

        time.sleep(2)

        server_response = urllib.request.urlopen("http://localhost:9294/myendpoint1").read()

        self.assertEqual("b'1'", str(server_response))

    def __remove_containers(self):
        print(f'Stopping containers with image: {self.image_name}')

        all_containers = self.docker_client.containers
        matching_containers = all_containers.list(filters={'ancestor': self.image_name})

        for container in matching_containers:
            container_id = container.id
            print(f'Stopping container {container_id}')
            self.docker_client.api.stop(container_id)
            print(f'Removing container {container_id}')
            self.docker_client.api.remove_container(container_id)

        self.docker_client.containers.prune()

    def __run_container(self, image_name):
        try:
            print(f'Running container for image: {image_name}')
            self.docker_client.containers.run(image_name, ports={'80/tcp': 9294})
        except Exception as err:
            print(err)
            pass

    @staticmethod
    def __create_conf(task_id):
        return {
            'task': task_id,
            'cmd': 'foo bar',
            'image': 'rainbow_server_image',
            'source': 'tests/runners/airflow/rainbow/myserver',
            'input_type': 'my_input_type',
            'input_path': 'my_input',
            'output_path': '/my_output.json',
            'endpoints': [
                {
                    'endpoint': '/myendpoint1',
                    'module': 'my_server',
                    'function': 'myendpoint1func'
                }
            ]
        }


if __name__ == '__main__':
    unittest.main()
