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

import json
import logging
import os
import threading
import time
import unittest
import urllib.request
from unittest import TestCase

import docker

from liminal.build.image.python_server.python_server import PythonServerImageBuilder
from liminal.build.python import PythonImageVersions

IMAGE_NAME = 'liminal_server_image'


class TestPythonServer(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.docker_client = docker.from_env()
        self.config = self.__create_conf()
        self.__remove_containers()

    def tearDown(self) -> None:
        self.__remove_containers()
        self.docker_client.close()

    def test_build_python_server(self):
        versions = list(PythonImageVersions().supported_versions)
        for version in versions:
            build_out = self.__test_build_python_server(python_version=version)
            self.assertTrue('RUN pip install -r requirements.txt' in build_out, 'Incorrect pip command')

    def test_build_python_server_with_pip_conf(self):
        build_out = self.__test_build_python_server(use_pip_conf=True)

        self.assertTrue(
            'RUN --mount=type=secret,id=pip_config,dst=/etc/pip.conf  pip install' in build_out,
            'Incorrect pip command',
        )

    def __test_build_python_server(self, use_pip_conf=False, python_version=None):
        base_path = os.path.join(os.path.dirname(__file__), '../../../liminal')

        config = self.__create_conf()

        if use_pip_conf:
            config['pip_conf'] = os.path.join(base_path, 'pip.conf')

        if python_version:
            config['python_version'] = python_version

        builder = PythonServerImageBuilder(
            config=config, base_path=base_path, relative_source_path='myserver', tag=IMAGE_NAME
        )

        build_out = str(builder.build())

        thread = threading.Thread(target=self.__run_container)
        thread.start()

        time.sleep(20)

        logging.info('Sending request to server')

        json_string = '{"key1": "val1", "key2": "val2"}'

        encoding = 'ascii'

        server_response = str(
            urllib.request.urlopen('http://localhost:9294/myendpoint1', data=json_string.encode(encoding))
            .read()
            .decode(encoding)
        )

        logging.info(f'Response from server: {server_response}')

        self.assertEqual(f'Input was: {json.loads(json_string)}', server_response)

        server_favicon_response = urllib.request.urlopen('http://localhost:9294/favicon.ico')

        self.assertEqual(204, server_favicon_response.status)

        self.__remove_containers()

        return build_out

    def __remove_containers(self):
        logging.info(f'Stopping containers with image: {IMAGE_NAME}')

        matching_containers = self.__get_docker_containers()

        for container in matching_containers:
            container_id = container.id
            logging.info(f'Stopping container {container_id}')
            self.docker_client.api.stop(container_id)
            logging.info(f'Removing container {container_id}')
            self.docker_client.api.remove_container(container_id)

        while len(matching_containers) > 0:
            matching_containers = self.__get_docker_containers()

    def __get_docker_containers(self):
        return self.docker_client.containers.list(filters={'ancestor': IMAGE_NAME})

    def __run_container(self):
        try:
            logging.info(f'Running container for image: {IMAGE_NAME}')
            self.docker_client.containers.run(IMAGE_NAME, ports={'80/tcp': 9294}, detach=True)
        except Exception as err:
            logging.exception(err)
            pass

    @staticmethod
    def __create_conf():
        return {
            'image': IMAGE_NAME,
            'cmd': 'foo bar',
            'source': 'baz',
            'input_type': 'my_input_type',
            'input_path': 'my_input',
            'output_path': '/my_output.json',
            'no_cache': True,
            'endpoints': [{'endpoint': '/myendpoint1', 'module': 'my_server', 'function': 'myendpoint1func'}],
        }


if __name__ == '__main__':
    unittest.main()
