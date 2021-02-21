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
import unittest
from unittest import TestCase

import docker

from liminal.build import liminal_apps_builder

class TestLiminalAppsBuilder(TestCase):
    __image_names = [
        'my_python_task_img',
        'my_parallelized_python_task_img'
    ]

    def setUp(self) -> None:
        self.docker_client = docker.client.from_env()
        self.__remove_images()

    def tearDown(self) -> None:
        self.__remove_images()
        self.docker_client.close()

    def __remove_images(self):
        for image_name in self.__image_names:
            if len(self.docker_client.images.list(image_name)) > 0:
                self.docker_client.images.remove(image=image_name, force=True)

    def test_build_liminal(self):
        liminal_apps_builder.build_liminal_apps(
            os.path.join(os.path.dirname(__file__), '../liminal'))

        for image in self.__image_names:
            self.docker_client.images.get(image)


if __name__ == '__main__':
    unittest.main()
