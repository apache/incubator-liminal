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
import shutil
import tempfile
import docker
from unittest import TestCase
from liminal.build.image.python.python import PythonImageBuilder
import logging

class TestPythonImageBuilder(TestCase):
    __IMAGE_NAME = 'my_python_task_img'

    def setUp(self) -> None:
        super().setUp()
        os.environ['TMPDIR'] = '/tmp'
        self.temp_dir = self.__temp_dir()
        self.temp_airflow_dir = self.__temp_dir()

    def tearDown(self) -> None:
        super().tearDown()
        self.__remove_dir(self.temp_dir)
        self.__remove_dir(self.temp_airflow_dir)

    def test_build(self):
        build_out = self.__test_build()

        self.assertTrue('RUN pip install -r requirements.txt' in build_out, 'Incorrect pip command')

        self.__test_image()

    def test_build_with_pip_conf(self):
        build_out = self.__test_build(use_pip_conf=True)

        self.assertTrue(
            'RUN --mount=type=secret,id=pip_config,dst=/etc/pip.conf  pip install' in build_out,
            'Incorrect pip command')

        self.__test_image()

    def __test_build(self, use_pip_conf=False):
        config = self.__create_conf('my_task')

        base_path = os.path.join(os.path.dirname(__file__), '../../liminal')

        if use_pip_conf:
            config['pip_conf'] = os.path.join(base_path, 'pip.conf')

        builder = PythonImageBuilder(config=config,
                                     base_path=base_path,
                                     relative_source_path='write_inputs',
                                     tag=self.__IMAGE_NAME)

        build_out = str(builder.build())

        return build_out

    def __test_image(self):
        docker_client = docker.from_env()
        docker_client.images.get(self.__IMAGE_NAME)

        cmds = ['/bin/bash', '-c', 'python write_inputs.py']

        container_log = docker_client.containers.run(self.__IMAGE_NAME,
                                                     cmds,
                                                     volumes={
                                                         self.temp_dir: {
                                                             'bind': '/mnt/vol1',
                                                             'mode': 'rw'
                                                         }
                                                     },
                                                     environment={
                                                         'NUM_FILES': 10,
                                                         'NUM_SPLITS': 3
                                                     })

        docker_client.close()

        logging.info(container_log)

        self.assertEqual(
            "b'"
            "Writing input file /mnt/vol1/inputs/0/input0.json\\n"
            "Writing input file /mnt/vol1/inputs/1/input1.json\\n"
            "Writing input file /mnt/vol1/inputs/2/input2.json\\n"
            "Writing input file /mnt/vol1/inputs/0/input3.json\\n"
            "Writing input file /mnt/vol1/inputs/1/input4.json\\n"
            "Writing input file /mnt/vol1/inputs/2/input5.json\\n"
            "Writing input file /mnt/vol1/inputs/0/input6.json\\n"
            "Writing input file /mnt/vol1/inputs/1/input7.json\\n"
            "Writing input file /mnt/vol1/inputs/2/input8.json\\n"
            "Writing input file /mnt/vol1/inputs/0/input9.json\\n"
            "'",
            str(container_log))

    def __create_conf(self, task_id):
        return {
            'task': task_id,
            'cmd': 'foo bar',
            'image': self.__IMAGE_NAME,
            'source': 'baz',
            'no_cache': True,
        }

    @staticmethod
    def __temp_dir():
        temp_dir = tempfile.mkdtemp()
        return temp_dir

    @staticmethod
    def __remove_dir(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)