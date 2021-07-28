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
import shutil
import tempfile
from unittest import TestCase

import docker

from liminal.build.image.spark.spark import SparkImageBuilder


class TestSparkImageBuilder(TestCase):
    __IMAGE_NAME = 'my_spark_image'

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
        self.assertTrue('RUN pip install -r requirements.txt' in build_out,
                        'Incorrect pip command')

        self.__test_image()

    def __test_build(self):
        config = self.__create_conf('my_task')

        base_path = os.path.join(os.path.dirname(__file__), '../../../apps/test_spark_app')

        builder = SparkImageBuilder(config=config,
                                    base_path=base_path,
                                    relative_source_path='wordcount',
                                    tag=self.__IMAGE_NAME)

        build_out = str(builder.build())

        return build_out

    def __test_image(self):
        docker_client = docker.from_env()
        docker_client.images.get(self.__IMAGE_NAME)

        cmds = ['spark-submit', 'wordcount.py', 'words.txt', '/mnt/vol1/outputs']

        container_log = docker_client.containers.run(self.__IMAGE_NAME,
                                                     cmds,
                                                     volumes={
                                                         self.temp_dir: {
                                                             'bind': '/mnt/vol1',
                                                             'mode': 'rw'
                                                         }
                                                     })

        docker_client.close()

        logging.info(container_log)

        self.assertEqual(
            "b'\\n"
            "my: 1\\n"
            "first: 1\\n"
            "liminal: 1\\n"
            "spark: 1\\n"
            "task: 1\\n"
            "writing the results to /mnt/vol1/outputs\\n'",
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
