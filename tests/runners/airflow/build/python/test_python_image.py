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

import docker

from rainbow.docker.python import python_image


def test_build(self):
    config = self.__create_conf('my_task')

    image_name = config['image']

    python_image.build('tests/runners/airflow/rainbow', 'hello_world', 'image_name')

    # TODO: elaborate test of image, validate input/output

    docker_client = docker.from_env()
    docker_client.images.get(image_name)
    container_log = docker_client.containers.run(image_name, "python hello_world.py")
    docker_client.close()

    self.assertEqual("b'Hello world!\\n'", str(container_log))
